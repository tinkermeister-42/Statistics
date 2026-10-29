#!/usr/bin/env python3
"""Write assessments/index.html: the teacher's bookmark page.

Lists every unit quiz, unit review and lesson handout, each with its key.
Like the quizzes and keys themselves it is unlisted: copied into the site by
_quarto.yml `resources:` but linked from no page and not in the search index.
Run by ./build.sh after a full build; rerun by hand after adding a unit.
"""
import html, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
out = root / "assessments" / "index.html"


def title_of(tex):
    """The sheet's own title: \\lessontitle{...}, or the first \\Large\\bfseries line."""
    text = tex.read_text()
    m = re.search(r"\\lessontitle\{([^}]*)\}", text) or re.search(r"\\Large\\bfseries ([^\\{}]+)", text)
    return m.group(1).strip() if m else tex.stem.replace("_", " ")


def row(label, pdf):
    """One table row: label, student PDF link, key PDF link (paths relative to assessments/)."""
    rel = pdf.relative_to(root)
    href = ("../" + str(rel)) if rel.parts[0] != "assessments" else str(pathlib.Path(*rel.parts[1:]))
    key = href[:-4] + "_KEY.pdf"
    return (f'    <tr><td>{html.escape(label)}</td>'
            f'<td><a href="{href}">Student</a></td>'
            f'<td><a class="key" href="{key}">Key</a></td></tr>')


def unit_num(p):
    return int(re.search(r"Unit_(\d+)", str(p)).group(1))


units = sorted({unit_num(p) for p in root.glob("handouts/Unit_*/*.tex")})
parts = []
for u in units:
    rows = []
    for tex in sorted(root.glob(f"assessments/Unit_{u}/*.tex")):
        rows.append(row(title_of(tex), tex.with_suffix(".pdf")))
    review = root / f"handouts/Unit_{u}/Unit_{u}_Review.tex"
    if review.exists():
        rows.append(row(title_of(review), review.with_suffix(".pdf")))
    lessons = [t for t in sorted(root.glob(f"handouts/Unit_{u}/*.tex"), key=lambda t: t.stem)
               if re.match(r"\d+\.\d+_", t.stem)]
    for tex in lessons:
        # the lesson page's own heading ("1.1 - Frequency Tables, ...") names it best
        qmd = root / f"chapters/Unit_{u}/{tex.stem}.qmd"
        h = re.match(r"#\s*(\S+)\s*-\s*(.+?)\s*\{", qmd.read_text()) if qmd.exists() else None
        label = f"{h.group(1)} {h.group(2)}" if h else f"{tex.stem.split('_')[0]} {title_of(tex)}"
        rows.append(row(label, tex.with_suffix(".pdf")))
    others = [t for t in sorted(root.glob(f"handouts/Unit_{u}/*.tex"))
              if t not in lessons and t != review]
    for tex in others:
        rows.append(row(title_of(tex), tex.with_suffix(".pdf")))
    parts.append(f"  <h2>Unit {u}</h2>\n  <table>\n" + "\n".join(rows) + "\n  </table>")

page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Quizzes and Keys - DHS Statistics</title>
<style>
  body { font-family: Helvetica, Arial, sans-serif; color: #222; background: #fff;
         max-width: 46rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.4; }
  h1 { margin: 0 0 .2rem; font-size: 1.6rem; }
  .sub { color: #555; margin-bottom: 1rem; }
  h2 { font-size: 1.15rem; margin: 1.6rem 0 .3rem; border-bottom: 2px solid #2c3e50; padding-bottom: .2rem; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: .3rem .5rem; border-bottom: 1px solid #e5e5e5; }
  td:nth-child(2), td:nth-child(3) { width: 5rem; text-align: right; white-space: nowrap; }
  a { color: #18bc9c; text-decoration: none; }
  a:hover { text-decoration: underline; }
  a.key { color: #b03030; }
</style>
</head>
<body>
  <h1>Quizzes and Keys</h1>
  <div class="sub">DHS Statistics. Teacher bookmark: no page in the book links here.</div>
""" + "\n".join(parts) + """
</body>
</html>
"""
out.parent.mkdir(exist_ok=True)
out.write_text(page)
print(f"wrote {out.relative_to(root)}")
