# Prompt library

Canned user prompts organized by use case, plus tips for getting good output. Paste any of these to Claude (with the skill installed); Claude runs the discovery loop, fills gaps, and renders.

Each prompt has:
- the **prompt text** (copy-paste)
- the **default template** Claude should start from (`pptx new <template>`)
- the **expected output shape** (slide count, theme, key kinds)

If the user just says "make me a deck" with no specifics, offer the menu below.

---

## 1. Business / Sales pitch

> **Prompt:** "Create a 10-slide pitch deck for a [fintech startup] aimed at [early-stage VCs]. Include slides for problem, solution, market size, business model, traction, team, and a clear call-to-action. Use a confident, concise, and professional tone."

- **Template**: `pitch-sample` (filled sample with realistic content) or `pitch` (skeleton).
- **Theme**: `pitch-noir`, `pitch-electric`, or `pitch-violet` for VC audiences. `stripe` if more conservative.
- **Output**: 10 slides — title, problem stat (`[stat]`), problem (`[bullets]`), section divider, insight headline, solution, market chart, traction (`[metric_grid]`), team, CTA.
- **Variant placeholders to swap**: `[fintech startup]` → user's company; `[early-stage VCs]` → audience; substitute real numbers for traction.

```bash
pptx new pitch-sample -o my-pitch.md --theme pitch-noir
# edit problem statement, market numbers, traction, team
pptx render my-pitch.md
```

---

## 2. Executive summary / board update

> **Prompt:** "Create a 5-slide executive update for the senior leadership team on our [Q4 2025] results. Include: headline results, key drivers, risks, mitigation actions, and 3 key decisions needed. Use a concise, data-driven tone and a clean layout with minimal text per slide."

- **Template**: `exec-update`
- **Theme**: `mckinsey` (navy classic) or `corporate-default`.
- **Output**: 5 slides — title, headline metrics (`[metric_grid]`), key drivers (`[bullets]`), risks vs mitigation (`[two-col]`), decisions needed (`[cta]`).
- **Lint check**: ≤5 bullets per slide, ≤12 words each.

```bash
pptx new exec-update -o q4-update.md
# replace numbers with your actuals
pptx render q4-update.md --target-slides 5
```

---

## 3. Case study / client presentation

> **Prompt:** "Create a 6-slide client presentation showing how our product helped [Client Name] increase revenue. Use a [problem-solution-result] structure. Focus on ROI and specific metrics. The tone should be consultative and persuasive."

- **Template**: `case-study`
- **Theme**: `stripe`, `corporate-default`, or `healthcare` (for clinical clients).
- **Output**: 6 slides — title, problem (`[bullets]`), solution (`[bullets]`), implementation (`[timeline]`), results (`[metric_grid]`), CTA.

```bash
pptx new case-study -o acme-success.md
# replace [Client Name] and metrics
pptx render acme-success.md
```

---

## 4. Training / educational session

> **Prompt:** "Create a 12-slide training presentation to teach beginners about [Prompt Engineering]. Include learning objectives, step-by-step processes, common mistakes, and practice exercises. Use simple, clear language."

- **Template**: `training`
- **Theme**: `linear` (dark, dev-tools sharp) or `corporate-default`.
- **Output**: 12 slides — title, agenda, why-this-matters, section divider, 4 building blocks, common mistakes (`[comparison]`), practice round, resources, Q&A CTA.

```bash
pptx new training -o ai-training.md --theme linear
# replace [Topic] and content blocks
pptx render ai-training.md --target-slides 12
```

---

## 5. Data-driven insight (single slide)

> **Prompt:** "Create a slide showing the trend for [Net Revenue Retention] over the last [4] quarters. Include a simple line chart, 3 bullets explaining what changed and why, and a clear headline insight."

- **Template**: `data-insight`
- **Theme**: `stripe` or `corporate-default`.
- **Output**: 1 slide — line chart with multi-series + headline that conveys the takeaway, not just the metric name.

```bash
pptx new data-insight -o nrr-q4.md
# swap categories, series values, and the headline insight
pptx render nrr-q4.md
```

---

## 6. QBR (quarterly business review)

> **Prompt:** "Create a 13-slide QBR for our [enterprise customer Acme] covering Q3 [topline, segment mix, risks, Q4 plan]. Use a corporate, data-friendly theme."

- **Template**: `qbr`
- **Theme**: `stripe` (default), `mckinsey`, or `healthcare` for clinical accounts.
- **Output**: title, agenda, topline metrics, segment mix table, charts, risks vs mitigations, Q4 plan, CTA.

```bash
pptx new qbr -o acme-q3-qbr.md
pptx render acme-q3-qbr.md
```

---

## 7. Sales / outbound deck

> **Prompt:** "Create a 7-slide outbound sales deck for [Acme Corp] showing how we solve [their compliance pain]. End with a meeting CTA."

- **Template**: `sales`
- **Theme**: `stripe`, `corporate-default`.
- **Output**: title, problem framing, solution, social proof, ROI metrics, comparison vs status quo, CTA.

```bash
pptx new sales -o acme-outbound.md
pptx render acme-outbound.md
```

---

## 8. All-hands

> **Prompt:** "Create an 8-slide all-hands deck for [Q3 2026]. Cover company-wide wins, roadmap, hiring, and one tough message about [headcount freeze]."

- **Template**: `allhands`
- **Theme**: `stripe`, `corporate-default`, `apple`.
- **Output**: title, the wins, key metrics, roadmap timeline, hiring update, the tough message, recognitions, Q&A.

```bash
pptx new allhands -o q3-allhands.md
pptx render q3-allhands.md
```

---

## 9. Postmortem

> **Prompt:** "Create a 9-slide blameless postmortem for [the 2026-01-15 billing outage]. Include timeline, root cause, what worked, what didn't, action items."

- **Template**: `postmortem`
- **Theme**: `monochrome` (zero-color seriousness) or `linear`.
- **Output**: title, incident summary, impact metrics, timeline, root cause, contributing factors, what worked / didn't, action items, follow-up.

```bash
pptx new postmortem -o billing-outage.md --theme monochrome
pptx render billing-outage.md
```

---

## 10. Healthcare-specific

The skill also ships specialized examples (not user-facing templates yet — copy from `examples/`):

- **Clinical research readout** → `examples/clinical_research_deck.py` (CONSORT/STROBE structure, RCT readout)
- **Grand rounds / M&M** → `examples/grand_rounds_deck.py`
- **Hospital admin board update** → `examples/hospital_admin_deck.py`
- **Healthcare CIO/CMIO/CISO** → `examples/healthcare_it_deck.py`

Healthcare prompts: include `Use the healthcare theme. Never embed real PHI — flag any patient identifiers and use synthetic data.`

---

## Tips for better prompts

These translate directly to better Claude output. Stack them.

### Specify structure

- "3 bullets per slide, max 10 words per bullet"
- "Use one `[metric_grid]` slide for KPIs instead of bullets"
- "Include a section divider between major topics"
- "End with a `[cta]` slide naming the action and the contact email"

### Define visuals

- "Use a clean, minimalist layout with plenty of white space"
- "Replace bullet lists with `[chart]`, `[metric_grid]`, or `[big_stat]` where possible"
- "Include a `[timeline]` for the rollout schedule"
- "Add a `[comparison]` table for us vs competitors"

### Give constraints

- "Avoid clip art, gradients, drop shadows, and centered everything"
- "Use a professional, modern style — no emojis, no exclamation marks"
- "Don't fabricate numbers — use `{{TBD}}` placeholders if I haven't given them"
- "Limit to 10 slides. Warn if my outline drifts."

### Add context (most important)

- "Use the data in the table I'm pasting below — don't summarize, present it as-is"
- "Tone should match this previous deck: [paste 1-2 slides]"
- "Audience: [board / customer / VC / engineer]. Adjust vocabulary."
- "Brand: accent `#0E8388`, logo at `/Users/me/logo.png`, footer `Acme Confidential`"

### Specify the controls (the skill listens for these)

| User says | Skill flag |
|---|---|
| "Use #0E8388 as accent" | `--colors "accent=#0E8388"` |
| "10 slides exactly" | `--target-slides 10` |
| "Background image is /path/bg.png" | `--bg /path/bg.png` |
| "Cover image on slide 1" | `--slide-bg "1=/path/cover.png"` |
| "Dark mode" | `--mode dark` |
| "Don't include footer" | `--brand ""` |
| "Save as q3-deck.pptx" | `-o q3-deck.pptx` |

---

## Vague prompt? Offer the menu

When the user says "make me a slide deck" with no specifics, present the 5 categories as a menu:

> "I can build any of these — pick one and I'll fill in the gaps:
>
> 1. **Business / sales pitch** — 10 slides, VC-ready
> 2. **Executive update** — 5 slides, board-style, data-dense
> 3. **Case study** — 6 slides, problem-solution-result
> 4. **Training session** — 12 slides, beginner-friendly
> 5. **Data insight** — 1 slide, single chart with takeaway
> 6. **Other** — tell me the audience + topic and I'll structure it"

Once they pick, ask only the gaps from the 7-input discovery (audience, theme/colors, slide count, backgrounds, logo, output path).

---

## Filling templates with real data

Two patterns:

**A. User pastes data directly into the prompt.**
> "Use these Q3 numbers: ARR $4.2M (+28% YoY), 412 new customers, 99.97% uptime, NPS 4.8."

Claude inserts them into a `[metric_grid]` slide. Do not fabricate any number the user didn't give.

**B. User points at a file or sheet.**
> "Pull numbers from `~/work/q3-results.csv`."

If the skill can read the file, do so and surface what was extracted. If not, ask the user to paste the relevant rows or columns. Don't guess.

For unfilled placeholders, use `{{TBD}}` — visible markers in the rendered deck the user can spot and replace before sharing.
