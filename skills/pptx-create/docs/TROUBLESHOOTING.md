# Troubleshooting

Common issues, in rough order of likelihood. Each entry has the symptom, root cause, and fix.

## Install / setup

### `pptx: command not found`

The CLI shim isn't on your `PATH`.

```bash
export PATH="$PATH:$HOME/code/agent-skills/skills/pptx-create/bin"
```

Add to `~/.zshrc` / `~/.bashrc`. Or call the shim directly: `~/code/agent-skills/skills/pptx-create/bin/pptx`.

### `ModuleNotFoundError: No module named 'pptx'`

The core dep isn't installed for the Python interpreter the shim uses.

```bash
python3 -m pip install --user -r skills/pptx-create/requirements.txt
```

Re-run from the same shell. If you use multiple Pythons, check which one the shim hits:

```bash
head -1 ~/code/agent-skills/skills/pptx-create/bin/pptx
which python3
```

### `pptx new` says "template not found"

Template name is the file stem (no `.md`). Available: `qbr`, `sales`, `pitch`, `allhands`, `postmortem`. List them:

```bash
ls skills/pptx-create/templates/
```

## Render

### `MarkdownError: line 24: slide #5 ... missing required content`

Schema validation. Check the suggestion line — it tells you what's missing. Common cases:

| Error | Fix |
|---|---|
| `[chart]` missing categories | Add `## categories: a, b, c` |
| `[chart]` missing series | Add `## series Name: 1, 2, 3` |
| `[two-col]` missing | Need exactly two `## ` blocks |
| `[table]` / `[comparison]` missing | Need header row + ≥1 body row |
| `[image]` / `[video]` missing | Need `![alt](path)` |

### `Deck.image() missing required keyword argument: 'alt'`

Image alt text is mandatory for accessibility. Pass `alt="describe what the image shows"`. For decorative images (purely visual flourish), pass `alt=""` explicitly to acknowledge.

### Bullets render at tiny font

Auto-shrink kicked in: too many bullets / too long. Floor is 14pt, then a continuation slide opens. Fixes:

- Tighten copy. ≤5 bullets, ≤12 words each is the corporate rule.
- Split into two `# slides` yourself.
- Use `[two-col]` to split horizontally instead.

### Custom font shows as Calibri in PowerPoint

Two layers — make sure both are set:

1. Theme uses the font: `font = "Inter"` in the TOML.
2. Theme embeds the font: `font_path = "/abs/path/Inter.ttf"`.

Without `font_path`, PowerPoint substitutes Calibri on machines where Inter isn't installed. Verify post-build:

```bash
unzip -l deck.pptx | grep fntdata    # should list ppt/fonts/font1.fntdata
```

If empty, embedding silently failed. Check the warning that `Deck.save()` would have printed.

### Embedded font rejected on opening

PowerPoint only accepts TrueType (`.ttf`). OpenType (`.otf`) is silently dropped. Convert with `fonttools` or pick a TTF source.

Also: the font's OS/2 fsType bits may forbid embedding. The skill doesn't check — if PowerPoint refuses, swap fonts or contact the foundry.

## Lint

### `error contrast: text #X on bg #Y contrast 3.21 < 4.5 (WCAG AA)`

Theme color choice fails accessibility. Options:

- Pick a darker `ink` against light bg, or lighter `ink` against dark bg.
- Override at the brand layer in `brand.toml`:

  ```toml
  accent = "#0E5460"     # darker than the original #0E8388
  ```
- For pitch decks where headlines are the focus, the lint is currently strict on body text. We don't relax for >18pt yet.

### `warning caps-mixed: title casing inconsistent`

Some titles are `Title Case Like This`, others are `Sentence case like this`. Pick one and apply throughout. Quick one-liner:

```bash
sed -i.bak -E 's/^# (.)(.*)/# \U\1\L\2/' outline.md   # sentence case
```

(Backup `.bak` so you can revert.)

### `warning overflow: text shape may overflow`

Heuristic — counts characters/lines vs box height. False positives possible if your text wraps gracefully. Visual check in PowerPoint is the source of truth. To silence the warning, shorten the text or split the slide.

## Export / PDF / thumbs

### `error: LibreOffice not found`

`pptx export --pdf` and `--thumbs` need LibreOffice. Install:

- macOS: `brew install --cask libreoffice` or download from libreoffice.org.
- Linux: `apt install libreoffice` / `dnf install libreoffice`.
- Windows: use the LibreOffice Portable build.

The skill checks `soffice` / `libreoffice` on `PATH` and `/Applications/LibreOffice.app/Contents/MacOS/soffice` on macOS. If installed elsewhere, symlink it onto `PATH`.

### `error: install pdf2image (pip) or poppler (pdftoppm)`

PNG slicing needs one of:

```bash
python3 -m pip install --user pdf2image   # cross-platform, requires poppler
brew install poppler                       # macOS — provides pdftoppm
apt install poppler-utils                  # Debian/Ubuntu
```

### Reveal.js slides lose images / charts when using `pptx export --reveal`

`export --reveal` reads the binary `.pptx` and can only recover text. For full fidelity (Chart.js charts, copied images, code highlight, speaker notes), render from the source markdown:

```bash
pptx reveal outline.md -o web/
```

## Watch mode

### `pptx render --watch` doesn't pick up changes

Default is a 0.5s polling loop on file mtime. Network mounts (NFS, SMB) sometimes report stale mtime. Edit the file in place rather than swapping it via `mv` (some editors write a temp + rename, which can confuse poll loops).

For better watch on large dirs install `watchdog`:

```bash
pip install watchdog
```

The CLI uses native polling today; watchdog integration is on the roadmap.

## Snapshot tests

### `snapshot drift for X` — but I didn't change examples

Likely a helper change (theme color, slide layout, a new master shape) bled into example output. The snapshot hash captures slide titles + shape kinds, so any structural change shows up.

If the change was intentional:

```bash
PPTX_SNAPSHOT_UPDATE=1 pytest tests/
git diff tests/snapshots/
```

If unintentional, the diff tells you which slide/example. Inspect with:

```bash
python3 examples/<which>_deck.py
pptx inspect <which>_deck.pptx --json
```

## Brand kit / theme

### `brand.toml` ignored

Loader only reads `brand.toml` from the **current working directory** (or `--brand-file` path). If you run `pptx render` from a different directory, it won't find it.

```bash
cd ~/work/q3-deck    # where brand.toml lives
pptx render outline.md
```

Or pass the path explicitly:

```bash
pptx render outline.md --brand-file ~/work/q3-deck/brand.toml
```

### TOML theme not appearing in `pptx themes`

Two possibilities:

1. Python <3.11 without `tomli` installed. Fix: `pip install -r requirements-extras.txt`.
2. TOML parse error — check for stray `[colors]`/`[type]`/`[brand]` typos. The loader prints `warn: failed to parse <file>: ...` to stderr.

## Healthcare-specific

### Lint flags PHI-looking content

Lint doesn't currently run a PHI detector — Claude (the agent) is the gate. If you're authoring decks programmatically, check your inputs by hand. Real MRNs, full DOB, full ZIP, dates of service all need to be removed or synthesized before embedding.

## Still stuck?

- File an issue with: input markdown (or example you ran), the exact command, the full traceback, and `pptx version`.
- Run `pptx inspect deck.pptx --json` and attach — gives the structural fingerprint without sharing the file.
