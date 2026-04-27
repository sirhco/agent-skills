"""Example: physician grand rounds case presentation.

Audience: attending physicians, residents, fellows.
Style: corporate (healthcare theme).
Length: ~12 slides. Case-driven teaching format.

Run: python3 grand_rounds_deck.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.build_deck import Deck
from themes.themes import get_theme


def build(out="grand_rounds_deck.pptx"):
    d = Deck(theme=get_theme("healthcare"),
             brand="Medicine Grand Rounds · 2026-04-27")

    d.title("Diagnostic anchoring in atypical chest pain",
            "Internal Medicine Grand Rounds · 2026-04-27 · 60 min",
            notes="Open with case. No spoilers — let audience anchor as we did.")

    d.bullets("Learning objectives",
              ["Recognize atypical presentations of acute aortic syndrome",
               "Apply Bayesian reasoning to overturn anchored diagnoses",
               "Identify imaging cues that triage chest pain workup",
               "Discuss systems-level changes to reduce missed dissection"])

    d.section("Case", number=1)

    d.bullets("HPI",
              ["62 yo F, htn + smoker, presents with sudden interscapular pain",
               "Initial triage: GERD vs MSK. Discharged after normal ECG/trop",
               "Returns 14 hours later: hypotension, AMS, asymmetric pulses",
               "POCUS: pericardial effusion. CTA: type A aortic dissection"])

    d.table("Vitals — visit 1 vs visit 2",
            ["Vital", "Visit 1 (T0)", "Visit 2 (T+14h)"],
            [["BP (mmHg)",  "152/88",   "78/42 → 96/52 R, 64/40 L"],
             ["HR",         "82",       "118"],
             ["SpO2",       "98% RA",   "94% 4L NC"],
             ["Mental",     "Alert",    "Confused, GCS 13"],
             ["Pain",       "6/10",     "9/10, tearing"]])

    d.section("Diagnostic reasoning", number=2)

    d.two_col("What we missed",
              "Anchored framing",
              ["Normal ECG and trop closed cardiac",
               "Pain quality matched MSK pattern",
               "Discharged on PPI + NSAID",
               "No d-dimer, no CXR widened mediastinum check"],
              "What we should have asked",
              ["Sudden onset → vascular until proven otherwise",
               "Interscapular radiation: classic dissection",
               "Pulse exam not documented",
               "Aortic dissection detection risk score not applied"])

    d.bullets("Bayesian update",
              ["Pre-test prob aortic dissection: ~3% in undifferentiated chest pain",
               "Add: sudden onset (LR+ 2.6) → ~8%",
               "Add: tearing radiation (LR+ 10.8) → ~48%",
               "Add: pulse deficit (LR+ 5.7) → ~84% — must rule out"])

    d.section("Evidence", number=3)

    d.table("Aortic Dissection Detection Risk Score (ADD-RS)",
            ["Category",                  "1 point each", "Total"],
            [["High-risk conditions",     "Marfan, FHx, AV disease, recent inst.", "0–1"],
             ["Pain features",            "Abrupt, severe, ripping/tearing",       "0–1"],
             ["Exam",                     "Pulse deficit, BP differential, neuro deficit", "0–1"],
             ["Score 0",                  "very low risk — d-dimer ok",            "—"],
             ["Score ≥1",                 "imaging required (CTA preferred)",      "—"]])

    d.bullets("Key literature",
              ["IRAD registry (JAMA 2018): 28% misdiagnosed at first presentation",
               "Nazerian et al (Circulation 2018): ADD-RS + d-dimer NPV 99.7%",
               "ACEP 2024 clinical policy: ADD-RS ≥1 → CTA, do not rule out with ECG/trop"])

    d.section("Outcome + lessons", number=4)

    d.bullets("Outcome",
              ["Emergent OR for type A repair",
               "Survived; discharged POD12 to rehab",
               "M&M reviewed; no individual blame — system gap"])

    d.bullets("System change recommendations",
              ["ADD-RS prompt embedded in EHR triage for chest pain",
               "Pulse exam + BP differential as required fields",
               "Discharge stop: any sudden chest/back pain triggers d-dimer",
               "Quarterly audit of CTA-positive dissection cases for missed first visit"])

    d.cta("Take-aways",
          sub="Anchoring is the enemy. Sudden onset = vascular until proven otherwise.",
          contact="discussant: dr.smith@institution.edu  ·  next GR: 2026-05-04")

    d.save(out)
    return out


if __name__ == "__main__":
    path = build()
    from pptx import Presentation
    import os
    print(f"saved: {path}  slides: {len(Presentation(path).slides)}  "
          f"size: {os.path.getsize(path)} bytes")
