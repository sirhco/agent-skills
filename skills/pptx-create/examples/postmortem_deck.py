"""Example: incident postmortem deck.

Style: corporate (monochrome — no color noise, all attention on facts).
Audience: eng leadership + affected teams.
Length: ~9 slides. Blameless template.

Run: python3 postmortem_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="postmortem_deck.pptx"):
    d = Deck(theme=get_theme("monochrome"), brand="INC-2026-0142 · postmortem")

    d.title("Incident postmortem · INC-2026-0142",
            "Checkout outage · 2026-04-22 · 14:08–14:53 UTC")

    d.table("Summary",
            ["Field", "Value"],
            [["Severity",     "SEV1"],
             ["Duration",     "45 min"],
             ["Users impacted", "~120K (38% of checkout traffic)"],
             ["Revenue impact", "~$48K"],
             ["Root cause",   "Migration locked checkout_orders table"],
             ["Detection",    "Synthetic monitor (4 min after onset)"]])

    d.section("Timeline", number=1)

    d.table("Timeline (UTC)",
            ["Time", "Event"],
            [["14:04", "Migration job started"],
             ["14:08", "Lock contention; checkout reads queue"],
             ["14:12", "Synthetic alert fires"],
             ["14:15", "On-call paged, incident declared"],
             ["14:31", "Migration killed"],
             ["14:42", "Locks cleared, traffic recovers"],
             ["14:53", "Full recovery confirmed"]])

    d.section("Root cause", number=2)

    d.bullets("What happened",
              ["Migration added an index on `checkout_orders`",
               "Ran `CREATE INDEX` (not CONCURRENTLY)",
               "Acquired ACCESS EXCLUSIVE lock on hot table",
               "All checkout reads/writes blocked"])

    d.section("Action items", number=3)

    d.table("Follow-ups",
            ["#", "Action", "Owner", "Due"],
            [["1", "Migrations require CONCURRENTLY for hot tables", "Platform", "2026-05-05"],
             ["2", "Pre-deploy lint blocks non-concurrent index on >1M rows", "DBRE", "2026-05-10"],
             ["3", "Synthetic for checkout end-to-end every 60s", "SRE", "2026-04-30"],
             ["4", "Runbook: how to kill migration safely", "On-call lead", "2026-05-01"]])

    d.quote("We could have caught this in CI. The lint rule existed; it wasn't enforced.",
            attribution="DBRE, in retro")

    d.cta("No blame. Lessons logged.",
          sub="Action items tracked in #incident-followups",
          contact="postmortem doc: bit.ly/inc-2026-0142")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
