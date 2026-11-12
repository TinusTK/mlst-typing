#!/usr/bin/env python3
"""
mlst_typing_update.py - rebuild database/ for mlst-typing from PubMLST,
BIGSdb-Pasteur and EnteroBase, then write a change summary. Run it as
scripts/update_database.py (same options):

    python scripts/update_database.py --db database --summary CHANGES_DB.md
    python scripts/update_database.py --db database --source enterobase

For every scheme listed in database/schemes.tsv it downloads
  - the allele FASTA of each locus   -> <folder>/<scheme>/<locus>.tfa
  - the ST profiles (ST + loci only) -> <folder>/<scheme>/<scheme>.txt
PubMLST and BIGSdb-Pasteur schemes (BIGSdb REST API) go to pubmlst/ and the
BLAST database blast/mlst.fa.*; EnteroBase schemes (its public scheme
folders, source "enterobase" in schemes.tsv) go to enterobase/ and
blast/enterobase.fa.*. The two are kept apart so the tool can type against
each source on its own. It also writes manifest.tsv (per-scheme counts,
taxon, last_updated) and VERSION.txt (line 1 PubMLST, line 2 EnteroBase).

Data access
-----------
Without authentication both servers only return data submitted up to
31 Dec 2024 (the standard, freely available data), and that is all this
script fetches by itself. Newer PubMLST data needs the user's own account
and key: `mlst-typing --setup` (mlst_typing_setup.py) sets SIGNER below and
runs this updater on a private copy of the database, outside the repo (see
database/README.md).

Exit codes: 0 = updated (changes written), 3 = no changes, other = error.
"""

import argparse
import csv
import datetime as dt
import email.utils
import gzip
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

NO_CHANGES = 3
USER_AGENT = "mlst-typing-updater"
# Columns in profiles_csv that are not loci
NOT_LOCI = {"ST"}


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

# Requests with the user's own PubMLST key, only set by mlst_typing_setup.py:
# an object with wants(url) -> bool, apply(url) -> (url, extra headers) and
# renew() -> get a new OAuth session token. None = no login (free data).
SIGNER = None


def http_get(url, retries=4, pause=0.2, raw=False):
    """Text of url; with raw=True (bytes, Last-Modified header or '')."""
    signed = SIGNER is not None and SIGNER.wants(url)
    renewed = False
    attempt = 0
    while True:
        try:
            target, extra = SIGNER.apply(url) if signed else (url, {})
            req = urllib.request.Request(target,
                                         headers={"User-Agent": USER_AGENT, **extra})
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = resp.read()
                modified = resp.headers.get("Last-Modified", "")
            time.sleep(pause)  # be gentle with the public API
            return (data, modified) if raw else data.decode("utf-8")
        except urllib.error.HTTPError as e:
            # signed request refused: the session token (12 h) may have run
            # out, so renew it once; after that the account has no access
            if signed and e.code in (401, 403):
                if e.code == 401 and not renewed:
                    renewed = True
                    SIGNER.renew()
                    continue
                raise RuntimeError(f"GET {url} refused (HTTP {e.code})") from e
            attempt += 1
            if attempt >= retries:
                raise RuntimeError(f"GET {url} failed: {e}") from e
            time.sleep(5 * attempt)
        except Exception as e:  # noqa: BLE001
            attempt += 1
            if attempt >= retries:
                raise RuntimeError(f"GET {url} failed: {e}") from e
            time.sleep(5 * attempt)


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


def fetch_enterobase(row, outdir):
    """Download one EnteroBase scheme folder into outdir/<scheme>/.

    row["api"] is the public folder, e.g.
    https://enterobase.warwick.ac.uk/schemes/Escherichia.Achtman7GeneMLST
    holding profiles.list.gz (TAB: ST + loci) and <locus>.fasta.gz
    (headers >locus_N). Returns a manifest dict.
    """
    name, url = row["scheme"], row["api"].rstrip("/")
    data, modified = http_get(f"{url}/profiles.list.gz", raw=True)
    prof = gzip.decompress(data).decode("utf-8")
    rows = [r for r in csv.reader(io.StringIO(prof), delimiter="\t") if r]
    header = rows[0] if rows else []
    if not header or header[0] != "ST" or len(header) < 2:
        raise RuntimeError(f"{name}: unexpected profiles header {header[:12]}")
    loci = header[1:]
    sdir = os.path.join(outdir, name)
    os.makedirs(sdir)

    n_alleles = 0
    for locus in loci:
        gz, _ = http_get(f"{url}/{locus}.fasta.gz", raw=True)
        fasta, ids = normalise_fasta(gzip.decompress(gz).decode("utf-8"), locus)
        if not ids:
            raise RuntimeError(f"{name}: no alleles for locus {locus}")
        with open(os.path.join(sdir, f"{locus}.tfa"), "w") as fh:
            fh.write(fasta)
        n_alleles += len(ids)

    with open(os.path.join(sdir, f"{name}.txt"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["ST"] + loci)
        n_prof = 0
        for r in rows[1:]:
            if not r[0]:
                continue
            w.writerow([r[0]] + [r[i] if i < len(r) else "" for i in range(1, len(loci) + 1)])
            n_prof += 1

    try:
        updated = email.utils.parsedate_to_datetime(modified).date().isoformat()
    except (TypeError, ValueError):
        updated = dt.date.today().isoformat()
    return dict(scheme=name, source=row["source"], loci=len(loci),
                alleles=n_alleles, profiles=n_prof, last_updated=updated,
                taxon=" ".join(x for x in (row["genus"], row["species"]) if x),
                api=url, restricted=False)


# Where each source lives: schemes folder and BLAST database name.
ENTEROBASE = "enterobase"
FOLDERS = {"pubmlst": "mlst.fa", ENTEROBASE: "enterobase.fa"}


def folder_of(source):
    """pubmlst and pasteur schemes share pubmlst/; EnteroBase has its own."""
    return ENTEROBASE if source == ENTEROBASE else "pubmlst"


# --------------------------------------------------------------------------
# BLAST database
# --------------------------------------------------------------------------

def build_blastdb(pubmlst_dir, blast_dir, name="mlst.fa"):
    os.makedirs(blast_dir, exist_ok=True)
    fa = os.path.join(blast_dir, name)
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
        lines += ["PubMLST and BIGSdb-Pasteur data is the **standard, freely "
                  "available** set: alleles and profiles submitted up to "
                  "**31 Dec 2024** (no authentication).", ""]
    n_eb = sum(m["source"] == ENTEROBASE for m in man)
    if n_eb:
        lines += [f"EnteroBase: {n_eb} schemes from its public scheme folders "
                  "(current data).", ""]
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

def old_row(old_man, name):
    """Manifest row of the previous database, typed like a fresh one."""
    m = dict(old_man[name])
    for k in ("loci", "alleles", "profiles"):
        m[k] = int(m[k])
    m["restricted"] = m.get("restricted") == "True"
    return m


def read_version(db):
    """(PubMLST label, EnteroBase label) from VERSION.txt; '' when missing."""
    try:
        with open(os.path.join(db, "VERSION.txt")) as fh:
            lines = [l.strip() for l in fh if l.strip()]
    except OSError:
        lines = []
    return (lines + ["", ""])[0], (lines + ["", ""])[1]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="update_database.py",
                                 description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", default="database", help="database folder [database]")
    ap.add_argument("--schemes", help="scheme list [<db>/schemes.tsv]")
    ap.add_argument("--only", help="comma-separated scheme names (for testing)")
    ap.add_argument("--source", choices=["all", "pubmlst", ENTEROBASE], default="all",
                    help="refresh only this part; the other is kept as it is [all]")
    ap.add_argument("--version-label",
                    help="VERSION.txt line 1, set when PubMLST schemes changed "
                         "[PubMLST_<YYYY-MM-DD>]")
    ap.add_argument("--enterobase-label",
                    help="VERSION.txt line 2, set when EnteroBase schemes changed "
                         "[EnteroBase_<YYYY-MM-DD>]")
    ap.add_argument("--summary", help="write a Markdown change summary here")
    args = ap.parse_args(argv)

    db = os.path.abspath(args.db)
    rows = read_scheme_list(args.schemes or os.path.join(db, "schemes.tsv"))
    want = set(args.only.split(",")) if args.only else None
    fetch = [r for r in rows
             if args.source in ("all", folder_of(r["source"]))
             and (want is None or r["scheme"] in want)]
    if shutil.which("makeblastdb") is None:
        sys.exit("makeblastdb not found (install BLAST+)")

    old_man = read_manifest(os.path.join(db, "manifest.tsv"))
    tmp = tempfile.mkdtemp(prefix="mlstdb_", dir=db)
    for folder in FOLDERS:
        os.makedirs(os.path.join(tmp, folder))
    man, failed = [], []
    try:
        for i, row in enumerate(fetch, 1):
            name, folder = row["scheme"], folder_of(row["source"])
            new_dir, old = os.path.join(tmp, folder), os.path.join(db, folder, name)
            print(f"[{i}/{len(fetch)}] {name}", file=sys.stderr)
            try:
                fetcher = fetch_enterobase if folder == ENTEROBASE else fetch_scheme
                man.append(fetcher(row, new_dir))
            except Exception as e:  # noqa: BLE001
                failed.append((name, str(e)[:200]))
                print(f"  FAILED: {e}", file=sys.stderr)
                shutil.rmtree(os.path.join(new_dir, name), ignore_errors=True)
                if os.path.isdir(old):
                    shutil.copytree(old, os.path.join(new_dir, name))
                    if name in old_man:
                        man.append(old_row(old_man, name))
        # partial run (--only or --source): carry over every scheme not fetched
        for folder in FOLDERS:
            old_dir, new_dir = os.path.join(db, folder), os.path.join(tmp, folder)
            partial = want is not None or args.source not in ("all", folder)
            if not (partial and os.path.isdir(old_dir)):
                continue
            done = {m["scheme"] for m in man}
            for s in os.listdir(old_dir):
                if s not in done and s not in os.listdir(new_dir):
                    shutil.copytree(os.path.join(old_dir, s), os.path.join(new_dir, s))
                    if s in old_man:
                        man.append(old_row(old_man, s))

        added, removed, changed, touched = [], [], [], set()
        for folder in FOLDERS:
            a, r, c = compare(os.path.join(db, folder), os.path.join(tmp, folder))
            added, removed, changed = added + a, removed + r, changed + c
            if a or r or c:
                touched.add(folder)
        if not touched and os.path.isdir(os.path.join(db, "pubmlst")):
            print("No changes.", file=sys.stderr)
            return NO_CHANGES

        # BLAST databases: rebuild a source only when its schemes changed
        today = dt.date.today().isoformat()
        old_pub_label, old_eb_label = read_version(db)
        labels = {"pubmlst": old_pub_label, ENTEROBASE: old_eb_label}
        blast_new = os.path.join(tmp, "blast")
        os.makedirs(blast_new)
        for folder, fa in FOLDERS.items():
            old_idx = [f for f in os.listdir(os.path.join(db, "blast"))
                       if f.startswith(fa + ".")] if os.path.isdir(os.path.join(db, "blast")) else []
            if folder not in touched and old_idx:
                for f in old_idx:
                    shutil.copy2(os.path.join(db, "blast", f), blast_new)
            elif os.listdir(os.path.join(tmp, folder)):
                build_blastdb(os.path.join(tmp, folder), blast_new, fa)
            if folder in touched or not labels[folder]:
                labels[folder] = ((args.version_label or f"PubMLST_{today}")
                                  if folder == "pubmlst" else
                                  (args.enterobase_label or f"EnteroBase_{today}"))
        if not os.listdir(os.path.join(tmp, ENTEROBASE)):
            labels[ENTEROBASE] = ""
        version = " + ".join(x for x in (labels["pubmlst"], labels[ENTEROBASE]) if x)

        man.sort(key=lambda m: m["scheme"])
        with open(os.path.join(tmp, "manifest.tsv"), "w", newline="") as fh:
            cols = ["scheme", "source", "loci", "alleles", "profiles",
                    "last_updated", "restricted", "taxon", "api"]
            w = csv.DictWriter(fh, cols, delimiter="\t", lineterminator="\n",
                               extrasaction="ignore")
            w.writeheader()
            w.writerows(man)
        with open(os.path.join(tmp, "VERSION.txt"), "w") as fh:
            fh.write("".join(x + "\n" for x in (labels["pubmlst"], labels[ENTEROBASE]) if x))

        # swap in
        for part in ("pubmlst", ENTEROBASE, "blast", "manifest.tsv", "VERSION.txt"):
            dst = os.path.join(db, part)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            elif os.path.exists(dst):
                os.remove(dst)
            if part == ENTEROBASE and not os.listdir(os.path.join(tmp, part)):
                continue
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
