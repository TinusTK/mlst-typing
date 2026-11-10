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
checked against mlst on the same database: the same scheme, ST, alleles,
status and score on mlst's own test genomes and on one public genome for
every scheme, apart from ties that mlst breaks at random and the deliberate
differences listed below ([validation/REPORT.md](validation/REPORT.md)).

What changed:

- **Python** (3.9+, standard library only) plus BLAST+. No Perl modules and
  no any2fasta: FASTA, GenBank and EMBL, plain or `.gz`, `.bz2`, `.zip`, are
  read directly.
- **Database updater** (`scripts/update_database.py`) rebuilds every scheme
  from the PubMLST / BIGSdb-Pasteur REST API and records the version.
- **Database fixes**: profile files hold only ST and loci, so extra columns
  such as `MLST_cluster` are no longer treated as a locus; loci with names
  like `EF-2` or `rpoB'` are now matched.
- **Ties are shown, not hidden.** When two or more schemes get the same top
  score, mlst picks one of them at random, so the same genome can get a
  different scheme and ST from run to run. mlst-typing reports the first by
  name (the same answer every run) and lists every tied scheme with its ST
  in a new last column, `WARNINGS`.
- **MULTICOPY, a new status.** Some loci (16S, 23S and others) are in the
  genome in several copies. When every copy is the same allele, e.g.
  `16S(5,5,5,5,5)`, mlst reports `MIXED` and no ST. mlst-typing keeps all the
  copies in the output, looks up the ST and reports `MULTICOPY`, so `MIXED`
  only means different alleles at one locus, e.g. `glyA(1,142)`.
- **Clearer `--full` report**: columns FILE, SCHEME, ST, ALLELES, STATUS,
  SCORE, WARNINGS, and the status `OK` (some loci not exact, no ST) is
  renamed `PARTIAL` so it is not mistaken for a good result.
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

### What the output looks like

`mlst-typing --full` on a few genomes (real results from
[validation/REPORT.md](validation/REPORT.md) and the test files). The output
is tab-separated; shown here as a table:

| FILE | SCHEME | ST | ALLELES | STATUS | SCORE | WARNINGS |
|---|---|---|---|---|---|---|
| SF370.fna (*S. pyogenes*, Group A Strep) | spyogenes | 28 | gki(4);gtr(3);murI(4);mutS(4);recP(4);xpt(2);yqiL(4) | PERFECT | 100 | |
| FA1090.fna (*N. gonorrhoeae*) | neisseria | 1899 | abcZ(109);adk(39);aroE(67);fumC(190);gdh(147);pdhC(71);pgm(65) | PERFECT | 100 | |
| Ss046.fna (*Shigella sonnei*) | ecoli_achtman_4 | 152 | adk(11);fumC(63);gyrB(7);icd(1);mdh(14);purA(7);recA(7) | PERFECT | 100 | |
| novel.fasta.bz2 (*Leptospira*) | leptospira_2 | - | adk_2(85);glmU_2(~24);icdA_2(~46);lipL32_2(20);lipL41_2(39);mreA_2(~56);pntA_2(~26) | PARTIAL | 74 | |
| HS11286.fna (*K. pneumoniae*) | ecoli_achtman_4 | 14464 | adk(1769);fumC(1664);gyrB(193);icd(1804);mdh(986);purA(745);recA(866) | PERFECT | 100 | TIE: ecoli_achtman_4 (ST14464), klebsiella (ST11) |
| ruckeri.fna (*Y. ruckeri*) | yersinia | 44 | aarF(13);dfp(10);galR(14);glnS(13);hemA(15);rfaE(14);speA(14) | PERFECT | 100 | TIE: yersinia (ST44), ypseudotuberculosis_achtman_3 (ST276), yruckeri (ST33) |
| none.fa (no MLST genes) | - | - | | NONE | 0 | |

Without `--full` the layout is the same as mlst: FILE, SCHEME, ST, one
column per locus, then WARNINGS.

| Call  | Meaning |
|---|---|
| `N`   | exact match to allele N |
| `~N`  | full length but not exact; closest is N (possible novel allele) |
| `N?`  | partial match (coverage at least `--mincov`) |
| `-`   | missing |
| `N,N` | more than one copy of the same exact allele (multi-copy locus) |
| `N,M` | more than one different exact allele (possible contamination) |

`--full` puts the alleles in one column and adds STATUS and SCORE (out of
100). STATUS is one of:

| STATUS | Meaning |
|---|---|
| `PERFECT` | all loci exact and the profile has an ST |
| `PARTIAL` | all loci found, some not exact (`~N`/`N?`), so no ST (mlst calls this `OK`) |
| `NOVEL` | all alleles exact, but a combination with no ST yet |
| `MULTICOPY` | a locus is there in several copies of the same allele (`N,N`); the ST is reported when the profile has one (mlst calls this `MIXED`, without an ST) |
| `MIXED` | different exact alleles at one locus (`N,M`), so no ST (possible contamination) |
| `MISSING` | a locus was not found |
| `BAD` | score under 70 |
| `NONE` | no scheme matched |
 `--json FILE` and `--novel FILE` write JSON
results and novel allele sequences.

**WARNINGS** (last column in the default and `--full` layouts, `warnings`
in JSON) is empty unless several schemes tie for the top score. It then
reads `TIE: scheme (STx), scheme (STy)`. The tied schemes number their STs
separately, so the ST depends on which scheme is right for your species:
for example *Klebsiella pneumoniae* HS11286 ties between `klebsiella` ST11
(correct) and `ecoli_achtman_4` ST14464. Check the species and use that
scheme, or rerun with `--scheme`.

Compared with mlst 2.35.0: the default layout only gains the WARNINGS
column at the end, so pipelines that read it by position keep working. The
`--full` layout is reordered to FILE, SCHEME, ST, ALLELES, STATUS, SCORE,
WARNINGS, and mlst's `OK` status is called `PARTIAL`. Genomes with several
identical copies of a locus are `MULTICOPY` with their ST, where mlst
reports `MIXED` and no ST.

## Database

`database/` is bundled with every release and never downloaded at run time.

| Version | Schemes | Data |
|---|---|---|
| `PubMLST_2026-11` | 162 | PubMLST + BIGSdb-Pasteur, submitted up to 31 Dec 2024 |

See [database/README.md](database/README.md) for the source, the terms of
use and how to update it.

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
- **Galaxy Australia** (https://usegalaxy.org.au), where the Galaxy wrapper
  is meant to run. Galaxy Australia is a service provided by Australian
  BioCommons and its partners. The service receives NCRIS funding through
  Bioplatforms Australia and the Australian Research Data Commons
  (https://doi.org/10.47486/PL105), as well as The University of Melbourne
  and Queensland Government RICF funding.

## Licence

GPL-2.0, see [LICENSE](LICENSE). Allele and profile data remain under the
terms of PubMLST and BIGSdb-Pasteur.
