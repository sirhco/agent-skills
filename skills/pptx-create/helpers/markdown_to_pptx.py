"""Markdown -> .pptx converter.

Each `# Heading` is a new slide. Optional inline marker `[type]` after the
heading picks slide type: title, section, bullets (default), two-col,
table, chart, quote, stat, cta.

Run:
  python3 markdown_to_pptx.py input.md --theme stripe -o out.pptx
  python3 markdown_to_pptx.py input.md --list-themes

See templates/*.md for full syntax examples.
"""

import argparse
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from helpers.build_deck import Deck
from themes.themes import get_theme, list_themes


# heading detection: "# Title [type]" -> ("Title", "type")
_HEADING_RE = re.compile(r"^#\s+(.+?)(?:\s+\[(\w+(?::[^\]]+)?)\])?\s*$")
# subheading: "## ..."
_SUB_RE = re.compile(r"^##\s+(.+?)\s*$")
# bullet: "- item" or "* item"
_BUL_RE = re.compile(r"^[-*]\s+(.+?)\s*$")
# notes inline: "[notes: text]"
_NOTES_RE = re.compile(r"\[notes:\s*(.+?)\]", re.DOTALL)
# table row: "| a | b |"
_TBL_RE = re.compile(r"^\|(.+)\|\s*$")
# table separator: "| --- | --- |"
_SEP_RE = re.compile(r"^\|[\s\-:|]+\|\s*$")


def parse_md(md_text):
    """Return list of slide dicts."""
    # strip HTML comments first
    md_text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)
    lines = md_text.splitlines()
    slides = []
    cur = None

    for raw in lines:
        line = raw.rstrip()
        m = _HEADING_RE.match(line)
        if m:
            if cur is not None:
                slides.append(cur)
            title = m.group(1).strip()
            kind_raw = (m.group(2) or "bullets").strip()
            # split optional arg "stat: 73%" -> kind=stat, arg="73%"
            if ":" in kind_raw:
                kind, arg = kind_raw.split(":", 1)
                kind, arg = kind.strip(), arg.strip()
            else:
                kind, arg = kind_raw, None
            cur = {
                "kind": kind,
                "title": title,
                "arg": arg,
                "subs": [],          # list of (sub_heading, [bullets])
                "body": [],          # raw body lines
                "table": [],         # list of rows (each list of cells)
                "notes": "",
            }
            continue
        if cur is None:
            continue

        # capture inline notes
        nm = _NOTES_RE.search(line)
        if nm:
            cur["notes"] = (cur["notes"] + " " + nm.group(1).strip()).strip()
            line = _NOTES_RE.sub("", line).rstrip()

        if not line.strip():
            cur["body"].append("")
            continue

        sm = _SUB_RE.match(line)
        if sm:
            cur["subs"].append((sm.group(1).strip(), []))
            cur["body"].append(line)
            continue

        bm = _BUL_RE.match(line)
        if bm:
            txt = bm.group(1).strip()
            if cur["subs"]:
                cur["subs"][-1][1].append(txt)
            cur["body"].append(line)
            continue

        if _SEP_RE.match(line):
            continue
        tm = _TBL_RE.match(line)
        if tm:
            row = [c.strip() for c in tm.group(1).split("|")]
            cur["table"].append(row)
            continue

        cur["body"].append(line)

    if cur is not None:
        slides.append(cur)
    return slides


def _bullets_from_body(slide):
    out = []
    for ln in slide["body"]:
        bm = _BUL_RE.match(ln)
        if bm:
            out.append(bm.group(1).strip())
    return out


def _body_text(slide):
    """Body minus headings and bullets — used for stat caption etc."""
    out = []
    for ln in slide["body"]:
        if not ln.strip():
            continue
        if _SUB_RE.match(ln) or _BUL_RE.match(ln):
            continue
        out.append(ln.strip())
    return " ".join(out).strip()


def _kv_subs(slide):
    """Pull `## key: value` style subs into dict."""
    out = {}
    for sub, _ in slide["subs"]:
        if ":" in sub:
            k, v = sub.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def _chart_from_subs(slide):
    """Parse `## categories: a, b, c` and `## series Name: 1, 2, 3`."""
    cats = []
    series = {}
    for sub, _ in slide["subs"]:
        if sub.lower().startswith("categories:"):
            cats = [c.strip() for c in sub.split(":", 1)[1].split(",")]
        elif sub.lower().startswith("series "):
            head, vals = sub.split(":", 1)
            name = head[len("series "):].strip()
            try:
                series[name] = tuple(float(x.strip()) for x in vals.split(","))
            except ValueError:
                series[name] = tuple(x.strip() for x in vals.split(","))
    return cats, series


def build_from_md(md_text, theme_name="corporate", brand=""):
    theme = get_theme(theme_name)
    slides = parse_md(md_text)
    d = Deck(theme=theme, brand=brand)

    for s in slides:
        kind = s["kind"]
        title = s["title"]
        notes = s["notes"]

        if kind == "title":
            sub = s["subs"][0][0] if s["subs"] else ""
            d.title(title, sub, notes=notes)

        elif kind == "section":
            d.section(title, notes=notes)

        elif kind == "stat":
            stat = s["arg"] or title
            caption = _body_text(s) or title
            d.big_stat(stat, caption, notes=notes)

        elif kind == "two-col":
            if len(s["subs"]) >= 2:
                lh, li = s["subs"][0]
                rh, ri = s["subs"][1]
                d.two_col(title, lh, li, rh, ri, notes=notes)
            else:
                d.bullets(title, _bullets_from_body(s), notes=notes)

        elif kind == "table":
            if len(s["table"]) >= 2:
                headers = s["table"][0]
                rows = s["table"][1:]
                d.table(title, headers, rows, notes=notes)
            else:
                d.bullets(title, _bullets_from_body(s), notes=notes)

        elif kind == "chart":
            cats, series = _chart_from_subs(s)
            if cats and series:
                d.chart(title, cats, series, notes=notes)
            else:
                d.bullets(title, _bullets_from_body(s), notes=notes)

        elif kind == "quote":
            kv = _kv_subs(s)
            d.quote(title, attribution=kv.get("attribution", ""), notes=notes)

        elif kind == "cta":
            kv = _kv_subs(s)
            d.cta(title, sub=kv.get("sub", ""),
                  contact=kv.get("contact", ""), notes=notes)

        else:  # bullets default
            bullets = _bullets_from_body(s)
            if not bullets and s["subs"]:
                bullets = [sub[0] for sub in s["subs"]]
            d.bullets(title, bullets or [title], notes=notes)

    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", help="markdown file")
    ap.add_argument("-o", "--out", default="deck.pptx")
    ap.add_argument("-t", "--theme", default="corporate")
    ap.add_argument("--brand", default="")
    ap.add_argument("--list-themes", action="store_true")
    args = ap.parse_args()

    if args.list_themes:
        import json
        print(json.dumps(list_themes(), indent=2))
        return

    if not args.input:
        ap.error("input markdown file required")

    md = Path(args.input).read_text()
    deck = build_from_md(md, theme_name=args.theme, brand=args.brand)
    out = deck.save(args.out)

    from pptx import Presentation
    import os
    p = Presentation(out)
    print(f"saved: {out}")
    print(f"theme: {args.theme}")
    print(f"slides: {len(p.slides)}")
    print(f"size: {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
