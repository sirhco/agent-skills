# Themes

A theme is a dict of colors + font + mode that every slide builder reads. You can use a built-in, override a built-in via `extends`, or write a fresh one.

## Built-in themes

```bash
pptx themes
```

| Theme | Mode | Best for |
|---|---|---|
| `corporate-default` | corporate | safe neutral white + blue accent |
| `stripe` | corporate | fintech violet on white |
| `linear` | corporate | dark dev-tools sharp |
| `mckinsey` | corporate | navy consulting classic |
| `apple` | corporate | mono with red accent |
| `monochrome` | corporate | postmortems, zero accent |
| `finance` | corporate | forest green, traditional |
| `healthcare` | corporate | teal, soft warm |
| `pitch-noir` | pitch | black + orange punch |
| `pitch-editorial` | pitch | warm cream, burnt accent |
| `pitch-electric` | pitch | black + lime, modern |
| `pitch-violet` | pitch | midnight purple, futurist |
| `pitch-clay` | pitch | earthy terracotta |

Run `./scripts/render_theme_screenshots.sh` to populate `themes/screenshots/<name>.png` (requires LibreOffice).

## Theme schema

Two ways to define a theme: legacy Python dict in `themes/themes.py`, or external TOML file in `themes/<name>.toml`. **Prefer TOML for new themes** — no code edits, supports `extends`, future-proof.

### TOML schema

```toml
# themes/acme-brand.toml
name = "acme-brand"             # optional; defaults to filename stem
extends = "stripe"              # optional inheritance — pull missing fields from parent
mode = "corporate"              # corporate | pitch (controls title slide layout)

[colors]
bg = "#FFFFFF"                  # slide background
ink = "#0A2540"                 # primary text
muted = "#425466"               # secondary / footer text
accent = "#0E8388"              # rules, chart series, CTA fill
accent2 = "#E3F4F4"             # surfaces (panels, code blocks, KPI tiles)

[type]
font = "Calibri"                # ships with PowerPoint by default
font_path = "/abs/path/Inter.ttf"  # optional — embedded into pptx via OOXML
title_size = 36                 # informational; consumers may override
body_size = 18
caption_size = 11

[brand]
logo_path = "/abs/path/logo.png"
logo_position = "tr"            # tl | tr | bl | br
footer_text = "Acme Confidential · 2026"
```

Only `[colors]` and `mode` are strictly required. Everything else has sensible defaults.

### Inheritance

```toml
extends = "stripe"
[colors]
accent = "#0E8388"   # only override what you change
```

The loader merges your overrides over the parent. Resolution order: `name`, then `extends`, then explicit fields. Missing fields fall back to parent → `corporate-default`.

### Dark / light variants

`get_theme(name, mode="dark")` flips `bg ↔ ink` for a light theme; pre-dark themes (`linear`, `pitch-noir`, etc.) are returned as-is. CLI:

```bash
pptx render outline.md --theme stripe --mode dark
```

Heuristic uses bg luminance (<0.5 → already dark). For pixel-perfect dark variants, ship a separate TOML (`stripe-dark.toml`).

## brand.toml — per-project override

Drop `brand.toml` next to your decks (or pass `--brand-file path`). Overrides theme accent / logo / footer / font on every render in that directory. No code change required.

```toml
# ./brand.toml
accent = "#0E8388"
logo_path = "/Users/me/work/acme-logo.png"
logo_position = "tr"
footer_text = "Acme Confidential"
font = "Calibri"
```

Precedence (lowest to highest):

1. theme defaults (`themes/themes.py` or `themes/*.toml`)
2. theme's own `[brand]` block
3. `brand.toml` discovered in CWD (or `--brand-file`)
4. explicit `Deck(brand_kit=...)` argument
5. CLI flags (`--brand`, `--theme`)

## Adding a custom theme

1. Pick a parent (or none): `stripe`, `linear`, `mckinsey`, etc.
2. Create `themes/<your-name>.toml`. Set `extends = "<parent>"` if reusing.
3. Override the colors you actually change. Keep `font = "Calibri"` unless you also embed a font.
4. Test: `pptx render examples/qbr-template.md --theme <your-name> -o test.pptx`.
5. Lint: `pptx lint test.pptx` — fails on contrast violations (WCAG AA <4.5).
6. Optional: render a screenshot. `./scripts/render_theme_screenshots.sh`.

## Contrast rules of thumb

WCAG AA requires contrast ≥ 4.5:1 for body text. Lint enforces this against `text fg vs slide bg`.

- Pure white `#FFFFFF` background → ink darker than `#767676`.
- Near-black `#0A0A0A` background → ink lighter than `#9A9A9A`.
- Accent on background also needs contrast if used for body text. Headlines (>18pt) get a slight pass (3:1) but lint doesn't currently relax.
- `accent2` is for surfaces, not body text. Use `ink` on top of it.

Quick check before lint: `python3 -c "from helpers.lint_deck import _contrast; print(_contrast('#0A2540', '#FFFFFF'))"`.

## Embedding a custom font

Two layers:

1. **Theme uses the font.** Set `font = "Inter"` in the TOML. PowerPoint will substitute Calibri if Inter isn't installed on the recipient's machine.
2. **Embed it.** Set `font_path = "/abs/path/Inter.ttf"` in the same TOML. `Deck.save()` runs `helpers/embed_font.py` post-save, which adds the TTF as `ppt/fonts/font<N>.fntdata` and registers it via OOXML.

Caveats:

- TrueType (`.ttf`) only. OpenType (`.otf`) is rejected by PowerPoint when embedded.
- Adds 100KB–1MB+ to file size. Skip for fonts already on every recipient (Calibri, Arial, Aptos).
- Font license must permit embedding. The skill does **not** check OS/2 fsType — your responsibility.

## Where themes live

```
themes/
├── themes.py                # legacy Python dict registry (still loaded)
├── *.toml                   # external themes loaded by themes._load_toml_themes()
└── screenshots/<name>.png   # populated by scripts/render_theme_screenshots.sh
```

`pptx themes` enumerates everything the loader sees, deduped by name. Last loader wins (TOML overrides legacy dict if names collide).
