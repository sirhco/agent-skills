"""Example: Quarterly Business Review (QBR) deck.

Style: corporate (Stripe theme).
Audience: customer success + customer exec sponsor.
Length: ~12 slides.

Run: python3 qbr_deck.py
Output: qbr_deck.pptx
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptx.enum.chart import XL_CHART_TYPE
from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="qbr_deck.pptx"):
    d = Deck(theme=get_theme("stripe"), brand="Acme · QBR · Q3 2026")

    d.title("Quarterly Business Review",
            "Acme Corp · Q3 2026 · 2026-04-27",
            notes="Welcome. Frame: progress vs goals, what's next.")

    d.bullets("Agenda",
              ["Executive summary",
               "Adoption + usage",
               "Outcomes vs goals",
               "Roadmap preview",
               "Renewal + expansion"])

    d.section("Executive summary", number=1)

    d.two_col("Headlines",
              "Wins",
              ["DAU up 38% QoQ",
               "Time-to-value cut 6d → 2d",
               "3 new teams onboarded"],
              "Watch items",
              ["API error rate trending up",
               "EU data residency open",
               "Two seats unused 60+ days"])

    d.section("Adoption + usage", number=2)

    d.chart("Daily active users",
            ["Wk1", "Wk2", "Wk3", "Wk4", "Wk5", "Wk6", "Wk7", "Wk8",
             "Wk9", "Wk10", "Wk11", "Wk12"],
            {"DAU": (124, 138, 151, 167, 182, 195, 211, 224,
                     238, 251, 268, 284)},
            chart_type=XL_CHART_TYPE.LINE,
            notes="Steady ramp. No regression after 4.2 release.")

    d.table("Usage by team",
            ["Team", "Seats", "DAU", "Top feature"],
            [["Platform", 32, 28, "API access"],
             ["Data", 18, 16, "Notebooks"],
             ["Mobile", 24, 19, "CI integration"],
             ["Growth", 11, 7,  "Reports"]])

    d.section("Outcomes vs goals", number=3)

    d.chart("Goal progress (% of target)",
            ["Adoption", "TTV", "NPS", "Cost savings"],
            {"Target": (100, 100, 100, 100),
             "Actual": (112, 134, 92, 88)},
            notes="Adoption + TTV beat. NPS + cost savings slightly under.")

    d.quote("Cut our incident response time by half. Tooling paid for itself in Q2.",
            attribution="Director of Platform")

    d.section("Roadmap + renewal", number=4)

    d.bullets("Roadmap preview · Q4",
              ["SSO with Okta + Azure AD (GA)",
               "EU data residency (private beta)",
               "Audit log export to S3",
               "Mobile app v2"])

    d.cta("Renewal: 2026-09-30",
          sub="Proposed: +12 seats, +Enterprise tier, multi-year",
          contact="csm@acme.com  ·  ae@acme.com")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
