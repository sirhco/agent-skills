# Contributing to pptx-create

How to extend the skill: add a slide kind, theme, example, or fix a bug. Keep the surface stable — the agent (Claude) and CLI consumers depend on it.

## Layout

```
skills/pptx-create/
├── SKILL.md           # agent quickstart (≤80 lines)
├── REFERENCE.md       # full API
├── README.md          # human landing
├── CHANGELOG.md
├── helpers/           # python modules + CLI dispatcher
├── themes/            # themes.py registry + *.toml files
├── templates/         # markdown deck starters
├── examples/          # runnable Python decks
├── docs/              # human-facing prose
├── tests/             # pytest snapshots
└── bin/pptx           # CLI shim
```

## Add a slide kind

A slide kind = a `Deck.<name>(...)` method + a markdown parser hook + (optional) a Reveal.js renderer.

### 1. Method on `Deck`

`helpers/build_deck.py` — add the method alongside the others:

```python
def my_kind(self, title, payload, *, notes=""):
    slide = self._new()
    self._title_bar(slide, title)
    # draw shapes via add_text / add_rect / shape primitives
    add_notes(slide, notes)
    return slide
```

Conventions:

- First arg always `title` (string).
- Use theme dict — `t = self.theme; t["accent"]; t["bg"]; t["ink"]; t["muted"]; t["accent2"]; t["font"]`.
- Use `Inches()` and `Pt()` for sizing. Slide is 13.333 × 7.5 in. Title bar takes top ~1.5 in. Footer takes bottom ~0.5 in.
- Always call `add_notes(slide, notes)` last.
- For images, require `alt` keyword (accessibility).

### 2. Markdown parser hook

`helpers/markdown_to_pptx.py` — add a branch in `build_from_md`:

```python
elif kind == "my_kind":
    payload = ... # parse from s["subs"] / s["body"] / s["arg"] / s["table"]
    d.my_kind(title, payload, notes=notes)
```

If the kind has hard requirements (table rows, two `## ` blocks, etc.), add to `_KIND_SCHEMAS`:

```python
_KIND_SCHEMAS["my_kind"] = {"requires": "table", "hint": "add a `| h1 | h2 |` table"}
```

The validator raises `MarkdownError` with line numbers when content is missing.

### 3. Reveal.js renderer

`helpers/markdown_to_reveal.py` — add `_section_my_kind(s)` returning an HTML `<section>...</section>` string. Wire into the `for s in slides` dispatch in `render_markdown_to_reveal`. Use the `:root` CSS variables (`--bg`, `--accent`, etc.) for theme integration.

### 4. Document

- `docs/MARKDOWN.md` — add a `### [my_kind]` section with input + behavior.
- `REFERENCE.md` — add a row to the slide methods table.
- `SKILL.md` — append `my_kind` to the slide methods sentence.
- `CHANGELOG.md` — under `[Unreleased]`.

### 5. Test

```bash
PPTX_SNAPSHOT_UPDATE=1 pytest tests/   # bootstrap if you added a new example
pytest tests/                          # confirm pass
```

If you added a new example deck, the parametrized `test_example_snapshot` picks it up automatically.

## Add a theme

Prefer TOML over Python dict for new themes.

1. Create `themes/<name>.toml`. Set `extends = "stripe"` (or any base) to inherit.
2. Override only the fields that differ.
3. Lint: `pptx render examples/qbr.md --theme <name> -o /tmp/test.pptx && pptx lint /tmp/test.pptx`. Fix contrast errors.
4. Add a row to `docs/THEMES.md` built-ins table.
5. Re-render screenshots: `./scripts/render_theme_screenshots.sh`.
6. Bump CHANGELOG.

## Add an example

Pick the closest existing example, copy it, edit. Required pattern:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.build_deck import Deck
from themes.themes import get_theme

def build():
    d = Deck(theme=get_theme("stripe"), brand="Example Co · 2026")
    d.title("Title", "Subtitle")
    # ... slides ...
    d.save("my_example_deck.pptx")

def main():
    build()

if __name__ == "__main__":
    main()
```

Run once locally to confirm. Update `examples/README.md` with the new row. Bootstrap snapshot:

```bash
PPTX_SNAPSHOT_UPDATE=1 pytest tests/test_examples.py::test_example_snapshot[my_example_deck]
pytest tests/test_examples.py::test_example_snapshot[my_example_deck]
```

Commit the snapshot JSON.

## Snapshot test workflow

When intentional structural change shifts a snapshot:

```bash
PPTX_SNAPSHOT_UPDATE=1 pytest tests/
git diff tests/snapshots/   # review the structural change
git add tests/snapshots/
```

When unintentional drift happens, your build_deck change leaked into example output. Inspect the JSON, find which slide shifted, fix the helper, re-run.

## Version + CHANGELOG

`helpers/build_deck.py` exports `__version__`. Bump on every release. Follow [SemVer](https://semver.org/):

- patch: bug fixes that don't change observable output
- minor: additive (new slide kind, new theme, new flag) — backward compatible
- major: breaking (renamed Deck method, removed flag, signature change)

CHANGELOG follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Group entries under `Added` / `Changed` / `Fixed` / `Removed` / `Deprecated`.

## CLI subcommand additions

`helpers/pptx_cli.py` is the dispatcher. Add a `cmd_<name>(args)` function and register it in `build_parser()` with `sub.add_parser("<name>", ...)`. Document in `docs/CLI.md`.

## Style

- Pure-Python core. The only required runtime dep is `python-pptx` + `pillow`. Anything else (pygments, cairosvg, watchdog, lxml) is in `requirements-extras.txt` with a graceful fallback path.
- No system binaries required for build / inspect / lint. PDF + thumbnails are optional via LibreOffice; the CLI exits with a clear message when LO is missing.
- Keep `helpers/*` modules importable both as `python3 helpers/foo.py` (script) and `from helpers.foo import bar` (library).
- Don't bypass the type system — `from __future__ import annotations` at the top of new files lets you use `str | None` style in helpers.

## PR checklist

- [ ] New code has line-numbered errors / clear failure messages.
- [ ] CHANGELOG bumped.
- [ ] Docs updated (`MARKDOWN.md` / `THEMES.md` / `CLI.md` as relevant).
- [ ] Lint passes on the example output: `pptx lint examples/<related>.pptx`.
- [ ] Snapshot tests pass: `pytest tests/`.
- [ ] If you added a new dep, it's in `requirements-extras.txt` (not core) unless absolutely required.
