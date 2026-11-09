#!/usr/bin/env python3
"""
pick_validation_genomes.py - choose one free public NCBI assembly for every
scheme in database/manifest.tsv and write validation/genomes.tsv.

    python scripts/pick_validation_genomes.py

Taxon per scheme: validation/taxon_overrides.tsv if listed there, otherwise
the NCBI taxon PubMLST gives for the scheme. For each taxon the NCBI
reference genome is taken; failing that a complete genome; failing that any
assembly. Extra genomes (TK's priority organisms) come from
validation/extra_genomes.tsv and are appended unchanged.

Needs the NCBI `datasets` CLI.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_tsv(path):
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return list(csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t"))


def schemes_from_api(schemes_tsv):
    """Fallback before manifest.tsv exists: taxon straight from each scheme's API record."""
    rows = []
    for r in read_tsv_plain(schemes_tsv):
        taxon = ""
        try:
            req = urllib.request.Request(r[2], headers={"User-Agent": "mlst-typing-validation"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                info = json.loads(resp.read())
            taxon = "; ".join(t.get("name", "") for t in info.get("ncbi_taxon") or [])
        except Exception as e:  # noqa: BLE001
            print(f"{r[0]}: no taxon ({e})", file=sys.stderr)
        rows.append({"scheme": r[0], "taxon": taxon})
    return rows


def read_tsv_plain(path):
    with open(path) as fh:
        return [l.rstrip("\n").split("\t") for l in fh if l.strip() and not l.startswith("#")]


def first_assembly(taxon, *flags, source="RefSeq"):
    cmd = ["datasets", "summary", "genome", "taxon", taxon, "--limit", "1",
           "--as-json-lines", *flags] + (["--assembly-source", source] if source else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    line = r.stdout.strip().splitlines()[:1]
    if r.returncode != 0 or not line:
        return None
    d = json.loads(line[0])
    return d["accession"], d["organism"]["organism_name"], d["assembly_info"]["assembly_level"]


def pick(taxon):
    for flags in (["--reference"], ["--assembly-level", "complete"], []):
        hit = first_assembly(taxon, *flags)
        if hit:
            return hit
    return first_assembly(taxon, source=None)   # GenBank-only taxa (e.g. fungi)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--manifest", default=os.path.join(ROOT, "database", "manifest.tsv"))
    ap.add_argument("--outdir", default=os.path.join(ROOT, "validation"))
    args = ap.parse_args()

    over = {r["scheme"]: r["taxon"] for r in read_tsv(os.path.join(args.outdir, "taxon_overrides.tsv"))}
    rows = []
    if os.path.exists(args.manifest):
        schemes = read_tsv(args.manifest)
    else:
        schemes = schemes_from_api(os.path.join(ROOT, "database", "schemes.tsv"))
    for m in schemes:
        s = m["scheme"]
        taxon = over.get(s) or (m["taxon"].split(";")[0].strip() if m["taxon"] else "")
        hit = pick(taxon) if taxon else None
        acc, org, level = hit if hit else ("", "", "")
        print(f"{s}\t{taxon}\t{acc}\t{org}", file=sys.stderr)
        rows.append(dict(scheme=s, taxon=taxon, accession=acc, organism=org,
                         level=level, note="" if hit else "no NCBI assembly found"))
    for e in read_tsv(os.path.join(args.outdir, "extra_genomes.tsv")):
        rows.append(dict(scheme=e["scheme"], taxon=e["taxon"], accession=e["accession"],
                         organism=e["taxon"], level="", note=e.get("note", "priority")))

    out = os.path.join(args.outdir, "genomes.tsv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, ["scheme", "taxon", "accession", "organism", "level", "note"],
                           delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    missing = sum(1 for r in rows if not r["accession"])
    print(f"Wrote {out}: {len(rows)} rows, {missing} without a genome", file=sys.stderr)


if __name__ == "__main__":
    main()
