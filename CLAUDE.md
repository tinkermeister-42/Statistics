# DHS Statistics: Project Context

Mini lessons for the Statistics class at Frederick Douglass High School. The
students work self-paced in Khan Academy's **Statistics essentials**; each
mini lesson opens a class block and matches one or two Khan lessons. The
course map (all 29 mini lessons and the Khan lessons each one covers) is the
table in `index.md`. It follows Khan's order on purpose, so a sheet always
matches what the students see on screen. Grouping is by cognitive load, not
by a fixed number of Khan lessons.

Built from the DHS Algebra 1 book (`tinkermeister-42/Algebra1`): same theme,
callouts, glossary and headings extensions. Less depth: a mini lesson is
notes, a worked example or two, one You Try, and the practice set.

## Build & Deploy
- **Handouts:** `./build.sh [1.3 ...]` builds `handouts/Unit_X/<name>.pdf` and
  `<name>_KEY.pdf` from one `.tex` (pdflatex, TikZ). Commit the PDFs
- **Web figures:** `scripts/make-figures.sh [1.3 ...]` turns
  `figures/Unit_X/<name>.tex` into `images/Unit_X/<name>.svg`. Shared macros
  are in `figures/preamble.tex`
- **Render:** `quarto render --to html` (run it twice on a fresh clone: the
  glossary post-render writes `glossary.json` after the copy step)
- **Deploy:** `./deploy.sh` renders, runs `scripts/check-site-assets.py`
  (fails on a missing or stale PDF or SVG), and force-pushes `_book` to
  `gh-pages`. `.github/workflows/sync-to-work.yml` then mirrors `gh-pages` to
  the work account (`WORK_OWNER`/`WORK_REPO`, branch `prod`) using the
  `WORK_TOKEN` secret
- A container needs quarto >= 1.7 (tarball from the quarto-cli releases into
  `/opt/quarto`), pdflatex, `pdftocairo` (poppler), and a clean tree

## Structure
```
chapters/Unit_1…7/     # Lessons: #.#_Topic.qmd, index.qmd
handouts/Unit_1…7/     # Printable mini lessons: .tex source, student + _KEY PDFs
figures/Unit_1…7/      # TikZ sources for web figures -> images/Unit_X/*.svg
scripts/               # JS helpers, glossary build, figure build, asset check
styles/                # CSS (copied from the Algebra 1 book)
_extensions/           # glossary, headings
glossary.qmd           # Source -> glossary.json on render
```

## Lesson Page Pattern
Title, a concrete hook, `.objectives`, `.vocab`, a `.guided-notes-link` to
the student PDF, `{{< learn >}}` with numbered `### #.#.# -` sections, then
`{{< practice >}}` restating the handout problems. Callouts are the Algebra 1
set (`.remember`, `.you-try`, `.you-try-m` + `.answer`, `.think`, `.gotcha`,
`.note`, `.real-world`).

- **Lesson, handout and figures are one change.** The page restates the
  handout's notes and problems, and the handout draws its own copy of each
  figure. Edit all three together
- **Keys are unlisted.** `<name>_KEY.pdf` is served beside the student PDF
  but nothing links to it. The URL is predictable on purpose so it can be
  shared with colleagues. Practice answers are not printed on the page
- **A key answers the paper in the space provided.** Answers go inline with
  `\ans{...}` in the handout `.tex`; drawn answers (dot plots, box plots,
  histograms) are drawn in red inside `\ifkey ... \fi`
- **Quartiles follow Khan:** with an odd count the median is left out of both
  halves
- **Money in prose is math:** write `$\$84{,}000$`, as the Algebra book does.
  A bare `$84,000` pairs with the next dollar sign in the paragraph and
  MathJax renders the text between them as math
- Worksheet directions say "Work with a partner", never "work by yourself"

## Branches

Keep the repository clean. Dead branches are clutter.

- Work happens on a feature branch. Granular commits there are fine and
  wanted while the feature is still being worked on, which is exactly when
  the branch still exists
- When a feature is finished it goes to `main` as **one squashed commit**
  naming the feature. `main` keeps a history of what was added, not of every
  step it took to get there
- The branch is deleted once it is merged
- **Nothing is merged or deleted without the teacher signing off on it.**
  Propose it, show what would land, and wait

Two things that bite:

- **Deploying is not merging.** `deploy.sh` force-pushes the built `_book` to
  `gh-pages` and touches nothing else, so a change can be live on the site
  while its source exists only on a feature branch. Check
  `git rev-list --count origin/main..HEAD` before assuming work is safe
- **This session's credentials cannot delete branches.** `git push origin
  --delete` returns HTTP 403. That is a permission limit, not a safety
  refusal, so branch removal is the teacher's to do

**Checking a branch is safe to delete.** Because the convention here is to
squash, the branch's own commits never become ancestors of `main`, so
`git merge-base --is-ancestor` and a zero count from `git rev-list
origin/main..origin/<branch>` both report a squash-merged branch as unmerged.
They are the right check only for a branch merged the ordinary way.

What settles it for a squashed branch is the content:

```
git diff origin/main origin/<branch>      # empty output means nothing would be lost
```

Do not judge by `git diff --name-only main branch` and count the files. That
reports differences in both directions, so a branch long since merged can look
like it carries hundreds of unmerged files when those files are `main`'s own
later work.

## Writing Style

**Who is reading this.** About 80% of the students are not native English
speakers. Many read well below grade level, and some have never been to school
before and are placed in a class because of their age. Reading is the barrier,
not the mathematics. Every sentence a student has to decode twice is a sentence
that costs them the math.

Write for that reader:

- **Short sentences.** One idea each. Split a sentence before adding a clause
- **Common words.** Prefer "use" to "utilize", "shows" to "demonstrates",
  "same" to "equivalent" outside the glossary term itself
- **No colloquialisms or figurative idioms**, where the literal words do not
  give the meaning: "earns its keep", "comes in handy", "takes forever",
  "falls apart", "gets in the way", "what your gut tells you". Plain phrasal
  verbs ("show up", "figure out") are fine
- **No dash asides.** AI writes "the total goes up - removing a fee is like
  being handed the money" constantly; this teacher almost never does. The fix is
  not a different dash character, it is a different sentence. Split it in two,
  use a comma, or put a short aside in parentheses. Labels in a list take a
  colon ("**Substitution**: replace one variable"). Section headings keep the
  spaced hyphen they already use
- **Lead with the concrete.** A number, a picture, or a story first; the general
  rule after. The job ad in 1.2 is the pattern to copy
- **Do not let prose carry the math.** If a step matters, it belongs in a
  worked example, a labelled figure, or a fill-in blank, not buried in a
  paragraph

**The mathematics does not get easier.** These students still sit the EOC, and
it is written at full difficulty in dense language. Simplify the sentence, never
the problem: keep the multi-step work, the negatives, the word problems, the
rigour. The goal is that reading stops hiding what a student actually knows.

Because EOC items are wordy, the book should also build that reading up rather
than avoid it: introduce a type of problem in plain language first, then show
the same problem worded the way the test words it.

## Curriculum Judgment

**Do not propose cutting a lesson.** The teacher has taught geometry, statistics,
Algebra 2 and Algebra 1, and did mathematics professionally for twenty years
before that. Scope decisions are his.

Report what the measurements say and let him decide.
