"""Markdown → Reveal.js HTML, full fidelity.

Same parser as markdown_to_pptx (parse_md), so all slide kinds work:
title, section, bullets, two-col, big_stat (stat), quote, cta,
table, chart (chart.js), code (highlight.js), agenda, pricing,
comparison, timeline, metric_grid, before_after, image, video.

Output: a directory containing index.html + assets/ (copied images).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from html import escape
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from helpers.markdown_to_pptx import parse_md, _bullets_from_body, _kv_subs, _chart_from_subs, _parse_frontmatter
from themes.themes import get_theme


# ---------- per-kind renderers ----------

def _esc(s: str) -> str:
    return escape(s or "", quote=True)


def _section_title(s):
    return f'<section data-background-color="{{bg}}"><h1>{_esc(s["title"])}</h1>{_subtitle(s)}</section>'


def _subtitle(s):
    if s["subs"]:
        return f'<h3 class="subtitle">{_esc(s["subs"][0][0])}</h3>'
    return ""


def _section_section(s):
    return f'<section class="divider" data-background-color="{{accent}}"><h1>{_esc(s["title"])}</h1></section>'


def _section_bullets(s):
    bullets = _bullets_from_body(s) or [s["title"]]
    items = "".join(f"<li>{_esc(b)}</li>" for b in bullets)
    return f'<section><h2>{_esc(s["title"])}</h2><ul>{items}</ul></section>'


def _section_two_col(s):
    if len(s["subs"]) < 2:
        return _section_bullets(s)
    (lh, li), (rh, ri) = s["subs"][0], s["subs"][1]
    left = "".join(f"<li>{_esc(b)}</li>" for b in li)
    right = "".join(f"<li>{_esc(b)}</li>" for b in ri)
    return (f'<section><h2>{_esc(s["title"])}</h2>'
            f'<div class="two-col">'
            f'<div><h3>{_esc(lh)}</h3><ul>{left}</ul></div>'
            f'<div><h3>{_esc(rh)}</h3><ul>{right}</ul></div>'
            f'</div></section>')


def _section_stat(s):
    stat = s["arg"] or s["title"]
    caption = " ".join(b for b in s["body"] if b.strip()) or s["title"]
    return (f'<section class="big-stat" data-background-color="{{bg}}">'
            f'<div class="stat">{_esc(stat)}</div>'
            f'<div class="caption">{_esc(caption)}</div></section>')


def _section_quote(s):
    kv = _kv_subs(s)
    attrib = kv.get("attribution", "")
    return (f'<section><blockquote>“{_esc(s["title"])}”</blockquote>'
            f'{(f"<p class=attrib>— {_esc(attrib)}</p>" if attrib else "")}</section>')


def _section_cta(s):
    kv = _kv_subs(s)
    sub = kv.get("sub", "")
    contact = kv.get("contact", "")
    return (f'<section class="cta" data-background-color="{{accent}}">'
            f'<h1>{_esc(s["title"])}</h1>'
            f'{(f"<p>{_esc(sub)}</p>" if sub else "")}'
            f'{(f"<p class=contact>{_esc(contact)}</p>" if contact else "")}'
            f'</section>')


def _section_table(s):
    if len(s["table"]) < 2:
        return _section_bullets(s)
    headers, rows = s["table"][0], s["table"][1:]
    th = "".join(f"<th>{_esc(c)}</th>" for c in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in row) + "</tr>"
        for row in rows
    )
    return (f'<section><h2>{_esc(s["title"])}</h2>'
            f'<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></section>')


def _section_comparison(s):
    if len(s["table"]) < 2:
        return _section_bullets(s)
    headers, rows = s["table"][0], s["table"][1:]
    th = "".join(f"<th>{_esc(c)}</th>" for c in headers)
    body_rows = []
    for row in rows:
        cells = []
        for ci, val in enumerate(row):
            v = str(val).strip().lower()
            if ci > 0 and v in ("yes", "true", "y", "✓", "1"):
                cells.append('<td class="yes">✓</td>')
            elif ci > 0 and v in ("no", "false", "n", "✗", "0", "—", "-"):
                cells.append('<td class="no">—</td>')
            else:
                cells.append(f"<td>{_esc(val)}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<section><h2>{_esc(s["title"])}</h2>'
            f'<table class="comparison"><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(body_rows)}</tbody></table></section>')


def _section_chart(s, idx):
    cats, series = _chart_from_subs(s)
    if not cats or not series:
        return _section_bullets(s)
    datasets = [{"label": name, "data": list(values)} for name, values in series.items()]
    config = {
        "type": "bar" if s["arg"] in (None, "column") else s["arg"],
        "data": {"labels": cats, "datasets": datasets},
        "options": {"responsive": True, "maintainAspectRatio": False},
    }
    return (f'<section><h2>{_esc(s["title"])}</h2>'
            f'<div class="chart-wrap"><canvas data-chart-config=\'{escape(json.dumps(config))}\' id="chart-{idx}"></canvas></div></section>')


def _section_code(s):
    code = s.get("code") or "\n".join(s["body"])
    lang = s.get("code_lang") or "text"
    return (f'<section><h2>{_esc(s["title"])}</h2>'
            f'<pre><code class="language-{_esc(lang)}">{_esc(code)}</code></pre></section>')


def _section_agenda(s):
    items = [sub for sub, _ in s["subs"]] or _bullets_from_body(s)
    try:
        current = int(s["arg"]) if s["arg"] else None
    except ValueError:
        current = None
    rendered = []
    for i, item in enumerate(items):
        cls = "current" if i == current else ""
        rendered.append(f'<li class="{cls}"><span class="num">{i+1:02d}</span> {_esc(item)}</li>')
    return f'<section><h2>{_esc(s["title"])}</h2><ol class="agenda">{"".join(rendered)}</ol></section>'


def _section_pricing(s):
    cards = []
    for sub, items in s["subs"]:
        parts = [p.strip() for p in sub.split("|")]
        name = parts[0] if parts else ""
        price = parts[1] if len(parts) > 1 else ""
        period = parts[2] if len(parts) > 2 and parts[2] != "featured" else ""
        featured = "featured" in parts[2:]
        feat_html = "".join(f"<li>{_esc(f)}</li>" for f in items)
        klass = "card featured" if featured else "card"
        cards.append(
            f'<div class="{klass}"><h3>{_esc(name)}</h3>'
            f'<div class="price">{_esc(price)}</div>'
            f'<div class="period">{_esc(period)}</div>'
            f'<ul>{feat_html}</ul></div>'
        )
    return f'<section><h2>{_esc(s["title"])}</h2><div class="pricing">{"".join(cards)}</div></section>'


def _section_metric_grid(s):
    tiles = []
    for sub, _ in s["subs"]:
        parts = [p.strip() for p in sub.split("|")]
        while len(parts) < 3:
            parts.append("")
        value, label, delta = parts[:3]
        delta_html = ""
        if delta:
            cls = "delta-pos" if delta.startswith("+") else "delta-neg"
            delta_html = f'<div class="{cls}">{_esc(delta)}</div>'
        tiles.append(
            f'<div class="metric"><div class="value">{_esc(value)}</div>'
            f'<div class="label">{_esc(label)}</div>{delta_html}</div>'
        )
    return f'<section><h2>{_esc(s["title"])}</h2><div class="metric-grid">{"".join(tiles)}</div></section>'


def _section_timeline(s):
    events = []
    for sub, _ in s["subs"]:
        if ":" in sub:
            d, lbl = sub.split(":", 1)
            events.append((d.strip(), lbl.strip()))
    if not events:
        return _section_bullets(s)
    items = "".join(
        f'<li><span class="date">{_esc(d)}</span><span class="label">{_esc(lbl)}</span></li>'
        for d, lbl in events
    )
    return f'<section><h2>{_esc(s["title"])}</h2><ol class="timeline">{items}</ol></section>'


def _section_image(s, asset_dir, src_dir):
    img = s.get("image") or {}
    alt = img.get("alt", "")
    src = img.get("path", "")
    caption = img.get("caption", "")
    asset_rel = _copy_asset(src, src_dir, asset_dir) if src else ""
    if not asset_rel:
        return f'<section><h2>{_esc(s["title"])}</h2><p>[image not found: {_esc(src)}]</p></section>'
    cap_html = f'<figcaption>{_esc(caption)}</figcaption>' if caption else ''
    return (f'<section><h2>{_esc(s["title"])}</h2>'
            f'<figure><img src="{_esc(asset_rel)}" alt="{_esc(alt)}">{cap_html}</figure></section>')


def _section_video(s, asset_dir, src_dir):
    img = s.get("image") or {}
    poster_src = img.get("path", "")
    alt = img.get("alt") or s["title"]
    poster_rel = _copy_asset(poster_src, src_dir, asset_dir) if poster_src else ""
    return (f'<section><h2>{_esc(s["title"])}</h2>'
            f'<div class="video-frame"' + (f' style="background-image:url({_esc(poster_rel)})"' if poster_rel else '') + '>'
            f'<div class="play">▶</div></div>'
            f'<p class="caption">{_esc(alt)}</p></section>')


def _section_before_after(s):
    before = {"label": "", "body": ""}
    after = {"label": "", "body": ""}
    for sub, items in s["subs"]:
        lc = sub.lower()
        target = before if "before" in lc else after if "after" in lc else None
        if not target:
            continue
        target["body"] = "\n".join(items) or sub.split(":", 1)[-1].strip()
        if ":" in sub:
            target["label"] = sub.split(":", 1)[1].strip()
    return (f'<section><h2>{_esc(s["title"])}</h2>'
            f'<div class="ba"><div class="before"><h3>BEFORE</h3>'
            f'<p>{_esc(before["body"])}</p>'
            f'{(f"<small>{_esc(before['label'])}</small>" if before["label"] else "")}</div>'
            f'<div class="after"><h3>AFTER</h3>'
            f'<p>{_esc(after["body"])}</p>'
            f'{(f"<small>{_esc(after['label'])}</small>" if after["label"] else "")}</div></div></section>')


def _copy_asset(src: str, src_dir: Path, asset_dir: Path) -> str:
    if not src:
        return ""
    p = (src_dir / src).resolve() if not Path(src).is_absolute() else Path(src)
    if not p.is_file():
        # try as-is
        p2 = Path(src)
        if not p2.is_file():
            return ""
        p = p2
    asset_dir.mkdir(parents=True, exist_ok=True)
    dst = asset_dir / p.name
    shutil.copy2(p, dst)
    return f"assets/{p.name}"


# ---------- master render ----------

def render_markdown_to_reveal(in_path: Path, out_dir: Path, *, theme=None, brand=""):
    md_text = in_path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(md_text)
    md_body = fm["body"]
    theme_name = theme or fm["meta"].get("theme") or "corporate-default"
    chosen_brand = brand or fm["meta"].get("brand", "")

    slides = parse_md(md_body)
    asset_dir = out_dir / "assets"
    src_dir = in_path.resolve().parent

    sections = []
    for i, s in enumerate(slides):
        kind = s["kind"]
        if kind == "title":
            sections.append(_section_title(s))
        elif kind == "section":
            sections.append(_section_section(s))
        elif kind == "two-col":
            sections.append(_section_two_col(s))
        elif kind == "stat":
            sections.append(_section_stat(s))
        elif kind == "quote":
            sections.append(_section_quote(s))
        elif kind == "cta":
            sections.append(_section_cta(s))
        elif kind == "table":
            sections.append(_section_table(s))
        elif kind == "chart":
            sections.append(_section_chart(s, i))
        elif kind == "comparison":
            sections.append(_section_comparison(s))
        elif kind == "code":
            sections.append(_section_code(s))
        elif kind == "agenda":
            sections.append(_section_agenda(s))
        elif kind == "pricing":
            sections.append(_section_pricing(s))
        elif kind == "metric_grid":
            sections.append(_section_metric_grid(s))
        elif kind == "timeline":
            sections.append(_section_timeline(s))
        elif kind == "before_after":
            sections.append(_section_before_after(s))
        elif kind == "image":
            sections.append(_section_image(s, asset_dir, src_dir))
        elif kind == "video":
            sections.append(_section_video(s, asset_dir, src_dir))
        else:
            sections.append(_section_bullets(s))

        # speaker notes
        if s.get("notes"):
            sections[-1] = sections[-1].replace(
                "</section>",
                f'<aside class="notes">{_esc(s["notes"])}</aside></section>',
                1,
            )

    theme_dict = get_theme(theme_name)
    bg = "#" + str(theme_dict.get("bg", "")).upper()
    accent = "#" + str(theme_dict.get("accent", "")).upper()
    ink = "#" + str(theme_dict.get("ink", "")).upper()
    muted = "#" + str(theme_dict.get("muted", "")).upper()
    accent2 = "#" + str(theme_dict.get("accent2", "")).upper()

    body = "\n".join(s.format(bg=bg, accent=accent) for s in sections)

    html = TEMPLATE.format(
        title=_esc(in_path.stem),
        brand=_esc(chosen_brand),
        bg=bg, accent=accent, ink=ink, muted=muted, accent2=accent2,
        sections=body,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    return out_dir / "index.html"


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reset.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11/styles/github.min.css">
<style>
  :root {{ --bg: {bg}; --accent: {accent}; --ink: {ink}; --muted: {muted}; --accent2: {accent2}; }}
  .reveal {{ background: var(--bg); color: var(--ink); font-family: 'Inter','Calibri',sans-serif; }}
  .reveal h1, .reveal h2, .reveal h3 {{ color: var(--ink); text-transform: none; }}
  .reveal h2 {{ border-bottom: 4px solid var(--accent); padding-bottom: 0.2em; display: inline-block; }}
  .reveal section.divider {{ color: #fff; }}
  .reveal section.divider h1 {{ color: #fff; font-size: 3em; }}
  .reveal section.cta h1 {{ color: #fff; font-size: 3em; }}
  .reveal section.cta {{ color: #fff; }}
  .reveal blockquote {{ border-left: 4px solid var(--accent); padding-left: 1em; }}
  .reveal table {{ width: 100%; border-collapse: collapse; }}
  .reveal th {{ background: var(--accent); color: var(--bg); padding: 0.5em; text-align: left; }}
  .reveal td {{ border-bottom: 1px solid var(--accent2); padding: 0.4em 0.6em; }}
  .reveal td.yes {{ color: var(--accent); font-weight: bold; }}
  .reveal td.no  {{ color: var(--muted); }}
  .reveal .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; }}
  .reveal .big-stat .stat {{ font-size: 8em; font-weight: 800; color: var(--accent); line-height: 1; }}
  .reveal .big-stat .caption {{ font-size: 1.1em; color: var(--muted); margin-top: 1em; }}
  .reveal .metric-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1em; }}
  .reveal .metric {{ background: var(--accent2); padding: 1em; border-radius: 8px; }}
  .reveal .metric .value {{ font-size: 3em; font-weight: 700; color: var(--accent); }}
  .reveal .metric .label {{ color: var(--ink); }}
  .reveal .metric .delta-pos {{ color: var(--accent); }}
  .reveal .metric .delta-neg {{ color: var(--muted); }}
  .reveal .pricing {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap: 1em; }}
  .reveal .pricing .card {{ background: var(--accent2); padding: 1em; border-radius: 8px; }}
  .reveal .pricing .card.featured {{ background: var(--accent); color: var(--bg); }}
  .reveal .pricing .price {{ font-size: 2em; font-weight: 700; }}
  .reveal .agenda {{ list-style: none; counter-reset: item; }}
  .reveal .agenda li {{ font-size: 1.4em; margin: 0.3em 0; color: var(--muted); }}
  .reveal .agenda li.current {{ color: var(--ink); font-weight: 700; }}
  .reveal .agenda .num {{ color: var(--accent); margin-right: 0.5em; font-weight: 700; }}
  .reveal .timeline {{ list-style: none; padding: 0; }}
  .reveal .timeline li {{ display: flex; gap: 1em; padding: 0.4em 0; border-left: 3px solid var(--accent); padding-left: 1em; }}
  .reveal .timeline .date {{ color: var(--muted); min-width: 6em; }}
  .reveal .ba {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1em; }}
  .reveal .ba .before {{ background: var(--accent2); padding: 1em; }}
  .reveal .ba .after {{ background: var(--accent); color: var(--bg); padding: 1em; }}
  .reveal .video-frame {{ width: 100%; aspect-ratio: 16/9; background: var(--accent2); display: flex; align-items: center; justify-content: center; background-size: cover; background-position: center; }}
  .reveal .video-frame .play {{ font-size: 6em; color: var(--accent); }}
  .reveal .chart-wrap {{ height: 60vh; }}
  .reveal .subtitle {{ color: var(--muted); }}
  .reveal pre code {{ font-size: 0.7em; }}
  .reveal small {{ color: var(--muted); }}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
{sections}
</div></div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/highlight/highlight.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/notes/notes.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script>
Reveal.initialize({{
  hash: true,
  plugins: [ RevealHighlight, RevealNotes ]
}});
Reveal.on('ready', () => {{
  document.querySelectorAll('canvas[data-chart-config]').forEach(c => {{
    const cfg = JSON.parse(c.getAttribute('data-chart-config'));
    new Chart(c.getContext('2d'), cfg);
  }});
}});
</script>
</body>
</html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(prog="markdown_to_reveal")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="reveal_out", help="output directory")
    ap.add_argument("--theme", default=None)
    ap.add_argument("--brand", default="")
    args = ap.parse_args(argv)

    out = render_markdown_to_reveal(Path(args.input), Path(args.output),
                                    theme=args.theme, brand=args.brand)
    print(f"+ {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
