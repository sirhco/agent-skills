# Agent workflow — Claude with a user

How Claude (or any tool-using LLM) should drive `pptx-create` to produce a deck the user actually wants. The original goal of this skill is **Claude-generated, user-customizable powerpoints** — this doc is the playbook.

## Core loop

```
discover → confirm → build → inspect → lint → present → iterate
```

Don't skip steps. Each one cuts a class of failures.

## 1. Discover

Ask for the **7 inputs** below. If the user gave any of them in the original prompt, don't re-ask. Collapse to the gaps.

| # | Input | What you actually need | Default if user shrugs |
|---|---|---|---|
| 1 | Topic + audience | Subject of the deck + who's in the room | Ask — don't guess |
| 2 | Mode | corporate / pitch | corporate (safer) |
| 3 | Slide count | How many slides | Offer template via `pptx new` |
| 4 | Theme + colors | Built-in theme name OR explicit hex codes | `corporate-default` if no brand |
| 5 | Backgrounds | Any background image(s) and paths (default + per-slide) | None |
| 6 | Logo + brand text | Optional logo path + footer text | None |
| 7 | Output path | Where to save | `./deck.pptx` |

### Discovery script (paste-grade)

> "To build this deck I need a few quick things:
> 1. Who's the audience? (board, customer, prospect, team, investor)
> 2. Tone — corporate (data-dense, structured) or pitch (bold, editorial)?
> 3. Roughly how many slides, or want me to start from a template (qbr / sales / pitch / allhands / postmortem)?
> 4. Theme — pick a built-in (`pptx themes`) or give me hex codes for accent / bg / ink?
> 5. Any background image(s)? Either one for every slide or specific slides — give me the file path(s).
> 6. Logo or footer text I should include?
> 7. Where to save the file?"

### Translating user answers to render flags

| User says | Action |
|---|---|
| "use #0E8388 as the accent" | `--colors "accent=#0E8388"` (or frontmatter `colors.accent: "#0E8388"`) |
| "white bg with navy text" | `--colors "bg=#FFFFFF,ink=#0A2540"` |
| "10 slides" | `--target-slides 10` (or frontmatter `slides: 10`) |
| "background image at /Users/me/bg.png on every slide" | `--bg /Users/me/bg.png` |
| "use cover.png on slide 1 and section.jpg on slide 5" | `--slide-bg "1=cover.png,5=section.jpg"` |
| "our logo is /Users/me/logo.png in the top-right" | `brand.toml` → `logo_path` + `logo_position = "tr"` |
| "footer should say Confidential 2026" | `--brand "Confidential 2026"` (or `brand.toml` → `footer_text`) |

If the user already gave you obvious answers ("Q3 board update for Acme using their teal accent"), skip to confirming the missing 1-2.

### When to default vs ask

- **Default**: theme, output path, slide count when they gave a clear template.
- **Ask**: actual content (numbers, claims, names), audience, brand assets you don't have.

## 2. Confirm

Before generating, restate what you'll build in one sentence:

> "Building a 10-slide corporate QBR for the Acme board, theme `mckinsey`, saving to `./acme-q3.pptx`. Want me to use the `qbr` template as the skeleton?"

User says yes → build. User says no → adjust → confirm again.

This step exists because the unit cost of a wrong assumption is one full deck rebuild. Asking saves time net.

## 3. Build

```bash
pptx new qbr -o outline.md --theme mckinsey
# edit outline.md to fill placeholders with the user's content
pptx render outline.md -o acme-q3.pptx
```

Two patterns for filling the outline:

- **User has content** — paste their bullets/numbers into the markdown directly. One slide per topic.
- **User just gave a topic** — generate plausible structure but **flag every fabricated detail**. Better: ask for the data before generating.

Programmatic path (custom data, generated charts, lots of conditional logic):

```python
from helpers.build_deck import Deck
from themes.themes import get_theme

d = Deck(theme=get_theme("mckinsey"), brand="Acme · Q3 2026")
# ... slide methods ...
d.save("acme-q3.pptx")
```

Use the programmatic path when the deck shape is data-dependent (e.g., one chart per region, generated from a CSV).

## 4. Inspect + lint

```bash
pptx inspect acme-q3.pptx
pptx lint acme-q3.pptx
```

`inspect` confirms structure (slide count, titles, shape kinds). `lint` catches:

- Image alt-text missing → fix before handing off
- Contrast < 4.5:1 → swap theme or override accent
- Likely overflow → tighten copy
- Duplicate titles → rename
- Caps-mixed → pick one casing

**Surface lint output to the user.** Don't quietly suppress.

## 5. Present

End-of-build message template:

> "Built `acme-q3.pptx`: 10 slides, theme `mckinsey`. 1 lint warning: capitalization mixed across titles (5 title-case, 5 sentence-case). Want me to standardize? Open the file in PowerPoint to check the look."

Always include:

- File path
- Slide count + theme
- Any lint warnings/errors
- Honest disclaimer that you can't visually verify rendering

## 6. Iterate

Most user follow-ups are **single-slide tweaks** or **deck-wide style shifts**. Don't rebuild the whole thing.

| User says | Edit | Re-render |
|---|---|---|
| "Slide 5 needs more punch" | Change just the slide-5 block in outline.md | yes |
| "Use our brand colors" | Write/update `brand.toml` | yes (auto-discovered) |
| "Make it dark" | Add `--mode dark` to render command | yes |
| "Convert to pitch style" | Change theme + tighten content (1 idea/slide) | yes |
| "Add a chart for Q3 revenue" | Insert one `# Revenue [chart]` block | yes |
| "Switch to teal accent" | `brand.toml` → `accent = "#0E8388"` | yes |
| "Shorter" | Combine `[bullets]` slides into `[two-col]`. Drop redundant sections. | yes |
| "Fix typo on slide 3" | Edit that line | yes |

See `CUSTOMIZATION.md` for the full pattern catalog.

### When to ask vs. just edit

Ask when:

- The change implies new data ("add Q4 forecast" — you don't have the numbers)
- The change is ambiguous ("make slide 4 better")
- The cost of a wrong tweak is high (renaming the deck, deleting slides)

Just edit when:

- The change is mechanical (typo, theme swap, brand color)
- The user named the slide and the change

## Output contract

After every build, give the user:

```
✓ deck.pptx (10 slides · theme: mckinsey)
  lint: 0 errors · 1 warning
  - caps-mixed (slide 0): title casing inconsistent
  inspect: pptx inspect deck.pptx
  next:    open deck.pptx (or: pptx export deck.pptx --pdf)
```

## Anti-patterns

- **Don't fabricate data.** If user asks for "a chart of customer growth" without numbers, ask for the numbers first. Made-up percentages erode trust.
- **Don't ignore lint.** Contrast and alt-text are accessibility blockers, not stylistic preferences. Fix before shipping.
- **Don't rewrite the whole deck for one tweak.** Edit the affected slide. Re-render.
- **Don't claim visual fidelity.** You read structure, not pixels. The user's PowerPoint open is the ground truth.
- **Don't bundle brand kit into theme TOML by default.** `brand.toml` is per-project; theme is portable. Mixing them couples brand to theme distribution.
- **Don't auto-install LibreOffice.** Optional. If user wants PDF export and lacks LO, name the install and let them decide.
- **Don't bypass alt text.** `Deck.image(alt="")` for decorative is fine — making the choice explicit. Don't skip the kwarg.
- **Don't write speaker notes only when prompted.** Always include 1-2 lines of notes per content slide. Notes are cheap insurance for the speaker.

## PHI / regulated content

For healthcare decks (`healthcare`, `clinical_research`, `grand_rounds`, `hospital_admin`, `healthcare_it` examples):

- Never embed real MRNs, full DOB, full ZIP, dates of service, patient names. Use synthetic / de-identified data.
- If user pastes data that looks real, **flag and ask** before generating.
- Cite clinical claims (study + year, or guideline body). "Data on file" if internal.
- Use exact regulatory vocabulary (HIPAA, OCR, HITRUST; KDIGO, USPSTF, SCCM). The audience notices.
- Mark forecasts as `(proj)`. Don't imply certainty.

## When the user just gives you a long prompt

Pattern: "make me a 10-slide pitch deck about AI safety". No content.

Don't generate a fully-fabricated deck. Instead:

1. Build the **structural skeleton** (title, problem, market, solution, traction, ask).
2. Fill placeholders with `{{...}}` markers visible in the markdown.
3. Render anyway so user sees the shape.
4. Show the slide list and ask which sections need real content.

This way they get useful structure without fake data, and the iteration loop is short.

## Reference for further detail

- `SKILL.md` — quickstart + decision flow
- `docs/MARKDOWN.md` — md syntax per slide kind
- `docs/CUSTOMIZATION.md` — recipes for "make it X"
- `docs/THEMES.md` — TOML themes + `brand.toml`
- `docs/TROUBLESHOOTING.md` — when something breaks
