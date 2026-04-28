# CLI reference

Every subcommand of `pptx`. Run `pptx <cmd> --help` for the same in argparse form.

The `pptx` shim lives at `skills/pptx-create/bin/pptx`. Add that dir to `PATH` for global use, or call helpers directly:

```bash
python3 skills/pptx-create/helpers/pptx_cli.py <cmd> ...
```

---

## `pptx new <template>` — scaffold

Drops a starter `.md` from `templates/` into the current directory.

```
pptx new <template> [-o PATH] [--theme NAME] [--force]
```

| Flag | Meaning |
|---|---|
| `template` | One of `qbr`, `sales`, `pitch`, `allhands`, `postmortem` (or any `.md` in `templates/`). |
| `-o, --output` | Output path. Default: `./<template>.md`. |
| `--theme` | Inject `theme: <name>` into frontmatter. |
| `--force` | Overwrite existing file. |

```bash
pptx new qbr -o my-q3.md --theme stripe
pptx new pitch --theme pitch-noir
```

---

## `pptx render <input.md>` — markdown → pptx

Build a `.pptx` from markdown. The default workflow.

```
pptx render <input.md> [-o PATH] [--theme NAME] [--mode light|dark]
                       [--brand TEXT] [--brand-file PATH]
                       [--watch] [--open]
```

| Flag | Meaning |
|---|---|
| `input` | Markdown file. Frontmatter optional. |
| `-o, --output` | Output `.pptx`. Default: `<input-stem>.pptx`. |
| `--theme` | Theme name (overrides frontmatter `theme:`). |
| `--mode` | `light` or `dark`. Flips bg/ink for compatible themes. |
| `--brand` | Footer-left brand string (overrides frontmatter `brand:`). |
| `--brand-file` | Path to a `brand.toml`. Default: `./brand.toml` if present. |
| `--colors` | Inline palette override. Format: `"bg=#FFF,accent=#0E8388,ink=#0A2540"`. Keys: `bg`, `ink`, `muted`, `accent`, `accent2`, `font`. Wins over theme + frontmatter `colors:`. |
| `--bg` | Path to a default background image used on every slide. Wins over theme/`brand.toml` `background_image`. |
| `--slide-bg` | Per-slide background overrides. Format: `"3=cover.png,5=section.jpg"`. Indices are 1-based. Replaces default for that slide. |
| `--target-slides` | Warn if the rendered slide count differs from N. Doesn't abort the build. |
| `--watch` | Rebuild on file change. Polls every 0.5s. Ctrl-C stops. |
| `--open` | Open the pptx in default viewer after build. |

```bash
pptx render outline.md                           # → outline.pptx
pptx render outline.md --theme stripe --mode dark
pptx render outline.md --colors "accent=#0E8388,bg=#FFF"
pptx render outline.md --bg ./assets/bg.png
pptx render outline.md --slide-bg "1=cover.png,5=closing.jpg"
pptx render outline.md --target-slides 10        # warn if outline drifts
pptx render outline.md --watch --open            # live-preview loop
pptx render outline.md --brand-file ./acme-brand.toml
```

---

## `pptx inspect <deck.pptx>` — structure dump

Read-only structural dump. Use to sanity-check before handing the deck to a user.

```
pptx inspect <deck.pptx> [--notes] [--json]
```

| Flag | Meaning |
|---|---|
| `--notes` | Include speaker notes. |
| `--json` | Emit JSON instead of markdown. |

```bash
pptx inspect deck.pptx
pptx inspect deck.pptx --json | jq '.slides[].title'
```

Output: per-slide title, shape kinds + counts, body text. Cannot verify visual rendering — use a lint or open in PowerPoint for that.

---

## `pptx lint <deck.pptx>` — quality checks

```
pptx lint <deck.pptx> [--strict] [--json]
```

| Severity | Code | Meaning |
|---|---|---|
| error | `alt-missing` | Picture has no `descr` / `title` attr. |
| error | `contrast` | Text vs background contrast < 4.5:1 (WCAG AA). |
| warning | `overflow` | Text shape likely overflows its box. |
| warning | `dup-title` | Two slides share a title. |
| warning | `caps-mixed` | Title casing inconsistent (e.g. mix of Title Case + Sentence case). |

| Flag | Meaning |
|---|---|
| `--strict` | Exit nonzero on warnings too (default: only on errors). |
| `--json` | Emit machine-readable output. |

```bash
pptx lint deck.pptx                  # exits 1 only on errors
pptx lint deck.pptx --strict         # exits 1 on any warning
pptx lint deck.pptx --json | jq      # for CI pipelines
```

---

## `pptx diff <a.pptx> <b.pptx>` — structural diff

```
pptx diff <a> <b> [--json]
```

Renders both decks to a per-slide `(title, body, shape_kinds)` summary, runs `difflib.unified_diff` on the text. Reports shape-kind disparities separately. Exits nonzero when decks differ.

```bash
pptx diff before.pptx after.pptx
pptx diff before.pptx after.pptx --json | jq .differs
```

---

## `pptx export <deck.pptx>` — PDF / thumbs / reveal

```
pptx export <deck.pptx> [--pdf [PATH]] [--thumbs DIR] [--reveal DIR]
```

| Flag | Meaning |
|---|---|
| `--pdf [path]` | Convert to PDF via LibreOffice. Path optional; defaults to deck stem. |
| `--thumbs DIR` | Per-slide PNGs in `DIR`. Requires LibreOffice + (`pdf2image` or `pdftoppm`). |
| `--reveal DIR` | Text-only Reveal.js bundle from the binary `.pptx`. (For full-fidelity, see `pptx reveal` from the source markdown instead.) |

```bash
pptx export deck.pptx --pdf
pptx export deck.pptx --pdf out.pdf --thumbs out_pngs/
```

LibreOffice locations checked: `soffice` / `libreoffice` on `PATH`, plus `/Applications/LibreOffice.app/Contents/MacOS/soffice` on macOS.

---

## `pptx reveal <input.md>` — markdown → Reveal.js (full fidelity)

Same parser as `pptx render`, but emits HTML. Charts via Chart.js. Code highlight via highlight.js. Images copied to `assets/`. Speaker notes via the notes plugin.

```
pptx reveal <input.md> [-o DIR] [--theme NAME] [--brand TEXT] [--open]
```

```bash
pptx reveal outline.md -o web/ --open
```

Outputs `<DIR>/index.html` plus optional `<DIR>/assets/` for images.

---

## `pptx themes` — list themes

```
pptx themes
```

Prints `name  mode  accent_hex` for every theme the loader sees (built-in + external `themes/*.toml`).

---

## `pptx version`

```
pptx version
```

Prints `pptx-create <semver>` from `helpers/build_deck.__version__`.

---

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success or no issues. |
| 1 | Error: missing input, invalid args, lint errors, render exception, decks differ. |

CI-friendly: `pptx render && pptx lint --strict` will fail the build on any quality issue.
