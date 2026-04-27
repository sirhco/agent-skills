"""Example: company all-hands deck.

Style: corporate (Apple theme — clean, mono + red accent).
Audience: full company.
Length: ~9 slides.

Run: python3 allhands_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="allhands_deck.pptx"):
    d = Deck(theme=get_theme("apple"), brand="Acme · All-Hands · 2026-04")

    d.title("All-Hands", "April 2026 · 2026-04-27")

    d.bullets("Today",
              ["Wins from March",
               "Q2 priorities",
               "New hires + role changes",
               "Open Q&A"])

    d.section("Wins", number=1)

    d.bullets("March highlights",
              ["Shipped billing v2 — on time, on scope",
               "Closed largest deal to date: $1.4M ACV",
               "NPS hit 67 (from 54)",
               "Zero P0 incidents"])

    d.quote("Best month in company history. By every metric we track.",
            attribution="Chris, CEO")

    d.section("Q2 priorities", number=2)

    d.bullets("Three things",
              ["Ship EU region",
               "Launch self-serve",
               "Hire VP Eng + 4 engineers"])

    d.section("People", number=3)

    d.two_col("This month",
              "New hires",
              ["Sarah K · Senior Eng (Platform)",
               "Marco D · Designer (Brand)",
               "Priya R · CSM (Enterprise)"],
              "Role changes",
              ["Alex → EM, Mobile",
               "Jamie → Tech Lead, Data",
               "Tomas → Head of Sales"])

    d.cta("Questions?",
          sub="AMA channel open all week.",
          contact="#all-hands-april")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
