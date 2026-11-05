#!/usr/bin/env python3
"""Build the printable handouts: one HTML page per sheet, student copy and key.

Each sheet lives in handouts/src/<name>.html as a body fragment with a small
metadata header (the pattern of the Algebra 1 book's guided notes).  This
script wraps it in the shared page shell and writes

    handouts/Unit_<n>/<name>.html        the student copy
    handouts/Unit_<n>/<name>_KEY.html    the key (only if the sheet has answers)

    python3 scripts/build-handouts.py              # every sheet
    python3 scripts/build-handouts.py 5.3 Unit_5   # sheets whose name starts so

Fragment conventions
  {{a}}...{{/a}}      an answer: dropped on the student copy, red on the key.
                      An answer alone on its line takes the line with it.
  $...$  $$...$$      math, written as TeX like the lesson pages.  Converted to
                      MathML by pandoc here, so the page needs no JavaScript.
                      Write \\$ for a dollar sign in prose.  Never put {{a}}
                      inside math: put the math inside the answer instead.
  {{fig Unit_5/5.3_design}}        a figure from images/, printed at the size
                      LaTeX drew it; the key uses <name>_KEY.svg when one
                      exists.  Options after the name: w=3in (a different
                      width), left (not centered).
  {{opt A}} {{optans A}}           a choice; optans is circled on the key
  {{tally 7}}         seven tally strokes
  {{partner}}         the "Work with a partner" line
  {{practice-head}}   page break + the practice header with a name line and
                      the "Work with a partner" line under it
  {{break}}           page break
"""
import html, os, re, subprocess, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "handouts", "src")
OUT = os.path.join(ROOT, "handouts")

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{heading}{title_suffix}</title>
<link rel="stylesheet" href="../assets/handouts.css">
</head>
<body>
<section class="sheet">

  <div class="masthead">
    <a class="backlink" href="../../chapters/Unit_{unit}/{back}.html">&larr; back to the {backword}</a>
    <h1>{heading_html}</h1>
    <div class="sub">{kind} - Unit {unit}: {unit_title} - DHS Statistics</div>
    {idline}
  </div>

{body}
</section>
</body>
</html>
"""

IDLINE = ('<div class="idline"><span>Name</span>'
          '<span class="small">Date</span><span class="small">Period</span></div>')
KEYLINE = '<div class="keybadge">Teacher Key: answers in red</div>'
PARTNER = '<p class="partner">Work with a partner. Compare answers when you finish each problem.</p>'

HEADER_RE = re.compile(r"\A<!--(.*?)-->\s*", re.S)
ANS_RE = re.compile(r"\{\{a\}\}(.*?)\{\{/a\}\}", re.S)
BLOCK_RE = re.compile(r"<(table|div|p|ul|ol|h[1-6])\b", re.I)
# $$display$$ first, then $inline$; \$ is a literal dollar sign
MATH_RE = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$|(?<!\\)\$(.+?)(?<!\\)\$", re.S)
FIG_RE = re.compile(r"\{\{fig ([^\s}]+)((?: [^}]*)?)\}\}")
OPT_RE = re.compile(r"\{\{(opt|optans) ([^}]+)\}\}")
TALLY_RE = re.compile(r"\{\{tally (\d+)\}\}")
BREAK_RE = re.compile(r"\{\{break\}\}\s*<([a-zA-Z][\w-]*)([^>]*)>")
SEP = "MATHSEPARATOR"


def add_class(attrs, cls):
    if re.search(r'\bclass="', attrs):
        return re.sub(r'\bclass="([^"]*)"', lambda m: 'class="%s %s"' % (m.group(1), cls), attrs, count=1)
    return ' class="%s"%s' % (cls, attrs)


def parse(path):
    raw = open(path).read()
    m = HEADER_RE.match(raw)
    if not m:
        raise SystemExit(f"{path}: missing metadata header comment")
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    for key in ("title", "unit", "unit_title", "kind", "back"):
        if key not in meta:
            raise SystemExit(f"{path}: metadata is missing '{key}'")
    return meta, raw[m.end():]


def to_mathml(spans, where):
    """Convert TeX math spans to MathML with one pandoc call."""
    if not spans:
        return []
    doc = ("\n\n" + SEP + "\n\n").join(
        ("\\[" + tex + "\\]") if disp else ("\\(" + tex + "\\)") for disp, tex in spans)
    out = subprocess.run(["pandoc", "-f", "latex", "-t", "html", "--mathml"],
                         input=doc, capture_output=True, text=True, check=True).stdout
    parts = [p.strip() for p in out.split("<p>" + SEP + "</p>")]
    if len(parts) != len(spans):
        raise SystemExit(f"{where}: math conversion lost track ({len(parts)} vs {len(spans)})")
    result = []
    for (disp, tex), part in zip(spans, parts):
        m = re.search(r"<math.*</math>", part, re.S)
        if not m:
            raise SystemExit(f"{where}: pandoc could not read the math ${tex}$")
        # capital Greek is upright in mathematics: Sigma, not an italic one
        mml = re.sub(r"<mi>([\u0391-\u03a9])</mi>", r'<mi mathvariant="normal">\1</mi>', m.group(0))
        # pandoc marks plain ( ) as stretchy, so a bar over x inside them makes
        # the parentheses grow and pushes an exponent up.  Only \left \right stretch.
        if "\\left" not in tex:
            mml = re.sub(r'<mo stretchy="true" form="(prefix|postfix)">([()\[\]|])</mo>',
                         r'<mo stretchy="false" form="\1">\2</mo>', mml)
        # 4{,}500: pandoc splits it into 4 , 500 with list spacing; one number
        if "{,}" in tex:
            prev = None
            while prev != mml:
                prev = mml
                mml = re.sub(r"<mn>(\d{1,3}(?:,\d{3})*)</mn><mo>,</mo><mn>(\d{3}(?:\.\d+)?)</mn>",
                             r"<mn>\1,\2</mn>", mml)
        # a minus right after = or another operator is a sign, not subtraction:
        # say so, or the browser spaces = -2.5 as "= - 2.5"
        mml = re.sub(r"(<mo[^>]*>([^<]*)</mo>|<mrow>)<mo>([−+])</mo>",
                     lambda m: m.group(1) + ("<mo>%s</mo>" % m.group(3)
                                             if m.group(2) in (")", "]", "|") else
                                             '<mo form="prefix">%s</mo>' % m.group(3)), mml)
        # a hat over one letter (y-hat) keeps its size instead of stretching wide
        mml = mml.replace('<mo accent="true">̂</mo>', '<mo accent="true" stretchy="false">̂</mo>')
        # \displaystyle: full-size fractions and roots, as in LaTeX
        if "\\displaystyle" in tex:
            mml = mml.replace("<math ", '<math displaystyle="true" ', 1)
        result.append(mml)
    return result


def convert_math(body, where):
    spans, keys = [], []
    for m in MATH_RE.finditer(body):
        tex = m.group(1) if m.group(1) is not None else m.group(2)
        if "{{" in tex:
            raise SystemExit(f"{where}: shorthand inside math ${tex}$: put the math inside the answer")
        spans.append((m.group(1) is not None, tex))
    mathml = iter(to_mathml(spans, where))
    body = MATH_RE.sub(lambda m: next(mathml), body)
    return body.replace("\\$", "$")


def drop_answers(body):
    sent = "\x00"
    lines = []
    for line in ANS_RE.sub(sent, body).split("\n"):
        if sent in line and not line.replace(sent, "").strip():
            continue
        lines.append(line.replace(sent, ""))
    return "\n".join(lines)


def show_answers(body):
    def repl(m):
        inner = m.group(1)
        tag = "div" if BLOCK_RE.search(inner) else "span"
        return '<%s class="ans-key">%s</%s>' % (tag, inner, tag)
    return ANS_RE.sub(repl, body)


def figure(m, key, where):
    name, opts = m.group(1), m.group(2).split()
    unit, stem = name.split("/")
    src = os.path.join(ROOT, "images", unit, stem + ".svg")
    if not os.path.exists(src):
        raise SystemExit(f"{where}: no figure images/{name}.svg (run scripts/make-figures.sh)")
    if key and os.path.exists(os.path.join(ROOT, "images", unit, stem + "_KEY.svg")):
        stem += "_KEY"
    cls = "fig" + (" left" if "left" in opts else "")
    widths = [o[2:] for o in opts if o.startswith("w=")]
    if not widths:
        # pdftocairo writes the width in points with no unit, which a browser
        # reads as pixels (3/4 of a point).  Print at the size LaTeX drew it.
        m = re.search(r'<svg[^>]*\swidth="([\d.]+)(pt)?"', open(src).read(4000))
        widths = ["%.2fin" % (float(m.group(1)) / 72)] if m else []
    style = "".join(f' style="width:{w}"' for w in widths)
    return f'<img class="{cls}" src="../../images/{unit}/{stem}.svg"{style} alt="">'


def build(path, key=False):
    meta, body = parse(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    body = convert_math(body, stem)
    body = show_answers(body) if key else drop_answers(body)
    body = FIG_RE.sub(lambda m: figure(m, key, stem), body)
    body = OPT_RE.sub(lambda m: '<span class="opt%s">%s</span>'
                      % (" circ" if key and m.group(1) == "optans" else "", m.group(2)), body)
    body = TALLY_RE.sub(lambda m: '<span class="tally">%s</span>' % ("|" * int(m.group(1))), body)
    heading = (meta["lesson"] + "  " if meta.get("lesson") else "") + meta["title"]
    heading_html = (meta["lesson"] + " &nbsp;" if meta.get("lesson") else "") + html.escape(meta["title"])
    body = body.replace("{{partner}}", PARTNER)
    body = body.replace("{{practice-head}}",
                        '{{break}}<div class="parthead"><b>%s - Practice</b>%s</div>\n  %s'
                        % (heading_html, "" if key else '<span class="nm">Name</span>', PARTNER))
    # A page break goes on the element after it, not on an empty div: an empty
    # div left at the foot of a full page gets a page of its own, then breaks
    # again, and the printout gains a blank page.
    body = BREAK_RE.sub(lambda m: "<%s%s>" % (m.group(1), add_class(m.group(2), "brk")), body)
    body = body.replace("{{break}}", '<div class="pagebreak"></div>')
    idline = KEYLINE if key else ("" if meta.get("idline") == "no" else IDLINE)
    # header keys the shell fills itself must not be passed twice
    fields = {k: v for k, v in meta.items() if k not in ("idline", "body", "heading", "title_suffix")}
    fields["backword"] = meta.get("backword", "lesson")
    page = SHELL.format(body=body.rstrip() + "\n", heading=html.escape(heading),
                        heading_html=heading_html, idline=idline,
                        title_suffix=" (Teacher Key)" if key else "", **fields)
    unit_dir = os.path.join(OUT, "Unit_%s" % meta["unit"])
    os.makedirs(unit_dir, exist_ok=True)
    dest = os.path.join(unit_dir, stem + ("_KEY" if key else "") + ".html")
    with open(dest, "w") as f:
        f.write(page)
    return os.path.relpath(dest, ROOT)


if __name__ == "__main__":
    wanted = sys.argv[1:]
    made = []
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".html"):
            continue
        stem = name[:-5]
        if wanted and not any(stem.startswith(w) for w in wanted):
            continue
        path = os.path.join(SRC, name)
        made.append(build(path))
        if ANS_RE.search(open(path).read()):
            made.append(build(path, key=True))
    for m in made:
        print("built", m)
