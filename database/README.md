# Database

Built by `scripts/update_database.py` from the PubMLST and BIGSdb-Pasteur
REST APIs and from EnteroBase's public scheme downloads. Do not edit by hand
(except `schemes.tsv`).

```text
schemes.tsv                    schemes to fetch: name, source, API URL (hand-maintained)
VERSION.txt                    line 1 PubMLST_2026-11, line 2 EnteroBase_2026-11-11
manifest.tsv                   per scheme: source, loci, alleles, STs, last_updated, taxon
pubmlst/<scheme>/<locus>.tfa   alleles, >locus_N
pubmlst/<scheme>/<scheme>.txt  ST profiles (ST + loci only)
blast/mlst.fa.*                BLAST+ index of all PubMLST/Pasteur alleles, >scheme.locus_N
enterobase/<scheme>/…          EnteroBase schemes, same two file types
blast/enterobase.fa.*          BLAST+ index of the EnteroBase alleles
```

PubMLST and EnteroBase are kept apart on purpose: the tool types a genome
against each one on its own and then combines the two results (see "How to
read the report" in the main README).

The layout matches mlst's `db/`, so upstream mlst can also run on it
(`--blastdb database/blast/mlst.fa --datadir database/pubmlst`).

## Data and terms

The PubMLST and BIGSdb-Pasteur data is the **standard, freely available**
set: alleles and profiles submitted to PubMLST up to **31 December 2024**, which is what the server
gives without authentication. Data submitted from 2025 on is covered by
newer PubMLST terms (no redistribution) and is not included.

To use data submitted from 2025 onward you must create your own PubMLST
account at https://pubmlst.org and accept its terms. Then create a key in
your account profile (the Public data access key, or an OAuth key) and run
`mlst-typing --setup`: it downloads the current schemes into a database of
your own, on your computer (`~/.local/share/mlst-typing/database`), and the
tool uses it from then on. That database is yours alone; it is never part
of this repository, the releases or the Galaxy tool.

Allele and profile definitions are the work of the PubMLST and
BIGSdb-Pasteur curators. Please cite PubMLST (Jolley et al. 2018,
https://doi.org/10.12688/wellcomeopenres.14826.1) and check the terms at
https://pubmlst.org before reusing the data.

## EnteroBase

Five 7-gene MLST schemes come from EnteroBase's public scheme folders
(`https://enterobase.warwick.ac.uk/schemes/<folder>/`: `profiles.list.gz`
and one `<locus>.fasta.gz` per locus). The data is current on the day of
the download (line 2 of `VERSION.txt`).

| Scheme here | EnteroBase folder | PubMLST copy with the same numbering |
|---|---|---|
| `ecoli_achtman_enterobase` | `Escherichia.Achtman7GeneMLST` | `ecoli_achtman_4` |
| `senterica_achtman_enterobase` | `Salmonella.Achtman7GeneMLST` | `salmonella`, `senterica_achtman_2` |
| `ypseudotuberculosis_achtman_enterobase` | `Yersinia.Achtman7GeneMLST` | `ypseudotuberculosis_achtman_3` |
| `yersinia_mcnally_enterobase` | `Yersinia.McNally` | `yersinia` |
| `mcatarrhalis_achtman_enterobase` | `Moraxella.Achtman7GeneMLST` | `mcatarrhalis_achtman_6` |

Checked on 11 Nov 2026: every allele and every ST that is in both the
EnteroBase scheme and its PubMLST copy is identical, so an ST number means
the same in both. EnteroBase's *Clostridioides difficile* scheme
(`clostridium.Griffiths`) is **left out**: it numbers alleles and STs
differently from PubMLST, so its STs would be misread.

Terms: EnteroBase is provided for academic use; redistributed data must
name EnteroBase as the source (https://enterobase.warwick.ac.uk/terms). The
files here are EnteroBase's schemes, changed only in file layout (headers
`>locus_N`, profiles as ST + loci). Please cite Zhou et al. 2020, Genome
Res 30:138-152 (https://doi.org/10.1101/gr.251678.119). For any other use,
ask EnteroBase (enterobase@warwick.ac.uk).

## Updating

```bash
python scripts/update_database.py --db database --version-label PubMLST_YYYY-MM \
    --summary CHANGES_DB.md
```

`scripts/update_database.py` only calls `tool/mlst_typing_update.py`, where
the code lives so that a pip install carries it for `mlst-typing --setup`.
Without a key it fetches the free data only, and that is what the bundled
database and the yearly refresh use.

The database is refreshed **once a year** (1 January) by a GitHub Actions
workflow. It downloads the schemes again, runs the tests and, if anything
changed, opens a pull request with a summary of the changes to accept or
reject. Nothing changes in the tool until that pull request is merged.

Add `--source enterobase` (or `--source pubmlst`) to refresh one part and
leave the other as it is; the EnteroBase part takes under a minute.

Exit code 3 means nothing changed. After an update: run the tests and
`scripts/validate.py`, add the new version to the README table, and raise
the `+galaxyN` suffix in `galaxywrapper/tool.xml` (database-only change).
