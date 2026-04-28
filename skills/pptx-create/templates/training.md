---
theme: linear
brand: "Training · 2026"
slides: 12
---

<!--
Training / educational session — 12 slides for beginners.
Run:
  pptx render templates/training.md -o training.pptx
Replace [Topic] and content with your subject matter.
-->

# Prompt Engineering 101 [title]
## A practical intro for new users

# What you'll learn [agenda]
## How LLMs interpret prompts
## The 4 building blocks of a great prompt
## Common mistakes and how to fix them
## Practice: write your first 3 prompts

# Why this matters [bullets]
- Better prompts = better output, less iteration
- Saves 30–60 min per task on average
- Same model, 10× the value with the right framing

# The 4 building blocks [section]

# Block 1 — Role
- Tell the model who it is
- Sets vocabulary, expertise, tone
- Example: "You are a senior data engineer reviewing schemas"

# Block 2 — Task
- One verb, one clear outcome
- "Refactor", "Summarize", "Identify", "Generate"
- Avoid: "help me with", "do something about"

# Block 3 — Context
- Paste the actual data, code, or document
- LLMs can't infer what they can't see
- More context > clever wording

# Block 4 — Constraints
- Format: bullets / table / code block
- Length: "≤200 words", "exactly 5 bullets"
- Style: "concise", "no headers", "preserve XML structure"

# Common mistakes [comparison]
| Mistake | Fix |
| --- | --- |
| Vague task ("help me") | Use one explicit verb |
| Missing context | Paste real input, not a description |
| No format constraint | Specify structure |
| One-shot expectation | Iterate; refine the prompt |

# Practice round [bullets]
- Write a prompt to summarize this training in 100 words
- Write a prompt to extract action items from a meeting transcript
- Write a prompt to refactor a Python function for readability
- We'll review yours in 10 minutes

# Resources [bullets]
- Internal prompt library (link)
- Anthropic prompt engineering guide (link)
- #ai-help Slack channel for live questions

# Questions? [cta]
## sub: Recording + slides will be posted
## contact: training@company.com
