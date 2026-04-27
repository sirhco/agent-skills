"""Example: product launch deck.

Style: pitch (editorial cream theme).
Audience: customers + press.
Length: ~10 slides.

Run: python3 product_launch_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="product_launch_deck.pptx"):
    d = Deck(theme=get_theme("pitch-editorial"), brand="Acme")

    d.title("Acme Studio", "A new way to design with your team. Out today.")

    d.big_stat("90s", "from blank canvas to shared draft.")

    d.bullets("What's new",
              ["Real-time multiplayer canvas",
               "AI brainstorm partner",
               "Native export to Figma, PDF, deck"])

    d.big_stat("4×", "faster iteration vs. legacy tools (internal benchmark).")

    d.section("Built for teams", number=1)

    d.two_col("Designers",
              "Now",
              ["Brushes, layers, vectors",
               "Live cursor sync",
               "Comment threads"],
              "Soon",
              ["Hand-drawn → vector",
               "Brand kits",
               "Plugin SDK"])

    d.quote("Replaced three tools. Team is shipping in days, not weeks.",
            attribution="Head of Design, Series-B SaaS")

    d.bullets("Pricing",
              ["Free for individuals",
               "$12 / seat / month for teams",
               "Enterprise: custom"])

    d.cta("Try Acme Studio today",
          sub="Free 30-day team trial · no credit card",
          contact="acme.com/studio")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
