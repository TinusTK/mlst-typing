#!/usr/bin/env python3
"""
update_database.py - rebuild database/ for mlst-typing from PubMLST and
BIGSdb-Pasteur, then write a change summary.

    python scripts/update_database.py --db database --summary CHANGES_DB.md

For every scheme listed in database/schemes.tsv it downloads, through the
BIGSdb REST API:
  - the allele FASTA of each locus   -> pubmlst/<scheme>/<locus>.tfa
  - the ST profiles (ST + loci only) -> pubmlst/<scheme>/<scheme>.txt
then joins all alleles into one BLAST database (blast/mlst.fa.*) and writes
manifest.tsv (per-scheme counts, taxon, last_updated) and VERSION.txt.

Data access
-----------
Without authentication both servers only return data submitted up to
31 Dec 2024 (the standard, freely available data). Authenticated access to
newer data is not wired in yet: it depends on PubMLST's terms (see
database/README.md).

Exit codes: 0 = updated (changes written), 3 = no changes, other = error.
"""

import argparse
import csv
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

NO_CHANGES = 3
USER_AGENT = "mlst-typing-updater"
# Columns in profiles_csv that are not loci
NOT_LOCI = {"ST"}


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def http_get(url, retries=4, pause=0.2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = resp.read().decode("utf-8")
            time.sleep(pause)  # be gentle with the public API
            return data
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise RuntimeError(f"GET {url} failed: {e}") from e
            time.sleep(5 * (attempt + 1))


def http_json(url):
    return json.loads(http_get(url))


# --------------------------------------------------------------------------
# Scheme list
# --------------------------------------------------------------------------

def read_scheme_list(path):
    """schemes.tsv -> list of dicts (scheme, source, api, genus, species)."""
    rows = []
    with open(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            f += [""] * (5 - len(f))
            rows.append(dict(scheme=f[0], source=f[1], api=f[2],
                             genus=f[3], species=f[4]))
    names = [r["scheme"] for r in rows]
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        raise RuntimeError(f"duplicate scheme names in {path}: {sorted(dup)}")
    return rows


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def normalise_fasta(text, locus):
    """Rewrite headers to >{locus}_{allele_id}; return (fasta, ids)."""
    out, ids = [], []
    prefix = locus + "_"
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            raw = line[1:].split()[0]
            allele = raw[len(prefix):] if raw.startswith(prefix) else raw.rsplit("_", 1)[-1]
            ids.append(allele)
            out.append(f">{locus}_{allele}")
        else:
            out.append(line.upper())
    return ("\n".join(out) + "\n") if out else "", ids


def fetch_scheme(row, outdir):
    """Download one scheme into outdir/<scheme>/. Returns manifest dict."""
    name, url = row["scheme"], row["api"].rstrip("/")
    info = http_json(url)
    loci = [u.rstrip("/").split("/")[-1] for u in info["loci"]]
    sdir = os.path.join(outdir, name)
    os.makedirs(sdir)

    n_alleles = 0
    for locus in loci:
        fasta, ids = normalise_fasta(http_get(f"{url.split('/schemes/')[0]}/loci/{locus}/alleles_fasta"), locus)
        with open(os.path.join(sdir, f"{locus}.tfa"), "w") as fh:
            fh.write(fasta)
        n_alleles += len(ids)

    # profiles_csv is tab-delimited despite the name. Keep ST + loci only,
    # in the server's column order (extra columns such as clonal_complex,
    # species or MLST_cluster are not loci).
    prof = http_get(info.get("profiles_csv") or f"{url}/profiles_csv")
    rows = [r for r in csv.reader(io.StringIO(prof), delimiter="\t") if r]
    header = rows[0] if rows else ["ST"] + loci
    # the ST column is the scheme's primary key; a few schemes call it
    # something else (mhominis_3: eST). mlst expects "ST".
    pk = (info.get("primary_key_field") or "").rstrip("/").split("/")[-1]
    if header and pk and header[0] == pk and pk != "ST":
        header = ["ST"] + header[1:]
    if header[0] != "ST" or any(l not in header for l in loci):
        raise RuntimeError(f"{name}: unexpected profiles header {header[:12]}")
    order = [l for l in header if l in loci]
    idx = [header.index(l) for l in order]
    with open(os.path.join(sdir, f"{name}.txt"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["ST"] + order)
        n_prof = 0
        for r in rows[1:]:
            if not r[0]:
                continue
            w.writerow([r[0]] + [r[i] if i < len(r) else "" for i in idx])
            n_prof += 1

    taxa = info.get("ncbi_taxon") or []
    taxon = "; ".join(t.get("name", "") for t in taxa)
    return dict(scheme=name, source=row["source"], loci=len(loci),
                alleles=n_alleles, profiles=n_prof,
                last_updated=info.get("last_updated", ""),
                taxon=taxon or " ".join(x for x in (row["genus"], row["species"]) if x),
                api=url,
                restricted="restricted" in info.get("message", "")
                           or "2024-12-31" in info.get("message", ""))


# --------------------------------------------------------------------------
# BLAST database
# --------------------------------------------------------------------------

def build_blastdb(pubmlst_dir, blast_dir):
    os.makedirs(blast_dir, exist_ok=True)
    fa = os.path.join(blast_dir, "mlst.fa")
    with open(fa, "w") as out:
        for scheme in sorted(os.listdir(pubmlst_dir)):
            sdir = os.path.join(pubmlst_dir, scheme)
            if not os.path.isdir(sdir):
                continue
            for tfa in sorted(f for f in os.listdir(sdir) if f.endswith(".tfa")):
                with open(os.path.join(sdir, tfa)) as fh:
                    for line in fh:
                        if "not a locus" in line:
                            continue
                        out.write(">" + scheme + "." + line[1:] if line.startswith(">") else line)
    subprocess.run(["makeblastdb", "-hash_index", "-in", fa, "-dbtype", "nucl",
                    "-title", "mlst-typing", "-parse_seqids"],
                   check=True, stdout=subprocess.DEVNULL)
    os.remove(fa)  # the index holds the sequences; keep the repo smaller


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

def read_manifest(path):
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        return {r["scheme"]: r for r in csv.DictReader(fh, delimiter="\t")}


def scheme_digest(sdir):
    """Content of a scheme folder, for change detection."""
    out = {}
    for f in sorted(os.listdir(sdir)):
        with open(os.path.join(sdir, f)) as fh:
            out[f] = fh.read()
    return out


def compare(old_pub, new_pub):
    old = set(os.listdir(old_pub)) if os.path.isdir(old_pub) else set()
    new = set(os.listdir(new_pub))
    changed = sorted(s for s in old & new
                     if scheme_digest(os.path.join(old_pub, s))
                     != scheme_digest(os.path.join(new_pub, s)))
    return sorted(new - old), sorted(old - new), changed


def write_summary(path, version, man, added, removed, changed, failed):
    restricted = any(m["restricted"] for m in man)
    lines = [f"# Database update {version}", ""]
    if restricted:
        lines += ["Data is the **standard, freely available** set: alleles and "
                  "profiles submitted up to **31 Dec 2024** (no authentication).", ""]
    lines += [f"- Schemes: {len(man)} "
              f"({sum(m['loci'] for m in man)} loci, "
              f"{sum(m['alleles'] for m in man)} alleles, "
              f"{sum(m['profiles'] for m in man)} STs)",
              f"- Added: {', '.join(added) or 'none'}",
              f"- Removed: {', '.join(removed) or 'none'}",
              f"- Changed: {len(changed)}" + (f" ({', '.join(changed)})" if changed else "")]
    if failed:
        lines += ["", "**Failed (kept the previous copy):**", ""]
        lines += [f"- {n}: {e}" for n, e in failed]
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", default="database", help="database folder [database]")
    ap.add_argument("--schemes", help="scheme list [<db>/schemes.tsv]")
    ap.add_argument("--only", help="comma-separated scheme names (for testing)")
    ap.add_argument("--version-label",
                    help="VERSION.txt label [PubMLST_<YYYY-MM-DD>]")
    ap.add_argument("--summary", help="write a Markdown change summary here")
    args = ap.parse_args()

    db = os.path.abspath(args.db)
    rows = read_scheme_list(args.schemes or os.path.join(db, "schemes.tsv"))
    if args.only:
        want = set(args.only.split(","))
        rows = [r for r in rows if r["scheme"] in want]
    if shutil.which("makeblastdb") is None:
        sys.exit("makeblastdb not found (install BLAST+)")

    old_pub = os.path.join(db, "pubmlst")
    old_man = read_manifest(os.path.join(db, "manifest.tsv"))
    tmp = tempfile.mkdtemp(prefix="mlstdb_", dir=db)
    new_pub = os.path.join(tmp, "pubmlst")
    os.makedirs(new_pub)
    man, failed = [], []
    try:
        for i, row in enumerate(rows, 1):
            print(f"[{i}/{len(rows)}] {row['scheme']}", file=sys.stderr)
            try:
                man.append(fetch_scheme(row, new_pub))
            except Exception as e:  # noqa: BLE001
                failed.append((row["scheme"], str(e)[:200]))
                print(f"  FAILED: {e}", file=sys.stderr)
                shutil.rmtree(os.path.join(new_pub, row["scheme"]), ignore_errors=True)
                old = os.path.join(old_pub, row["scheme"])
                if os.path.isdir(old):
                    shutil.copytree(old, os.path.join(new_pub, row["scheme"]))
                    if row["scheme"] in old_man:
                        m = dict(old_man[row["scheme"]])
                        for k in ("loci", "alleles", "profiles"):
                            m[k] = int(m[k])
                        m["restricted"] = m.get("restricted") == "True"
                        man.append(m)
        if args.only and os.path.isdir(old_pub):
            # partial run: carry over every scheme we did not fetch
            done = {m["scheme"] for m in man}
            for s in os.listdir(old_pub):
                if s not in done and s not in os.listdir(new_pub):
                    shutil.copytree(os.path.join(old_pub, s), os.path.join(new_pub, s))
                    if s in old_man:
                        m = dict(old_man[s])
                        for k in ("loci", "alleles", "profiles"):
                            m[k] = int(m[k])
                        m["restricted"] = m.get("restricted") == "True"
                        man.append(m)

        added, removed, changed = compare(old_pub, new_pub)
        if not (added or removed or changed) and os.path.isdir(old_pub):
            print("No changes.", file=sys.stderr)
            return NO_CHANGES

        version = args.version_label or f"PubMLST_{dt.date.today().isoformat()}"
        build_blastdb(new_pub, os.path.join(tmp, "blast"))
        man.sort(key=lambda m: m["scheme"])
        with open(os.path.join(tmp, "manifest.tsv"), "w", newline="") as fh:
            cols = ["scheme", "source", "loci", "alleles", "profiles",
                    "last_updated", "restricted", "taxon", "api"]
            w = csv.DictWriter(fh, cols, delimiter="\t", lineterminator="\n",
                               extrasaction="ignore")
            w.writeheader()
            w.writerows(man)
        with open(os.path.join(tmp, "VERSION.txt"), "w") as fh:
            fh.write(version + "\n")

        # swap in
        for part in ("pubmlst", "blast", "manifest.tsv", "VERSION.txt"):
            dst = os.path.join(db, part)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            elif os.path.exists(dst):
                os.remove(dst)
            shutil.move(os.path.join(tmp, part), dst)
        if args.summary:
            write_summary(args.summary, version, man, added, removed, changed, failed)
        print(f"Database {version}: {len(man)} schemes, "
              f"+{len(added)} -{len(removed)} ~{len(changed)}, {len(failed)} failed",
              file=sys.stderr)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
