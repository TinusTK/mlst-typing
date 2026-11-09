# mlst-typing

Automatic MLST (multi-locus sequence typing) of assembled bacterial genomes
against the PubMLST typing schemes. Give it one or more assemblies; it finds
the scheme that fits best and reports the sequence type (ST) and the allele
of every locus. You do not need to know the species first.

## Why this tool

mlst-typing is a redesign of Torsten Seemann's
[mlst](https://github.com/tseemann/mlst). I rebuilt it in Python in place of
the original Perl, and added a database updater so typing can follow the
current PubMLST schemes. The typing method (BLAST of every scheme's alleles,
the scoring and the allele notation) follows mlst, and the results are
checked against mlst on the same database: identical output on mlst's own
test genomes and on one public genome for every scheme
([validation/REPORT.md](validation/REPORT.md)).

What changed:

- **Python** (3.9+, standard library only) plus BLAST+. No Perl modules and
  no any2fasta: FASTA, GenBank and EMBL, plain or `.gz`, `.bz2`, `.zip`, are
  read directly.
- **Database updater** (`scripts/update_database.py`) rebuilds every scheme
  from the PubMLST / BIGSdb-Pasteur REST API and records the version.
- **Database fixes**: profile files hold only ST and loci, so extra columns
  such as `MLST_cluster` are no longer treated as a locus; loci with names
  like `EF-2` or `rpoB'` are now matched.
- **Ties** between equally scoring schemes are settled in name order every
  run (mlst picks at random) and are still reported as a warning.
- **Galaxy wrapper** ready for Galaxy Australia.

## Install

```bash
conda env create -f environment.yml    # python 3.12 + blast 2.16.0
conda activate mlst-typing
pip install .                          # gives the mlst-typing command
```

or run the script directly: `python tool/mlst_typing.py`.

## Use

```bash
mlst-typing contigs.fasta                       # auto-detect the scheme
mlst-typing --full *.fasta > results.tsv        # STATUS and SCORE columns
mlst-typing --scheme spyogenes genome.gbk.gz    # force one scheme
mlst-typing --list | --longlist | --info        # what is in the database
mlst-typing --version                           # tool and database version
```

Output (default, tab-separated):

```
FILE          SCHEME        ST   ALLELES...
sample1.fasta sepidermidis  184  arcC(16) aroE(20) gtr(5) mutS(5) pyrR(15) tpiA(5) yqiL(16)
```

| Call  | Meaning |
|---|---|
| `N`   | exact match to allele N |
| `~N`  | full length but not exact; closest is N (possible novel allele) |
| `N?`  | partial match (coverage at least `--mincov`) |
| `-`   | missing |
| `N,M` | more than one exact allele (possible contamination) |

`--full` adds STATUS (`PERFECT`, `OK`, `NOVEL`, `MIXED`, `MISSING`, `BAD`,
`NONE`) and SCORE (out of 100). `--json FILE` and `--novel FILE` write JSON
results and novel allele sequences. The options and output are the same as
mlst 2.35.0, so existing pipelines can switch without changes.

## Database

`database/` is bundled with every release and never downloaded at run time.

| Version | Schemes | Data |
|---|---|---|
| `PubMLST_2026-11` | 162 | PubMLST + BIGSdb-Pasteur, submitted up to 31 Dec 2024 |

See [database/README.md](database/README.md) for the source, the terms of
use and how to update it.

## Galaxy

`tool/tool.xml` is the Galaxy wrapper. Build an installable bundle with
`bash scripts/bundle_tool.sh` (it copies the database next to the wrapper)
and lint or test that bundle with planemo.

## Credits and citation

- **mlst**: Seemann T, https://github.com/tseemann/mlst. mlst-typing follows
  its method and is released under the same licence (GPL-2.0).
- **PubMLST**: Jolley KA, Bray JE, Maiden MCJ. Open-access bacterial
  population genomics: BIGSdb software, the PubMLST.org website and their
  applications. Wellcome Open Res 2018, 3:124.
  https://doi.org/10.12688/wellcomeopenres.14826.1
- This publication made use of the PubMLST website (https://pubmlst.org/)
  developed by Keith Jolley and sited at the University of Oxford. The
  development of that website was funded by the Wellcome Trust.
- BIGSdb-Pasteur (https://bigsdb.pasteur.fr) for the schemes hosted there.

## Licence

GPL-2.0, see [LICENSE](LICENSE). Allele and profile data remain under the
terms of PubMLST and BIGSdb-Pasteur.
