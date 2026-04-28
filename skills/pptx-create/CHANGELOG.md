# Changelog

All notable changes to the `pptx-create` skill.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- **End-user documentation suite** under `docs/`: `TUTORIAL.md` (5-min walkthrough), `MARKDOWN.md` (full md syntax with per-kind examples), `THEMES.md` (theme TOML schema, `extends`, `brand.toml`), `CLI.md` (every flag), `CONTRIBUTING.md` (extend the skill), `TROUBLESHOOTING.md` (common errors + fixes). Skill-root `README.md` added as human landing distinct from `SKILL.md`.
- **Slide masters populated by theme** — `Deck._apply_master` sets background, brand footer, and logo on `prs.slide_master` so master edits propagate.
- **Font embedding** — `helpers/embed_font.py` adds a TrueType font as `ppt/fonts/font<N>.fntdata`, registers it in `[Content_Types].xml`, `presentation.xml.rels`, and `presentation.xml`. `Deck.save()` invokes it automatically when the theme has `font_path`.
- **Reveal.js full-fidelity export** — `helpers/markdown_to_reveal.py` (and `pptx reveal` subcommand) renders every slide kind to HTML: charts via Chart.js, code via highlight.js, images copied into `assets/`, speaker notes via the notes plugin.
- **Theme screenshots script** — `scripts/render_theme_screenshots.sh` builds `theme_gallery.pptx`, converts to PDF via LibreOffice, slices per-theme PNGs into `themes/screenshots/`.
- **Snapshot baselines** — initial JSON snapshots committed under `tests/snapshots/` for all 11 example decks (10 worked decks + theme gallery).
- `__version__` constant in `helpers/build_deck.py`.
- `REFERENCE.md` — full API + conventions reference. `SKILL.md` now quickstart-only.
- `CHANGELOG.md` — this file.
- `requirements.txt` (core) + `requirements-extras.txt` (pygments, cairosvg).
- Unified `pptx` CLI (`bin/pptx`) with subcommands: `new`, `render`, `inspect`, `lint`, `diff`, `export`, `themes`, `watch`.
- External theme files (`themes/*.toml`) with `extends` inheritance.
- `brand.toml` loader for project-wide brand override (logo, accent, footer).
- Theme dark/light variants (`--mode`).
- Optional font embedding from theme `font_path`.
- Logo slot + agenda progress strip in slide footer.
- Native editable PPTX charts (column, bar, line, pie) replacing image-based charts.
- Image slide: `fit=cover|contain`, optional rounded mask, caption overlay, **alt text required**.
- Bullet auto-shrink + overflow split.
- New slide kinds: `timeline`, `comparison`, `metric_grid`, `code` (pygments), `agenda`, `pricing`, `before_after`, `video_placeholder`.
- Bundled icon library (Lucide PNGs) + `bullets(icons=[...])` and `icon_grid` slide.
- Markdown frontmatter (theme/brand/author/date), `>` speaker notes, `:::kind` fenced blocks, code fences, `![alt](path "caption")` image syntax.
- Watch mode (`pptx render --watch`) + `--open` to relaunch viewer.
- Line-numbered markdown errors with suggestions; per-kind schema validation.
- `pptx lint`: WCAG AA contrast, text overflow, missing alt-text, inconsistent caps.
- `pptx diff`: structural + textual diff between two `.pptx` files.
- Snapshot tests for every `examples/*.py` deck.
- `pptx export --pdf` (LibreOffice) and `--thumbs` (per-slide PNGs).
- Reveal.js HTML export from same markdown input.
- `pptx new <template>` scaffolder.
- Theme gallery deck + committed theme screenshots.
- Renamed `copilot-prompt.md` → `agent-prompt.md`. Added `examples/README.md` mapping example → use-case → command.

## [0.1.0] — initial

### Added
- `Deck` class + 10 slide methods.
- 13 themes (8 corporate + 5 pitch).
- `markdown_to_pptx.py` converter.
- `inspect_deck.py` structure verifier.
- 10 worked example decks (general business + healthcare).
- 5 markdown templates.
