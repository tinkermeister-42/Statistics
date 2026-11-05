#!/usr/bin/env python3
"""Fail the deploy if a printable is missing from the site or stale.

Handouts: each handouts/src/<name>.html must be built to
handouts/Unit_X/<name>.html (and <name>_KEY.html when it has answers), newer
than the fragment and the builder, and copied into _book/ with the shared
assets.  Run ./build.sh (it runs scripts/build-handouts.py) to fix.

Quizzes: each assessments/Unit_X/<name>.tex must have <name>.pdf and
<name>_KEY.pdf in _book/, newer than the .tex, the shared preambles, and any
figure it pulls in with \\fig{}.  Run ./build.sh to fix.

Figures: each figures/Unit_X/<name>.tex must have images/Unit_X/<name>.svg
(and <name>_KEY.svg when it uses \\ifkey), newer than its source.

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
    if "\\input{../preamble}" in text or "\\input{../../handouts/preamble}" in text:
        paths += [root / "handouts" / "preamble.tex", root / "figures" / "preamble.tex"]
    paths += [root / "figures" / (m + ".tex") for m in FIG.findall(text)]
    return max(stamp(p) for p in paths if p.exists())


for tex in sorted(root.glob("handouts/Unit_*/*.tex")) + sorted(root.glob("assessments/Unit_*/*.tex")):
    for suffix in ("", "_KEY"):
        pdf = tex.with_name(tex.stem + suffix + ".pdf")
        built = root / "_book" / pdf.relative_to(root)
        if not pdf.exists():
            bad.append(f"missing {pdf.relative_to(root)} (run ./build.sh)")
        elif stamp(pdf) < newest_source(tex):
            bad.append(f"stale {pdf.relative_to(root)} (run ./build.sh)")
        elif not built.exists():
            bad.append(f"not in site: {built.relative_to(root)}")
builder = root / "scripts" / "build-handouts.py"
for frag in sorted(root.glob("handouts/src/*.html")):
    text = frag.read_text()
    unit = re.search(r"^unit:\s*(\d+)", text, re.M)
    if not unit:
        bad.append(f"no unit in {frag.relative_to(root)}")
        continue
    for suffix in ("", "_KEY") if "{{a}}" in text else ("",):
        out = root / "handouts" / f"Unit_{unit.group(1)}" / f"{frag.stem}{suffix}.html"
        built = root / "_book" / out.relative_to(root)
        if not out.exists():
            bad.append(f"missing {out.relative_to(root)} (run ./build.sh)")
        elif stamp(out) < max(stamp(frag), stamp(builder)):
            bad.append(f"stale {out.relative_to(root)} (run ./build.sh)")
        elif not built.exists():
            bad.append(f"not in site: {built.relative_to(root)}")
for asset in sorted((root / "handouts" / "assets").glob("*")):
    if not (root / "_book" / asset.relative_to(root)).exists():
        bad.append(f"not in site: _book/{asset.relative_to(root)}")
for svg_src in sorted(root.glob("figures/Unit_*/*.tex")):
    names = [svg_src.stem] + ([svg_src.stem + "_KEY"] if "\\ifkey" in svg_src.read_text() else [])
    for name in names:
        svg = root / "images" / svg_src.parent.name / (name + ".svg")
        if not svg.exists() or stamp(svg) < stamp(svg_src):
            bad.append(f"stale or missing {svg.relative_to(root)} (run scripts/make-figures.sh)")
if bad:
    print("check-site-assets:\n  " + "\n  ".join(bad))
    sys.exit(1)
print("check-site-assets: ok")
