<!--
QBR template — fill placeholders, then run:
  python3 helpers/markdown_to_pptx.py templates/qbr.md --theme stripe -o qbr.pptx

Each `# Heading` becomes a slide. Markers:
  [title]      — title slide (use "## subtitle" line for subtitle)
  [section]    — section divider
  [stat: N]    — big stat slide (caption from body)
  [bullets]    — bullet list slide (default if no marker)
  [two-col]    — two columns (## Left ## Right with bullets under each)
  [table]      — markdown table
  [chart]      — chart from "## categories: ..." and "## series Name: ..." lines
  [quote]      — quote slide ("## attribution: ..." optional)
  [cta]        — closing CTA ("## sub: ..." and "## contact: ..." optional)
  [notes: ...] — speaker notes (per slide, anywhere in body)
-->

# Quarterly Business Review [title]
## {{Customer}} · Q{{N}} {{YYYY}} · {{date}}

# Agenda
- Executive summary
- Adoption + usage
- Outcomes vs goals
- Roadmap preview
- Renewal + expansion

# Executive summary [section]

# Headlines [two-col]
## Wins
- {{Win 1}}
- {{Win 2}}
- {{Win 3}}
## Watch items
- {{Risk 1}}
- {{Risk 2}}
- {{Risk 3}}

# Adoption + usage [section]

# Daily active users [chart]
## categories: Wk1, Wk2, Wk3, Wk4, Wk5, Wk6, Wk7, Wk8
## series DAU: 124, 138, 151, 167, 182, 195, 211, 224
[notes: steady ramp, no regression]

# Usage by team [table]
| Team | Seats | DAU | Top feature |
| --- | --- | --- | --- |
| {{Team A}} | 32 | 28 | API access |
| {{Team B}} | 18 | 16 | Notebooks |

# Outcomes vs goals [section]

# Goal progress [chart]
## categories: Adoption, TTV, NPS, Cost
## series Target: 100, 100, 100, 100
## series Actual: 112, 134, 92, 88

# {{Customer quote}} [quote]
## attribution: {{Name, Title}}

# Roadmap + renewal [section]

# Roadmap · Q{{next}}
- {{Item 1}}
- {{Item 2}}
- {{Item 3}}

# Renewal: {{date}} [cta]
## sub: Proposed: +{{N}} seats, +Enterprise tier, multi-year
## contact: csm@acme.com
