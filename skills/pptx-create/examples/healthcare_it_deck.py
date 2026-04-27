"""Example: healthcare IT leader update (CIO/CMIO/CISO).

Audience: hospital exec committee + board IT/cyber subcommittee.
Style: corporate (linear theme — dark, sharp, infra-feel).
Length: ~14 slides. Covers EHR program, security, infra, AI governance.

Run: python3 healthcare_it_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptx.enum.chart import XL_CHART_TYPE
from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="healthcare_it_deck.pptx"):
    d = Deck(theme=get_theme("linear"),
             brand="IT Quarterly · CIO/CISO/CMIO · CONFIDENTIAL")

    d.title("Healthcare IT — Q1 2026 Update",
            "EHR · cybersecurity · infrastructure · AI governance",
            notes="Three priorities: Epic upgrade, ransomware posture, AI guardrails.")

    d.bullets("Agenda",
              ["EHR program: Epic 2026 upgrade",
               "Cybersecurity posture",
               "Infrastructure + uptime",
               "Clinical informatics + physician burden",
               "AI governance + data strategy",
               "Budget + ask"])

    d.section("EHR program", number=1)

    d.table("Epic 2026 upgrade — status",
            ["Workstream",            "Status",   "Go-live",    "Risk"],
            [["Inpatient + ED",       "Build 92%", "2026-09-14", "Med"],
             ["Ambulatory",           "Build 86%", "2026-09-14", "Med"],
             ["Revenue cycle",        "Build 78%", "2026-10-26", "High"],
             ["Lab + imaging",        "Build 95%", "2026-09-14", "Low"],
             ["Patient portal",       "Build 88%", "2026-09-14", "Low"],
             ["Training + readiness", "On track",  "rolling",    "Med"]])

    d.bullets("Top issues + decisions needed",
              ["Revenue cycle build behind — extra contractors approved",
               "End-user training: 4,200 staff, 96 hrs each, $1.8M backfill",
               "Decision needed: dual-record period 2 vs 4 weeks",
               "Decision needed: order-set rationalization (cut from 3,800 → 2,400)"])

    d.section("Cybersecurity", number=2)

    d.table("Security scorecard",
            ["Control",                          "Status",  "Target",  "Note"],
            [["MFA coverage (privileged)",       "100%",    "100%",    "—"],
             ["MFA coverage (workforce)",        "97%",     "100%",    "Holdouts: 3rd-party access"],
             ["Endpoint EDR coverage",           "98.2%",   "≥99%",    "Legacy biomed devices"],
             ["Vuln remediation SLA (critical)", "94%",     "≥95%",    "On watch"],
             ["Phishing click rate",             "3.4%",    "<4%",     "Down from 8% YoY"],
             ["Backup integrity test (immutable)","Pass Q1","Quarterly","Last test 2026-03-15"]])

    d.chart("Phishing click rate (%) — quarterly",
            ["Q1'25", "Q2'25", "Q3'25", "Q4'25", "Q1'26"],
            {"Click rate": (8.1, 6.4, 5.2, 4.0, 3.4)},
            chart_type=XL_CHART_TYPE.LINE)

    d.bullets("Threat posture",
              ["Healthcare ransomware up 38% YoY (HHS HC3 brief)",
               "3rd-party breach risk: 14 BAAs reviewed, 2 require remediation",
               "Ransomware tabletop scheduled 2026-06-12 (full exec + clinical)",
               "Cyber insurance renewal: 12% premium increase, MFA + EDR clauses tightened"])

    d.bullets("Compliance + privacy",
              ["HIPAA risk assessment: complete, 4 findings (all medium, plan filed)",
               "OCR audit readiness binder: refreshed Q1",
               "PHI access reviews: monthly cadence stable, 0 unresolved >30d"])

    d.section("Infrastructure", number=3)

    d.table("Reliability — clinical systems",
            ["System",                  "Uptime SLO",  "Q1 actual",  "Incidents"],
            [["Epic Hyperspace",         "99.9%",      "99.97%",     "0 P1"],
             ["PACS",                    "99.9%",      "99.92%",     "1 P2"],
             ["Lab (Beaker)",            "99.9%",      "99.99%",     "0"],
             ["Pharmacy automation",     "99.5%",      "99.81%",     "1 P2"],
             ["Epic MyChart (patient)",  "99.5%",      "99.78%",     "2 P2"]])

    d.bullets("Infra moves",
              ["Hybrid-cloud DR site cutover: complete, RTO 2h / RPO 15min",
               "Clinical network segmentation: 78% of biomed VLANs migrated",
               "Wi-Fi refresh: 6 floors complete, 4 remaining (Q2)",
               "Legacy app retirement: 11 apps decommissioned in Q1"])

    d.section("Clinical informatics", number=4)

    d.bullets("Physician burden — what we measured",
              ["EHR time outside scheduled hours (pajama time): median 64 min/day",
               "Inbox volume per physician: 142 messages/day (target <100)",
               "Order-set complexity: 31% of order sets used <5×/year",
               "Documentation burden: 3.4× clicks per encounter vs benchmark"])

    d.bullets("What we shipped",
              ["AI scribe pilot: 42 clinicians, 38% reduction in documentation time",
               "Inbox triage automation: routine results auto-released, -22% inbox volume",
               "Order-set sunset committee: 412 sets retired",
               "BPA fatigue audit: 28% of alerts disabled or thresholds tuned"])

    d.section("AI + data", number=5)

    d.table("AI governance — current model inventory",
            ["Use case",            "Status",        "Risk class",  "Gov status"],
            [["AI scribe (ambient)",  "Pilot 42 MD",  "Low",         "Approved"],
             ["Sepsis early warning", "Production",   "High",        "Annual revalidation due"],
             ["Imaging triage (CT head)", "Pilot",     "High",       "Bias audit complete"],
             ["Inbox triage",         "Production",   "Medium",      "Approved"],
             ["Coding assist",        "Evaluation",   "Medium",      "Vendor diligence"]])

    d.bullets("Governance posture",
              ["AI oversight committee: chartered Q4'25, meets monthly",
               "Algorithmic bias audits: required for all clinical-decision AI",
               "Data sharing: 3 research IRBs approved with DUA + de-identification",
               "Transparency: model cards posted on staff intranet"])

    d.section("Budget + ask", number=6)

    d.table("FY26 IT capital — status",
            ["Program",                "Approved",  "Spend YTD",  "Forecast"],
            [["Epic 2026 upgrade",      "$14.2M",    "$5.8M",      "On budget"],
             ["Cybersecurity refresh",  "$3.6M",     "$1.1M",      "On budget"],
             ["Network + Wi-Fi refresh","$2.1M",     "$0.9M",      "On budget"],
             ["AI + analytics",         "$1.4M",     "$0.3M",      "Under-spend"],
             ["Telecom + endpoints",    "$1.8M",     "$0.6M",      "On budget"]])

    d.cta("Asks for the committee",
          sub="(1) approve dual-record period (2 vs 4 wks)  (2) sign off on AI oversight charter v2  (3) endorse cyber tabletop participation",
          contact="cio@memorial.org · ciso@memorial.org · cmio@memorial.org")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
