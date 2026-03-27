---
name: add-paper
description: Use this skill to add a paper to the ligon.github.io academic website. This skill should be used when the user wants to add a published paper or working paper, including generating a cover image and writing the org-mode entry.
license: Apache-2.0
---

# Add Paper to ligon.github.io

## Trigger

- User asks to add a paper to the website.
- User mentions adding older papers, publications, or working papers.
- User references a paper by title, author-year key, or eScholarship link.

## Prerequisites

- Repository: `/home/coder/mirrors/ligon.github.io`
- Python with Pillow, matplotlib, scipy (use `/tmp/imgenv` venv or create one)
- EB Garamond font at `/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Bold.ttf`
- Hugo binary at `/tmp/hugo` (download if missing)
- ox-hugo available via Emacs batch

## Overview

All website content is authored in `content-org/website.org` and exported
by ox-hugo to Hugo markdown.  The `content/` directory is generated and
not checked in.  Adding a paper means:

1. Gather metadata
2. Generate a cover image
3. Add an org entry to `website.org`
4. Export and build to verify

## Step 1: Gather Metadata

Collect these fields (CV PDF at `static/cv.pdf` is the primary source):

| Field | Example | Required |
|-------|---------|----------|
| Title | Motives for Sharing in Social Networks | Yes |
| Authors | Ethan Ligon and Laura Schechter | Yes |
| Year | 2012 | Yes |
| Journal | Journal of Development Economics | Yes (published) |
| Volume / Issue / Pages | 99(1):13--26 | Yes (published) |
| DOI | 10.1016/j.jdeveco.2011.12.002 | Yes (published) |
| eScholarship URL | https://escholarship.org/uc/item/XXXX | Preferred |
| Abstract | Full text | Yes |
| BibTeX key | ligon-schechter12 | Yes |

### Key conventions

- **BibTeX key**: `author-YY` for sole author, `author1-author2YY` for two,
  `author1-etal-YY` for three+.  Use last two digits of year.
- **Tags**: 3--6 org tags, underscore-separated multi-word (e.g., `Risk_sharing`).
- **Abstract source**: Try eScholarship, then DOI page, then web search.
  eScholarship often blocks programmatic access; web search is more reliable.
- **BibTeX entry type**: `@Article` for published, `@InCollection` for book
  chapters, `@Unpublished` for working papers.

## Step 2: Generate Cover Image

All covers are 1536 x 1024 PNG in the site palette:

```python
navy  = (26, 39, 68)     # '#1a2744'
cream = (232, 220, 200)   # '#e8dcc8'
amber = (181, 101, 29)    # '#b5651d'
mid_blue = '#3a5a8c'
peach    = '#d4956a'
```

Font: EB Garamond 12 Bold, all-caps, navy text with cream halo.

### Cover image paths (choose one)

**A. Text-only** (fastest, good for most papers):

```sh
python scripts/gen_cover.py \
  --title "Paper Title Here" \
  --output static/images/key.png
```

**B. With data figure** (paper has a signature visualisation):

1. Reproduce the figure with matplotlib using the site's palette (no axis
   labels, ticks, or chrome).
2. Save as `/tmp/vis.png`.
3. Composite:

```sh
python scripts/gen_cover.py \
  --title "Paper Title Here" \
  --background /tmp/vis.png \
  --output static/images/key.png
```

**C. With symbolic illustration** (user provides or agent generates an image):

Same as (B) but the background is an illustration rather than a data figure.

**D. Custom title lines** (override automatic line-breaking):

```sh
python scripts/gen_cover.py \
  --title "ignored" \
  --lines "MOTIVES FOR:56" "SHARING:82" "IN SOCIAL NETWORKS:50" \
  --output static/images/key.png
```

### Title text placement

- Title sits in the **upper portion** of the canvas (top ~6% down).
- Background figures should occupy the **lower portion**.
- The alpha mask fades the background under the title for legibility.
- Ask the user to review; layout preferences are subjective.

## Step 3: Add Org Entry

Insert under `* Papers` in `website.org`.  Entries are ordered
**newest first**.  Generate a fresh UUID for `:ID:`.

### Template

```org
** Paper Title Here :Tag_One:Tag_Two:
:PROPERTIES:
:export_hugo_bundle: papers/bibtex-key
:EXPORT_FILE_NAME: index
:ID:       <fresh-uuid>
:EXPORT_DATE: <YYYY-MM-DD Day>
:EXPORT_HUGO_CUSTOM_FRONT_MATTER+: :cover '((image . "images/COVER.png") (alt . "ALT TEXT") (relative . t))
:END:

#+begin_description
One-sentence description for HTML meta / list pages.
#+end_description

[[/images/COVER.png]]

#+begin_summary
Two-sentence plain-language summary for the card on the home page.
#+end_summary

*** Download
- [[https://doi.org/DOI][Paper]]
*** Abstract
Full abstract here.
*** BibTeX

#+begin_src bibtex
@Article{	  bibtex-key,
  author	= {First Last and First Last},
  title		= {Full Title},
  journal	= {Journal Name},
  year		= YYYY,
  volume	= VV,
  number	= N,
  pages		= {PP--PP},
  doi		= {DOI}
}
#+end_src
```

### Checklist (common pitfalls)

- [ ] `:ID:` is a fresh UUID (run `python3 -c "import uuid; print(uuid.uuid4())"`)
- [ ] No duplicate tags in the headline
- [ ] Bundle path (`papers/bibtex-key`) matches BibTeX key
- [ ] Cover image exists in `static/images/` and is 1536 x 1024 PNG
- [ ] Inline image uses `/images/COVER.png` (not `./static/images/...`)
- [ ] Download link uses DOI URL (`https://doi.org/...`) when available
- [ ] BibTeX entry type matches publication status
- [ ] Entry is inserted in correct chronological position (newest first)
- [ ] No references to dead URLs (e.g., `are.berkeley.edu/~ligon/`)

## Step 4: Export and Build

```sh
# Export org to markdown
emacs --batch \
  --eval '(dolist (d (quote ("ox-hugo" "tomelr" "s"))) (add-to-list (quote load-path) (concat "/home/coder/.emacs.d/.local/straight/repos/" d "/")))' \
  --eval '(require (quote org))' \
  --eval '(require (quote ox-hugo))' \
  --find-file content-org/website.org \
  --eval '(org-hugo-export-wim-to-md :all-subtrees)'

# Build (downloads hugo once)
[ -x /tmp/hugo ] || curl -sL https://github.com/gohugoio/hugo/releases/download/v0.148.2/hugo_extended_0.148.2_linux-arm64.tar.gz | tar xz -C /tmp hugo
/tmp/hugo --minify

# Or use dev server for live preview
/tmp/hugo server --bind 0.0.0.0 --baseURL http://localhost:1313
```

Verify:
- All subtrees export without errors
- Hugo builds with no errors
- New paper page exists at `public/papers/bibtex-key/`
- Cover image renders in HTML output

## Batch Workflow

When adding many papers at once:

1. Parse the CV's "Published Papers" section for all missing entries.
2. For each: gather metadata via web search, generate text-only cover,
   write org entry.
3. Flag papers that have signature figures for manual cover treatment.
4. Export and build once at the end.

## Pitfalls

- **eScholarship PDFs** often return empty via `curl`; use web search for
  abstracts instead.
- **Python environment**: system Python lacks pip; use a venv
  (`python3 -m venv /tmp/imgenv && /tmp/imgenv/bin/pip install Pillow matplotlib scipy`).
- **Cover image iteration**: the user will likely want to adjust title
  placement or figure prominence; expect 1--2 rounds of tweaks.
- **DOI links preferred** over journal-specific URLs (which go stale when
  publishers reorganise).
- **Org export date**: use the publication date, not today's date.
  Format: `<YYYY-MM-DD Day>` where Day is the day-of-week abbreviation.

## Related

- Site guide: `CLAUDE.md` in the repo root (full image spec, colour
  constants, hero image recipe).
- Content source: `content-org/website.org` (the single source of truth).
- CV: `static/cv.pdf` (publication list with URLs).
