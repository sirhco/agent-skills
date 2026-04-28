# Customization recipes

Pattern-matched fixes for common user requests. Each entry: trigger phrase → diff → command.

Use this as Claude's lookup table when the user says "make it X". The point is to never rewrite the whole deck for one tweak.

## Visual / layout

### "Make it more visual" / "less text"

Swap text-heavy slides for visual kinds.

```diff
-# Q3 wins
-- Closed 14 enterprise deals
-- Shipped billing v2
-- 99.97% uptime
-- 4.8 CSAT
+# Q3 wins [metric_grid]
+## 14 | Enterprise deals | +5
+## v2 | Billing shipped |
+## 99.97% | Uptime |
+## 4.8 / 5 | CSAT | +0.3
```

Other swaps:
- Bullets of percentages → `[chart]`
- A single hero number → `[big_stat:73%]`
- A list of phases → `[timeline]`
- A feature list → `[comparison]` table vs competitor
- A row of features at price points → `[pricing]`

### "Make it shorter" / "trim by 30%"

1. Combine adjacent `[bullets]` slides into one `[two-col]`.
2. Drop redundant section dividers (keep one per ~5 content slides).
3. Cut bullets to ≤4 per slide, ≤10 words each.
4. Replace summary slides with a single `[big_stat]` or `[cta]`.

### "Make it longer" / "more depth"

1. Split dense `[two-col]` into two `[bullets]` slides.
2. Add `[section]` dividers between major topics.
3. Add an `[agenda:N]` after the title (with `current` updated per section).
4. Add `[chart]` or `[table]` to back up claims.

### "Make slide N <change>"

Edit only that slide block in outline.md. Re-render. Don't touch the others.

```bash
# in outline.md, find:
# # Title for slide 5 [bullets]
# - old bullet 1
# ... edit ...
pptx render outline.md
```

## Theme + brand

### "Use our brand colors"

Three ways, lowest to highest precedence:

**A. CLI flag (one-shot)**

```bash
pptx render outline.md --colors "accent=#0E8388,bg=#FFFFFF,ink=#0A2540"
```

Keys accepted: `bg`, `ink`, `muted`, `accent`, `accent2`, `font`. Comma-separated, no spaces around `=`.

**B. Frontmatter (per-deck)**

```yaml
---
theme: stripe
colors:
  accent: "#0E8388"
  bg: "#FFFFFF"
  ink: "#0A2540"
---
```

**C. brand.toml (per-project, every deck in dir)**

```toml
accent = "#0E8388"
footer_text = "Acme Confidential · 2026"
# logo_path = "/abs/path/to/logo.png"
# logo_position = "tr"
```

Auto-discovered when running from the same directory. Or `--brand-file path/to/brand.toml`.

User passes only hex codes? Use **A** for the speed path.

### "Use this background image"

**A. Single bg for every slide (CLI)**

```bash
pptx render outline.md --bg /path/to/bg.png
```

**B. Per-slide overrides (CLI)**

```bash
pptx render outline.md --slide-bg "1=cover.png,3=section.jpg,5=closing.png"
```

Slide indices are 1-based. Per-slide overrides replace the default; they do not stack.

**C. Frontmatter**

```yaml
---
theme: stripe
backgrounds:
  default: assets/bg.png
  1: assets/cover.png
  5: assets/closing.png
---
```

**D. brand.toml (every deck in dir)**

```toml
background_image = "/abs/path/bg.png"
background_image_position = "cover"   # cover | contain
```

**E. Theme TOML (when bundling with a theme)**

```toml
# themes/acme-brand.toml
extends = "stripe"
[brand]
background_image = "/abs/path/bg.png"
background_image_position = "cover"
```

Position semantics: `cover` fills the slide and crops the image; `contain` letterboxes it. Default is `cover`.

### "Target N slides"

```bash
pptx render outline.md --target-slides 10
```

Or frontmatter `slides: 10`. The CLI prints `warn: target was 10 slides, rendered 12` and **does not abort** — it surfaces drift so you can decide whether the outline matches the brief.

When user gave a slide count up front, capture it as a check, not a hard limit. If their outline naturally lands at a different count, ask: cut to target, or keep as-is?

### "Add our logo"

```toml
# brand.toml
logo_path = "/Users/me/work/acme-logo.png"
logo_position = "tr"   # tl | tr | bl | br
```

Logo appears on slide master + per slide. PNG with transparent background works best.

### "Make it dark"

```bash
pptx render outline.md --mode dark
```

For light themes (`stripe`, `mckinsey`, `apple`, etc.), this swaps bg ↔ ink. Pre-dark themes (`linear`, `pitch-noir`) are unchanged. For pixel-perfect dark variants, ship a separate TOML (`acme-brand-dark.toml`).

### "Use a different theme"

```bash
pptx render outline.md --theme pitch-noir -o pitch-version.pptx
```

Themes preview: `pptx themes`. See `docs/THEMES.md` for descriptions. Don't fully rewrite the deck — same content, different theme.

### "Make it pitch-style" (corporate → pitch)

This **does** require some content rework, not just a theme swap.

1. Switch theme: `--theme pitch-noir` (or `pitch-electric` / `pitch-violet`).
2. Restructure: one idea per slide.
3. Replace `[bullets]` slides with `[big_stat]` + caption.
4. Replace tables/charts with hero numbers.
5. Strip footer brand (pitch decks rarely show it).
6. Make headlines do the work — short, declarative.

```diff
-# Why now [bullets]
-- Market is at $50B and growing 30%/yr
-- Incumbents stuck in legacy
-- AI shift creates a 10x opportunity
+# $50B [stat]
+## market growing 30% per year
+
+# Incumbents are stuck. [section]
+
+# 10× opportunity [stat:10x]
+## AI shift opens a window incumbents can't enter
```

### "Switch from pitch back to corporate"

Reverse: `--theme stripe` (or `mckinsey`). Re-add `[bullets]`, `[two-col]`, `[chart]`, `[table]`. Pitch decks often lack data — ask user for the numbers.

## Content patterns

### "Add a chart for revenue"

Need numbers from user first. Then:

```markdown
# Revenue [chart]
## categories: Q1, Q2, Q3, Q4
## series Actual: 2.1, 2.6, 3.4, 4.1
## series Plan: 2.0, 2.5, 3.0, 3.5
```

Default kind is column. Override:

```markdown
# Revenue trend [chart:line]
```

Other kinds: `bar`, `line`, `pie`, `area`, `doughnut`. Pie/doughnut want a single series; bar charts work better than column for >5 categories.

### "Add a comparison table"

```markdown
# Us vs them [comparison]
| Feature | Acme | Competitor |
| --- | --- | --- |
| SSO + SCIM | yes | no |
| Audit log | yes | yes |
| Free tier | yes | no |
| API rate limit | unlimited | 1k/hr |
```

`yes/true/✓` → bold ✓ in accent. `no/false/—/-` → muted dash.

### "Add an agenda"

After the title slide:

```markdown
# Agenda [agenda]
## Topline
## Risks
## Q4 plan
```

For one with current-section highlight (works as a recurring slide between sections):

```markdown
# Agenda [agenda:1]
## Topline
## Risks         <- highlighted
## Q4 plan
```

### "Add speaker notes"

Two forms:

```markdown
# Slide title
- bullet

> note for speaker — multi-line ok
> won't show on the projected slide

[notes: legacy single-line form]
```

Use `>` lines. The whole block joins into one notes section.

### "Add a code sample"

````markdown
# Sample [code:python]
```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```
> remind audience this is illustrative
````

`pygments` highlights if installed (`requirements-extras.txt`). Falls back to plain mono. Lang values: `python`, `javascript`, `typescript`, `bash`, `sql`, `go`, `rust`, etc. — anything Pygments accepts.

### "Add an image"

```markdown
# Architecture [image]
![v2 stack diagram](diagrams/arch-v2.png "v2 architecture overview")
```

Alt text required. Caption optional (in quotes). Standalone `![alt](path)` outside any heading creates an image slide.

### "Add a before/after"

```markdown
# Migration impact [before_after]
## before: 14 manual steps, 3-day cycle
- nightly batch
- engineer babysit
## after: API webhook, real-time
- self-serve
- audit log
```

## Quality gates

### "Lint failed — fix it"

For each issue type:

- **`alt-missing`** — add `alt="..."` to the image (or `alt=""` for purely decorative).
- **`contrast`** — pick a different theme, or override `accent` in `brand.toml` to a value that contrasts with `bg`. Quick check: `python3 -c "from helpers.lint_deck import _contrast; print(_contrast('#FG', '#BG'))"`. Need ≥4.5.
- **`overflow`** — shorten bullets. ≤5 per slide, ≤12 words each.
- **`dup-title`** — rename one. Add a section qualifier ("Risks · Customer" / "Risks · Internal").
- **`caps-mixed`** — pick title case OR sentence case, apply to all titles.

### "Make it accessible" / "WCAG compliant"

```bash
pptx lint deck.pptx --strict   # fail on warnings too
```

Beyond lint:

- Every image gets meaningful `alt` (not "image" or "picture of...").
- Every chart has a title that conveys the takeaway, not just "Revenue".
- Avoid color-only encodings — pair with text or icon.
- Slide titles are unique (screen readers read titles to navigate).

## Output

### "Export to PDF"

```bash
pptx export deck.pptx --pdf
```

Requires LibreOffice. If user lacks it, either name the install command or skip PDF and offer `pptx inspect` for structure.

### "Give me thumbnails"

```bash
pptx export deck.pptx --thumbs thumbs/
```

Per-slide PNGs in `thumbs/slide_001.png ...`. Useful for Slack share or README image grids.

### "Make a web version"

```bash
pptx reveal outline.md -o web/ --open
```

Reveal.js bundle from the same markdown. Charts render as Chart.js (interactive). Speaker notes via the notes plugin (press `s`).

## Diff + review

### "Show me what changed"

```bash
cp deck.pptx deck-v1.pptx   # before edits
# ... iterate ...
pptx render outline.md
pptx diff deck-v1.pptx deck.pptx
```

Unified diff of slide titles + body text + shape kind disparities. Useful in PR review.

## Reset / restart

### "Start over with a different template"

```bash
pptx new pitch -o outline2.md --theme pitch-noir --force
# fresh outline; original outline.md untouched
```

`--force` overwrites; without it, the CLI errors rather than clobber.

### "Throw away the brand kit"

Delete `brand.toml` from the dir, or pass `--brand-file /dev/null` (CLI ignores missing files). Or write an empty `brand.toml`.

## When recipes don't match

Two options:

1. **Ask the user to clarify.** Vague requests ("make it pop") don't have a deterministic edit. Push back with two concrete options.
2. **Edit the markdown directly.** It's a plain text file. Anything you can describe you can do by hand.

For genuinely new patterns, see `CONTRIBUTING.md` to add a slide kind, theme, or CLI flag.
