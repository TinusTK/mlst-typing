"""Tests for mlst-typing.

Unit tests need nothing. Run tests need blastn and the bundled database/.
Comparison tests also need upstream mlst: set MLST_UPSTREAM to its bin/mlst.
"""

import bz2
import gzip
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
DB = os.path.join(ROOT, "database")
sys.path.insert(0, os.path.join(ROOT, "tool"))

import mlst_typing as mt  # noqa: E402

TOOL = [sys.executable, os.path.join(ROOT, "tool", "mlst_typing.py")]
HAVE_BLAST = shutil.which("blastn") is not None
HAVE_DB = os.path.isdir(os.path.join(DB, "blast"))
needs_blast = pytest.mark.skipif(not (HAVE_BLAST and HAVE_DB),
                                 reason="needs blastn and database/")
UPSTREAM = os.environ.get("MLST_UPSTREAM")
needs_upstream = pytest.mark.skipif(not (UPSTREAM and HAVE_BLAST and HAVE_DB),
                                    reason="set MLST_UPSTREAM to upstream bin/mlst")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def hit(sid, hlen, alen, nident, qseq="ACGT", strand="plus"):
    return mt.parse_hit(f"{sid}\t{hlen}\t{alen}\t{nident}\tq1\t1\t{alen}\t{qseq}\t{strand}")


def make_scheme(tmp_path, name, rows):
    d = tmp_path / name
    d.mkdir()
    (d / f"{name}.txt").write_text("\n".join("\t".join(r) for r in rows) + "\n")
    return mt.Scheme(str(tmp_path), name)


@pytest.fixture(autouse=True)
def quiet():
    mt.Log.quiet, mt.Log.debug = True, False


# --------------------------------------------------------------------------
# hit ids
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sid,expect", [
    ("saureus.arcC_1", ("saureus", "arcC", "1")),
    ("ngstar.penA_2.002", ("ngstar", "penA", "2.002")),
    ("leptospira.glmU_1_12", ("leptospira", "glmU_1", "12")),
    ("halobacteria.EF-2_3", ("halobacteria", "EF-2", "3")),   # mlst misses this
    ("halobacteria.rpoB'_4", ("halobacteria", "rpoB'", "4")),
])
def test_parse_hit_ids(sid, expect):
    h = hit(sid, 100, 100, 100)
    assert (h["scheme"], h["gene"], h["num"]) == expect


def test_parse_hit_rejects_junk():
    assert mt.parse_hit("nonsense\t1\t2") is None
    assert hit("noscheme_1", 1, 1, 1) is None


# --------------------------------------------------------------------------
# allele calling
# --------------------------------------------------------------------------

def test_exact_inexact_partial_calls():
    hits = [hit("s.a_1", 100, 100, 100),     # exact
            hit("s.b_2", 100, 100, 98),      # full length with SNPs
            hit("s.c_3", 100, 60, 60),       # partial
            hit("s.d_4", 100, 30, 30)]       # below mincov 50 -> ignored
    res, nov = mt.call_alleles(hits, mincov=50)
    assert res == {"s": {"a": "1", "b": "~2", "c": "3?"}}
    assert nov == {"s": {"a": mt.SEEN}}


def test_exact_beats_inexact_and_duplicates_join():
    hits = [hit("s.a_5", 100, 100, 97), hit("s.a_1", 100, 100, 100),
            hit("s.a_7", 100, 100, 100)]
    res, _ = mt.call_alleles(hits, mincov=50)
    assert res["s"]["a"] == "1,7"


def test_first_inexact_kept():
    res, _ = mt.call_alleles([hit("s.a_5", 100, 100, 97), hit("s.a_6", 100, 100, 96)], 50)
    assert res["s"]["a"] == "~5"


def test_force_scheme_and_exclude():
    hits = [hit("s.a_1", 10, 10, 10), hit("t.a_1", 10, 10, 10)]
    assert set(mt.call_alleles(hits, 50, force_scheme="t")[0]) == {"t"}
    assert set(mt.call_alleles(hits, 50, exclude={"s"})[0]) == {"t"}


def test_novel_sequence_revcom():
    res, nov = mt.call_alleles([hit("s.a_1", 4, 4, 3, qseq="AACG", strand="minus")],
                               50, novel=True)
    assert nov["s"]["a"] == "CGTT"


# --------------------------------------------------------------------------
# schemes, scoring, status
# --------------------------------------------------------------------------

@pytest.fixture
def scheme(tmp_path):
    return make_scheme(tmp_path, "s", [
        ["ST", "a", "b", "c", "clonal_complex"],
        ["1", "1", "1", "1", "CC1"],
        ["2", "1", "2", "0", ""],          # null allele at c
    ])


def test_scheme_reads_loci_only(scheme):
    assert scheme.genes == ["a", "b", "c"]
    assert scheme.genotypes == {"1/1/1": "1", "1/2/-": "2"}
    # like mlst, the missing-locus marker counts as an allele (c_-)
    assert scheme.num_genotypes == 2 and scheme.num_alleles == 5


def test_score_perfect(scheme):
    assert mt.score_scheme(scheme, {"a": "1", "b": "1", "c": "1"}) == ("1", "1/1/1", 100)


def test_score_null_allele(scheme):
    assert mt.score_scheme(scheme, {"a": "1", "b": "2"}) == ("2", "1/2/0", 100)


def test_score_penalties(scheme):
    st, sig, score = mt.score_scheme(scheme, {"a": "~1", "b": "2?"})
    assert (st, sig) == ("-", "~1/2?/-")
    assert score == int((3 - 0.3 - 0.5 - 1.0) * 90 / 3)


def test_best_scheme_tie_picks_name_order(tmp_path):
    a = make_scheme(tmp_path, "aaa", [["ST", "x"], ["1", "1"]])
    b = make_scheme(tmp_path, "bbb", [["ST", "x"], ["1", "1"]])
    res = {"bbb": {"x": "1"}, "aaa": {"x": "1"}}
    best = mt.best_scheme(res, {"aaa": a, "bbb": b}, minscore=50)
    assert best[0] == "aaa"
    assert best[4] == "TIE: aaa (ST1), bbb (ST1)"


def test_best_scheme_no_tie_no_warning(tmp_path):
    a = make_scheme(tmp_path, "aaa", [["ST", "x"], ["1", "1"]])
    b = make_scheme(tmp_path, "bbb", [["ST", "x"], ["1", "1"]])
    best = mt.best_scheme({"aaa": {"x": "1"}, "bbb": {"x": "~1"}}, {"aaa": a, "bbb": b}, 0)
    assert best[0] == "aaa" and best[4] == ""


def test_tie_text_no_st():
    assert mt.tie_text([("a", "5"), ("b", "-")]) == "TIE: a (ST5), b (no ST)"
    assert mt.tie_text([("a", "5")]) == ""


def test_best_scheme_none(tmp_path):
    assert mt.best_scheme({}, {}, 50) == ("-", "-", "-/-/-/-/-/-/-", 0, "")


@pytest.mark.parametrize("st,score,code,status", [
    ("5", 100, ["1", "2"], "PERFECT"),
    ("-", 0, [], "NONE"),
    ("-", 90, ["1", "2"], "NOVEL"),
    ("-", 80, ["1,2", "~3"], "MIXED"),
    ("5", 100, ["3,3,3", "2"], "MULTICOPY"),      # identical copies, full ST
    ("-", 90, ["3,3", "2"], "MULTICOPY"),         # identical copies, no ST
    ("-", 90, ["1,1,4,4", "2"], "MIXED"),         # two different alleles
    ("-", 85, ["3,3", "~2"], "MULTICOPY"),
    ("-", 80, ["1", "-"], "MISSING"),
    ("-", 60, ["1", "~2"], "BAD"),
    ("-", 85, ["1", "~2"], "PARTIAL"),
])
def test_status(st, score, code, status):
    assert mt.status_column(st, score, code) == status


def test_collapse_copies():
    assert [mt.collapse_copies(c) for c in ["5,5,5", "1,142", "7", "~3", "-"]] == \
        ["5", "1,142", "7", "~3", "-"]


def test_multicopy_gets_st():
    class S:
        num_genes = 2
        genes = ["a", "b"]
        genotypes = {"5/2": "9"}
        signature_of = mt.Scheme.signature_of
        sequence_type = mt.Scheme.sequence_type
    assert mt.score_scheme(S(), {"a": "5,5,5", "b": "2"}) == ("9", "5,5,5/2", 100)
    assert mt.score_scheme(S(), {"a": "5,6", "b": "2"}) == ("-", "5,6/2", 90)


def test_sort_duplicates():
    assert mt.sort_duplicates(["10,2", "3,3", "~4", "2.002,1"]) == ["2,10", "3,3", "~4", "1,2.002"]


# --------------------------------------------------------------------------
# input reading
# --------------------------------------------------------------------------

FASTA = ">c1 desc\nACGT\nacgt\n>c2\nGGGG\n"
GENBANK = ("LOCUS       C1   8 bp    DNA     linear\nFEATURES\nORIGIN\n"
           "        1 acgtacgt\n//\n")


def test_parse_fasta():
    assert mt.parse_sequences(FASTA) == [("c1", "ACGTacgt"), ("c2", "GGGG")]


def test_parse_genbank():
    assert mt.parse_sequences(GENBANK) == [("C1", "acgtacgt")]


def test_parse_empty_errors():
    with pytest.raises(mt.MlstError, match="no data"):
        mt.parse_sequences(">empty\n\n")


@pytest.mark.parametrize("pack", ["plain", "gz", "bz2", "zip"])
def test_read_bytes_compressed(tmp_path, pack):
    raw = FASTA.encode()
    p = tmp_path / "x"
    if pack == "gz":
        raw = gzip.compress(raw)
    elif pack == "bz2":
        raw = bz2.compress(raw)
    elif pack == "zip":
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("x.fa", FASTA)
        raw = buf.getvalue()
    p.write_bytes(raw)
    assert mt.read_bytes(str(p)) == FASTA


def test_row_quoting():
    buf = io.StringIO()
    mt.RowWriter(buf, ",").row("a,b", 'q"x', 3)
    assert buf.getvalue() == '"a,b","q""x",3\n'


# --------------------------------------------------------------------------
# running the tool
# --------------------------------------------------------------------------

def run(*args):
    return subprocess.run(TOOL + ["--db", DB, *args], capture_output=True, text=True)


def test_version():
    r = run("--version")
    assert r.returncode == 0 and r.stdout.startswith("mlst-typing ")


@needs_blast
def test_list_and_info():
    r = run("--list")
    assert r.returncode == 0 and "saureus" in r.stdout.split()
    r = run("--info")
    assert r.stdout.startswith("SCHEME\tLOCII")


@needs_blast
@pytest.mark.parametrize("name", ["example.fna.gz", "example.gbk.gz"])
def test_sepidermidis(name):
    r = run("-q", os.path.join(DATA, name))
    assert r.returncode == 0, r.stderr
    f = r.stdout.rstrip("\n").split("\t")
    assert f[1] == "sepidermidis" and f[2] == "184"
    assert f[-1] == ""          # WARNINGS column, empty: no tie


@needs_blast
def test_full_layout():
    """--full: one column per allele, always ALLELE1..ALLELE10."""
    r = run("-q", "--full", "--nopath", os.path.join(DATA, "example.fna.gz"),
            os.path.join(DATA, "none.fa"))
    head, row, none = r.stdout.splitlines()
    assert head.split("\t") == (["FILE", "SCHEME", "ST"] + [f"ALLELE{i}" for i in range(1, 11)]
                                + ["STATUS", "SCORE", "WARNINGS"])
    assert row.split("\t") == ["example.fna.gz", "sepidermidis", "184", "arcC(16)", "aroE(1)",
                               "gtr(2)", "mutS(1)", "pyrR(2)", "tpiA(1)", "yqiL(1)", "", "", "",
                               "PERFECT", "100", ""]
    assert none.split("\t") == (["none.fa", "-", "-"] + [""] * 10
                                + ["NONE", "0", "No ST: PubMLST NONE, EnteroBase NONE"])


@needs_blast
@pytest.mark.parametrize("scheme,loci", [("tpallidum", 3), ("brucella", 9), ("vvulnificus", 10)])
def test_full_layout_any_locus_count(scheme, loci):
    """Schemes with 3 to 10 loci all give 16 columns; unused allele cells are empty."""
    r = run("-q", "--full", "--scheme", scheme, os.path.join(DATA, "none.fa"))
    assert r.returncode == 0, r.stderr
    head, row = (line.split("\t") for line in r.stdout.splitlines())
    assert len(head) == len(row) == 16
    cells = row[3:13]
    assert all(c.endswith("(-)") for c in cells[:loci]) and cells[loci:] == [""] * (10 - loci)


def test_allele_columns_fit_every_scheme():
    """No bundled scheme has more loci than the --full layout has allele columns."""
    with open(os.path.join(DB, "manifest.tsv")) as fh:
        rows = [line.rstrip("\n").split("\t") for line in fh]
    col = rows[0].index("loci")
    assert max(int(r[col]) for r in rows[1:]) <= mt.ALLELE_COLUMNS == 10


@needs_blast
def test_combine_alleles():
    """--full --combine-alleles: the single ALLELES column of versions before 0.3.0."""
    r = run("-q", "--full", "--combine-alleles", os.path.join(DATA, "example.fna.gz"))
    head, row = r.stdout.splitlines()[:2]
    assert head.split("\t") == ["FILE", "SCHEME", "ST", "ALLELES", "STATUS", "SCORE", "WARNINGS"]
    f = row.split("\t")
    assert f[2] == "184" and f[4] == "PERFECT" and f[5] == "100"
    assert f[3] == "arcC(16);aroE(1);gtr(2);mutS(1);pyrR(2);tpiA(1);yqiL(1)"
    r = run("-q", "--combine-alleles", os.path.join(DATA, "example.fna.gz"))
    assert r.returncode != 0 and "--combine-alleles" in r.stderr


@needs_blast
def test_compressed_inputs():
    r = run("-q", os.path.join(DATA, "novel.fasta.bz2"), os.path.join(DATA, "mixed.fa.zip"))
    assert r.returncode == 0, r.stderr
    assert "leptospira_2" in r.stdout and "mgen" in r.stdout
    assert "pgm(3,3)" in r.stdout


@needs_blast
def test_errors():
    assert run(DATA).returncode == 1
    assert run(os.path.join(DATA, "null.fa")).returncode == 1
    r = run(os.path.join(DATA, "empty.fa"))
    assert r.returncode == 1 and "no data" in r.stderr
    assert run("--legacy", os.path.join(DATA, "none.fa")).returncode == 1
    assert run("--scheme", "nosuchscheme", os.path.join(DATA, "none.fa")).returncode == 1


@needs_blast
def test_json_and_novel(tmp_path):
    js, nv = tmp_path / "o.json", tmp_path / "n.fa"
    r = run("-q", "--json", str(js), "--novel", str(nv), os.path.join(DATA, "novel.fasta.bz2"))
    assert r.returncode == 0, r.stderr
    data = json.loads(js.read_text())
    assert data[0]["scheme"] != "-"
    assert nv.read_text().count(">") >= 1


# --------------------------------------------------------------------------
# same answers as upstream mlst on the same database
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# PubMLST + EnteroBase: the combined row (README "How to read the report")
# --------------------------------------------------------------------------

ACHTMAN = ["adk", "fumC", "gyrB", "icd", "mdh", "purA", "recA"]


def res(scheme="-", st="-", sig="1/1/1/1/1/1/1", score=None, genes=ACHTMAN, warnings=""):
    if score is None:
        score = 0 if scheme == "-" else (100 if st != "-" else 90)
    return mt.Result(scheme, st, sig, score, warnings, genes)


P_ST = dict(scheme="ecoli_achtman_4", st="10")
P_NOVEL = dict(scheme="ecoli_achtman_4")
P_MISSING = dict(scheme="ecoli_achtman_4", sig="1/1/1/1/1/1/-", score=77)
E_SAME = dict(scheme="ecoli_achtman_enterobase", st="10")
E_OTHER_ST = dict(scheme="ecoli_achtman_enterobase", st="11")
E_NOVEL = dict(scheme="ecoli_achtman_enterobase")
E_OTHER_SCHEME = dict(scheme="yersinia_mcnally_enterobase", st="5",
                      genes=["aarF", "dfp", "galR", "glnS", "hemA", "rfaE", "speA"])
NOTHING = {}


@pytest.mark.parametrize("case,pub,eb,source,warning", [
    (1, P_ST, NOTHING, "pubmlst", ""),
    (2, P_ST, E_SAME, "pubmlst", ""),
    (3, P_ST, E_OTHER_ST, "pubmlst",
     "EnteroBase differs: ecoli_achtman_enterobase (ST11)"),
    (4, P_ST, E_NOVEL, "pubmlst", ""),
    (5, P_ST, E_OTHER_SCHEME, "pubmlst", ""),
    (6, P_NOVEL, E_SAME, "enterobase",
     "EnteroBase ST, no PubMLST (PubMLST: ecoli_achtman_4 NOVEL)"),
    (6, dict(scheme="klebsiella", genes=["gapA", "infB", "mdh", "pgi", "phoE", "rpoB", "tonB"]),
     E_SAME, "enterobase", "EnteroBase ST, no PubMLST (PubMLST: klebsiella NOVEL)"),
    (7, NOTHING, E_SAME, "enterobase", "EnteroBase ST, no PubMLST (PubMLST: NONE)"),
    (8, P_MISSING, E_NOVEL, "pubmlst",
     "No ST: PubMLST MISSING, EnteroBase ecoli_achtman_enterobase NOVEL"),
    (9, P_NOVEL, NOTHING, "pubmlst", "No ST: PubMLST NOVEL, EnteroBase NONE"),
    (10, NOTHING, E_NOVEL, "pubmlst",
     "No ST: PubMLST NONE, EnteroBase ecoli_achtman_enterobase NOVEL"),
    (11, NOTHING, NOTHING, "pubmlst", "No ST: PubMLST NONE, EnteroBase NONE"),
])
def test_combine_cases(case, pub, eb, source, warning):
    p, e = res(**pub), res(**eb)
    shown, src, warn = mt.combine(p, e)
    assert (src, warn) == (source, warning)
    assert shown is (e if source == "enterobase" else p)


def test_combine_keeps_tie_of_row_shown():
    tie = "TIE: a (ST1), b (ST2)"
    _, _, warn = mt.combine(res(**P_ST, warnings=tie), res(**E_OTHER_ST))
    assert warn == "EnteroBase differs: ecoli_achtman_enterobase (ST11); " + tie
    _, _, warn = mt.combine(res(**P_NOVEL, warnings=tie), res(**E_SAME, warnings="TIE: x (ST3)"))
    assert warn == ("EnteroBase ST, no PubMLST (PubMLST: ecoli_achtman_4 NOVEL); "
                    "TIE: x (ST3)")
    _, _, warn = mt.combine(res(**P_NOVEL, warnings=tie), res())
    assert warn == "No ST: PubMLST NOVEL, EnteroBase NONE; " + tie


def test_combine_multicopy_st_counts_as_st():
    p = res(scheme="ecoli_achtman_4", st="10", sig="1,1/1/1/1/1/1/1")
    assert p.status == "MULTICOPY" and p.has_st
    assert mt.combine(p, res())[1:] == ("pubmlst", "")


EB_ONLY = os.path.join(DATA, "ecoli_enterobase_only.fa")   # ST17227, EnteroBase only
EB_ROW = ("ecoli_achtman_enterobase\t17227\t"
          "adk(10);fumC(11);gyrB(4);icd(8);mdh(8);purA(8);recA(644)\tPERFECT\t100\t")
PM_ROW = ("ecoli_achtman_4\t-\t"
          "adk(10);fumC(11);gyrB(4);icd(8);mdh(8);purA(8);recA(644)\tNOVEL\t90\t")


@needs_blast
def test_three_reports(tmp_path):
    files = [EB_ONLY, os.path.join(DATA, "example.fna.gz"), os.path.join(DATA, "none.fa")]
    pm, eb = tmp_path / "pubmlst.tsv", tmp_path / "enterobase.tsv"
    r = run("-q", "--full", "--combine-alleles", "--nopath", "--outfile-pubmlst", str(pm),
            "--outfile-enterobase", str(eb), *files)
    assert r.returncode == 0, r.stderr
    head = "FILE\tSCHEME\tST\tALLELES\tSTATUS\tSCORE\tWARNINGS\n"
    sepi = ("example.fna.gz\tsepidermidis\t184\t"
            "arcC(16);aroE(1);gtr(2);mutS(1);pyrR(2);tpiA(1);yqiL(1)\tPERFECT\t100\t\n")
    assert r.stdout == (
        head
        + "ecoli_enterobase_only.fa\t" + EB_ROW
        + "EnteroBase ST, no PubMLST (PubMLST: ecoli_achtman_4 NOVEL)\n"
        + sepi
        + "none.fa\t-\t-\t\tNONE\t0\tNo ST: PubMLST NONE, EnteroBase NONE\n")
    assert pm.read_text() == (head + "ecoli_enterobase_only.fa\t" + PM_ROW + "\n" + sepi
                              + "none.fa\t-\t-\t\tNONE\t0\t\n")
    assert eb.read_text() == (head + "ecoli_enterobase_only.fa\t" + EB_ROW + "\n"
                              + "example.fna.gz\t-\t-\t\tNONE\t0\t\n"
                              + "none.fa\t-\t-\t\tNONE\t0\t\n")


@needs_blast
def test_no_enterobase_is_pubmlst_only(tmp_path):
    pm = tmp_path / "pubmlst.tsv"
    a = run("-q", "--full", "--combine-alleles", "--no-enterobase", EB_ONLY)
    b = run("-q", "--full", "--combine-alleles", "--outfile-pubmlst", str(pm), "--outfile", os.devnull, EB_ONLY)
    assert a.returncode == b.returncode == 0, a.stderr + b.stderr
    assert a.stdout == pm.read_text()
    assert a.stdout.splitlines()[1].endswith("NOVEL\t90\t")
    r = run("-q", "--no-enterobase", "--outfile-enterobase", str(tmp_path / "x"), EB_ONLY)
    assert r.returncode != 0 and "--outfile-enterobase" in r.stderr


@needs_blast
def test_forced_enterobase_scheme_and_lists():
    r = run("-q", "--full", "--combine-alleles", "--scheme", "ecoli_achtman_enterobase", EB_ONLY)
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines()[1].endswith(EB_ROW.rstrip("\t") + "\t")   # no cross-check
    r = run("-q", "--full", "--combine-alleles", "--scheme", "ecoli_achtman_4", EB_ONLY)
    assert r.stdout.splitlines()[1].endswith(PM_ROW.rstrip("\t") + "\t")
    names = run("--list").stdout.split()
    assert "ecoli_achtman_enterobase" in names and "ecoli_achtman_4" in names
    assert "ecoli_achtman_enterobase" not in run("--list", "--no-enterobase").stdout.split()


@needs_blast
def test_json_has_both_sources(tmp_path):
    js = tmp_path / "out.json"
    r = run("-q", "--json", str(js), "--outfile", os.devnull, EB_ONLY)
    assert r.returncode == 0, r.stderr
    row = json.loads(js.read_text())[0]
    assert row["scheme"] == "ecoli_achtman_enterobase" and row["sequence_type"] == "17227"
    assert row["source"] == "enterobase"
    assert row["warnings"] == ["EnteroBase ST, no PubMLST (PubMLST: ecoli_achtman_4 NOVEL)"]
    assert row["pubmlst"]["scheme"] == "ecoli_achtman_4"
    assert row["pubmlst"]["status"] == "NOVEL" and row["pubmlst"]["sequence_type"] == "-"
    assert row["enterobase"]["status"] == "PERFECT"


INPUTS = ["example.fna.gz", "example.gbk.gz", "novel.fasta.bz2", "mixed.fa.zip",
          "none.fa", "novel.fa"]
MODES = [[], ["--full"], ["--csv"], ["--scheme", "sepidermidis", "--legacy"],
         ["--minid", "90", "--mincov", "30"]]


def upstream(*args):
    return subprocess.run([UPSTREAM, "--blastdb", os.path.join(DB, "blast", "mlst.fa"),
                           "--datadir", os.path.join(DB, "pubmlst"), *args],
                          capture_output=True, text=True)


def drop_warnings(text, sep):
    """Remove mlst-typing's extra last column (WARNINGS) to compare with mlst."""
    return "".join(line.rsplit(sep, 1)[0] + "\n" for line in text.splitlines())


def as_mlst_full(text):
    """mlst-typing --full -> mlst --full: FILE SCHEME ST STATUS SCORE ALLELES;
    mlst says OK for PARTIAL and MIXED for MULTICOPY."""
    out = []
    for line in text.splitlines():
        f = line.split("\t")[:6]                    # drop WARNINGS
        f = f[:3] + [f[4].replace("PARTIAL", "OK").replace("MULTICOPY", "MIXED"), f[5], f[3]]
        out.append("\t".join(f) + "\n")
    return "".join(out)


@needs_upstream
@pytest.mark.parametrize("mode", MODES, ids=lambda m: " ".join(m) or "default")
def test_same_as_upstream(mode):
    files = [os.path.join(DATA, f) for f in INPUTS]
    a = upstream("-q", *mode, *files)
    extra = ["--combine-alleles"] if "--full" in mode else []   # mlst's one ALLELES column
    b = run("-q", "--no-enterobase", *mode, *extra, *files)   # mlst has no EnteroBase
    assert a.returncode == b.returncode == 0, a.stderr + b.stderr
    if "--legacy" in mode:
        ours = b.stdout
    elif "--full" in mode:
        ours = as_mlst_full(b.stdout)
    else:
        ours = drop_warnings(b.stdout, "," if "--csv" in mode else "\t")
    assert ours == a.stdout


# --------------------------------------------------------------------------
# setup: the user's own PubMLST key and database (command line only)
# --------------------------------------------------------------------------

import http.server  # noqa: E402
import stat  # noqa: E402
import threading  # noqa: E402
import urllib.parse  # noqa: E402

import mlst_typing_setup as su  # noqa: E402
import mlst_typing_update as up  # noqa: E402


@pytest.fixture
def home(tmp_path, monkeypatch):
    """Private config and data folders, so tests never see a real key."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.delenv(mt.ENV_DB, raising=False)
    monkeypatch.setattr(su, "say", lambda *a: None)
    return mt.setup_paths()


def make_own(paths):
    os.makedirs(os.path.join(paths["db"], "blast"))
    open(os.path.join(paths["db"], "blast", "mlst.fa.nsq"), "w").close()


def test_oauth_signature_matches_the_published_example():
    """OAuth Core 1.0, Appendix A.5.2."""
    url = su.oauth_url("GET", "http://photos.example.net/photos?file=vacation.jpg&size=original",
                       "dpf43f3p2l4k3l03", "kd94hf93k423kf44",
                       "nnch734d00sl2jdk", "pfkkdhi9sl3r4s00",
                       nonce="kllo9940pd9333jh", timestamp=1191242096)
    q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
    assert q["oauth_signature"] == "tR3+Ty81lMeYAr/Fid0kMTYa/WM="
    assert q["file"] == "vacation.jpg" and q["oauth_version"] == "1.0"


def test_database_order(home, monkeypatch, tmp_path):
    bundled = mt.find_database("")
    assert bundled == os.path.realpath(DB)                  # no own database yet
    make_own(home)
    assert mt.find_database("") == os.path.realpath(home["db"])
    assert mt.find_database("", own=False) == bundled       # what setup copies from
    other = tmp_path / "other"
    other.mkdir()
    assert mt.find_database(str(other)) == os.path.realpath(other)     # --db wins
    monkeypatch.setenv(mt.ENV_DB, str(other))
    assert mt.find_database("") == os.path.realpath(other)             # then the env


def test_question_only_on_a_first_run_by_hand(home, monkeypatch):
    o = mt.get_args(["x.fa"])
    assert not mt.first_run_due(o)                          # pytest: no terminal
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(sys.stderr, "isatty", lambda: True, raising=False)
    assert mt.first_run_due(o)
    assert not mt.first_run_due(mt.get_args(["--db", DB, "x.fa"]))     # Galaxy passes --db
    for flag in ("--version", "--list", "--check"):
        assert not mt.first_run_due(mt.get_args([flag]))
    monkeypatch.setenv(mt.ENV_DB, DB)
    assert not mt.first_run_due(o)
    monkeypatch.delenv(mt.ENV_DB)
    su.save_answer(home, "skipped")
    assert not mt.first_run_due(o)                          # asked once


def test_skip_is_remembered(home, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("what?\ns\n"))
    su.first_run(home, DB)
    st = su.status(home)
    assert st["asked"] and st["answer"] == "skipped"
    assert not st["key_saved"] and not st["own_database"]


def test_credentials_file_is_private(home):
    su.save_credentials(home, {"type": "apikey", "key": "k"})
    mode = stat.S_IMODE(os.stat(os.path.join(home["config"], "credentials.json")).st_mode)
    assert mode == 0o600
    assert su.load_credentials(home)["key"] == "k"


def test_setup_needs_a_terminal_and_status_is_json(tmp_path):
    env = {**os.environ, "XDG_CONFIG_HOME": str(tmp_path / "c"),
           "XDG_DATA_HOME": str(tmp_path / "d")}
    env.pop(mt.ENV_DB, None)
    r = subprocess.run(TOOL + ["--setup"], capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, env=env)
    assert r.returncode == 1 and "needs a terminal" in r.stderr
    r = subprocess.run(TOOL + ["--update"], capture_output=True, text=True, env=env)
    assert r.returncode == 1 and "--setup" in r.stderr
    r = subprocess.run(TOOL + ["--setup-status"], capture_output=True, text=True, env=env)
    st = json.loads(r.stdout)
    assert st["asked"] is False and st["key_saved"] is False
    assert st["database"] == os.path.realpath(DB) and st["version"] == mt.VERSION


def test_galaxy_bundle_has_no_setup(tmp_path):
    """The bundle script copies mlst_typing.py only; alone it types as
    before and says setup is not there."""
    with open(os.path.join(ROOT, "scripts", "bundle_tool.sh")) as fh:
        copies = [l for l in fh if l.lstrip().startswith("cp ")]
    assert copies and not any("mlst_typing_setup" in l or "mlst_typing_update" in l
                              for l in copies)
    with open(os.path.join(ROOT, "galaxywrapper", "tool.xml")) as fh:
        xml = fh.read()
    assert "--db '$__tool_directory__/database'" in xml
    assert "--setup" not in xml and "mlst_typing_setup" not in xml
    shutil.copy(os.path.join(ROOT, "tool", "mlst_typing.py"), tmp_path)
    alone = [sys.executable, str(tmp_path / "mlst_typing.py")]
    r = subprocess.run(alone + ["--setup"], capture_output=True, text=True)
    assert r.returncode == 1 and "not part of this install" in r.stderr
    r = subprocess.run(alone + ["--db", DB, "--version"], capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.startswith("mlst-typing ")


# A stand-in for rest.pubmlst.org: one scheme ("tiny"), the key test route
# and the three OAuth routes. Data routes want the API key or a signed
# request with the current session token.
class FakePubMLST(http.server.BaseHTTPRequestHandler):
    KEY = "good-key"
    CLIENT = ("ck", "cs")
    UPDATED = "2026-11-01"   # the scheme's date of last change
    tokens = {}          # token -> secret, filled as the sign-in goes on
    session = ["sess1"]  # the session token accepted right now

    def log_message(self, *a):
        pass

    def reply(self, code, body, kind="application/json"):
        data = (json.dumps(body) if kind.endswith("json") else body).encode()
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def signed_by(self, token_ok):
        """True when the OAuth signature in the query is right."""
        parts = urllib.parse.urlsplit(self.path)
        q = dict(urllib.parse.parse_qsl(parts.query))
        sig, token = q.pop("oauth_signature", ""), q.get("oauth_token", "")
        if q.get("oauth_consumer_key") != self.CLIENT[0] or not token_ok(token):
            return False
        extra = {k: v for k, v in q.items() if not k.startswith("oauth_")
                 or k in ("oauth_callback", "oauth_verifier")}
        again = su.oauth_url("GET", f"http://{self.headers['Host']}{parts.path}",
                             *self.CLIENT, token, self.tokens.get(token, ""),
                             extra=extra, nonce=q["oauth_nonce"],
                             timestamp=q["oauth_timestamp"])
        return dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(again).query)
                    )["oauth_signature"] == sig

    def allowed(self):
        if "X-API-Key" in self.headers:
            return self.headers["X-API-Key"] == self.KEY
        if "oauth_token" in self.path:
            return self.signed_by(lambda t: t == self.session[0])
        return None      # no login: the free data

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        base = f"http://{self.headers['Host']}"
        t = self.tokens
        if path.endswith("/oauth/get_request_token"):
            if not self.signed_by(lambda tok: tok == ""):
                return self.reply(401, {"message": "bad client key"})
            t["req"] = "reqsecret"
            return self.reply(200, {"oauth_token": "req", "oauth_token_secret": "reqsecret"})
        if path.endswith("/oauth/get_access_token"):
            if not (self.signed_by(lambda tok: tok == "req") and "oauth_verifier=1234" in self.path):
                return self.reply(401, {"message": "bad verifier"})
            t["acc"] = "accsecret"
            return self.reply(200, {"oauth_token": "acc", "oauth_token_secret": "accsecret"})
        if path.endswith("/oauth/get_session_token"):
            if not self.signed_by(lambda tok: tok == "acc"):
                return self.reply(401, {"message": "bad access token"})
            t[self.session[0]] = "sesssecret"
            return self.reply(200, {"oauth_token": self.session[0],
                                    "oauth_token_secret": "sesssecret"})
        ok = self.allowed()
        if ok is False:
            return self.reply(401, {"message": "The API key used cannot access this resource"})
        if path == su.CHECK_PATH or path == "/db/tiny_seqdef/schemes/1":
            info = {"loci": [f"{base}/db/tiny_seqdef/loci/abc"],
                    "profiles_csv": f"{base}/db/tiny_seqdef/schemes/1/profiles_csv",
                    "last_updated": self.UPDATED}
            if ok is None:
                info["message"] = "you are currently restricted to accessing data ... 2024-12-31"
            return self.reply(200, info)
        if path == "/db/tiny_seqdef/loci/abc/alleles_fasta":
            fa = ">abc_1\nACGTACGTAC\n" + (">abc_2\nACGTACGTAA\n" if ok else "")
            return self.reply(200, fa, "text/plain")
        if path == "/db/tiny_seqdef/schemes/1/profiles_csv":
            return self.reply(200, "ST\tabc\n1\t1\n" + ("2\t2\n" if ok else ""), "text/plain")
        return self.reply(404, {"message": "no such route"})


@pytest.fixture
def pubmlst(monkeypatch):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FakePubMLST)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    monkeypatch.setattr(su, "REST", base)
    FakePubMLST.tokens, FakePubMLST.session = {}, ["sess1"]
    FakePubMLST.UPDATED = "2026-11-01"
    yield base
    server.shutdown()


def tiny_bundled(tmp_path, base):
    """A bundled database with one scheme, as the free data has it."""
    db = tmp_path / "bundled"
    (db / "pubmlst" / "tiny").mkdir(parents=True)
    (db / "blast").mkdir()
    (db / "schemes.tsv").write_text(f"tiny\tpubmlst\t{base}/db/tiny_seqdef/schemes/1\t\t\n")
    (db / "pubmlst" / "tiny" / "abc.tfa").write_text(">abc_1\nACGTACGTAC\n")
    (db / "pubmlst" / "tiny" / "tiny.txt").write_text("ST\tabc\n1\t1\n")
    (db / "manifest.tsv").write_text(
        "scheme\tsource\tloci\talleles\tprofiles\tlast_updated\trestricted\ttaxon\tapi\n"
        f"tiny\tpubmlst\t1\t1\t1\t2024-12-01\tTrue\t\t{base}/db/tiny_seqdef/schemes/1\n")
    (db / "VERSION.txt").write_text("PubMLST_free\n")
    return str(db)


def test_key_check(pubmlst):
    assert su.check_key(su.KeySigner({"key": "good-key"})) is True
    with pytest.raises(su.SetupError, match="401"):
        su.check_key(su.KeySigner({"key": "wrong"}))


@pytest.mark.skipif(not shutil.which("makeblastdb"), reason="needs makeblastdb")
def test_key_file_builds_own_database(home, pubmlst, tmp_path, monkeypatch):
    monkeypatch.setattr(up.time, "sleep", lambda s: None)
    bundled = tiny_bundled(tmp_path, pubmlst)
    keyfile = tmp_path / "key.txt"
    keyfile.write_text("wrong\n")
    with pytest.raises(su.SetupError):
        su.setup_with_key(home, bundled, str(keyfile))
    assert not su.status(home)["key_saved"]                 # a refused key is not kept
    keyfile.write_text("good-key\n")
    assert su.setup_with_key(home, bundled, str(keyfile)) == 0
    st = su.status(home)
    assert st["key_saved"] and st["key_type"] == "apikey" and st["own_database"]
    own = home["db"]
    assert open(os.path.join(own, "VERSION.txt")).read().endswith("(own account)\n")
    assert ">abc_2" in open(os.path.join(own, "pubmlst", "tiny", "abc.tfa")).read()
    assert "\tFalse\t" in open(os.path.join(own, "manifest.tsv")).read()
    assert mt.find_database("") == os.path.realpath(own)
    # the bundled database is untouched, and nothing is left half-built
    assert open(os.path.join(bundled, "pubmlst", "tiny", "tiny.txt")).read() == "ST\tabc\n1\t1\n"
    assert not os.path.exists(own + ".new") and up.SIGNER is None
    assert su.update(home, bundled) == 0                    # nothing newer: still fine
    su.remove(home)
    st = su.status(home)
    assert not st["key_saved"] and not st["own_database"] and st["answer"] == "skipped"
    assert mt.find_database("") == os.path.realpath(DB)


def test_oauth_sign_in_and_session_renewal(home, pubmlst, monkeypatch):
    monkeypatch.setattr(up.time, "sleep", lambda s: None)
    monkeypatch.setattr(su, "ask", lambda prompt, hidden=False: "1234")
    with pytest.raises(su.SetupError):
        su.oauth_sign_in("ck", "not-the-secret")
    cred = su.oauth_sign_in("ck", "cs")
    assert cred["access_token"] == "acc" and cred["session_token"] == "sess1"
    signer = su.signer_for(cred, home)
    assert su.check_key(signer) is True
    # the session token runs out: the updater renews it once and carries on
    FakePubMLST.session[0] = "sess2"
    monkeypatch.setattr(up, "SIGNER", signer)
    assert "2\t2" in up.http_get(f"{pubmlst}/db/tiny_seqdef/schemes/1/profiles_csv")
    assert cred["session_token"] == "sess2"
    assert su.load_credentials(home)["session_token"] == "sess2"


# --------------------------------------------------------------------------
# setup without a terminal: OAuth in two steps and the check for newer data
# (what an app with its own "add your key" screen calls)
# --------------------------------------------------------------------------

def newer(capsys):
    return json.loads(capsys.readouterr().out)


def test_update_check_before_the_first_download(home, pubmlst, tmp_path, capsys):
    bundled = tiny_bundled(tmp_path, pubmlst)
    with pytest.raises(su.SetupError, match="no PubMLST key"):
        su.check_newer(home, bundled)
    su.save_credentials(home, {"type": "apikey", "key": "good-key"})
    assert su.check_newer(home, bundled) == 0
    found = newer(capsys)
    # the bundled database holds the free data; the key gives more
    assert found["newer"] is True and found["schemes_newer"] == ["tiny"]
    assert found["schemes_checked"] == 1 and found["schemes_failed"] == []
    assert found["database"] == bundled and found["database_version"] == "PubMLST_free"
    assert not su.status(home)["own_database"]              # nothing was downloaded
    # a key PubMLST refuses: the scheme counts as not checked, not as newer
    su.save_credentials(home, {"type": "apikey", "key": "wrong"})
    assert su.check_newer(home, bundled) == 0
    found = newer(capsys)
    assert found["newer"] is False and found["schemes_failed"] == ["tiny"]


@pytest.mark.skipif(not shutil.which("makeblastdb"), reason="needs makeblastdb")
def test_oauth_without_a_terminal(home, pubmlst, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(up.time, "sleep", lambda s: None)
    bundled = tiny_bundled(tmp_path, pubmlst)
    with pytest.raises(su.SetupError, match="--oauth-start"):
        su.oauth_finish(home, bundled, "1234")              # nothing started yet
    keys = tmp_path / "oauth.txt"
    keys.write_text("ck\n")
    with pytest.raises(su.SetupError, match="client secret"):
        su.oauth_start(home, str(keys))
    keys.write_text("ck\nnot-the-secret\n")
    with pytest.raises(su.SetupError):
        su.oauth_start(home, str(keys))
    assert not su.status(home)["oauth_waiting_for_code"]
    keys.write_text("ck\ncs\n")
    assert su.oauth_start(home, str(keys)) == 0
    page = json.loads(capsys.readouterr().out)["approve_url"]
    assert "page=authorizeClient" in page and page.endswith("oauth_token=req")
    st = su.status(home)
    assert st["oauth_waiting_for_code"] and not st["key_saved"]
    pending = os.path.join(home["config"], "oauth_pending.json")
    assert stat.S_IMODE(os.stat(pending).st_mode) == 0o600
    with pytest.raises(su.SetupError):
        su.oauth_finish(home, bundled, "0000")              # a wrong code ...
    assert su.status(home)["oauth_waiting_for_code"]        # ... can be given again
    assert su.oauth_finish(home, bundled, " 1234\n") == 0
    st = su.status(home)
    assert st["key_saved"] and st["key_type"] == "oauth" and st["own_database"]
    assert not st["oauth_waiting_for_code"] and not os.path.exists(pending)
    assert ">abc_2" in open(os.path.join(home["db"], "pubmlst", "tiny", "abc.tfa")).read()
    capsys.readouterr()
    # nothing newer than what was just downloaded
    assert su.check_newer(home, bundled) == 0
    found = newer(capsys)
    assert found["newer"] is False and found["schemes_checked"] == 1
    assert found["database"] == home["db"]
    # PubMLST changes the scheme: the check says so and downloads nothing
    FakePubMLST.UPDATED = "2026-12-01"
    assert su.check_newer(home, bundled) == 0
    assert newer(capsys)["schemes_newer"] == ["tiny"]
    assert "2026-11-01" in open(os.path.join(home["db"], "manifest.tsv")).read()
    # a sign-in left waiting is forgotten with the key
    assert su.oauth_start(home, str(keys)) == 0
    su.remove(home)
    st = su.status(home)
    assert not st["oauth_waiting_for_code"] and not st["key_saved"] and not st["own_database"]


def test_setup_options_without_a_terminal(tmp_path):
    env = {**os.environ, "XDG_CONFIG_HOME": str(tmp_path / "c"),
           "XDG_DATA_HOME": str(tmp_path / "d")}
    env.pop(mt.ENV_DB, None)

    def tool(*args):
        return subprocess.run(TOOL + list(args), capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, env=env)

    r = tool("--oauth-finish", "1234")
    assert r.returncode == 1 and "go with --setup" in r.stderr
    r = tool("--setup", "--oauth-start")
    assert r.returncode == 1 and "--key-file" in r.stderr
    r = tool("--setup", "--oauth-finish", "1234")
    assert r.returncode == 1 and "--oauth-start" in r.stderr
    r = tool("--update-check")
    assert r.returncode == 1 and "no PubMLST key" in r.stderr
    st = json.loads(tool("--setup-status").stdout)
    assert st["oauth_waiting_for_code"] is False and st["version"] == mt.VERSION
