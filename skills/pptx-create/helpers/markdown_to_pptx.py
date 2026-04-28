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
# notes block: "> note text"
_BLOCK_NOTE_RE = re.compile(r"^>\s+(.+?)\s*$")
# table row: "| a | b |"
_TBL_RE = re.compile(r"^\|(.+)\|\s*$")
# table separator: "| --- | --- |"
_SEP_RE = re.compile(r"^\|[\s\-:|]+\|\s*$")
# image syntax: ![alt](path "caption")
_IMG_RE = re.compile(r'^!\[(.*?)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)\s*$')
# fenced slide block opener: ":::kind [title]" or ":::kind:arg [title]"
_FENCE_OPEN_RE = re.compile(r"^:::(\w+(?::[^\s]+)?)\s*(.*?)\s*$")
_FENCE_CLOSE_RE = re.compile(r"^:::\s*$")
# code fence: ``` or ```lang
_CODE_FENCE_RE = re.compile(r"^```(\w*)\s*$")


class MarkdownError(ValueError):
    """Parser error with line number."""
    def __init__(self, message, line_no=None, suggestion=None):
        self.line_no = line_no
        self.suggestion = suggestion
        prefix = f"line {line_no}: " if line_no else ""
        full = f"{prefix}{message}"
        if suggestion:
            full += f"\n  suggestion: {suggestion}"
        super().__init__(full)


# Per-kind required field schema for validation.
_KIND_SCHEMAS = {
    "table":     {"requires": "table",    "hint": "add a `| h1 | h2 |` table after the heading"},
    "chart":     {"requires": "chart",    "hint": "add `## categories: a, b, c` and `## series Name: 1, 2, 3`"},
    "two-col":   {"requires": "two_subs", "hint": "add two `## subheading` blocks with `- bullets`"},
    "comparison": {"requires": "table",   "hint": "add a `| feature | a | b |` table with yes/no rows"},
    "image":     {"requires": "image",    "hint": "add `![alt](path \"caption\")` after the heading"},
    "video":     {"requires": "image",    "hint": "add `![alt](poster.png)` for the video poster"},
}


def _new_slide(title="", kind="bullets", arg=None):
    return {
        "kind": kind,
        "title": title,
        "arg": arg,
        "subs": [],
        "body": [],
        "table": [],
        "notes": "",
        "code": None,
        "code_lang": None,
        "image": None,    # dict {alt, path, caption}
    }


def parse_md(md_text):
    """Return list of slide dicts. Raises MarkdownError on schema violations."""
    md_text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)
    lines = md_text.splitlines()
    slides = []
    cur = None
    in_code_fence = False
    code_buf = []
    code_lang = None

    for line_no, raw in enumerate(lines, start=1):
        line = raw.rstrip()

        # code fence handling — capture verbatim into cur["code"]
        cf = _CODE_FENCE_RE.match(line)
        if cf:
            if not in_code_fence:
                in_code_fence = True
                code_lang = cf.group(1) or None
                code_buf = []
            else:
                in_code_fence = False
                if cur is None:
                    raise MarkdownError("code fence outside of any slide", line_no=line_no,
                                        suggestion="add a `# Heading [code]` before the fence")
                cur["code"] = "\n".join(code_buf)
                cur["code_lang"] = code_lang or "text"
                if cur["kind"] == "bullets":
                    cur["kind"] = "code"
            continue
        if in_code_fence:
            code_buf.append(raw)
            continue

        # fenced slide block opener / closer (alternative to # heading [kind])
        fo = _FENCE_OPEN_RE.match(line)
        if fo and not _CODE_FENCE_RE.match(line):
            if cur is not None:
                slides.append(cur)
            kind_raw = fo.group(1).strip()
            title = fo.group(2).strip()
            if ":" in kind_raw:
                kind, arg = kind_raw.split(":", 1)
                kind, arg = kind.strip(), arg.strip()
            else:
                kind, arg = kind_raw, None
            cur = _new_slide(title=title or kind.title(), kind=kind, arg=arg)
            continue
        if _FENCE_CLOSE_RE.match(line):
            if cur is not None:
                slides.append(cur)
                cur = None
            continue

        # heading: open new slide
        m = _HEADING_RE.match(line)
        if m:
            if cur is not None:
                slides.append(cur)
            title = m.group(1).strip()
            kind_raw = (m.group(2) or "bullets").strip()
            if ":" in kind_raw:
                kind, arg = kind_raw.split(":", 1)
                kind, arg = kind.strip(), arg.strip()
            else:
                kind, arg = kind_raw, None
            cur = _new_slide(title=title, kind=kind, arg=arg)
            continue

        # standalone image syntax → synthesize image slide if no current slide
        im = _IMG_RE.match(line)
        if im:
            alt, path, caption = im.group(1), im.group(2), (im.group(3) or "")
            if cur is None:
                cur = _new_slide(title=alt or "Image", kind="image")
                cur["image"] = {"alt": alt, "path": path, "caption": caption}
                slides.append(cur)
                cur = None
            else:
                cur["image"] = {"alt": alt, "path": path, "caption": caption}
                if cur["kind"] == "bullets":
                    cur["kind"] = "image"
            continue

        if cur is None:
            continue

        # block-style speaker note: "> text"
        bn = _BLOCK_NOTE_RE.match(line)
        if bn:
            cur["notes"] = (cur["notes"] + " " + bn.group(1).strip()).strip()
            continue

        # inline notes
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

    if in_code_fence:
        raise MarkdownError("unterminated code fence", suggestion="add closing ``` to balance")
    if cur is not None:
        slides.append(cur)

    _validate_schemas(slides)
    return slides


def _validate_schemas(slides):
    for i, s in enumerate(slides, start=1):
        schema = _KIND_SCHEMAS.get(s["kind"])
        if not schema:
            continue
        req = schema["requires"]
        ok = True
        if req == "table" and len(s["table"]) < 2:
            ok = False
        elif req == "chart":
            has_cats = any(sub.lower().startswith("categories:") for sub, _ in s["subs"])
            has_series = any(sub.lower().startswith("series ") for sub, _ in s["subs"])
            ok = has_cats and has_series
        elif req == "two_subs" and len(s["subs"]) < 2:
            ok = False
        elif req == "image" and not s.get("image"):
            ok = False
        if not ok:
            raise MarkdownError(
                f"slide #{i} '{s['title']}' kind={s['kind']!r} missing required content",
                suggestion=schema["hint"],
            )


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


def build_from_md(md_text, theme_name="corporate", brand="", *, mode=None, brand_kit=None):
    theme = get_theme(theme_name, mode=mode, brand=brand_kit)
    slides = parse_md(md_text)
    d = Deck(theme=theme, brand=brand, brand_kit=brand_kit, auto_brand_kit=False)

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

        elif kind == "image":
            img = s.get("image") or {}
            d.image(title, img.get("path", ""), alt=img.get("alt", ""),
                    caption=img.get("caption", ""), notes=notes)

        elif kind == "video":
            img = s.get("image") or {}
            d.video_placeholder(title, alt=img.get("alt") or title,
                                poster_path=img.get("path"), notes=notes)

        elif kind == "code":
            d.code(title, s.get("code") or _body_text(s),
                   lang=s.get("code_lang") or "text", notes=notes)

        elif kind == "timeline":
            events = []
            for sub, _ in s["subs"]:
                if ":" in sub:
                    date, label = sub.split(":", 1)
                    events.append((date.strip(), label.strip()))
            if events:
                d.timeline(title, events, notes=notes)
            else:
                d.bullets(title, _bullets_from_body(s), notes=notes)

        elif kind == "comparison":
            if len(s["table"]) >= 2:
                d.comparison(title, s["table"][0], s["table"][1:], notes=notes)
            else:
                d.bullets(title, _bullets_from_body(s), notes=notes)

        elif kind == "metric_grid":
            metrics = []
            for sub, _ in s["subs"]:
                # "value | label | delta"
                parts = [p.strip() for p in sub.split("|")]
                while len(parts) < 2:
                    parts.append("")
                metrics.append(tuple(parts[:3]))
            d.metric_grid(title, metrics, notes=notes)

        elif kind == "agenda":
            items = [sub for sub, _ in s["subs"]] or _bullets_from_body(s)
            current = None
            try:
                current = int(s["arg"]) if s["arg"] else None
            except ValueError:
                current = None
            d.agenda(title, items, current=current, notes=notes)

        elif kind == "pricing":
            plans = []
            for sub, items in s["subs"]:
                # "Pro | $49/mo | featured"
                parts = [p.strip() for p in sub.split("|")]
                plan = {
                    "name": parts[0] if parts else "",
                    "price": parts[1] if len(parts) > 1 else "",
                    "period": parts[2] if len(parts) > 2 and parts[2] not in ("featured",) else "",
                    "featured": "featured" in (parts[2:] if len(parts) > 2 else []),
                    "features": items,
                }
                plans.append(plan)
            d.pricing(title, plans, notes=notes)

        elif kind == "before_after":
            before = {"label": "", "body": ""}
            after = {"label": "", "body": ""}
            for sub, items in s["subs"]:
                lc = sub.lower()
                target = before if "before" in lc else after if "after" in lc else None
                if target is None:
                    continue
                target["body"] = "\n".join(items) or sub.split(":", 1)[-1].strip()
                if ":" in sub:
                    target["label"] = sub.split(":", 1)[1].strip()
            d.before_after(title, before, after, notes=notes)

        else:  # bullets default
            bullets = _bullets_from_body(s)
            if not bullets and s["subs"]:
                bullets = [sub[0] for sub in s["subs"]]
            d.bullets(title, bullets or [title], notes=notes)

    return d


def render_markdown_to_pptx(in_path, out_path, *, theme=None, mode=None, brand="", brand_file=None):
    """Programmatic entry. Used by pptx_cli.cmd_render."""
    md = Path(in_path).read_text(encoding="utf-8")
    fm = _parse_frontmatter(md)
    md_body = fm["body"]
    chosen_theme = theme or fm["meta"].get("theme") or "corporate-default"
    chosen_brand = brand or fm["meta"].get("brand", "")
    from helpers.brand_kit import load_brand_kit
    kit = load_brand_kit(brand_file)
    deck = build_from_md(md_body, theme_name=chosen_theme, brand=chosen_brand,
                         mode=mode, brand_kit=kit)
    return deck.save(str(out_path))


_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(md):
    m = _FM_RE.match(md)
    if not m:
        return {"meta": {}, "body": md}
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return {"meta": meta, "body": md[m.end():]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", help="markdown file")
    ap.add_argument("-o", "--out", default="deck.pptx")
    ap.add_argument("-t", "--theme", default="corporate")
    ap.add_argument("--brand", default="")
    ap.add_argument("--list-themes", action="store_true")
    args = ap.parse_args(argv)

    if args.list_themes:
        import json
        print(json.dumps(list_themes(), indent=2))
        return 0

    if not args.input:
        ap.error("input markdown file required")

    out = render_markdown_to_pptx(args.input, args.out, theme=args.theme, brand=args.brand)
    from pptx import Presentation
    import os
    p = Presentation(out)
    print(f"saved: {out}")
    print(f"theme: {args.theme}")
    print(f"slides: {len(p.slides)}")
    print(f"size: {os.path.getsize(out)} bytes")
    return 0


if __name__ == "__main__":
    main()
