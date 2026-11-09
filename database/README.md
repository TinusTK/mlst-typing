# Database

Built by `scripts/update_database.py` from the PubMLST and BIGSdb-Pasteur
REST APIs. Do not edit by hand (except `schemes.tsv`).

```text
schemes.tsv                    schemes to fetch: name, source, API URL (hand-maintained)
VERSION.txt                    e.g. PubMLST_2026-11
manifest.tsv                   per scheme: loci, alleles, STs, last_updated, taxon
pubmlst/<scheme>/<locus>.tfa   alleles, >locus_N
pubmlst/<scheme>/<scheme>.txt  ST profiles (ST + loci only)
blast/mlst.fa.*                BLAST+ index of all alleles, >scheme.locus_N
```

The layout matches mlst's `db/`, so upstream mlst can also run on it
(`--blastdb database/blast/mlst.fa --datadir database/pubmlst`).

## Data and terms

The data is the **standard, freely available** set: alleles and profiles
submitted to PubMLST / BIGSdb-Pasteur up to **31 December 2024**, which is
what both servers give without authentication. Data submitted from 2025 on
is covered by newer PubMLST terms (no redistribution) and is not included.

Allele and profile definitions are the work of the PubMLST and
BIGSdb-Pasteur curators. Please cite PubMLST (Jolley et al. 2018,
https://doi.org/10.12688/wellcomeopenres.14826.1) and check the terms at
https://pubmlst.org before reusing the data.

## Updating

```bash
python scripts/update_database.py --db database --version-label PubMLST_YYYY-MM \
    --summary CHANGES_DB.md
```

Exit code 3 means nothing changed. After an update: run the tests and
`scripts/validate.py`, add the new version to the README table, and raise
the `+galaxyN` suffix in `tool/tool.xml` (database-only change).
