---
name: pptx-create
description: Generate .pptx slide decks using python-pptx. Pure-Python — only one pip dependency, no external binaries, safe for locked-down corporate / hospital machines. Two style modes — corporate (data-dense, structured, neutral palette) and pitch (editorial typography, asymmetric layouts, bold color). Includes 13 prebuilt themes (Stripe, Linear, McKinsey, Apple, monochrome, finance, healthcare, pitch-noir, pitch-editorial, pitch-electric, pitch-violet, pitch-clay), 10 worked examples spanning general business (QBR, sales, pitch, all-hands, postmortem, product launch) and healthcare (clinical research readout, physician grand rounds, hospital admin board update, healthcare IT/CIO update), 5 markdown templates, a markdown→pptx converter, native editable charts, lint + diff + PDF export, and a structure inspector. Trigger when user asks to "make a deck", "create slides", "build a powerpoint", "generate pptx", or references a .pptx output. Skip when user wants Google Slides API or Keynote.
---

# pptx-create

Build .pptx files with python-pptx. Three workflows.

## Quickstart

**A. Markdown → pptx** (fastest, when user has outline):

```bash
pptx render outline.md --theme stripe -o deck.pptx
```

**B. Programmatic** (custom data / charts):

```python
from helpers.build_deck import Deck
from themes.themes import get_theme

d = Deck(theme=get_theme("stripe"), brand="Acme · Q3 2026")
d.title("Q3 Business Review", "2026-04-27")
d.bullets("Agenda", ["Topline", "Risks", "Q4 plan"])
d.chart("Revenue", ["Q1","Q2","Q3"], {"$M": (12, 15, 18)})
d.cta("Q4 plan: ship billing v2", contact="ops@acme.com")
d.save("deck.pptx")
```

**C. Copy an example** (`examples/<name>.py`), edit, run.

## Decision flow

1. Markdown outline? → A (`pptx render`).
2. Data + code? → B (`Deck` class).
3. Known shape? → C (copy example).
4. Vague request? Ask: topic, audience, mode (corporate/pitch), slide count, brand colors, output path.

## Pick an example

| User wants | File |
|---|---|
| QBR for customer | `examples/qbr_deck.py` |
| Outbound sales | `examples/sales_deck.py` |
| VC pitch | `examples/pitch_deck.py` |
| All-hands | `examples/allhands_deck.py` |
| Postmortem | `examples/postmortem_deck.py` |
| Product launch | `examples/product_launch_deck.py` |
| Clinical trial readout | `examples/clinical_research_deck.py` |
| Grand rounds / M&M | `examples/grand_rounds_deck.py` |
| Hospital board | `examples/hospital_admin_deck.py` |
| Healthcare CIO | `examples/healthcare_it_deck.py` |

## Pick a theme

Corporate: `corporate-default`, `stripe`, `linear`, `mckinsey`, `apple`, `monochrome`, `finance`, `healthcare`.
Pitch: `pitch-noir`, `pitch-editorial`, `pitch-electric`, `pitch-violet`, `pitch-clay`.

`pptx themes` lists all with one-line descriptions.

## Slide methods

`title`, `section`, `bullets`, `two_col`, `big_stat`, `quote`, `chart`, `table`, `image`, `cta`, `timeline`, `comparison`, `metric_grid`, `code`, `agenda`, `pricing`, `before_after`, `video_placeholder`. All accept `notes=` for speaker notes.

## Verify before handoff

```bash
pptx inspect deck.pptx        # structure: titles, shape counts, bodies
pptx lint deck.pptx           # contrast (WCAG AA), overflow, missing alt-text
```

You **cannot visually verify** rendering — state this. User opens in PowerPoint to confirm look.

## Critical rules

- Calibri default (ships with PowerPoint). Other fonts only if user confirms install.
- Corporate: ≤5 bullets/slide, ≤12 words each. Tables/charts > prose for numbers.
- Pitch: one idea/slide. Headline does work. Big stats carry deck.
- **PHI**: never include real patient identifiers in healthcare decks. Flag if user pastes real-looking data.
- **Image alt text required** for accessibility — `Deck.image(alt="...")`.

## Install

```bash
python3 -m pip install python-pptx pillow
```

Optional extras (`pip install -r requirements-extras.txt`): `pygments` (code highlighting), `cairosvg` (icon SVGs). LibreOffice optional, only for `pptx export --pdf`.

## More detail

`REFERENCE.md` — full slide-method API, theme color schema, markdown syntax, healthcare conventions, style rules, common pitfalls.
`agent-prompt.md` — model-agnostic prompt for LLMs without this skill.
