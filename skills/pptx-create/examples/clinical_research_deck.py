"""Example: clinical research readout deck.

Audience: PI, co-investigators, sponsor, IRB.
Style: corporate (healthcare theme — teal, soft warm).
Length: ~14 slides. Standard CONSORT-aligned structure.

Run: python3 clinical_research_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptx.enum.chart import XL_CHART_TYPE
from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="clinical_research_deck.pptx"):
    d = Deck(theme=get_theme("healthcare"),
             brand="STUDY-2026-0142 · Sponsor: NIH R01")

    d.title("Phase II RCT readout: Drug X vs standard of care",
            "Acute kidney injury in post-cardiac-surgery patients · "
            "ClinicalTrials.gov NCT0XXXXXXX",
            notes="Frame: primary endpoint met. Safety profile clean. "
                  "Discussion focuses on subgroup signals.")

    d.bullets("Agenda",
              ["Background + hypothesis",
               "Trial design + CONSORT flow",
               "Baseline characteristics",
               "Primary + secondary endpoints",
               "Safety + adverse events",
               "Subgroup analyses",
               "Limitations + next steps"])

    d.section("Background + hypothesis", number=1)

    d.bullets("Clinical question",
              ["AKI occurs in 25–30% of post-CPB patients",
               "Current SOC: supportive care, no targeted intervention",
               "Drug X mechanism: blocks ischemia-reperfusion cascade",
               "Hypothesis: 30% relative reduction in stage-2+ AKI by POD7"])

    d.section("Trial design", number=2)

    d.table("Design summary",
            ["Element", "Value"],
            [["Design",        "Multicenter, double-blind, placebo-controlled RCT"],
             ["Sites",         "12 academic centers, US + EU"],
             ["Enrollment",    "n=420 randomized (1:1)"],
             ["Primary EP",    "Stage 2+ AKI by KDIGO, POD0–POD7"],
             ["Secondary EPs", "Mortality 30d/90d, RRT initiation, LOS"],
             ["Power",         "85% to detect 30% RRR, alpha 0.05"]])

    d.bullets("CONSORT flow",
              ["Assessed for eligibility: n=612",
               "Excluded (n=192): ineligible 134, declined 58",
               "Randomized: n=420 → Drug X 210, placebo 210",
               "Lost to follow-up: 4 vs 6",
               "Analyzed (mITT): n=206 vs n=204"])

    d.section("Baseline characteristics", number=3)

    d.table("Baseline (mITT, n=410)",
            ["Variable",          "Drug X (n=206)", "Placebo (n=204)"],
            [["Age, mean (SD)",    "67.4 (9.8)",    "66.9 (10.2)"],
             ["Female, n (%)",     "78 (37.9)",     "82 (40.2)"],
             ["eGFR, mean (SD)",   "62.1 (14.3)",   "61.7 (15.0)"],
             ["Diabetes, n (%)",   "94 (45.6)",     "97 (47.5)"],
             ["EF <40%, n (%)",    "41 (19.9)",     "38 (18.6)"],
             ["CPB time, min",     "112 (28)",      "115 (31)"]])

    d.section("Endpoints", number=4)

    d.chart("Primary endpoint: stage 2+ AKI by POD7 (%)",
            ["Drug X", "Placebo"],
            {"Stage 2+ AKI (%)": (14.6, 22.5)},
            notes="ARR 7.9%, RRR 35%. p=0.024. NNT 13.")

    d.table("Secondary endpoints",
            ["Endpoint",            "Drug X",   "Placebo",  "Effect"],
            [["30-day mortality",   "3.4%",     "4.4%",     "HR 0.78 (0.32–1.91)"],
             ["RRT initiation",     "5.8%",     "10.3%",    "RR 0.57 (0.29–1.10)"],
             ["ICU LOS, days",      "3.2",      "4.1",      "diff -0.9 (p=0.04)"],
             ["Hospital LOS, days", "8.1",      "9.6",      "diff -1.5 (p=0.03)"]])

    d.section("Safety", number=5)

    d.table("Adverse events ≥grade 3",
            ["Event",                "Drug X (n=210)", "Placebo (n=210)"],
            [["Any SAE",              "31 (14.8%)",    "29 (13.8%)"],
             ["Hypotension",          "8 (3.8%)",      "5 (2.4%)"],
             ["Bleeding",             "4 (1.9%)",      "5 (2.4%)"],
             ["Hepatic enzyme ↑ ×3",  "3 (1.4%)",      "2 (1.0%)"],
             ["Drug discontinuation", "9 (4.3%)",      "7 (3.3%)"]])

    d.bullets("Safety summary",
              ["No imbalance in serious AEs",
               "No new safety signals vs Phase I",
               "DSMB review: no concerns at any interim"])

    d.section("Subgroups + limitations", number=6)

    d.two_col("Subgroup signals (forest)",
              "Larger effect (interaction p<0.10)",
              ["Pre-op eGFR 30–60: ARR 12.4%",
               "Diabetic: ARR 10.8%",
               "Redo cardiac surgery: ARR 14.1%"],
              "No effect / null",
              ["eGFR >90: ARR 1.2% (NS)",
               "Female sex: no signal",
               "Off-pump procedures: too few events"])

    d.bullets("Limitations",
              ["Open-label adjunctive diuretic per site protocol — possible confound",
               "AKI biomarker (NGAL) not collected at all sites",
               "90-day follow-up incomplete in 4.6% of mITT",
               "Effect smaller in eGFR >90 — generalizability question"])

    d.section("Next steps", number=7)

    d.bullets("Next steps",
              ["Submit primary results to NEJM by 2026-Q3",
               "Phase III protocol draft — target N=2,400",
               "FDA Type-C meeting requested for Phase III alignment",
               "Subgroup biomarker analysis underway (NGAL, KIM-1)"])

    d.cta("Co-author + sponsor review by 2026-05-15",
          sub="Manuscript draft circulating · IRB amendment for biomarker substudy filed",
          contact="pi@institution.edu · stats@institution.edu")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
