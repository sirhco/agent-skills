# Tutorial — your first deck in 5 minutes

This walks you through: install → render → swap theme → add brand → lint → export PDF. Copy-paste the commands. Each step verifies before moving on.

## 0. Prerequisites

- Python 3.8+ (`python3 --version`)
- Git (to clone the repo)
- Optional, only for PDF/thumbnails: LibreOffice (`brew install --cask libreoffice`)

## 1. Install (60s)

```bash
git clone git@github.com:sirhco/agent-skills.git ~/code/agent-skills
cd ~/code/agent-skills
./install.sh --skill pptx-create
# accept the deps prompts (python-pptx, pillow)
# extras prompt is optional (pygments, cairosvg, watchdog) — skip for now
```

Add the CLI shim to your `PATH`:

```bash
echo 'export PATH="$PATH:$HOME/code/agent-skills/skills/pptx-create/bin"' >> ~/.zshrc
source ~/.zshrc
```

Verify:

```bash
pptx version
# → pptx-create 0.2.0

pptx themes
# → 14 themes listed
```

## 2. Scaffold a starter outline (15s)

```bash
mkdir -p ~/work/first-deck && cd ~/work/first-deck
pptx new qbr -o outline.md --theme stripe
```

Open `outline.md` — that's your editable source. The frontmatter at the top sets the deck-wide theme:

```yaml
---
theme: stripe
---
```

## 3. Render → first .pptx (10s)

```bash
pptx render outline.md
# → + outline.pptx
```

Inspect what you got:

```bash
pptx inspect outline.pptx | head -30
```

Open it visually:

```bash
open outline.pptx        # macOS
start outline.pptx       # Windows
xdg-open outline.pptx    # Linux
```

PowerPoint or Keynote will open it. The slide structure follows the `qbr` template — you can edit `outline.md` and re-render.

## 4. Edit → live preview (45s)

Make a quick edit. Replace the first slide with your own:

```markdown
---
theme: stripe
---

# Acme Q3 Review [title]
## Operations + Product · 2026-04-28

# Q3 KPIs [metric_grid]
## $1.2M | ARR | +34%
## 412 | Customers | +58
## 99.97% | Uptime |
## 4.8 / 5 | CSAT | +0.3

# Top wins
- Closed 14 enterprise deals
- Shipped billing v2
- 99.97% uptime maintained

# Q4 plan: ship billing v2 [cta]
## sub: Close 3 deals before EOQ
## contact: ops@acme.com
```

Run watch mode for live rebuild:

```bash
pptx render outline.md --watch --open
```

Edit-and-save in your editor; the deck rebuilds in ~0.5s. Ctrl-C to stop.

## 5. Swap theme (10s)

Try another theme without editing the file:

```bash
pptx render outline.md --theme pitch-noir -o pitch-version.pptx
pptx render outline.md --theme mckinsey  -o board-version.pptx
pptx render outline.md --theme healthcare -o teal-version.pptx
```

`pptx themes` shows the full list. For dark variants of light themes:

```bash
pptx render outline.md --theme stripe --mode dark
```

## 6. Brand override via `brand.toml` (60s)

Drop this file next to your outline:

```toml
# ~/work/first-deck/brand.toml
accent = "#0E8388"
footer_text = "Acme Confidential · 2026"
# logo_path = "/Users/me/work/acme-logo.png"   # uncomment when ready
# logo_position = "tr"
```

Re-render — the brand kit is auto-discovered:

```bash
pptx render outline.md
```

Footer now reads "Acme Confidential · 2026". Accent shifted to teal regardless of which theme you pick. Useful when you want to keep theme typography but bend brand colors.

## 7. Lint before sharing (5s)

```bash
pptx lint outline.pptx
```

Catches:

- Image alt-text missing → fix by passing `alt="..."` in markdown
- Text contrast < 4.5:1 vs background (WCAG AA)
- Likely text overflow on a slide
- Duplicate slide titles
- Inconsistent capitalization across titles

In CI, run with `--strict` to fail on warnings too.

## 8. Diff against a previous version (5s)

```bash
cp outline.pptx outline-v1.pptx
# ... edit outline.md ...
pptx render outline.md
pptx diff outline-v1.pptx outline.pptx
```

Shows exactly which slides shifted. Useful for PR review without opening PowerPoint.

## 9. Export PDF (60s, optional)

Requires LibreOffice. Skip if you don't have it:

```bash
pptx export outline.pptx --pdf
# → + outline.pdf

pptx export outline.pptx --thumbs thumbs/
# → per-slide PNGs in thumbs/slide_001.png ...
```

For Slack-friendly thumbnails, the `--thumbs` output is what you want.

## 10. Reveal.js for the web (30s, optional)

Same markdown, web output:

```bash
pptx reveal outline.md -o web/ --open
```

Opens `web/index.html` in your browser. Charts are real Chart.js (interactive), code is syntax-highlighted, speaker notes render via the Reveal.js notes plugin.

## You're done

You now have:

- A markdown source you can keep editing
- One `.pptx` you can hand to PowerPoint users
- Optionally: PDF, slide PNGs, a Reveal.js web version

## Next steps

- [`docs/MARKDOWN.md`](MARKDOWN.md) — every slide kind with examples
- [`docs/THEMES.md`](THEMES.md) — write your own theme
- [`docs/CLI.md`](CLI.md) — every CLI flag
- [`examples/`](../examples/) — 10 full decks (QBR, sales, pitch, all-hands, postmortem, product launch, clinical, grand rounds, hospital admin, healthcare IT)

## Common stumbles

- **`pptx: command not found`** — see `docs/TROUBLESHOOTING.md`. Usually a `PATH` issue.
- **`MarkdownError: line 24 ...`** — the parser tells you exactly what's missing. Add the suggested content.
- **Bullets render tiny** — too many / too long. Tighten copy or split slides.
- **Theme contrast lint failure** — the theme's own colors fail AA. Pick a different theme or override `accent` via `brand.toml`.

Full troubleshooting list: [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md).
