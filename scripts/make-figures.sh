#!/bin/bash
# Render the web figures: figures/Unit_X/<name>.tex -> images/Unit_X/<name>.svg
#   scripts/make-figures.sh            all figures
#   scripts/make-figures.sh 1.3        only figures whose name starts with 1.3
# The handouts draw the same pictures in their own .tex, so a change to one
# is a change to the other.
set -euo pipefail
cd "$(dirname "$0")/.."
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
shopt -s nullglob
for tex in figures/Unit_*/*.tex; do
  name="$(basename "$tex" .tex)"
  if [[ $# -gt 0 ]]; then
    hit=false; for p in "$@"; do [[ "$name" == "$p"* ]] && hit=true; done
    $hit || continue
  fi
  unit="$(basename "$(dirname "$tex")")"
  mkdir -p "images/$unit"
  ( cd "$(dirname "$tex")" && pdflatex -interaction=nonstopmode -halt-on-error \
      -output-directory="$tmp" "$name.tex" >/dev/null ) \
    || { grep -A3 '^!' "$tmp/$name.log"; exit 1; }
  pdftocairo -svg "$tmp/$name.pdf" "images/$unit/$name.svg"
  echo "images/$unit/$name.svg"
done
