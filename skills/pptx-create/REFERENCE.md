# pptx-create — Reference

Full API + conventions. SKILL.md is the quickstart.

## Repo layout

```
skills/pptx-create/
├── SKILL.md                       # quickstart + index
├── REFERENCE.md                   # this file
├── CHANGELOG.md
├── agent-prompt.md                # model-agnostic LLM prompt
├── requirements.txt               # core (python-pptx, pillow)
├── requirements-extras.txt        # pygments, cairosvg
├── bin/pptx                       # unified CLI entry point
├── themes/
│   ├── themes.py                  # legacy dict (still loadable)
│   ├── *.toml                     # external theme definitions (extends supported)
│   └── screenshots/*.png          # rendered theme samples
├── helpers/
│   ├── build_deck.py              # Deck class
│   ├── markdown_to_pptx.py        # markdown -> pptx
│   ├── inspect_deck.py            # structure verifier
│   ├── pptx_cli.py                # subcommand dispatcher
│   ├── lint_deck.py               # WCAG + overflow + alt-text checks
│   ├── diff_deck.py               # structural diff
│   ├── export_deck.py             # pdf + thumbnails
│   └── icons/                     # bundled icon PNGs
├── templates/                     # markdown deck starters
└── examples/                      # runnable Python decks
```

## Workflow A — markdown to pptx

```bash
pptx render input.md --theme stripe -o deck.pptx
pptx render input.md --watch                 # rebuild on save
pptx render input.md --watch --open          # also relaunch viewer
```

Markdown syntax:

- `# Heading [kind]` opens a slide. Default kind: `bullets`.
- Available kinds: `title`, `section`, `bullets`, `two-col`, `table`, `chart`, `quote`, `stat`, `cta`, `timeline`, `comparison`, `metric_grid`, `code`, `agenda`, `pricing`, `before_after`, `image`, `video`.
- `## Subheading` for two-col split or column titles.
- `- item` for bullets.
- `> speaker note text` → speaker notes (block).
- `[notes: text]` legacy inline form (still accepted).
- `| a | b |` table row (separator `| --- | --- |` ignored).
- ` ```python ` code fence → `code` slide (pygments highlight if installed).
- `![alt](path "caption")` → `image` slide. Alt text required.
- `:::stat 73%` ... `:::` fenced block alternative to `[stat:73%]`.
- YAML frontmatter for deck-wide config:

  ```yaml
  ---
  theme: stripe
  brand: "Acme · Q3 2026"
  author: chris@acme.com
  date: 2026-04-27
  ---
  ```

Errors are line-numbered with suggestions.

## Workflow B — Deck class

```python
from helpers.build_deck import Deck
from themes.themes import get_theme

d = Deck(theme=get_theme("stripe"), brand="Acme · Q3 2026")
```

### Slide methods

| Method | Signature | Notes |
|---|---|---|
| `title` | `(title, subtitle="", notes="")` | First slide. |
| `section` | `(label, number=None, notes="")` | Divider. |
| `bullets` | `(title, bullets, icons=None, notes="")` | Auto-shrinks/splits if overflow. |
| `two_col` | `(title, lt, li, rt, ri, notes="")` | Side-by-side columns. |
| `big_stat` | `(stat, caption, notes="")` | Pitch hero. |
| `quote` | `(quote, attribution="", notes="")` | |
| `chart` | `(title, categories, series, kind="column", notes="")` | Native editable chart. `kind`: `column`, `bar`, `line`, `pie`. |
| `table` | `(title, headers, rows, notes="")` | |
| `image` | `(title, path, alt, caption="", fit="contain", notes="")` | `alt` required. `fit`: `cover`, `contain`. |
| `cta` | `(headline, sub="", contact="", notes="")` | Last slide. |
| `timeline` | `(title, events, notes="")` | `events`: list of `(date, label)`. |
| `comparison` | `(title, headers, rows, notes="")` | Feature matrix with checks. |
| `metric_grid` | `(title, metrics, notes="")` | 4-up KPI tiles. `metrics`: `[(value, label, delta), ...]`. |
| `code` | `(title, code, lang="python", notes="")` | Mono font + pygments. |
| `agenda` | `(title, items, current=None, notes="")` | TOC w/ optional highlight. |
| `pricing` | `(title, plans, notes="")` | Tiered cards. |
| `before_after` | `(title, before, after, notes="")` | Split layout. |
| `video_placeholder` | `(title, alt, poster_path=None, notes="")` | Frame + caption (no embed). |

### Accessibility

`image()` requires `alt`. Picture shapes get `descr` set so screen readers narrate. Slide title uniqueness enforced (warns on duplicates).

## Themes

External TOML definition under `themes/<name>.toml`. Schema:

```toml
extends = "stripe"            # optional inheritance

[colors]
bg = "#FFFFFF"
ink = "#0A0A23"
accent = "#635BFF"
muted = "#9A9AA8"
rule = "#E6E6F0"

[type]
font = "Calibri"
title_size = 36
body_size = 18
caption_size = 11

[brand]
logo_path = "/abs/path/logo.png"
logo_position = "tr"          # tl|tr|bl|br
footer_text = "Acme Confidential"

[modes]
default = "light"             # light | dark
```

`get_theme("stripe")` returns the resolved dict (TOML wins; legacy `themes.py` is fallback).

`brand.toml` in CWD overrides the brand block deck-wide (logo, accent, footer).

## Themes (current set)

Corporate: `corporate-default`, `stripe`, `linear`, `mckinsey`, `apple`, `monochrome`, `finance`, `healthcare`.
Pitch: `pitch-noir`, `pitch-editorial`, `pitch-electric`, `pitch-violet`, `pitch-clay`.

Each ships light + dark variant. `--mode dark` flips.

## CLI reference

```
pptx new <template> [--theme]    scaffold starter md from templates/
pptx render <md>                  markdown -> pptx (--watch, --open, --theme, -o)
pptx inspect <pptx>               structure dump (--notes, --json)
pptx lint <pptx>                  WCAG AA contrast + overflow + alt-text + caps
pptx diff <a.pptx> <b.pptx>       structural+textual diff
pptx export <pptx> [--pdf]        libreoffice pdf + per-slide thumbnails
pptx themes                       list themes with descriptions
```

Exit nonzero on lint errors so CI can gate.

## Style rules — corporate

- Calibri default (ships with PowerPoint). Inter / Aptos only if user confirms.
- Title 32–44pt, body 16–20pt, caption 11–12pt.
- One accent color. No gradients, drop shadows, clip art.
- ≤5 bullets per slide, ≤12 words each.
- Tables and charts beat prose for numbers.
- Slide footer: brand left, page number right.

## Style rules — pitch

- Display sans (Calibri default; Inter/Geist if installed). Headings 64–96pt.
- One idea per slide. Headline does the work.
- Asymmetric layout. Off-grid title. Generous whitespace.
- Big stats carry the deck.
- No bullet lists. No corporate iconography. No clip art.

## Healthcare conventions

Apply on top of corporate rules:

- **Theme**: `healthcare` (clinical/admin), `mckinsey` (board/exec), `linear` (IT/CIO).
- **PHI**: never include real patient identifiers (name, MRN, DOB, dates of service, full ZIP). Use synthetic / de-identified data. Flag if user pastes real-looking data.
- **Citations**: clinical claims need study + year, or guideline body. Note "data on file" if internal.
- **Reporting standards**: clinical research decks mirror CONSORT / STROBE / PRISMA. See `examples/clinical_research_deck.py`.
- **Number formatting**: CIs `(x.x–y.y)`, p-values `p=0.024`. Effect sizes with units. Keep decimals.
- **Acronyms**: spell out first use (HCAHPS, CAUTI, CLABSI, KDIGO, ADD-RS).
- **Quality vs safety vs experience**: keep separate on hospital admin decks.
- **Compliance vocab**: HIPAA, OCR, HITRUST, HITECH (privacy); KDIGO/SCCM/ACEP/USPSTF (clinical). Exact terminology — audience notices.
- **Forecasts vs actuals**: label projections `(proj)` or `forecast`. Don't imply certainty.

## Common pitfalls

- Custom fonts not installed → stay on Calibri unless user confirms.
- Image not found → `Deck.image()` validates path before `add_picture`.
- Mid-script crash → chart values must be numeric, table cells stringified.
- No visual verification possible without opening file. Trust `inspect_deck.py` + `lint_deck.py` for structure/quality. User opens in PowerPoint to confirm look.
- Color contrast: dark bg + dark accent fails. Themes pre-tuned; custom overrides need spot-check (lint catches).
- Overflowing bullets: auto-shrink/split kicks in, but check `inspect_deck` slide count if precise count matters.

## Verification — full

Pure-Python core. No system binaries required.

```bash
python3 -m pip install python-pptx pillow
pptx inspect deck.pptx
pptx lint deck.pptx
pptx export deck.pptx --pdf      # requires LibreOffice (optional)
```

LibreOffice is optional — only used by `pptx export --pdf`. Without it, build/inspect/lint still work.

## Snapshot tests

`tests/test_examples.py` renders every `examples/*.py` and hashes structure via `inspect_deck`. Run `pytest skills/pptx-create/tests` to gate regressions.
