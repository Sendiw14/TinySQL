#!/bin/sh
# Generates docs/route-matrix.csv from the route tables in master prompt Section 7.
# --check: fail if the committed CSV is stale or the counts are not 11 public + 7 studio.
set -eu
cd "$(dirname "$0")/.."
src=docs/implementation/master-prompt.md
out=docs/route-matrix.csv
gen() {
  echo "route,app,status,wireframe,implementation,navigation_test"
  awk '
    /^### A\. Public STATIC site/ { app="site" }
    /^### B\. LOCAL Studio/       { app="studio" }
    /^### C\./                    { app="" }
    app != "" && /^\| `\// { split($0, f, "`"); print f[2] "," app ",PROPOSED,UNVERIFIED,UNVERIFIED,UNVERIFIED" }
  ' "$src"
}
if [ "${1:-}" = "--check" ]; then
  tmp=$(mktemp); gen > "$tmp"
  site=$(grep -c ',site,' "$tmp"); studio=$(grep -c ',studio,' "$tmp")
  [ "$site" -eq 11 ] && [ "$studio" -eq 7 ] || { echo "route count wrong: site=$site studio=$studio"; rm -f "$tmp"; exit 1; }
  cmp -s "$tmp" "$out" || { echo "$out is stale; run scripts/gen-route-matrix.sh"; rm -f "$tmp"; exit 1; }
  rm -f "$tmp"; echo "route matrix OK: 11 site + 7 studio"
else
  gen > "$out"
fi
