---
name: pptx-create
description: Generate .pptx slide decks using python-pptx. Pure-Python — only one pip dependency, no external binaries, safe for locked-down corporate / hospital machines. Two style modes — corporate (data-dense, structured, neutral palette) and pitch (editorial typography, asymmetric layouts, bold color). Includes 13 prebuilt themes (Stripe, Linear, McKinsey, Apple, monochrome, finance, healthcare, pitch-noir, pitch-editorial, pitch-electric, pitch-violet, pitch-clay), 10 worked examples spanning general business (QBR, sales, pitch, all-hands, postmortem, product launch) and healthcare (clinical research readout, physician grand rounds, hospital admin board update, healthcare IT/CIO update), 5 markdown templates, a markdown→pptx converter, and a structure inspector. Trigger when user asks to "make a deck", "create slides", "build a powerpoint", "generate pptx", or references a .pptx output. Skip when user wants Google Slides API, Keynote, or HTML/Reveal.js decks.
---

# pptx-create

Build .pptx files programmatically with python-pptx. Three workflows depending on input.

## Files in this skill

```
~/.claude/skills/pptx-create/
├── SKILL.md                       # this file
├── copilot-prompt.md              # paste-ready prompt for Copilot/ChatGPT
├── themes/themes.py               # 13 named themes (corporate + pitch)
├── helpers/
│   ├── build_deck.py              # Deck class + slide builders
│   ├── markdown_to_pptx.py        # markdown -> .pptx CLI
│   └── inspect_deck.py            # pure-Python structure verifier (no external deps)
├── templates/                     # markdown deck templates
│   ├── qbr.md
│   ├── sales.md
│   ├── pitch.md
│   ├── allhands.md
│   └── postmortem.md
└── examples/                      # full deck builds, runnable
    ├── qbr_deck.py                       # general — QBR
    ├── sales_deck.py                     # general — outbound sales
    ├── pitch_deck.py                     # general — VC pitch
    ├── allhands_deck.py                  # general — all-hands
    ├── postmortem_deck.py                # general — incident postmortem
    ├── product_launch_deck.py            # general — product launch
    ├── clinical_research_deck.py         # healthcare — RCT readout
    ├── grand_rounds_deck.py              # healthcare — physician grand rounds
    ├── hospital_admin_deck.py            # healthcare — hospital board update
    └── healthcare_it_deck.py             # healthcare — CIO/CMIO/CISO update
```

## Workflow A — markdown to .pptx (fastest)

User has outline / template filled in. Convert directly.

```bash
python3 ~/.claude/skills/pptx-create/helpers/markdown_to_pptx.py \
    user_outline.md --theme stripe -o deck.pptx
```

Templates already cover common deck types — copy from `templates/`, fill placeholders, run.

## Workflow B — Deck class (programmatic, full control)

For decks with custom data, charts, images, generated content. Import the `Deck` class.

```python
import sys
sys.path.insert(0, "/Users/chrisolson/.claude/skills/pptx-create")
from helpers.build_deck import Deck
from themes.themes import get_theme

d = Deck(theme=get_theme("stripe"), brand="Acme · Q3 2026")
d.title("Q3 Business Review", "2026-04-27")
d.bullets("Agenda", ["Topline", "Risks", "Q4 plan"])
d.section("Topline", number=1)
d.chart("Revenue", ["Q1","Q2","Q3"], {"$M": (12, 15, 18)})
d.table("Mix", ["Segment","ARR","Growth"],
        [["Ent","11.2","+34%"],["Mid","5.8","+22%"]])
d.two_col("Risks vs Mitigations",
          "Risks", ["Hiring lag", "Renewal risk"],
          "Mitigations", ["EMEA contractors", "Exec sponsor"])
d.quote("Best month yet.", attribution="CEO")
d.big_stat("$1.2M", "ARR · 4 months")  # pitch mode shines here
d.image("Architecture", "diagram.png", caption="v2 stack")
d.cta("Q4 plan: ship billing v2", sub="Close 3 deals", contact="ops@acme.com")
d.save("deck.pptx")
```

Available slide methods: `title`, `section`, `bullets`, `two_col`, `big_stat`,
`quote`, `chart`, `table`, `image`, `cta`. All accept `notes=` for speaker notes.

## Workflow C — copy an example, edit, run

Closest example wins. Run, then customize.

| User wants… | Start from |
|---|---|
| Quarterly business review for customer | `examples/qbr_deck.py` |
| Outbound sales pitch for prospect | `examples/sales_deck.py` |
| VC pitch deck | `examples/pitch_deck.py` |
| Company all-hands | `examples/allhands_deck.py` |
| Incident postmortem | `examples/postmortem_deck.py` |
| Product launch deck | `examples/product_launch_deck.py` |
| Clinical trial readout / RCT results / IRB summary | `examples/clinical_research_deck.py` |
| Physician grand rounds / case presentation / M&M | `examples/grand_rounds_deck.py` |
| Hospital admin board update / CMO/CNO/CFO report | `examples/hospital_admin_deck.py` |
| Healthcare CIO / CMIO / CISO quarterly | `examples/healthcare_it_deck.py` |

## Themes

Listed in `themes/themes.py`. Pass name to `get_theme("...")`.

**Corporate** (clean, structured, data-friendly):
- `corporate-default` — neutral white + blue accent, safe default
- `stripe` — fintech violet, navy ink
- `linear` — near-black bg, dev-tools sharp
- `mckinsey` — navy + white, consulting classic
- `apple` — mono with red accent
- `monochrome` — pure black/white, postmortems
- `finance` — forest green, traditional finance
- `healthcare` — teal, soft warm

**Pitch** (bold, editorial, design-forward):
- `pitch-noir` — black + orange punch
- `pitch-editorial` — warm cream, burnt accent
- `pitch-electric` — black + lime, modern
- `pitch-violet` — midnight purple, futurist
- `pitch-clay` — earthy terracotta

User can override any color by editing the dict before passing to `Deck`.

## Verification

Pure-Python — works on any machine with `python-pptx` installed. No external
binaries, no LibreOffice. Safe for corporate / locked-down environments.

```bash
python3 ~/.claude/skills/pptx-create/helpers/inspect_deck.py deck.pptx
# add --notes to include speaker notes
# add --json for machine-readable output
```

Output: per-slide title, shape counts (text/table/chart/image), text bodies.
Use this to confirm slide count, structure, content presence before handing
the file to the user.

**You cannot visually verify rendering** — only structural integrity. State
this explicitly. User opens the file in PowerPoint / Keynote / Google Slides
to confirm look.

If user has LibreOffice installed and wants a PDF artifact, opt in:

```bash
python3 ~/.claude/skills/pptx-create/helpers/inspect_deck.py deck.pptx --render-pdf
# silently skipped if LibreOffice not present — no error, no warning
```

## Decision flow when user requests a deck

1. **Have markdown outline?** → Workflow A (markdown_to_pptx.py).
2. **Have data + want code path?** → Workflow B (Deck class).
3. **Want to start from a known shape?** → Workflow C (copy example).
4. **Vague request, no outline?** → Ask:
   - Topic / audience
   - Mode (corporate / pitch) — pick default by audience if obvious
   - Slide count + rough outline (offer to draft from a template)
   - Brand colors (default theme if none)
   - Output path

## Style rules — corporate

- Calibri default font (ships with PowerPoint). Inter / Aptos only if user confirms.
- Title 32–44pt, body 16–20pt, caption 11–12pt.
- One accent color. Avoid gradients, drop shadows, clip art.
- ≤5 bullets per slide, ≤12 words each.
- Tables and charts beat prose for numbers.
- Slide footer: brand left, page number right.

## Style rules — pitch

- Display sans (Calibri default; Inter/Geist if installed). Headings 64–96pt.
- One idea per slide. Headline does the work.
- Asymmetric layout. Off-grid title. Generous whitespace.
- Big stats (`big_stat` slide) carry the deck.
- No bullet lists. No corporate iconography. No clip art.

## Healthcare-specific guidance

For clinical, hospital, or health-IT decks, follow these conventions in addition to the corporate style rules:

- **Theme**: `healthcare` (teal) for clinical/admin; `mckinsey` (navy) for board/exec; `linear` (dark) for IT/CIO.
- **PHI**: never include real patient identifiers (name, MRN, DOB, dates of service, full ZIP, etc.). Use synthetic / de-identified data. If user pastes data that looks real, flag it before generating.
- **Citations**: clinical claims need a source (study name + year, guideline body). Note "data on file" if internal.
- **CONSORT / STROBE / PRISMA**: clinical research decks should mirror the relevant reporting standard. Use `clinical_research_deck.py` as the structural reference.
- **Number formatting**: confidence intervals as `(x.x–y.y)`, p-values as `p=0.024` (italics if rendered). Effect sizes with units. Don't drop decimals.
- **Acronyms**: spell out at first use (HCAHPS, CAUTI, CLABSI, KDIGO, ADD-RS, etc.). Audience-dependent — physicians know SIR; board members may not.
- **Quality vs safety vs experience**: keep these conceptually separate on hospital admin decks. Don't lump HCAHPS with HAI rates.
- **Compliance vocabulary**: HIPAA, OCR, HITRUST, HITECH for privacy; KDIGO/SCCM/ACEP/USPSTF for clinical guidelines. Use exact terminology — these audiences notice.
- **Forecasts vs actuals**: always label projections as "(proj)" or "forecast". Avoid implying certainty for unfilled cells in roadmaps.

## Common pitfalls

- **Custom fonts not installed**: stay on Calibri unless user confirms.
- **Image not found**: validate path before `add_picture` — `Deck.image()` does this.
- **Mid-script crash**: chart values must be numeric, table cells stringified.
- **No visual verification possible without opening the file**. Trust `inspect_deck.py` for structure. User must open in PowerPoint to confirm look.
- **Color contrast**: dark bg + dark accent fails. Themes are pre-tuned; custom overrides need spot-check.

## Companion file

`copilot-prompt.md` — paste-ready prompt for GitHub Copilot Chat, ChatGPT, or
other LLMs without this skill. Same instructions, model-agnostic phrasing.

## Install / dependencies

Only one Python package required. No system binaries. Works on locked-down
corporate machines.

```bash
python3 -m pip install python-pptx
# pillow is only needed if you call .image() with raster images
python3 -m pip install pillow
```

LibreOffice is **not required**. It is an optional opt-in path for users who
want a PDF render via `inspect_deck.py --render-pdf`; without it the skill
works fully (build, inspect, save). If your org blocks installs, ignore.
