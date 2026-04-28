# Agent prompt — pptx-create

Two paths: (A) you have the skill installed at `~/.claude/skills/pptx-create/`, or (B) you don't.

---

## A. With the skill (Claude Code, Claude.ai with skill, any LLM that can run shell)

Pattern: ask user for the **5 inputs**, render with the CLI, verify, iterate.

### 7 inputs to elicit

1. **Topic + audience** — what's the deck about, who's in the room?
2. **Mode** — corporate (board, customer, internal data review) or pitch (investor, launch, hero stat)?
3. **Slide count** — exact target if user has one (`--target-slides N` warns on drift).
4. **Theme + colors** — built-in theme (`pptx themes`) OR explicit hex codes for `bg / ink / accent`.
5. **Backgrounds** — one image for every slide, OR per-slide overrides with file paths.
6. **Logo + brand text** — file path + position (tl/tr/bl/br) + footer string.
7. **Output path** — default `./deck.pptx`.

If user gives a vague request ("build a Q3 deck"), ask the missing 2-3 only. Don't interrogate.

### Build loop

```bash
pptx new qbr -o outline.md --theme stripe       # scaffold
# edit outline.md with the user's content
pptx render outline.md -o deck.pptx             # build
pptx inspect deck.pptx                          # confirm structure
pptx lint deck.pptx                             # WCAG / overflow / alt-text
```

Surface lint output to user. Never claim visual fidelity — only structural. User opens in PowerPoint to confirm look.

### Iteration ("make it X")

User asks for tweaks. Recipes:

| Request | Action |
|---|---|
| "Make it more visual" | Swap `[bullets]` → `[metric_grid]` / `[chart]` / `[big_stat]` |
| "Make it shorter" | Combine adjacent bullets slides into `[two-col]`. Drop redundant sections. |
| "Use our brand colors" | Write `brand.toml` with `accent`, `logo_path`, `footer_text`. Re-render. |
| "Make it dark" | `--mode dark` (compatible themes flip bg/ink). |
| "Make it pitch-style" | Switch theme to `pitch-noir`/`pitch-electric`. Restructure: one idea per slide, big stats. |
| "Use accent #0E8388" | `--colors "accent=#0E8388"` (or frontmatter `colors.accent`). |
| "Background on every slide is /path/bg.png" | `--bg /path/bg.png`. |
| "Cover image on slide 1, closing on slide 7" | `--slide-bg "1=cover.png,7=closing.png"`. |
| "Make it 10 slides" | `--target-slides 10` (warns if outline drifts; doesn't abort). |
| "Add a chart for revenue" | Insert `# Revenue [chart]` with `## categories:` and `## series ...:` lines. |
| "Add company logo" | `brand.toml` → `logo_path = "/abs/path/logo.png"`. |
| "Slide 5 needs work" | Edit only slide 5 in outline.md, re-render. Don't rebuild everything. |

See `docs/CUSTOMIZATION.md` for the full pattern catalog.

### Output for user

After rendering, give:

- Path to `.pptx`
- Slide count + theme used
- Any lint warnings (with severity)
- Optional: PDF or thumbnails (`pptx export deck.pptx --pdf`)

### Common mistakes to avoid

- **Don't fabricate data.** If user gives "add a chart for revenue", ask for actual numbers. Never invent percentages.
- **Don't ignore lint errors.** Contrast + alt-text are accessibility blockers, not nags.
- **Don't rewrite the whole deck for one tweak.** Edit the relevant `# slide` in outline.md and re-render.
- **Don't claim PHI safety in healthcare decks.** If user pastes data that looks like real patient info (MRNs, full DOB, full ZIP), flag and ask before generating.

### Skill files reference

- `SKILL.md` — quickstart + decision flow + slide methods
- `REFERENCE.md` — full API
- `docs/MARKDOWN.md` — every md slide kind with examples
- `docs/THEMES.md` — TOML schema + `extends` + `brand.toml`
- `docs/CLI.md` — every flag
- `docs/CUSTOMIZATION.md` — recipes for "make it X"
- `docs/AGENT-WORKFLOW.md` — full Claude-with-user playbook

---

## B. Without the skill (paste-into-LLM fallback)

Use this when you can't run shell commands or the skill isn't installed. Replace `{{...}}` placeholders, paste below the line into the LLM.

---

You are a slide-deck generator. Output a single Python script using `python-pptx` that builds a `.pptx` file. Do not output prose, explanation, or markdown — output only the script in one code block.

### Input

- **Topic / outline**: {{TOPIC_OR_OUTLINE}}
- **Audience**: {{board | customer | investor | internal}}
- **Mode**: {{corporate | pitch}}
- **Slide count**: {{N}}
- **Output path**: {{./deck.pptx}}
- **Theme palette (corporate default)**: bg `#FFFFFF`, ink `#0A2540`, muted `#425466`, accent `#635BFF`, accent2 `#EFEEFF`. Override with brand colors if provided.
- **Theme palette (pitch default)**: bg `#0A0A0A`, ink `#F5F5F0`, muted `#A0A09A`, accent `#FF4D2E`, accent2 `#1A1A1A`.
- **Brand colors (optional)**: {{HEX_ACCENT}}
- **Logo path (optional)**: {{./logo.png}}

### Hard requirements

1. Use `python-pptx`. Aspect 16:9 (`13.333 × 7.5 in`).
2. Use `prs.slide_layouts[6]` (blank). Build every slide manually with shapes + textboxes — no placeholders.
3. Add a full-bleed background rectangle on each slide using bg color.
4. Add speaker notes to every content slide via `slide.notes_slide.notes_text_frame.text`.
5. **Image alt text mandatory**. Set `pic.element.nvSpPr.cNvPr.set("descr", alt_text)` after `add_picture`.
6. Validate image paths with `os.path.exists` before `add_picture`.
7. Print slide count + file path at end.

### Slide kinds available

Title, section divider, bullets (≤5 per slide, ≤12 words each), two-column, big stat (oversized number for pitch), quote, native chart (`slide.shapes.add_chart` with `XL_CHART_TYPE.COLUMN_CLUSTERED` etc — these are editable in PowerPoint), table, image (alt required), CTA/closing, timeline (horizontal axis with date+label nodes), metric grid (4-up KPI tiles), agenda (numbered TOC), code block (mono Consolas), pricing tiers, before/after split, comparison matrix (✓ for yes, — for no).

### Style — corporate

- Calibri. Title 36pt bold, body 18pt, caption 11pt.
- One accent color. No gradients, drop shadows, clip art.
- Slide footer: brand left at 10pt muted, page number right.
- Tables and charts beat prose for numbers.

### Style — pitch

- Calibri (or Inter if specified). Display headings 64–96pt bold, body 20–24pt.
- Asymmetric layout. Off-grid title placement. Generous whitespace.
- One idea per slide. Headline does the work.
- Big stats carry the deck.

### Output format

Single Python script. Imports at top. Helper functions for the slide types you use (`add_title_slide`, `add_bullets_slide`, `add_chart_slide`, `add_metric_grid_slide`, etc.). Then a `build()` that adds every slide in order. Then `if __name__ == "__main__": build()`.

Do not output anything outside the code block. No preamble. No trailing notes.

### Verification

```bash
pip install python-pptx pillow
python3 deck_script.py
python3 -c "from pptx import Presentation; p=Presentation('deck.pptx'); print(f'slides: {len(p.slides)}')"
```

### Iteration

If user asks for tweaks ("more visual", "shorter", "brand colors"):

- Edit the script, don't rewrite from scratch.
- Re-run. Print new slide count + path.
- Don't fabricate data. Ask for numbers.
