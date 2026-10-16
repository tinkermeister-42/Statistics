#!/usr/bin/env python3
"""Fail the deploy if a handout's PDFs are missing from the site or stale.

Each handouts/Unit_X/<name>.tex must have <name>.pdf and <name>_KEY.pdf in
_book/, and both must be newer than the .tex, the shared preambles, and any
figure it pulls in with \\fig{}.  Run ./build.sh to fix.
"""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
bad = []
FIG = re.compile(r"\\fig\{([^}]+)\}")


def newest_source(tex):
    """The .tex itself, the shared preambles, and every figure it \\fig's."""
    text = tex.read_text()
    paths = [tex]
    if "\\input{../preamble}" in text:
        paths += [root / "handouts" / "preamble.tex", root / "figures" / "preamble.tex"]
    paths += [root / "figures" / (m + ".tex") for m in FIG.findall(text)]
    return max(p.stat().st_mtime for p in paths if p.exists())


for tex in sorted(root.glob("handouts/Unit_*/*.tex")):
    for suffix in ("", "_KEY"):
        pdf = tex.with_name(tex.stem + suffix + ".pdf")
        built = root / "_book" / pdf.relative_to(root)
        if not pdf.exists():
            bad.append(f"missing {pdf.relative_to(root)} (run ./build.sh)")
        elif pdf.stat().st_mtime < newest_source(tex):
            bad.append(f"stale {pdf.relative_to(root)} (run ./build.sh)")
        elif not built.exists():
            bad.append(f"not in site: {built.relative_to(root)}")
for svg_src in sorted(root.glob("figures/Unit_*/*.tex")):
    svg = root / "images" / svg_src.parent.name / (svg_src.stem + ".svg")
    if not svg.exists() or svg.stat().st_mtime < svg_src.stat().st_mtime:
        bad.append(f"stale or missing {svg.relative_to(root)} (run scripts/make-figures.sh)")
if bad:
    print("check-site-assets:\n  " + "\n  ".join(bad))
    sys.exit(1)
print("check-site-assets: ok")
