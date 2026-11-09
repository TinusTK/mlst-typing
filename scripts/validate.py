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
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = [sys.executable, os.path.join(ROOT, "tool", "mlst_typing.py")]
sys.path.insert(0, os.path.join(ROOT, "tool"))
from mlst_typing import DEFAULT_EXCLUDE  # noqa: E402

EXCLUDED = set(DEFAULT_EXCLUDE.split(","))


TIE = re.compile(r"WARNING: (\S+)\((\S+)\)==(\S+)\((\S+)\) score=(\S+)")


def why_other(g, a, tied):
    """Plain-English reason a genome got another scheme than it was picked for."""
    if a[2] == "NONE":
        return ("NCBI genome is a species the scheme does not cover "
                f"({g['organism'].split(' (')[0]}), so no scheme matches")
    if g["scheme"] in EXCLUDED:
        return f"`{g['scheme']}` is skipped by default (`--exclude`), so the other scheme for this species is used"
    if g["scheme"] in tied:
        return f"Tie with `{g['scheme']}` (same score); the first by name is reported"
    return f"`{a[0]}` scores higher than `{g['scheme']}` for this genome"


def full_row(cmd, path):
    """(--full row without FILE, error, {tied scheme: ST}) for one genome."""
    r = subprocess.run(cmd + ["-q", "--full", path], capture_output=True, text=True)
    if r.returncode != 0:
        return None, r.stderr.strip()[-300:], {}
    lines = r.stdout.rstrip("\n").splitlines()   # keep trailing empty fields
    tied = {}
    for m in TIE.finditer(r.stderr):
        tied[m.group(1)] = m.group(2)
        tied[m.group(3)] = m.group(4)
    row = lines[1].split("\t")[1:] if len(lines) > 1 else None
    warn = ""
    if row and lines[0].endswith("\tWARNINGS"):
        warn = row.pop()   # mlst-typing's extra column; mlst has none
    tied["_warnings"] = warn
    return row, "", tied


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
            return g, None, None, "no genome", {}
        a, e1, tied = full_row(ours, path)
        b, e2, _ = full_row(theirs, path) if theirs else (None, "", {})
        warn = tied.pop("_warnings", "")
        g = dict(g, warnings=warn)
        print(f"{g['scheme']}\t{g['accession']}\t{a[:2] if a else e1}", file=sys.stderr)
        return g, a, b, e1 or e2, tied

    with ThreadPoolExecutor(args.jobs) as ex:
        results = list(ex.map(one, genomes))

    out = os.path.join(vdir, f"results_{version}.tsv")
    cols = ["expected_scheme", "accession", "organism", "scheme", "ST", "status",
            "score", "alleles", "warnings", "upstream_same", "note"]
    n = dict(typed=0, expected=0, perfect=0, same=0, tie=0, diff=0, missing=0)
    diffs, ties, wrong, nogenome = [], [], [], []
    tie_seen = set()
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(cols)
        for g, a, b, note, tied in results:
            if a is None:
                n["missing"] += 1
                nogenome.append(f"{g['scheme']} ({g['taxon'] or 'no taxon'}): {note}")
                w.writerow([g["scheme"], g["accession"], g["organism"], "", "", "", "", "",
                            "", "", note])
                continue
            n["typed"] += 1
            n["expected"] += a[0] == g["scheme"]
            n["perfect"] += a[2] == "PERFECT"
            same = ""
            if tied and g["accession"] not in tie_seen:
                # equal top scores: mlst picks one of the tied schemes at
                # random, mlst-typing always the first by name
                tie_seen.add(g["accession"])
                schemes = ", ".join(f"{s} ST{st}" for s, st in sorted(tied.items()))
                up = f"{b[0]} ST{b[1]}" if (theirs and b) else ""
                ties.append(f"| {g['organism']} ({g['accession']}) | {schemes} | "
                            f"{a[0]} ST{a[1]} | {up} | {a[3]} |")
            if theirs:
                if a == b:
                    same = "yes"
                elif b and a[3] == b[3]:
                    same = "tie"
                else:
                    same = "NO"
                    diffs.append(f"{g['accession']} ({g['scheme']}): mlst-typing {a[:4]} vs mlst {b[:4] if b else b}")
                n[{"yes": "same", "tie": "tie", "NO": "diff"}[same]] += 1
            if a[0] != g["scheme"]:
                st = f"ST{a[1]}" if a[1] != "-" else "-"
                wrong.append(f"| {g['scheme']} | {g['organism']} ({g['accession']}) | "
                             f"{a[0]} | {st} | {a[2]} | {why_other(g, a, tied)} |")
            w.writerow([g["scheme"], g["accession"], g["organism"], *a,
                        g.get("warnings", ""), same, g.get("note", "")])

    priority = [(g, a) for g, a, _, _, _ in results if g.get("note", "").startswith("priority")]
    lines = [f"# Validation, database {version}", "",
             f"Run {dt.date.today().isoformat()}: {len(genomes)} genomes listed "
             f"(one public NCBI assembly per scheme + priority organisms).", "",
             f"- Typed: {n['typed']} ({n['missing']} without a genome)",
             f"- Called the scheme the genome was picked for: {n['expected']}/{n['typed']}",
             f"- PERFECT (full ST): {n['perfect']}/{n['typed']}"]
    if theirs:
        total = n["same"] + n["tie"] + n["diff"]
        lines += [f"- Same result as upstream mlst on the same database: **{n['same']}/{total}**",
                  f"- Upstream picked another of the tied schemes this run: {n['tie']}/{total} "
                  f"(see Ties)",
                  f"- Real differences: **{n['diff']}/{total}**"]
    lines += ["", "## Priority organisms", "", "| Genome | Scheme | ST | Status | Alleles |",
              "|---|---|---|---|---|"]
    for g, a in priority:
        if a:
            lines.append(f"| {g['taxon']} ({g['accession']}) | {a[0]} | {a[1]} | {a[2]} | {a[4]} |")
        else:
            lines.append(f"| {g['taxon']} ({g['accession']}) | not run | | | |")
    tables = {
        "ties": ("Two or more schemes give these genomes the same top score. Upstream "
                 "mlst picks one of them at random (its answer can change from run to "
                 "run); mlst-typing always reports the first by name and prints a "
                 "warning listing the others.",
                 "| Genome | Tied schemes | mlst-typing reports | upstream mlst (this run) | Score |\n"
                 "|---|---|---|---|---|"),
        "wrong": ("Each genome was picked from NCBI for one scheme, but typing chose "
                  "another (or none). This is about the genome choice and overlapping "
                  "schemes, not a disagreement between the tools.",
                  "| Picked for scheme | Genome | Called scheme | ST | Status | Why |\n"
                  "|---|---|---|---|---|---|"),
    }
    for key, title, items in (("diffs", "Real differences from upstream mlst", diffs),
                              ("ties", "Ties (same top score for more than one scheme)", ties),
                              ("wrong", "Other scheme called than the one picked for", wrong),
                              ("none", "Schemes without a validation genome", nogenome)):
        lines += ["", f"## {title} ({len(items)})", ""]
        if not items:
            lines.append("None.")
        elif key in tables:
            intro, head = tables[key]
            lines += [intro, "", head, *items]
        else:
            lines += [f"- {x}" for x in items]
    with open(os.path.join(vdir, "REPORT.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Wrote {out} and validation/REPORT.md", file=sys.stderr)
    return 1 if n["diff"] else 0


if __name__ == "__main__":
    sys.exit(main())
