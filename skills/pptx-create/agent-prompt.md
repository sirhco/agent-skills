# PPTX Generation Prompt — paste into Copilot Chat / ChatGPT / any LLM

Copy everything below the `---` line. Replace `{{PLACEHOLDERS}}` before sending.

---

You are a slide-deck generator. Output a single Python script using `python-pptx` that builds a `.pptx` file. Do not output prose, explanation, or markdown — output only the script in one code block.

## Input

- **Topic / content**: {{TOPIC_OR_OUTLINE}}
- **Mode**: {{corporate | pitch}}
- **Slide count**: {{N}}
- **Output path**: {{./deck.pptx}}
- **Brand colors (optional)**: {{HEX_PRIMARY, HEX_ACCENT}}
- **Logo path (optional)**: {{./logo.png}}

## Requirements

1. Use `python-pptx`. Aspect ratio 16:9 (13.333 × 7.5 in).
2. Use `prs.slide_layouts[6]` (blank) for every slide. Build layouts manually with shapes and textboxes — do not rely on placeholder layouts.
3. Add speaker notes to every content slide via `slide.notes_slide.notes_text_frame.text`.
4. Validate any image paths exist before calling `add_picture` — wrap in `if os.path.exists(...)`.
5. Print slide count and file path at end of script.

## Style — corporate mode

- Fonts: Calibri. Title 36pt bold, body 18pt, caption 11pt.
- Palette: bg `#FFFFFF`, ink `#1A1A1A`, muted `#5F6B7A`, accent `#0B5FFF` (override with brand color if provided).
- Layout: title top-left, content below. Slide number bottom-right. Logo top-left if provided.
- Max 5 bullets per slide, ≤12 words each. Prefer tables and charts over prose for data.
- Slide types to use as needed: title, agenda, section divider, bullets, two-column, table, chart, quote, CTA/closing.
- Avoid: gradients, shadows, clip art, more than 2 fonts.

## Style — pitch mode

- Fonts: Calibri (or Inter if specified). Display headings 72–96pt bold, body 20–24pt.
- Palette: bg `#0A0A0A`, ink `#F5F5F0`, accent `#FF4D2E` (override with brand if provided).
- Layout: asymmetric, off-grid title placement, generous whitespace. Full-bleed background rectangle on every slide.
- One idea per slide. Headline does the work. Body text optional.
- Slide types: full-bleed title, problem statement, insight (oversized stat), product, market, traction, team, ask/CTA.
- Avoid: bullet lists, corporate iconography, centered everything, clip art.

## Output format

Single Python script. Imports at top. Helper functions for `add_title_slide`, `add_content_slide`, `add_chart_slide`, `add_section_divider`. Then a `build()` function that adds every slide in order. Then `if __name__ == "__main__": build()`.

Do not output anything outside the code block. No "Here is the script:" preamble. No trailing notes.

---

## Verification step (run after script)

```bash
python3 your_script.py
python3 -c "from pptx import Presentation; p=Presentation('deck.pptx'); print(f'slides: {len(p.slides)}')"
```

If `python-pptx` not installed: `pip install python-pptx pillow`.
