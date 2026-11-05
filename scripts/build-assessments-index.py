#!/usr/bin/env python3
"""Write assessments/index.html: the teacher's bookmark page.

Lists every unit quiz and test (PDF), then every handout sheet (HTML: unit
review, unit summary, lesson handouts, tables), each with its key when it has one.
Like the quizzes and keys themselves it is unlisted: copied into the site by
_quarto.yml `resources:` but linked from no page and not in the search index.
Run by ./build.sh after a full build; rerun by hand after adding a unit.
"""
import html, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
out = root / "assessments" / "index.html"


def title_of(tex):
    """A quiz's own title: \\lessontitle{...}."""
    text = tex.read_text()
    m = re.search(r"\\lessontitle\{([^}]*)\}", text)
    return m.group(1).strip() if m else tex.stem.replace("_", " ")


def meta_of(frag):
    """A handout fragment's metadata header (handouts/src/<name>.html)."""
    m = re.match(r"\A<!--(.*?)-->", frag.read_text(), re.S)
    meta = {}
    for line in (m.group(1) if m else "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def row(label, path):
    """One table row: label, student link, key link if a key exists
    (paths relative to assessments/)."""
    rel = path.relative_to(root)
    href = ("../" + str(rel)) if rel.parts[0] != "assessments" else str(pathlib.Path(*rel.parts[1:]))
    key = path.with_name(path.stem + "_KEY" + path.suffix)
    khref = href[: -len(path.suffix)] + "_KEY" + path.suffix
    keycell = f'<a class="key" href="{khref}">Key</a>' if key.exists() else ""
    return (f'    <tr><td>{html.escape(label)}</td>'
            f'<td><a href="{href}">Student</a></td><td>{keycell}</td></tr>')


sheets = {}  # unit -> [(fragment stem, meta)]
for frag in sorted((root / "handouts" / "src").glob("*.html")):
    meta = meta_of(frag)
    sheets.setdefault(int(meta.get("unit", 0)), []).append((frag.stem, meta))

parts = []
for u in sorted(k for k in sheets if k):
    rows = []
    for tex in sorted(root.glob(f"assessments/Unit_{u}/*.tex")):
        rows.append(row(title_of(tex), tex.with_suffix(".pdf")))
    order = {"Unit Review": 0, "Unit Summary": 1, "Mini Lesson": 2}
    for stem, meta in sorted(sheets[u], key=lambda sm: (order.get(sm[1].get("kind"), 3), sm[0])):
        label = (meta["lesson"] + " " if meta.get("lesson") else "") + meta.get("title", stem)
        rows.append(row(label, root / "handouts" / f"Unit_{u}" / f"{stem}.html"))
    parts.append(f"  <h2>Unit {u}</h2>\n  <table>\n" + "\n".join(rows) + "\n  </table>")

# Projects: finished files the teacher drops in projects/, served as they are.
# One link per file; a project has no key unless one sits beside it.
proj = [f for f in sorted((root / "projects").glob("*")) if f.is_file()]
if proj:
    prow = [f'    <tr><td>{html.escape(f.stem.replace("_", " "))}</td>'
            f'<td><a href="../projects/{html.escape(f.name)}">{f.suffix[1:].upper()}</a></td><td></td></tr>'
            for f in proj]
    parts.append("  <h2>Projects</h2>\n  <table>\n" + "\n".join(prow) + "\n  </table>")

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
