"""Example: outbound sales deck.

Style: corporate (Linear theme — dark, sharp).
Audience: prospect, first sales meeting.
Length: ~10 slides. Sales-narrative arc: pain -> insight -> product -> proof -> ask.

Run: python3 sales_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="sales_deck.pptx"):
    d = Deck(theme=get_theme("linear"), brand="Ferro for {{Prospect}}")

    d.title("Ship faster. Review smarter.",
            "Ferro · prepared for {{Prospect}} · 2026-04-27")

    d.big_stat("47%", "of dev time spent on code review and waiting on review.")

    d.bullets("The pain you're feeling",
              ["Review queues stall releases",
               "Reviewers context-switch every 12 minutes",
               "Bugs slip past tired eyes at 4pm"])

    d.section("What we do", number=1)

    d.two_col("How Ferro works",
              "Today",
              ["Manual review",
               "Slack pings + reminders",
               "Bugs caught in QA or prod"],
              "With Ferro",
              ["AI pre-review on every PR",
               "Auto-prioritized queue",
               "Bugs caught before reviewer reads"])

    d.bullets("What you get",
              ["Reviews 3.4× faster (median)",
               "60% fewer regressions in first 90 days",
               "Zero-config — works with GitHub, GitLab, Bitbucket",
               "SOC 2 Type II, SSO, data residency"])

    d.section("Proof", number=2)

    d.quote("We cut PR cycle time from 18 hours to 5. We don't ship without it.",
            attribution="VP Engineering, Series-C fintech")

    d.table("Customer outcomes",
            ["Customer", "Team size", "Cycle time ↓", "Bugs ↓"],
            [["Stripe-like fintech", 220, "72%", "61%"],
             ["DTC retail",          85, "58%", "44%"],
             ["B2B SaaS",            42, "65%", "52%"]])

    d.section("Investment", number=3)

    d.bullets("Pricing for {{Prospect}}",
              ["$24 / dev / month",
               "Annual commit, billed quarterly",
               "Pilot: 30 days, full access, no charge"])

    d.cta("Next step: 30-day pilot",
          sub="Connect your repo. See results in week 1.",
          contact="ae@ferro.ai · calendly.com/ferro-pilot")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
