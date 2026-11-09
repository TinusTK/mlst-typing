#!/usr/bin/env bash
# Download every assembly in validation/genomes.tsv into validation/genomes/
# as <accession>.fna.gz (skips ones already there). Needs NCBI `datasets`.
set -euo pipefail
cd "$(dirname "$0")/.."
out=validation/genomes
mkdir -p "$out"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

cut -f3 validation/genomes.tsv | tail -n +2 | grep -v '^$' | sort -u | while read -r acc; do
  [ -s "$out/$acc.fna.gz" ] && continue
  echo "Fetching $acc" >&2
  if datasets download genome accession "$acc" --include genome \
       --filename "$tmp/$acc.zip" --no-progressbar >/dev/null 2>&1; then
    unzip -p "$tmp/$acc.zip" 'ncbi_dataset/data/*/*.fna' | gzip -c > "$out/$acc.fna.gz"
    rm -f "$tmp/$acc.zip"
  else
    echo "  FAILED $acc" >&2
  fi
done
ls "$out" | wc -l | xargs echo "genomes in $out:" >&2
