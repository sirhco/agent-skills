"""Example: seed-stage VC pitch deck.

Style: pitch (electric theme — black + lime).
Audience: VC partner, first meeting.
Length: ~14 slides. Standard YC arc.

Run: python3 pitch_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="pitch_deck.pptx"):
    d = Deck(theme=get_theme("pitch-electric"), brand="Ferro")

    d.title("Ferro", "AI dev tools that ship themselves.")

    d.big_stat("$280B",
               "spent globally on software engineering labor each year.",
               notes="Set TAM context. Not the punchline yet.")

    d.bullets("Problem",
              ["Engineers spend more time reading code than writing it.",
               "Code review is the #1 bottleneck in shipping software.",
               "Existing tools are linters, not reviewers."])

    d.big_stat("47%", "of dev time lost to review queues. Every team. Every week.")

    d.section("Our insight", number=1)

    d.title("LLMs can review code.",
            "Not as gimmick. As primary reviewer. Humans approve.")

    d.bullets("Product",
              ["Auto-review on every PR",
               "Catches bugs, style, security",
               "Integrates GitHub / GitLab / Bitbucket — 90 second setup"])

    d.section("Traction", number=2)

    d.big_stat("$1.2M", "ARR in 4 months. 38 customers. 0 churn.")

    d.chart("ARR growth ($K)",
            ["M1", "M2", "M3", "M4"],
            {"ARR": (180, 420, 780, 1200)})

    d.bullets("Customers",
              ["3 unicorns + 12 Series-B",
               "Net dollar retention: 142%",
               "Enterprise pipeline: $4.8M"])

    d.section("Team", number=3)

    d.two_col("Founders",
              "Chris Olson · CEO",
              ["Ex-staff eng @ {{prior}}",
               "Built {{prior project}}",
               "10y in dev tools"],
              "Co-founder · CTO",
              ["Ex-principal @ {{prior}}",
               "PhD ML systems",
               "Open source: {{project}}"])

    d.section("The ask", number=4)

    d.cta("Raising $8M",
          sub="Seed · 18-month runway · close 2026-06",
          contact="chris@ferro.ai")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
