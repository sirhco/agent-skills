"""Render one slide per theme into a single deck for visual comparison.

Usage:
    python3 examples/theme_gallery.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT))

from helpers.build_deck import Deck
from themes.themes import get_theme, list_themes


def build():
    # use first theme to construct deck; we'll inject per-slide themes inline
    first = list_themes()[0]
    d = Deck(theme=get_theme(first), brand="theme gallery", auto_brand_kit=False)
    d.title("Theme Gallery", "One slide per theme — same content, different palette")

    for name in list_themes():
        theme = get_theme(name)
        d.theme = theme  # swap for next slide
        d.section(name, notes=f"theme: {name}, mode: {theme.get('mode','?')}")
        d.theme = theme
        d.bullets(f"{name} · sample bullets",
                  ["Calibri body, accent rule, branded footer.",
                   "Charts & tables use accent for headers.",
                   "CTA slide uses accent fill."])
        d.theme = theme
        d.metric_grid(f"{name} · KPIs",
                      [("$1.2M", "ARR", "+34%"),
                       ("412", "Customers", "+58"),
                       ("99.97%", "Uptime", ""),
                       ("4.8 / 5", "CSAT", "+0.3")])
        d.theme = theme
        d.cta(f"{name}", sub="Pick this theme with --theme " + name)

    out = "theme_gallery.pptx"
    d.save(out)
    print(f"saved: {out}")


def main():
    build()


if __name__ == "__main__":
    main()
