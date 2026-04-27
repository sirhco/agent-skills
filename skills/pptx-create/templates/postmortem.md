<!--
Postmortem template (blameless) — fill placeholders, then run:
  python3 helpers/markdown_to_pptx.py templates/postmortem.md --theme monochrome -o pm.pptx
-->

# Incident postmortem · {{INC-YYYY-NNNN}} [title]
## {{Service}} outage · {{date}} · {{start}}–{{end}} UTC

# Summary [table]
| Field | Value |
| --- | --- |
| Severity | {{SEV1}} |
| Duration | {{N}} min |
| Users impacted | ~{{N}}K ({{%}} of {{traffic}}) |
| Revenue impact | ~${{N}}K |
| Root cause | {{One-liner}} |
| Detection | {{How / when}} |

# Timeline [section]

# Timeline (UTC) [table]
| Time | Event |
| --- | --- |
| {{HH:MM}} | {{Event}} |
| {{HH:MM}} | {{Event}} |
| {{HH:MM}} | {{Event}} |
| {{HH:MM}} | {{Event}} |

# Root cause [section]

# What happened
- {{Step 1}}
- {{Step 2}}
- {{Step 3}}
- {{Step 4}}

# Action items [section]

# Follow-ups [table]
| # | Action | Owner | Due |
| --- | --- | --- | --- |
| 1 | {{Action}} | {{Team}} | {{date}} |
| 2 | {{Action}} | {{Team}} | {{date}} |
| 3 | {{Action}} | {{Team}} | {{date}} |

# {{Lesson}} [quote]
## attribution: {{Role, in retro}}

# No blame. Lessons logged. [cta]
## sub: Action items tracked in #incident-followups
## contact: postmortem doc: {{url}}
