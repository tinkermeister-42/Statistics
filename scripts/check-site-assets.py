#!/usr/bin/env python3
"""Fail the deploy if a handout's PDFs are missing from the site or stale.

Each handouts/Unit_X/<name>.tex must have <name>.pdf and <name>_KEY.pdf in
_book/, and both must be newer than the .tex, the shared preambles, and any
figure it pulls in with \\fig{}.  Run ./build.sh to fix.

"Newer" uses the last commit time for a file that is committed and unchanged,
and the file's mtime otherwise.  A checkout or fresh clone rewrites mtimes in
no useful order, so mtimes alone report clean files as stale.
"""
import pathlib, re, subprocess, sys

root = pathlib.Path(__file__).resolve().parent.parent
bad = []
FIG = re.compile(r"\\fig\{([^}]+)\}")


def git(*args):
    try:
        return subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return ""


dirty = set()
for line in git("status", "--porcelain", "-uall").splitlines():
    path = line[3:]
    dirty.add(path.split(" -> ")[-1])

committed = {}  # path -> time of the newest commit that touched it
when = None
for line in git("log", "--format=%x00%ct", "--name-only").splitlines():
    if line.startswith("\x00"):
        when = int(line[1:])
    elif line and line not in committed:
        committed[line] = when


def stamp(p):
    rel = p.relative_to(root).as_posix()
    if rel in committed and rel not in dirty:
        return committed[rel]
    return p.stat().st_mtime


def newest_source(tex):
    """The .tex itself, the shared preambles, and every figure it \\fig's."""
    text = tex.read_text()
    paths = [tex]
    if "\\input{../preamble}" in text:
        paths += [root / "handouts" / "preamble.tex", root / "figures" / "preamble.tex"]
    paths += [root / "figures" / (m + ".tex") for m in FIG.findall(text)]
    return max(stamp(p) for p in paths if p.exists())


for tex in sorted(root.glob("handouts/Unit_*/*.tex")):
    for suffix in ("", "_KEY"):
        pdf = tex.with_name(tex.stem + suffix + ".pdf")
        built = root / "_book" / pdf.relative_to(root)
        if not pdf.exists():
            bad.append(f"missing {pdf.relative_to(root)} (run ./build.sh)")
        elif stamp(pdf) < newest_source(tex):
            bad.append(f"stale {pdf.relative_to(root)} (run ./build.sh)")
        elif not built.exists():
            bad.append(f"not in site: {built.relative_to(root)}")
for svg_src in sorted(root.glob("figures/Unit_*/*.tex")):
    svg = root / "images" / svg_src.parent.name / (svg_src.stem + ".svg")
    if not svg.exists() or stamp(svg) < stamp(svg_src):
        bad.append(f"stale or missing {svg.relative_to(root)} (run scripts/make-figures.sh)")
if bad:
    print("check-site-assets:\n  " + "\n  ".join(bad))
    sys.exit(1)
print("check-site-assets: ok")
