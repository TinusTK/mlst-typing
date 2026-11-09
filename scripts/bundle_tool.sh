#!/usr/bin/env bash
# Assemble a Galaxy-installable tool directory with the database bundled:
#   bash scripts/bundle_tool.sh [outdir]   -> <outdir>/mlst_typing/
# Lint and test this bundle, never tool/ (database/ only sits next to
# tool.xml here, and <required_files> must match it).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/build}"
DEST="$OUT/mlst_typing"
[ -f "$ROOT/database/blast/mlst.fa.nsq" ] || {
  echo "database/ is empty - run scripts/update_database.py first" >&2; exit 1; }
rm -rf "$DEST" && mkdir -p "$DEST/database"
cp "$ROOT"/tool/tool.xml "$ROOT"/tool/mlst_typing.py "$ROOT"/.shed.yml "$ROOT"/LICENSE "$DEST"/
cp -r "$ROOT"/tool/test-data "$DEST"/
cp -r "$ROOT"/database/pubmlst "$ROOT"/database/blast "$DEST"/database/
cp "$ROOT"/database/VERSION.txt "$ROOT"/database/manifest.tsv "$ROOT"/database/README.md "$DEST"/database/
echo "Bundled tool at $DEST (database $(head -1 "$ROOT/database/VERSION.txt"))"
