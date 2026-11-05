#!/bin/bash
# Build the printables.
#   Handouts: handouts/src/<name>.html -> handouts/Unit_X/<name>.html and
#     _KEY.html (scripts/build-handouts.py).
#   Quizzes and tests: assessments/Unit_X/<name>.tex -> <name>.pdf and _KEY.pdf.
#   ./build.sh                 everything
#   ./build.sh 1.3             only sheets whose name starts with 1.3
#   ./build.sh Unit1_Quiz      just that quiz
set -euo pipefail
cd "$(dirname "$0")"
shopt -s nullglob
for tex in assessments/Unit_*/*.tex; do
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
# the HTML handouts (lessons, reviews, summaries, tables) from handouts/src/
python3 scripts/build-handouts.py "$@"
# the teacher's bookmark page of every quiz, review and key
python3 scripts/build-assessments-index.py
