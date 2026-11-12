# mlst-typing

Automatic MLST (multi-locus sequence typing) of assembled bacterial genomes
against the PubMLST typing schemes, cross-checked with EnteroBase. Give it
one or more assemblies; it finds the scheme that fits best and reports the
sequence type (ST) and the allele of every locus. You do not need to know
the species first.

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
  from the PubMLST / BIGSdb-Pasteur REST API and from EnteroBase's public
  scheme downloads, and records the version of each.
- **Your own PubMLST key (optional, command line).** PubMLST gives data
  submitted from 2025 on only to users with their own account. You can enter
  your own key (the Public data access key or an OAuth key) and the tool
  downloads an up-to-date database to your computer and types against it.
  Skip it and the built-in free database is used; you can add a key any
  time later with `mlst-typing --setup`
  ([details](#up-to-date-pubmlst-data-with-your-own-key-optional)).
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
- **Clearer `--full` report**: columns FILE, SCHEME, ST, ALLELE1 to
  ALLELE10 (one column per allele), STATUS, SCORE, WARNINGS, and the status
  `OK` (some loci not exact, no ST) is renamed `PARTIAL` so it is not
  mistaken for a good result.
- **EnteroBase as a second source.** Every genome is also typed against the
  EnteroBase 7-gene schemes (*Escherichia*, *Salmonella*, *Yersinia*,
  *Moraxella*), which hold newer STs than the free PubMLST data. PubMLST
  stays the main source: the EnteroBase result is only reported when PubMLST
  has no ST, and `WARNINGS` always says so. See
  [How to read the report](#how-to-read-the-report).
- **Galaxy wrapper** ready for Galaxy Australia, in
  [galaxywrapper/](galaxywrapper/).

## Install

```bash
conda env create -f environment.yml    # python 3.12 + blast 2.16.0
conda activate mlst-typing
pip install .                          # gives the mlst-typing command, with the database
```

The database is installed with it, so the command works from any folder. To
use another copy, pass `--db` or set `MLST_TYPING_DB`.

### Up-to-date PubMLST data with your own key (optional)

The built-in database holds PubMLST data submitted up to 31 December 2024,
which is free and needs no account. PubMLST gives newer data only to users
with their own account and key. The first time you run `mlst-typing` in a
terminal it explains this and asks once:

- **Add my key**: make a free account at https://pubmlst.org, accept its
  terms and create a key in your account profile. Either kind works: the
  *Public data access key* (one key, the simple way) or an *OAuth* key
  (client key and client secret, plus one approval in your browser). The
  tool tests the key, downloads the current schemes to your computer (about
  1.5 hours, once) and uses that database from then on.
- **Skip**: the built-in database is used. Nothing else changes.

You can skip now and add a key whenever you get one:

| Command | What it does |
|---|---|
| `mlst-typing --setup` | ask again: add or replace your key, then download |
| `mlst-typing --update` | refresh your own database with the saved key |
| `mlst-typing --setup --remove` | forget the key and your own database; back to the built-in one |
| `mlst-typing --setup --key-file FILE` | no questions: read the public data access key from `FILE` (`-` = stdin), for apps and scripts |
| `mlst-typing --setup-status` | where setup stands, as JSON (never shows the key) |

The key is kept in `~/.config/mlst-typing/credentials.json` (readable only
by you) and your database in `~/.local/share/mlst-typing/database`. It is
only on your computer: data from 2025 on may not be passed on. A scheme
PubMLST does not give your account keeps its built-in data. `--db` and
`MLST_TYPING_DB` still win over your own database.

The question is never asked when there is no terminal (pipelines, scripts)
or when `--db` or `MLST_TYPING_DB` is set. **Galaxy is not affected**: the
Galaxy tool always uses its bundled database and does not include the setup.

PubMLST says the public data access key is not for commercial software;
commercial users need OAuth application keys from PubMLST.

or run the script directly: `python tool/mlst_typing.py`.

## Use

```bash
mlst-typing contigs.fasta                       # auto-detect the scheme
mlst-typing --full *.fasta > results.tsv        # one column per allele, STATUS and SCORE
mlst-typing --full --combine-alleles *.fasta    # all alleles in one ALLELES column
mlst-typing --scheme spyogenes genome.gbk.gz    # force one scheme
mlst-typing --full *.fasta --outfile results.tsv \
    --outfile-pubmlst pubmlst.tsv --outfile-enterobase enterobase.tsv   # all three reports
mlst-typing --no-enterobase contigs.fasta       # PubMLST only
mlst-typing --list | --longlist | --info        # what is in the database
mlst-typing --version                           # tool and database version
```

### What the output looks like

`mlst-typing --full` on a few genomes (real results from
[validation/REPORT.md](validation/REPORT.md) and the test files). The output
is tab-separated; shown here as a table:

| FILE | SCHEME | ST | ALLELE1 | ALLELE2 | ALLELE3 | ALLELE4 | ALLELE5 | ALLELE6 | ALLELE7 | ALLELE8 | ALLELE9 | ALLELE10 | STATUS | SCORE | WARNINGS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SF370.fna (*S. pyogenes*, Group A Strep) | spyogenes | 28 | gki(4) | gtr(3) | murI(4) | mutS(4) | recP(4) | xpt(2) | yqiL(4) |  |  |  | PERFECT | 100 | |
| FA1090.fna (*N. gonorrhoeae*) | neisseria | 1899 | abcZ(109) | adk(39) | aroE(67) | fumC(190) | gdh(147) | pdhC(71) | pgm(65) |  |  |  | PERFECT | 100 | |
| Ss046.fna (*Shigella sonnei*) | ecoli_achtman_4 | 152 | adk(11) | fumC(63) | gyrB(7) | icd(1) | mdh(14) | purA(7) | recA(7) |  |  |  | PERFECT | 100 | |
| novel.fasta.bz2 (*Leptospira*) | leptospira_2 | - | adk_2(85) | glmU_2(~24) | icdA_2(~46) | lipL32_2(20) | lipL41_2(39) | mreA_2(~56) | pntA_2(~26) |  |  |  | PARTIAL | 74 | No ST: PubMLST PARTIAL, EnteroBase NONE |
| ecoli_enterobase_only.fa (*E. coli* test file) | ecoli_achtman_enterobase | 17227 | adk(10) | fumC(11) | gyrB(4) | icd(8) | mdh(8) | purA(8) | recA(644) |  |  |  | PERFECT | 100 | EnteroBase ST, no PubMLST (PubMLST: ecoli_achtman_4 NOVEL) |
| HS11286.fna (*K. pneumoniae*) | ecoli_achtman_4 | 14464 | adk(1769) | fumC(1664) | gyrB(193) | icd(1804) | mdh(986) | purA(745) | recA(866) |  |  |  | PERFECT | 100 | TIE: ecoli_achtman_4 (ST14464), klebsiella (ST11) |
| ruckeri.fna (*Y. ruckeri*) | yersinia | 44 | aarF(13) | dfp(10) | galR(14) | glnS(13) | hemA(15) | rfaE(14) | speA(14) |  |  |  | PERFECT | 100 | TIE: yersinia (ST44), ypseudotuberculosis_achtman_3 (ST276), yruckeri (ST33) |
| none.fa (no MLST genes) | - | - |  |  |  |  |  |  |  |  |  |  | NONE | 0 | No ST: PubMLST NONE, EnteroBase NONE |

Schemes have 3 to 10 loci. `--full` always writes ten allele columns,
ALLELE1 to ALLELE10, each holding one locus and its call (`gki(4)`); a scheme
with fewer loci leaves the last ones empty, so STATUS, SCORE and WARNINGS
are always in the same columns. `--full --combine-alleles` puts the alleles
in a single ALLELES column instead, joined with `;`
(`gki(4);gtr(3);murI(4);...`): FILE, SCHEME, ST, ALLELES, STATUS, SCORE,
WARNINGS. That was the `--full` layout up to version 0.2.0.

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

`--full` adds a header row, STATUS and SCORE (out of 100). STATUS is one of:

| STATUS | Meaning |
|---|---|
| `PERFECT` | all loci exact and the profile has an ST |
| `PARTIAL` | all loci found, some not exact (`~N`/`N?`), so no ST (mlst calls this `OK`) |
| `NOVEL` | all alleles exact, but a combination with no ST yet |
| `MULTICOPY` | a locus is there in several copies of the same allele (`N,N`); the ST is reported when the profile has one (mlst calls this `MIXED`, without an ST) |
| `MIXED` | different exact alleles at one locus (`N,M`), so no ST (possible contamination) |
| `MISSING` | at least one allele missing (`-`) |
| `BAD` | score under 70 |
| `NONE` | no scheme matched |
 `--json FILE` and `--novel FILE` write JSON
results and novel allele sequences.

### How to read the report

Every genome is typed twice: against **PubMLST** (the main source, with
BIGSdb-Pasteur) and against **EnteroBase**. The report combines the two, and
**WARNINGS** (last column in the default and `--full` layouts, `warnings` in
JSON) tells you which case you are looking at. SCHEME, ST, the alleles,
STATUS and SCORE always come from the source shown in the row; EnteroBase scheme
names end in `_enterobase`.

"ST" below means a numbered ST (STATUS `PERFECT`, or `MULTICOPY` with an
ST). "Same scheme" means the PubMLST and the EnteroBase scheme have the same
loci, e.g. `ecoli_achtman_4` and `ecoli_achtman_enterobase`.

| # | PubMLST | EnteroBase | Row shows | WARNINGS |
|---|---|---|---|---|
| 1 | ST | no scheme | PubMLST | (empty) |
| 2 | ST | same scheme, same ST | PubMLST | (empty) |
| 3 | ST | same scheme, different ST | PubMLST | `EnteroBase differs: <scheme> (ST<n>)` |
| 4 | ST | same scheme, no ST | PubMLST | (empty) |
| 5 | ST | different scheme (any result) | PubMLST | (empty); see the EnteroBase report |
| 6 | scheme, no ST | ST | **EnteroBase** | `EnteroBase ST, no PubMLST (PubMLST: <scheme> <STATUS>)` |
| 7 | no scheme | ST | **EnteroBase** | `EnteroBase ST, no PubMLST (PubMLST: NONE)` |
| 8 | scheme, no ST | scheme, no ST | PubMLST | `No ST: PubMLST <STATUS>, EnteroBase <scheme> <STATUS>` |
| 9 | scheme, no ST | no scheme | PubMLST | `No ST: PubMLST <STATUS>, EnteroBase NONE` |
| 10 | no scheme | scheme, no ST | PubMLST (`-`, `NONE`) | `No ST: PubMLST NONE, EnteroBase <scheme> <STATUS>` |
| 11 | no scheme | no scheme | PubMLST (`-`, `NONE`) | `No ST: PubMLST NONE, EnteroBase NONE` |

In short: an empty WARNINGS means PubMLST gave an ST and EnteroBase does not
contradict it. Anything else is worth a look.

- **Case 6 and 7** are the reason EnteroBase is there: the ST is newer than
  the free PubMLST data. The warning names what PubMLST found, so check it
  is the same organism: EnteroBase's *E. coli* scheme also holds STs of
  other species, so a *Klebsiella* could read
  `EnteroBase ST, no PubMLST (PubMLST: klebsiella NOVEL)`.
- **Case 3** should not happen for schemes that share their numbering; if it
  does, look at both reports.
- **EnteroBase NONE** in a warning is normal for any organism EnteroBase
  does not hold (everything outside the four genera above).

**Ties.** WARNINGS can also hold `TIE: scheme (STx), scheme (STy)` when
several schemes of the source shown tie for the top score (joined to the
text above with `; `). The tied schemes number their STs separately, so the
ST depends on which scheme is right for your species: for example
*Klebsiella pneumoniae* HS11286 ties between `klebsiella` ST11 (correct)
and `ecoli_achtman_4` ST14464. Check the species and use that scheme, or
rerun with `--scheme`.

**Three reports.** `--outfile` (or the screen) is the combined report
above. `--outfile-pubmlst` and `--outfile-enterobase` also save what each
source gives on its own, in the same layout (the PubMLST one is what
`--no-enterobase` prints). With `--scheme` only that scheme is typed and
the two sources are not compared.

Compared with mlst 2.35.0: the default layout only gains the WARNINGS
column at the end, so pipelines that read it by position keep working. The
`--full` layout is FILE, SCHEME, ST, ALLELE1 to ALLELE10, STATUS, SCORE,
WARNINGS (mlst: FILE, SCHEME, ST, STATUS, SCORE, ALLELES in one column),
and mlst's `OK` status is called `PARTIAL`. Genomes with several
identical copies of a locus are `MULTICOPY` with their ST, where mlst
reports `MIXED` and no ST.

## Database

`database/` is bundled with every release and never downloaded at run time.
(Your own database, if you add a PubMLST key, is downloaded once by
`mlst-typing --setup`: see Install.)

| Version | Schemes | Data |
|---|---|---|
| `PubMLST_2026-11` | 162 | PubMLST + BIGSdb-Pasteur, submitted up to 31 Dec 2024 |
| `EnteroBase_2026-11-11` | 5 | EnteroBase public scheme downloads, current on that day |

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
- **EnteroBase** (https://enterobase.warwick.ac.uk): Zhou Z, Alikhan N-F,
  Mohamed K, Fan Y, the Agama Study Group, Achtman M. The EnteroBase user's
  guide, with case studies on *Salmonella* transmissions, *Yersinia pestis*
  phylogeny, and *Escherichia* core genomic diversity. Genome Res 2020,
  30:138-152. https://doi.org/10.1101/gr.251678.119. The schemes named
  `*_enterobase` are EnteroBase's 7-gene MLST schemes, unmodified apart from
  the file layout. Cite EnteroBase when you report an EnteroBase ST.
- **Galaxy Australia** (https://usegalaxy.org.au), where the Galaxy wrapper
  is meant to run. Galaxy Australia is a service provided by Australian
  BioCommons and its partners. The service receives NCRIS funding through
  Bioplatforms Australia and the Australian Research Data Commons
  (https://doi.org/10.47486/PL105), as well as The University of Melbourne
  and Queensland Government RICF funding.

## Licence

GPL-2.0, see [LICENSE](LICENSE). Allele and profile data remain under the
terms of PubMLST, BIGSdb-Pasteur and EnteroBase (academic use; see
[database/README.md](database/README.md)).
