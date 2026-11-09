#!/usr/bin/env python3
"""
mlst-typing - automatic MLST typing of assembled genomes against PubMLST
schemes.

A Python redesign of Torsten Seemann's mlst (https://github.com/tseemann/mlst,
GPL-2.0). The typing method follows mlst: BLAST the genome against every
allele of every scheme at once, call alleles, score each scheme and report
the best one. Allele notation and output columns are the same as mlst.

    mlst-typing contigs.fasta [more.fasta ...]
    mlst-typing --scheme saureus --full contigs.gbk.gz
    mlst-typing --list | --longlist | --info

Needs only Python 3.8+ and BLAST+ (blastn).
"""

import argparse
import bz2
import csv
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

VERSION = "0.1.0"
EXE = "mlst-typing"
URL = "https://github.com/TinusTK/mlst-typing"

# Schemes ignored in automatic mode unless asked for (same as mlst 2.35.0)
DEFAULT_EXCLUDE = "ecoli,abaumannii,vcholerae_2,senterica_achtman_2"
# Profile columns that are not loci (older databases kept them)
NOT_LOCI = {"ST", "mlst_clade", "clonal_complex", "species", "CC", "Lineage"}
SEEN = "N"   # marker: an exact allele was found for this locus
ENV_DB = "MLST_TYPING_DB"

BLAST_FMT = "6 sseqid slen length nident qseqid qstart qend qseq sstrand"
HIT_ID = re.compile(r"^([^.]+)\.(.+)[_-](\d+(?:\.\d+)?)$")


# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

class Log:
    quiet = False
    debug = False

    @classmethod
    def msg(cls, *a):
        if not cls.quiet:
            print(*a, file=sys.stderr)

    @staticmethod
    def wrn(*a):
        print("WARNING:", *a, file=sys.stderr)

    @classmethod
    def dbg(cls, *a):
        if cls.debug:
            print("=" * 10, "DEBUG START", "=" * 10, file=sys.stderr)
            print(*a, file=sys.stderr)
            print("=" * 10, "DEBUG END", "=" * 10, file=sys.stderr)


class MlstError(Exception):
    pass


def err(text):
    raise MlstError(text)


# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------

def perl_or(value, default="-"):
    """Perl's `$x || '-'`: empty, missing or "0" counts as false."""
    return value if value not in (None, "", "0") else default


class Scheme:
    def __init__(self, datadir, name, last_updated="Unknown"):
        self.name = name
        self.last_updated = last_updated or "Unknown"
        path = os.path.join(datadir, name, f"{name}.txt")
        try:
            with open(path) as fh:
                rows = [line.rstrip("\n").split("\t") for line in fh]
        except OSError:
            err(f"Could not open scheme file: {path}")
        header = rows[0] if rows else []
        self.genes = [c for c in header if c not in NOT_LOCI]
        n = len(self.genes)
        self.genotypes = {}
        for row in rows[1:]:
            if row and row[0].startswith("ST"):
                continue
            sig = "/".join(perl_or(row[i] if i < len(row) else None)
                           for i in range(1, n + 1))
            self.genotypes[sig] = row[0] if row else ""

    @property
    def num_genes(self):
        return len(self.genes)

    @property
    def num_genotypes(self):
        return len(self.genotypes)

    @property
    def num_alleles(self):
        seen = set()
        for sig in self.genotypes:
            for g, a in zip(self.genes, sig.split("/")):
                seen.add(f"{g}_{a}")
        return len(seen)

    def signature_of(self, calls):
        return "/".join(perl_or(calls.get(g)) for g in self.genes)

    def sequence_type(self, sig):
        return perl_or(self.genotypes.get(sig))


def load_schemes(datadir):
    if not os.path.isdir(datadir):
        err(f"Database directory does not exist: {datadir}")
    updated = {}
    manifest = os.path.join(os.path.dirname(os.path.abspath(datadir)), "manifest.tsv")
    if os.path.exists(manifest):
        with open(manifest) as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                updated[r["scheme"]] = r.get("last_updated")
    names = sorted(d for d in os.listdir(datadir)
                   if not d.startswith(".") and os.path.isdir(os.path.join(datadir, d)))
    return {n: Scheme(datadir, n, updated.get(n)) for n in names}


def find_database(arg_db):
    """--db, then $MLST_TYPING_DB, then database/ next to or above this script."""
    here = os.path.dirname(os.path.realpath(__file__))
    for cand in (arg_db, os.environ.get(ENV_DB),
                 os.path.join(here, "database"),
                 os.path.join(here, "..", "database")):
        if cand and os.path.isdir(cand):
            return os.path.realpath(cand)
    return os.path.realpath(arg_db or os.environ.get(ENV_DB) or os.path.join(here, "database"))


def db_version(db):
    try:
        with open(os.path.join(db, "VERSION.txt")) as fh:
            return fh.readline().strip() or "unknown"
    except OSError:
        return "unknown"


# --------------------------------------------------------------------------
# Input: FASTA / GenBank / EMBL, plain or .gz / .bz2 / .zip
# --------------------------------------------------------------------------

def read_bytes(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    elif data[:3] == b"BZh":
        data = bz2.decompress(data)
    elif data[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            files = [n for n in z.namelist() if not n.endswith("/")]
            if not files:
                err(f"Zip file has no files in it: {path}")
            data = z.read(files[0])
    return data.decode("utf-8", errors="replace")


def parse_sequences(text):
    """Return a list of (id, sequence) from FASTA, GenBank or EMBL text."""
    lines = text.splitlines()
    first = next((l for l in lines if l.strip()), "")
    seqs = []
    if first.startswith(">"):
        name, parts = None, []
        for line in lines:
            if line.startswith(">"):
                if name is not None:
                    seqs.append((name, "".join(parts)))
                name, parts = (line[1:].split() or ["seq"])[0], []
            elif name is not None:
                parts.append("".join(line.split()))
        if name is not None:
            seqs.append((name, "".join(parts)))
    elif first.startswith("LOCUS") or first.startswith("ID "):
        genbank = first.startswith("LOCUS")
        name, parts, inseq = None, [], False
        for line in lines:
            if genbank and line.startswith("LOCUS"):
                name = (line.split()[1:2] or ["seq"])[0]
            elif not genbank and line.startswith("ID "):
                name = line[5:].split(";")[0].strip() or "seq"
            elif (genbank and line.startswith("ORIGIN")) or (not genbank and line.startswith("SQ ")):
                inseq, parts = True, []
            elif line.startswith("//"):
                if inseq:
                    seqs.append((name or f"seq{len(seqs) + 1}", "".join(parts)))
                inseq = False
            elif inseq:
                parts.append(re.sub(r"[^A-Za-z*-]", "", line))
        if inseq:
            seqs.append((name or f"seq{len(seqs) + 1}", "".join(parts)))
    else:
        err("Input is not FASTA, GenBank or EMBL")
    seqs = [(n, s) for n, s in seqs if s]
    if not seqs:
        err("Sequence contains no data")
    return seqs


def write_fasta(seqs, path):
    with open(path, "w") as fh:
        for i, (name, seq) in enumerate(seqs, 1):
            fh.write(f">{name}\n")
            for j in range(0, len(seq), 60):
                fh.write(seq[j:j + 60] + "\n")


# --------------------------------------------------------------------------
# Typing (same rules as mlst's find_mlst)
# --------------------------------------------------------------------------

def revcom(dna):
    return dna[::-1].translate(str.maketrans("ATGCatgc", "TACGtacg"))


def parse_hit(line):
    """BLAST tabular line -> dict, or None if the subject id is not scheme.locus_N."""
    f = line.rstrip("\n").split("\t")
    if len(f) < 9:
        return None
    m = HIT_ID.match(f[0])
    if not m:
        return None
    try:
        hlen, alen, nident = int(f[1]), int(f[2]), int(f[3])
    except ValueError:
        return None
    return dict(scheme=m.group(1), gene=m.group(2), num=m.group(3),
                hlen=hlen, alen=alen, nident=nident, qid=f[4],
                qstart=f[5], qend=f[6], qseq=f[7], sstrand=f[8])


def call_alleles(hits, mincov, force_scheme=None, exclude=(), novel=False):
    """Allele calls per scheme from BLAST hits (in BLAST output order).

    Returns (res, nov): res[scheme][gene] = call string; nov[scheme][gene] =
    SEEN (exact match) or the sequence of a full-length inexact hit.
    """
    res, nov = {}, {}
    for h in hits:
        sch, gene, num = h["scheme"], h["gene"], h["num"]
        hlen, alen, nident = h["hlen"], h["alen"], h["nident"]
        Log.dbg(f"{h['qid']}:{h['qstart']}-{h['qend']}({h['sstrand']}) | {sch} {gene} {num}"
                f" | id={nident}/{alen} | cov={alen}/{hlen}")
        if nident / hlen < mincov / 100:
            continue
        if force_scheme and sch != force_scheme:
            continue
        if sch in exclude:
            continue
        calls = res.setdefault(sch, {})
        if hlen == alen and nident == hlen:   # full length, 100% identity
            cur = calls.get(gene)
            if cur is not None and not re.search(r"[~?]", cur):
                Log.msg(f"WARNING: found additional exact allele match {sch}.{gene}-{num}")
                calls[gene] = f"{cur},{num}"
            else:
                Log.msg(f"Found exact allele match {sch}.{gene}-{num}")
                calls[gene] = num
            nov.setdefault(sch, {})[gene] = SEEN
        else:   # full length with SNPs (~N) or partial (N?)
            label = f"~{num}" if alen == hlen else f"{num}?"
            if not perl_or(calls.get(gene), ""):
                calls[gene] = label
            if novel and alen == hlen:
                seq = revcom(h["qseq"]) if h["sstrand"] == "minus" else h["qseq"]
                ng = nov.setdefault(sch, {})
                if not ng.get(gene):
                    ng[gene] = seq
    return res, nov


def score_scheme(scheme, calls):
    """(ST, signature, score) of one scheme, score out of 100."""
    sig = scheme.signature_of(calls)
    st = scheme.sequence_type(sig)
    if st != "-" and "/-" in sig:
        sig = sig.replace("/-", "/0")   # null alleles: gene(0), not gene(-)
    n = scheme.num_genes
    score = n
    score -= 0.3 * sig.count("~")
    score -= 0.5 * sig.count("?")
    score -= 1.0 * sig.count("-")
    score = int(score * 90 / n)
    if st != "-":
        score += 10
    return st, sig, score


def tie_text(tied):
    """WARNINGS text for schemes sharing the top score: 'TIE: a (ST1), b (ST2)'."""
    if len(tied) < 2:
        return ""
    return "TIE: " + ", ".join(
        f"{name} (ST{st})" if st != "-" else f"{name} (no ST)" for name, st in tied)


def best_scheme(res, schemes, minscore, force_scheme=None, allele_cnt=7, fname=""):
    """Pick the top-scoring scheme.

    Returns (scheme, ST, signature, score, warnings). On a tie the first
    scheme by name (A-Z) is reported (mlst picks one at random), and every
    tied scheme with its ST goes into warnings.
    """
    sigs = [((force_scheme or "-"), "-", "/".join(["-"] * allele_cnt), 0)]
    for name in sorted(res):
        if name not in schemes:
            Log.wrn(f"BLAST hit for scheme '{name}' that is not in the database")
            continue
        st, sig, score = score_scheme(schemes[name], res[name])
        Log.dbg(f"SCORE={score}\t{name}\t{st}\t{sig}\t({schemes[name].num_genes} genes)")
        if score >= minscore:
            sigs.append((name, st, sig, score))
    sigs.sort(key=lambda s: -s[3])   # stable: sentinel stays first on ties
    for other in sigs[1:]:
        if other[3] == sigs[0][3]:
            Log.wrn(f"{sigs[0][0]}({sigs[0][1]})=={other[0]}({other[1]}) score={other[3]} {fname}")
    sentinel = sigs[0] if sigs[0][1:] == ("-", "/".join(["-"] * allele_cnt), 0) else None
    tied = [(s[0], s[1]) for s in sigs if s is not sentinel and s[3] == sigs[0][3]]
    return (*sigs[0], tie_text(tied))


def status_column(st, score, code):
    if re.fullmatch(r"\d+", st):
        return "PERFECT"
    if score <= 0:
        return "NONE"
    if not any(re.search(r"\D", c) for c in code):
        return "NOVEL"
    if any("," in c for c in code):
        return "MIXED"
    if any("-" in c for c in code):
        return "MISSING"
    if score < 70:
        return "BAD"
    return "OK"


def sort_duplicates(code):
    """Sort multiple exact alleles numerically: '7,3' -> '3,7'."""
    out = []
    for c in code:
        if "," in c and re.fullmatch(r"[\d.,]+", c):
            c = ",".join(sorted(c.split(","), key=float))
        out.append(c)
    return out


def run_blast(fasta, blastdb, threads, minid, outfile):
    cmd = ["blastn", "-query", fasta, "-out", outfile, "-db", blastdb,
           "-num_threads", str(threads), "-ungapped", "-dust", "no",
           "-word_size", "32", "-max_target_seqs", "100000",
           "-perc_identity", f"{minid:g}", "-evalue", "1E-20",
           "-outfmt", BLAST_FMT]
    Log.msg("Running: " + " ".join(cmd))
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        err(f"COMMAND FAILED: {' '.join(cmd)}\n{r.stderr.strip()}")


def type_genome(path, label, opts, schemes, tmpdir, nov_all):
    fna = os.path.join(tmpdir, "mlst.fna")
    bls = os.path.join(tmpdir, "mlst.bls")
    write_fasta(parse_sequences(read_bytes(path)), fna)
    run_blast(fna, opts.blastdb, opts.threads, opts.minid, bls)
    with open(bls) as fh:
        hits = [h for h in (parse_hit(l) for l in fh) if h]
    res, nov = call_alleles(hits, opts.mincov, opts.scheme, opts.exclude_set,
                            bool(opts.novel))
    allele_cnt = len(schemes[opts.scheme].genes) if opts.scheme else 7
    sch, st, sig, score, warnings = best_scheme(res, schemes, opts.minscore,
                                                opts.scheme, allele_cnt, path)
    # keep novel alleles of the chosen scheme only
    nov_all.setdefault(label, {}).update({k: v for k, v in nov.items() if k == sch})
    for k in list(nov_all[label]):
        if k != sch:
            del nov_all[label][k]
    return sch, st, sig, score, warnings


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

class RowWriter:
    def __init__(self, fh, sep="\t"):
        self.fh, self.sep = fh, sep

    def row(self, *cols):
        out = []
        for c in map(str, cols):
            if '"' in c or self.sep in c:
                c = c.replace('"', '""').replace("\\", "\\\\")
                c = f'"{c}"'
            out.append(c)
        self.fh.write(self.sep.join(out) + "\n")


def novel_fasta(nov_all):
    seen, out = set(), []
    for label in nov_all:
        for sch in sorted(nov_all[label]):
            for gene in sorted(nov_all[label][sch]):
                seq = nov_all[label][sch][gene]
                if seq == SEEN:
                    continue
                sid = f"{sch}.{gene}-{hashlib.md5(seq.encode()).hexdigest()}"
                if sid in seen:
                    continue
                seen.add(sid)
                out.append(f">{sid} {label}\n{seq}\n")
    return out


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

def get_args(argv):
    p = argparse.ArgumentParser(
        prog=EXE, description="Automatic MLST calling from assembled contigs",
        epilog=f"Homepage: {URL}. Based on mlst by Torsten Seemann.")
    B = argparse.BooleanOptionalAction
    p.add_argument("files", nargs="*", metavar="contigs",
                   help="FASTA/GenBank/EMBL files, may be .gz/.bz2/.zip")
    g = p.add_argument_group("general")
    g.add_argument("--version", action="store_true", help="print version and exit")
    g.add_argument("--check", action=B, default=False, help="just check dependencies and exit")
    g.add_argument("--skipcheck", action=B, default=False, help="skip dependency check")
    g.add_argument("-q", "--quiet", action=B, default=False, help="no stderr messages")
    g.add_argument("--threads", type=int, default=1, help="BLAST threads [1]")
    g.add_argument("--debug", action=B, default=False, help="verbose debug output")
    g.add_argument("--fofn", default="", help="file of input filenames (optional TAB label)")
    g = p.add_argument_group("scheme")
    g.add_argument("--scheme", default="", help="do not auto-detect, force this scheme")
    g.add_argument("--info", action=B, default=False, help="more information about schemes")
    g.add_argument("--list", action=B, default=False, help="list scheme names")
    g.add_argument("--longlist", action=B, default=False, help="list loci of all schemes")
    g.add_argument("--exclude", default=DEFAULT_EXCLUDE,
                   help=f"ignore these schemes [{DEFAULT_EXCLUDE}]")
    g = p.add_argument_group("output format")
    g.add_argument("--full", action=B, default=False, help="detailed output (recommended)")
    g.add_argument("--legacy", action=B, default=False,
                   help="old output with allele header row (needs --scheme)")
    g.add_argument("--csv", action=B, default=False, help="CSV instead of TSV")
    g.add_argument("--label", default="", help="replace FILE with this name")
    g.add_argument("--nopath", action=B, default=False, help="strip paths from FILE column")
    g = p.add_argument_group("output files")
    g.add_argument("--outfile", default="", help="save output to this file [stdout]")
    g.add_argument("--novel", default="", help="save novel alleles to this FASTA file")
    g.add_argument("--json", default="", help="also write results as JSON")
    g = p.add_argument_group("scoring")
    g.add_argument("--minid", type=float, default=95, help="DNA %%identity of full allele for '~' [95]")
    g.add_argument("--mincov", type=float, default=50, help="DNA %%cov for partial '?' allele [50]")
    g.add_argument("--minscore", type=float, default=50,
                   help="minimum score out of 100 to match a scheme (auto mode) [50]")
    g = p.add_argument_group("database")
    g.add_argument("--db", default="", help=f"database folder [${ENV_DB} or bundled database/]")
    g.add_argument("--blastdb", default="", help="BLAST database prefix [<db>/blast/mlst.fa]")
    g.add_argument("--datadir", default="", help="scheme folders [<db>/pubmlst]")
    return p.parse_args(argv)


def main(argv=None):
    o = get_args(argv)
    Log.quiet, Log.debug = o.quiet, o.debug
    db = find_database(o.db)
    o.blastdb = o.blastdb or os.path.join(db, "blast", "mlst.fa")
    o.datadir = o.datadir or os.path.join(db, "pubmlst")
    if o.version:
        print(f"{EXE} {VERSION} (database {db_version(db)})")
        return 0
    try:
        return run(o, db)
    except MlstError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def run(o, db):
    Log.msg(f"This is {EXE} {VERSION} running on {sys.platform} with Python {sys.version.split()[0]}")
    Log.msg(f"Database: {db} ({db_version(db)})")
    if o.skipcheck:
        Log.msg("Skipping dependency check due to --skipcheck")
    else:
        Log.msg(f"Checking {EXE} dependencies:")
        exe = shutil.which("blastn")
        if not exe:
            err("Could not find 'blastn' - please install BLAST+")
        Log.msg(f"Found 'blastn' => {exe}")
        if o.check:
            Log.msg("OK.")
            return 0

    files = list(o.files)
    labels = {}
    if o.fofn:
        # one path per line; optional TAB + label (used by the Galaxy wrapper)
        Log.msg(f"Using '{o.fofn}' as source of input files")
        files = []
        with open(o.fofn) as fh:
            for line in fh:
                path, _, lab = line.rstrip("\n").partition("\t")
                files.append(path)
                if lab:
                    labels[path] = lab
        Log.msg(f"Read {len(files)} filenames")
    if o.label and len(files) > 1:
        err("Using --label when scanning multiple files does not make sense")
    if o.legacy and not o.scheme:
        err("Must specify a --scheme for --legacy output mode")

    schemes = load_schemes(o.datadir)
    if o.scheme and o.scheme not in schemes:
        err(f"Invalid --scheme '{o.scheme}'. Check using --list")
    if o.scheme and o.minscore != 0:
        Log.msg("Setting --minscore=0 because user chose --scheme")
        o.minscore = 0

    out = RowWriter(open(o.outfile, "w") if o.outfile else sys.stdout,
                    "," if o.csv else "\t")
    if o.list or o.longlist or o.info:
        if o.list:
            print(" ".join(sorted(schemes)))
        elif o.longlist:
            for s in schemes.values():
                out.row(s.name, *s.genes)
        else:
            out.row("SCHEME", "LOCII", "TYPES", "ALLELES", "DATE", "LOCII_NAMES")
            for s in schemes.values():
                out.row(s.name, s.num_genes, s.num_genotypes, s.num_alleles,
                        s.last_updated, " ".join(s.genes))
        return 0

    if not files:
        err("Please provide some FASTA/Genbank files to genotype (can be .gz)")
    o.exclude_set = set() if o.scheme else {x for x in o.exclude.split(",") if x}
    if o.exclude_set:
        Log.msg(f"Excluding {len(o.exclude_set)} schemes:", *sorted(o.exclude_set))

    if o.scheme and o.legacy:
        out.row("FILE", "SCHEME", "ST", *schemes[o.scheme].genes)
    elif o.full:
        out.row("FILE", "SCHEME", "ST", "STATUS", "SCORE", "ALLELES", "WARNINGS")

    results, nov_all = [], {}
    with tempfile.TemporaryDirectory(prefix="mlst-typing_") as tmp:
        for path in files:
            if os.path.isdir(path):
                err(f"'{path}' seems to be a directory, not a file")
            if not os.access(path, os.R_OK):
                err(f"Unable to read from '{path}'")
            label = o.label or labels.get(path) or (os.path.basename(path) if o.nopath else path)
            if label != path:
                Log.msg(f"Using label '{label}' for file {path}")
            sch, st, sig, score, warnings = type_genome(path, label, o, schemes, tmp, nov_all)
            if o.scheme and sch != o.scheme:
                err(f"BUG: got back {sch} despite --scheme {o.scheme}")
            code = [] if sch == "-" else sort_duplicates(sig.split("/"))
            genes = [] if sch == "-" else schemes[sch].genes
            if o.scheme and o.legacy:
                out.row(label, sch, st, *code)
            else:
                alleles = [f"{g}({c})" for g, c in zip(genes, code)]
                if o.full:
                    out.row(label, sch, st, status_column(st, score, code), score,
                            ";".join(alleles), warnings)
                else:
                    out.row(label, sch, st, *alleles, warnings)
            results.append({
                "id": label, "filename": path, "scheme": sch, "sequence_type": st,
                "alleles": None if sch == "-" else dict(zip(genes, code)),
                "warnings": [warnings] if warnings else [],
            })

    if o.json:
        Log.msg(f"Writing JSON: {o.json}")
        with open(o.json, "w") as fh:
            json.dump(results, fh, indent=3)
            fh.write("\n")
    if o.novel:
        new = novel_fasta(nov_all)
        Log.msg(f"Found {len(new)} novel alleles")
        with open(o.novel, "w") as fh:
            fh.writelines(new)
    if o.outfile:
        out.fh.close()
    Log.msg("Please cite mlst (Seemann, github.com/tseemann/mlst) and PubMLST "
            "(Jolley et al. 2018, https://pubmed.ncbi.nlm.nih.gov/30345391)")
    Log.msg("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
