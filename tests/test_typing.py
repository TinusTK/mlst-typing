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
    ("-", 80, ["1", "-"], "MISSING"),
    ("-", 60, ["1", "~2"], "BAD"),
    ("-", 85, ["1", "~2"], "OK"),
])
def test_status(st, score, code, status):
    assert mt.status_column(st, score, code) == status


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
def test_full_header_has_warnings():
    r = run("-q", "--full", os.path.join(DATA, "example.fna.gz"))
    assert r.stdout.splitlines()[0].split("\t")[-1] == "WARNINGS"


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


@needs_upstream
@pytest.mark.parametrize("mode", MODES, ids=lambda m: " ".join(m) or "default")
def test_same_as_upstream(mode):
    files = [os.path.join(DATA, f) for f in INPUTS]
    a = upstream("-q", *mode, *files)
    b = run("-q", *mode, *files)
    assert a.returncode == b.returncode == 0, a.stderr + b.stderr
    ours = b.stdout if "--legacy" in mode else drop_warnings(b.stdout, "," if "--csv" in mode else "\t")
    assert ours == a.stdout
