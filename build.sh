#!/bin/bash
# Build the printable mini lesson PDFs: student copy and _KEY copy from one .tex.
#   ./build.sh                 all handouts
#   ./build.sh 1.3             only lessons whose file name starts with 1.3
set -euo pipefail
cd "$(dirname "$0")"
shopt -s nullglob
for tex in handouts/Unit_*/*.tex; do
  base="$(basename "$tex" .tex)"
  if [[ $# -gt 0 ]]; then
    hit=false; for p in "$@"; do [[ "$base" == "$p"* ]] && hit=true; done
    $hit || continue
  fi
  dir="$(dirname "$tex")"
  ( cd "$dir"
    pdflatex -interaction=nonstopmode -halt-on-error "$base.tex" >/dev/null \
      || { grep -A3 '^!' "$base.log"; exit 1; }
    pdflatex -interaction=nonstopmode -halt-on-error -jobname="${base}_KEY" "\def\iskey{}\input{$base}" >/dev/null \
      || { grep -A3 '^!' "${base}_KEY.log"; exit 1; }
    rm -f "$base".{aux,log} "${base}_KEY".{aux,log} )
  echo "built $dir/$base(.pdf, _KEY.pdf)"
done
