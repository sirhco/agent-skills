"""Example: hospital administrator board update.

Audience: hospital board, C-suite (CMO, CNO, CFO).
Style: corporate (mckinsey theme — navy + white, executive feel).
Length: ~13 slides. Triple-aim framing: quality, finance, workforce.

Run: python3 hospital_admin_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptx.enum.chart import XL_CHART_TYPE
from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="hospital_admin_deck.pptx"):
    d = Deck(theme=get_theme("mckinsey"),
             brand="Memorial Hospital · Board · 2026-04 · CONFIDENTIAL")

    d.title("Q1 2026 Board Update",
            "Memorial Hospital · CEO report · 2026-04-27",
            notes="Open with topline: positive margin, quality up, workforce stable.")

    d.bullets("Agenda",
              ["Operating performance",
               "Quality + safety scorecard",
               "Workforce + nursing",
               "Capital + capacity",
               "Risks + outlook"])

    d.section("Operating performance", number=1)

    d.chart("Operating margin (%)",
            ["Q1'25", "Q2'25", "Q3'25", "Q4'25", "Q1'26"],
            {"Margin %": (-1.2, 0.4, 1.8, 2.6, 3.4)},
            chart_type=XL_CHART_TYPE.LINE,
            notes="Best quarter since pre-pandemic. Driven by ortho + cardio volume.")

    d.table("Volume + revenue",
            ["Metric",            "Q1'25",   "Q1'26",   "Δ"],
            [["Discharges",        "8,142",   "8,816",   "+8.3%"],
             ["ED visits",         "21,304",  "22,150",  "+4.0%"],
             ["OR cases",          "3,108",   "3,492",   "+12.4%"],
             ["Net patient revenue ($M)", "184.2", "201.7", "+9.5%"],
             ["Operating expenses ($M)",  "186.4", "194.8", "+4.5%"]])

    d.section("Quality + safety", number=2)

    d.table("Quality scorecard vs targets",
            ["Measure",                          "Q1'26",   "Target",  "Status"],
            [["HAI rate (per 1,000 pt-days)",    "0.42",    "<0.50",   "On track"],
             ["CAUTI SIR",                       "0.61",    "<1.00",   "On track"],
             ["CLABSI SIR",                      "0.84",    "<1.00",   "On track"],
             ["30-day readmit (all-cause)",      "11.8%",   "<12.0%",  "On track"],
             ["HCAHPS top-box (overall)",        "76",      "≥80",     "Watch"],
             ["Door-to-balloon (STEMI), median", "58 min",  "<90",     "On track"],
             ["Sepsis bundle compliance",        "82%",     "≥85%",    "Watch"]])

    d.bullets("Safety highlights + concerns",
              ["Zero serious safety events in Q1 (vs 2 in Q1'25)",
               "Falls with injury down 18% YoY — bedside shift report fully rolled out",
               "HCAHPS slip on responsiveness — nursing huddle pilot starting May",
               "Sepsis bundle gap: lactate redraw timing (work in progress)"])

    d.section("Workforce", number=3)

    d.chart("RN vacancy rate vs benchmark (%)",
            ["Q1'25", "Q2'25", "Q3'25", "Q4'25", "Q1'26"],
            {"Memorial":      (12.4, 11.1, 9.8, 8.4, 7.6),
             "Region median": (10.2, 10.0, 9.5, 9.2, 9.0)},
            chart_type=XL_CHART_TYPE.LINE)

    d.two_col("Workforce status",
              "Wins",
              ["RN vacancy below benchmark for first time since 2022",
               "Travel-nurse spend down 41% YoY",
               "New RN residency cohort: 38 hires (vs 22 plan)",
               "Physician engagement survey: 4.1 / 5"],
              "Watch items",
              ["Respiratory therapist shortage continues",
               "Surgical tech turnover 18% — retention task force",
               "Burnout index for ED nurses elevated",
               "Compensation review needed for advanced practice"])

    d.section("Capital + capacity", number=4)

    d.bullets("Capital projects",
              ["NICU expansion: on schedule, COD 2026-Q4 ($24M, 12 beds)",
               "Epic 2026 upgrade: go-live 2026-09 (see IT report)",
               "Ambulatory cardiology suite: design complete, GMP under review",
               "Heliport recertification: complete"])

    d.bullets("Capacity",
              ["Med-surg occupancy 92% (target 85%) — boarding hours up 14%",
               "ED LOS for admitted pts: 5.8 hr (target <4.5)",
               "ICU step-down constrained — RFI for 6 swing beds in Q2"])

    d.section("Risks + outlook", number=5)

    d.table("Top enterprise risks",
            ["#", "Risk",                                      "Owner",  "Mitigation"],
            [["1", "CMS reimbursement rule change (DRG drift)", "CFO",   "Coding audit + advocacy via state hosp assoc"],
             ["2", "Cyber: ransomware / 3rd-party breach",      "CIO",   "See IT report; tabletop scheduled June"],
             ["3", "Behavioral health surge in ED",             "CMO",   "BH consult-liaison expansion approved"],
             ["4", "Payer contract renegotiation (BCBS)",       "CFO",   "Q3 negotiation kickoff"]])

    d.cta("Q2 priorities",
          sub="Lift HCAHPS · close sepsis bundle gap · open ICU step-down beds",
          contact="board secretary: bsec@memorial.org")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
