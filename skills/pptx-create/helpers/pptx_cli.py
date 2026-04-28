"""Unified pptx CLI. Subcommands route to dedicated helpers.

Usage:
    pptx new <template> [--theme THEME] [-o PATH]
    pptx render <input.md> [--theme THEME] [-o PATH] [--watch] [--open] [--mode MODE]
    pptx inspect <deck.pptx> [--notes] [--json]
    pptx lint <deck.pptx> [--strict] [--json]
    pptx diff <a.pptx> <b.pptx> [--json]
    pptx export <deck.pptx> [--pdf] [--thumbs DIR] [--reveal DIR]
    pptx themes
    pptx version

Run `pptx <cmd> --help` for per-subcommand flags.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ---------- subcommands ----------

def cmd_version(args: argparse.Namespace) -> int:
    from helpers.build_deck import __version__
    print(f"pptx-create {__version__}")
    return 0


def cmd_themes(args: argparse.Namespace) -> int:
    from themes.themes import list_themes, get_theme
    for name in list_themes():
        t = get_theme(name)
        mode = t.get("mode", "corporate")
        accent = t.get("accent")
        try:
            accent_hex = "#" + str(accent).upper()
        except Exception:
            accent_hex = ""
        print(f"  {name:24s} {mode:10s} {accent_hex}")
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    template_dir = _ROOT / "templates"
    src = template_dir / f"{args.template}.md"
    if not src.is_file():
        avail = ", ".join(sorted(p.stem for p in template_dir.glob("*.md")))
        print(f"error: template '{args.template}' not found. available: {avail}", file=sys.stderr)
        return 1
    dst = Path(args.output) if args.output else Path.cwd() / f"{args.template}.md"
    if dst.exists() and not args.force:
        print(f"error: {dst} exists. use --force to overwrite.", file=sys.stderr)
        return 1
    text = src.read_text(encoding="utf-8")
    if args.theme and not text.lstrip().startswith("---"):
        # inject frontmatter
        text = f"---\ntheme: {args.theme}\n---\n\n{text}"
    elif args.theme:
        # crude: insert theme line under existing frontmatter
        text = text.replace("---\n", f"---\ntheme: {args.theme}\n", 1)
    dst.write_text(text, encoding="utf-8")
    print(f"+ {dst}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    from helpers.markdown_to_pptx import render_markdown_to_pptx

    in_path = Path(args.input)
    if not in_path.is_file():
        print(f"error: input not found: {in_path}", file=sys.stderr)
        return 1
    out_path = Path(args.output) if args.output else in_path.with_suffix(".pptx")

    brand_file = getattr(args, "brand_file", None)

    def build_once() -> int:
        try:
            render_markdown_to_pptx(
                in_path,
                out_path,
                theme=args.theme,
                mode=args.mode,
                brand=args.brand,
                brand_file=brand_file,
            )
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(f"+ {out_path}")
        if args.open:
            _open_in_viewer(out_path)
        return 0

    if not args.watch:
        return build_once()

    rc = build_once()
    print(f"watching {in_path} ... ctrl-c to stop")
    last_mtime = in_path.stat().st_mtime
    try:
        import time
        while True:
            time.sleep(0.5)
            try:
                m = in_path.stat().st_mtime
            except FileNotFoundError:
                continue
            if m > last_mtime:
                last_mtime = m
                print(f"~ change detected, rebuilding")
                build_once()
    except KeyboardInterrupt:
        print("\nstopped.")
    return rc


def cmd_inspect(args: argparse.Namespace) -> int:
    from helpers import inspect_deck
    argv = [args.deck]
    if args.notes:
        argv.append("--notes")
    if args.json:
        argv.append("--json")
    return inspect_deck.main(argv)


def cmd_lint(args: argparse.Namespace) -> int:
    from helpers.lint_deck import lint
    issues = lint(Path(args.deck))
    if args.json:
        print(json.dumps([i.to_dict() for i in issues], indent=2))
    else:
        if not issues:
            print("clean — no issues.")
        for i in issues:
            print(f"{i.severity:7s} slide {i.slide:>3} {i.code}: {i.message}")
    err_count = sum(1 for i in issues if i.severity == "error")
    if err_count or (args.strict and issues):
        return 1
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    from helpers.diff_deck import diff
    result = diff(Path(args.a), Path(args.b))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for line in result.get("text", []):
            print(line)
    return 0 if not result.get("differs") else 1


def cmd_reveal(args: argparse.Namespace) -> int:
    from helpers.markdown_to_reveal import render_markdown_to_reveal
    in_path = Path(args.input)
    if not in_path.is_file():
        print(f"error: input not found: {in_path}", file=sys.stderr)
        return 1
    out_dir = Path(args.output) if args.output else in_path.with_suffix("")
    render_markdown_to_reveal(in_path, out_dir, theme=args.theme, brand=args.brand or "")
    print(f"+ {out_dir / 'index.html'}")
    if args.open:
        _open_in_viewer(out_dir / "index.html")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    from helpers.export_deck import export_pdf, export_thumbs, export_reveal
    deck = Path(args.deck)
    rc = 0
    if args.pdf:
        out = Path(args.pdf) if isinstance(args.pdf, str) else deck.with_suffix(".pdf")
        rc |= export_pdf(deck, out)
    if args.thumbs:
        rc |= export_thumbs(deck, Path(args.thumbs))
    if args.reveal:
        rc |= export_reveal(deck, Path(args.reveal))
    if not (args.pdf or args.thumbs or args.reveal):
        print("error: pass --pdf, --thumbs DIR, or --reveal DIR.", file=sys.stderr)
        return 1
    return rc


# ---------- helpers ----------

def _open_in_viewer(path: Path) -> None:
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        elif os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception as e:
        print(f"  warn: could not open viewer: {e}", file=sys.stderr)


# ---------- argparse ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pptx", description="pptx-create CLI.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("new", help="scaffold starter md from a template")
    sp.add_argument("template", help="template name (qbr, sales, pitch, allhands, postmortem)")
    sp.add_argument("-o", "--output", help="output path (default: ./<template>.md)")
    sp.add_argument("--theme", help="inject theme into frontmatter")
    sp.add_argument("--force", action="store_true", help="overwrite existing file")
    sp.set_defaults(func=cmd_new)

    sp = sub.add_parser("render", help="markdown -> pptx")
    sp.add_argument("input", help="input markdown file")
    sp.add_argument("-o", "--output", help="output pptx path")
    sp.add_argument("--theme", help="theme name")
    sp.add_argument("--mode", choices=["light", "dark"], help="theme mode")
    sp.add_argument("--brand", help="brand string (footer left)")
    sp.add_argument("--brand-file", help="path to brand.toml (default: ./brand.toml if present)")
    sp.add_argument("--watch", action="store_true", help="rebuild on file change")
    sp.add_argument("--open", action="store_true", help="open in default app after build")
    sp.set_defaults(func=cmd_render)

    sp = sub.add_parser("inspect", help="dump deck structure")
    sp.add_argument("deck")
    sp.add_argument("--notes", action="store_true")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_inspect)

    sp = sub.add_parser("lint", help="WCAG / overflow / alt-text checks")
    sp.add_argument("deck")
    sp.add_argument("--strict", action="store_true", help="fail on warnings too")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_lint)

    sp = sub.add_parser("diff", help="structural+textual diff between two decks")
    sp.add_argument("a")
    sp.add_argument("b")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_diff)

    sp = sub.add_parser("export", help="pdf / thumbnails / reveal.js")
    sp.add_argument("deck")
    sp.add_argument("--pdf", nargs="?", const=True, default=False, help="export PDF (optional path)")
    sp.add_argument("--thumbs", help="dir for per-slide PNG thumbs")
    sp.add_argument("--reveal", help="dir for reveal.js html bundle")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("reveal", help="markdown -> reveal.js HTML (full fidelity)")
    sp.add_argument("input", help="input markdown file")
    sp.add_argument("-o", "--output", help="output directory (default: <input-stem>/)")
    sp.add_argument("--theme", help="theme name")
    sp.add_argument("--brand", help="brand string")
    sp.add_argument("--open", action="store_true", help="open index.html after build")
    sp.set_defaults(func=cmd_reveal)

    sp = sub.add_parser("themes", help="list available themes")
    sp.set_defaults(func=cmd_themes)

    sp = sub.add_parser("version", help="print version")
    sp.set_defaults(func=cmd_version)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
