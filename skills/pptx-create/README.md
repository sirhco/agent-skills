# pptx-create

Build .pptx slide decks programmatically with [python-pptx](https://github.com/scanny/python-pptx). Pure-Python core (one pip dep), no external binaries required for build/lint/inspect — safe for locked-down corporate / hospital machines. LibreOffice is optional and only needed for PDF + thumbnail export.

This is a [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills). Drop into `~/.claude/skills/` and Claude auto-discovers it. The skill can also be used standalone — every helper has a CLI.

## Install

From the repo root:

```bash
./install.sh --skill pptx-create
```

Or manual:

```bash
python3 -m pip install -r skills/pptx-create/requirements.txt
# optional extras (syntax highlight, SVG icons, watch backend, TOML on py<3.11):
python3 -m pip install -r skills/pptx-create/requirements-extras.txt
ln -s "$(pwd)/skills/pptx-create" ~/.claude/skills/pptx-create
```

Add `skills/pptx-create/bin/` to `PATH` to use the `pptx` CLI globally.

## First deck (60 seconds)

```bash
pptx new qbr -o my-deck.md --theme stripe   # scaffold from a template
pptx render my-deck.md -o my-deck.pptx       # build the .pptx
pptx inspect my-deck.pptx                    # confirm structure
pptx lint my-deck.pptx                       # WCAG / overflow / alt-text
open my-deck.pptx                            # macOS; PowerPoint takes it from here
```

## Three workflows

| Workflow | Command | When |
|---|---|---|
| Markdown → pptx | `pptx render outline.md` | You have an outline. Fastest. |
| Programmatic | `from helpers.build_deck import Deck` | Need custom data, charts, generated content. |
| Copy an example | edit `examples/<closest>.py`, run | Want a known-good shape to start from. |

## Capabilities

- 19 slide kinds: `title`, `section`, `bullets`, `two_col`, `big_stat`, `quote`, `cta`, `chart` (native editable column/bar/line/pie/area/doughnut), `table`, `image` (alt required, fit=contain/cover), `timeline`, `comparison` matrix, `metric_grid` (4-up KPI), `code` (pygments highlight), `agenda`, `pricing`, `before_after`, `video_placeholder`, plus markdown frontmatter / `:::` fences / `>` notes.
- 14 themes — 8 corporate (`stripe`, `linear`, `mckinsey`, `apple`, `monochrome`, `finance`, `healthcare`, `corporate-default`) + 5 pitch (`pitch-noir`, `pitch-editorial`, `pitch-electric`, `pitch-violet`, `pitch-clay`) + external TOML themes with `extends` inheritance.
- `brand.toml` per project — override accent / logo / footer / font deck-wide.
- Slide masters populated by theme — edit master in PowerPoint, changes propagate.
- Bullet auto-shrink + overflow split. Image alt-text required. WCAG-AA contrast lint. Duplicate-title + capitalization lint.
- Native editable charts (Chart.js when exporting Reveal.js).
- Font embedding via direct OOXML manipulation (TrueType only).
- Reveal.js full-fidelity export from same markdown.
- PDF + thumbnail export via LibreOffice.
- Snapshot tests for every example deck.

## Documentation

| Doc | Read when |
|---|---|
| [`SKILL.md`](SKILL.md) | You're an LLM agent — quickstart + decision flow. |
| [`REFERENCE.md`](REFERENCE.md) | Full API + style rules + healthcare conventions. |
| [`docs/AGENT-WORKFLOW.md`](docs/AGENT-WORKFLOW.md) | Driving this skill from Claude (or any tool-using LLM) — discovery, build loop, iteration. |
| [`docs/CUSTOMIZATION.md`](docs/CUSTOMIZATION.md) | Recipes for "make it X" — the day-to-day Claude playbook. |
| [`docs/TUTORIAL.md`](docs/TUTORIAL.md) | First time — 5-minute walkthrough. |
| [`docs/MARKDOWN.md`](docs/MARKDOWN.md) | Writing decks in markdown — full syntax + per-kind examples. |
| [`docs/THEMES.md`](docs/THEMES.md) | Adding a custom theme or brand kit. |
| [`docs/CLI.md`](docs/CLI.md) | Every `pptx <cmd>` flag with examples. |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | Adding a new slide kind / theme / example. |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Hit an error? Look here first. |
| [`agent-prompt.md`](agent-prompt.md) | Paste-into-LLM fallback when the skill isn't installed. |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed by version. |
| [`examples/README.md`](examples/README.md) | Map use case → starter file. |

## License

Apache 2.0 — see [`../../LICENSE`](../../LICENSE).
