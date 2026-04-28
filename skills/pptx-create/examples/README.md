# Examples

Each file is a runnable Python script that builds a `.pptx`. Pick the closest match to your use case, copy it, and edit. All examples assume the skill is on `sys.path`.

| Example | Use case | Run |
|---|---|---|
| `qbr_deck.py` | Quarterly business review for a customer | `python3 examples/qbr_deck.py` |
| `sales_deck.py` | Outbound sales pitch for a prospect | `python3 examples/sales_deck.py` |
| `pitch_deck.py` | VC pitch deck (pitch theme) | `python3 examples/pitch_deck.py` |
| `allhands_deck.py` | Company all-hands | `python3 examples/allhands_deck.py` |
| `postmortem_deck.py` | Incident postmortem | `python3 examples/postmortem_deck.py` |
| `product_launch_deck.py` | Product launch deck | `python3 examples/product_launch_deck.py` |
| `clinical_research_deck.py` | RCT readout / IRB summary (CONSORT/STROBE) | `python3 examples/clinical_research_deck.py` |
| `grand_rounds_deck.py` | Physician grand rounds / M&M | `python3 examples/grand_rounds_deck.py` |
| `hospital_admin_deck.py` | Hospital admin board update | `python3 examples/hospital_admin_deck.py` |
| `healthcare_it_deck.py` | Healthcare CIO/CMIO/CISO quarterly | `python3 examples/healthcare_it_deck.py` |
| `theme_gallery.py` | One slide per theme — for picking | `python3 examples/theme_gallery.py` |

## Verify

After running any example, inspect the output:

```bash
pptx inspect deck.pptx
pptx lint deck.pptx
```

## Tweak

Open the file and you'll see calls like `d.bullets(...)`, `d.chart(...)`, `d.cta(...)`. Edit values directly — every slide method is documented in `REFERENCE.md`.
