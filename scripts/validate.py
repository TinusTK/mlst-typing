#!/usr/bin/env python3
"""
validate.py - type every genome in validation/genomes.tsv with mlst-typing
(and, if --upstream is given, with Torsten Seemann's mlst on the same
database) and write validation/results_<DB>.tsv and validation/REPORT.md.

    python scripts/validate.py [--upstream Local/upstream-mlst/bin/mlst] [--jobs 6]

A genome "matches" when both tools give the same --full row (scheme, ST,
status, score, alleles). Any mismatch is listed in the report.
"""

import argparse
import csv
import datetime as dt
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = [sys.executable, os.path.join(ROOT, "tool", "mlst_typing.py")]


def full_row(cmd, path):
    r = subprocess.run(cmd + ["-q", "--full", path], capture_output=True, text=True)
    if r.returncode != 0:
        return None, r.stderr.strip()[-300:]
    lines = r.stdout.strip().splitlines()
    return (lines[1].split("\t")[1:] if len(lines) > 1 else None), ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", default=os.path.join(ROOT, "database"))
    ap.add_argument("--upstream", help="path to upstream mlst (bin/mlst) to compare with")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    vdir = os.path.join(ROOT, "validation")
    with open(os.path.join(vdir, "genomes.tsv")) as fh:
        genomes = list(csv.DictReader(fh, delimiter="\t"))
    with open(os.path.join(args.db, "VERSION.txt")) as fh:
        version = fh.read().strip()
    ours = TOOL + ["--db", args.db]
    theirs = ([args.upstream, "--blastdb", os.path.join(args.db, "blast", "mlst.fa"),
               "--datadir", os.path.join(args.db, "pubmlst")] if args.upstream else None)

    def one(g):
        path = os.path.join(vdir, "genomes", f"{g['accession']}.fna.gz")
        if not g["accession"] or not os.path.exists(path):
            return g, None, None, "no genome"
        a, e1 = full_row(ours, path)
        b, e2 = full_row(theirs, path) if theirs else (None, "")
        print(f"{g['scheme']}\t{g['accession']}\t{a[:2] if a else e1}", file=sys.stderr)
        return g, a, b, e1 or e2

    with ThreadPoolExecutor(args.jobs) as ex:
        results = list(ex.map(one, genomes))

    out = os.path.join(vdir, f"results_{version}.tsv")
    cols = ["expected_scheme", "accession", "organism", "scheme", "ST", "status",
            "score", "alleles", "upstream_same", "note"]
    n = dict(typed=0, expected=0, perfect=0, same=0, tie=0, diff=0, missing=0)
    diffs, ties, wrong, nogenome = [], [], [], []
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(cols)
        for g, a, b, note in results:
            if a is None:
                n["missing"] += 1
                nogenome.append(f"{g['scheme']} ({g['taxon'] or 'no taxon'}): {note}")
                w.writerow([g["scheme"], g["accession"], g["organism"], "", "", "", "", "",
                            "", note])
                continue
            n["typed"] += 1
            n["expected"] += a[0] == g["scheme"]
            n["perfect"] += a[2] == "PERFECT"
            if a[0] != g["scheme"]:
                wrong.append(f"{g['scheme']}: {g['accession']} {g['organism']} -> {a[0]} {a[1]} {a[2]}")
            same = ""
            if theirs:
                if a == b:
                    same = "yes"
                elif b and a[3] == b[3]:
                    # equal top scores: mlst picks one of the tied schemes at
                    # random, mlst-typing always the first by name
                    same = "tie"
                    ties.append(f"{g['accession']} ({g['scheme']}): mlst-typing "
                                f"{a[0]} ST{a[1]} / mlst {b[0]} ST{b[1]} (score {a[3]})")
                else:
                    same = "NO"
                    diffs.append(f"{g['accession']} ({g['scheme']}): mlst-typing {a[:4]} vs mlst {b[:4] if b else b}")
                n[{"yes": "same", "tie": "tie", "NO": "diff"}[same]] += 1
            w.writerow([g["scheme"], g["accession"], g["organism"], *a, same,
                        g.get("note", "")])

    priority = [(g, a) for g, a, _, _ in results if g.get("note", "").startswith("priority")]
    lines = [f"# Validation, database {version}", "",
             f"Run {dt.date.today().isoformat()}: {len(genomes)} genomes listed "
             f"(one public NCBI assembly per scheme + priority organisms).", "",
             f"- Typed: {n['typed']} ({n['missing']} without a genome)",
             f"- Called the scheme the genome was picked for: {n['expected']}/{n['typed']}",
             f"- PERFECT (full ST): {n['perfect']}/{n['typed']}"]
    if theirs:
        total = n["same"] + n["tie"] + n["diff"]
        lines += [f"- Same result as upstream mlst on the same database: **{n['same']}/{total}**",
                  f"- Ties (two schemes with the same top score; mlst picks one at random, "
                  f"mlst-typing the first by name): {n['tie']}/{total}",
                  f"- Real differences: **{n['diff']}/{total}**"]
    lines += ["", "## Priority organisms", "", "| Genome | Scheme | ST | Status | Alleles |",
              "|---|---|---|---|---|"]
    for g, a in priority:
        if a:
            lines.append(f"| {g['taxon']} ({g['accession']}) | {a[0]} | {a[1]} | {a[2]} | {a[4]} |")
        else:
            lines.append(f"| {g['taxon']} ({g['accession']}) | not run | | | |")
    for title, items in (("Real differences from upstream mlst", diffs),
                         ("Ties (both tools agree on the score; scheme choice differs)", ties),
                         ("Other scheme called than the one picked for", wrong),
                         ("Schemes without a validation genome", nogenome)):
        lines += ["", f"## {title} ({len(items)})", ""]
        lines += [f"- {x}" for x in items] or ["None."]
    with open(os.path.join(vdir, "REPORT.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Wrote {out} and validation/REPORT.md", file=sys.stderr)
    return 1 if n["diff"] else 0


if __name__ == "__main__":
    sys.exit(main())
