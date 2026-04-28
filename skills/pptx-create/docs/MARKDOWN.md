# Markdown syntax

Every `.md` input runs through `helpers/markdown_to_pptx.py`. Each `# Heading` opens a slide. The `[kind]` marker after the heading picks slide kind. Default kind: `bullets`.

## Frontmatter

YAML between `---` fences, top of file. Sets deck-wide defaults that flags can still override.

```markdown
---
theme: stripe
brand: "Acme · 2026"
slides: 10                       # target slide count — warns on mismatch
author: chris@acme.com
date: 2026-04-28
colors:                          # palette overrides — applied over theme
  accent: "#0E8388"
  bg: "#FFFFFF"
  ink: "#0A2540"
backgrounds:                     # background images
  default: assets/bg.png         # used on every slide unless overridden
  1: assets/cover.png            # per-slide override (1-based)
  5: assets/section.jpg
---
```

Recognized keys: `theme`, `brand`, `slides`, `colors.<key>`, `backgrounds.<n|default>`. The parser also accepts dotted-flat form (`colors.accent: "#0E8388"`) for tools that don't write nested YAML. Unknown keys are stored but ignored (free-form metadata for `author`, `date`, etc).

## Speaker notes

Two forms — both end up in the slide's notes:

```markdown
# My slide
- bullet one

> note for the speaker — won't show on the projected slide
> can span multiple lines

[notes: legacy inline form, still supported]
```

`>` lines anywhere inside a slide append to notes. `[notes: ...]` strips inline.

## Slide kinds

### `[title]` — opener

```markdown
# Q3 Business Review [title]
## Operations + Product · 2026-04-28
```

Subtitle comes from the first `## ...` line.

### `[section]` — divider

```markdown
# Topline [section]
```

Adds itself to the agenda progress strip on subsequent slides.

### `[bullets]` — default

```markdown
# Risks
- Hiring lag in EMEA
- Renewal risk on top 5 accounts
- Billing v2 schedule slip
```

No marker needed; `bullets` is the default. Auto-shrinks 20pt → 14pt floor; splits to a continuation slide if still over.

### `[two-col]` — side-by-side

```markdown
# Risks vs Mitigations [two-col]
## Risks
- Hiring lag
- Renewal risk
## Mitigations
- EMEA contractors
- Exec sponsor program
```

Exactly two `## ` columns. Bullets under each.

### `[stat:VALUE]` — pitch hero

```markdown
# ARR growth [stat:$1.2M]
4 months from launch · net new
```

Body text becomes the caption.

### `[quote]`

```markdown
# "Best month yet." [quote]
## attribution: Jane Doe, CEO
```

### `[cta]` — closer

```markdown
# Q4 plan: ship billing v2 [cta]
## sub: Close 3 deals before EOQ
## contact: ops@acme.com
```

### `[chart]` — native editable PowerPoint chart

```markdown
# Revenue [chart]
## categories: Q1, Q2, Q3
## series $M: 12, 15, 18
## series Plan: 11, 14, 17
```

Default: column. Override with `[chart:bar]`, `[chart:line]`, `[chart:pie]`, `[chart:area]`, `[chart:doughnut]`. Lines starting `series ` open a new series.

### `[table]`

```markdown
# Mix [table]
| Segment | ARR | Growth |
| --- | --- | --- |
| Ent | $11.2M | +34% |
| Mid | $5.8M  | +22% |
```

First row is header. Separator row (`| --- |`) ignored.

### `[comparison]` — feature matrix

```markdown
# Compare [comparison]
| Feature | Us | Them |
| --- | --- | --- |
| SSO | yes | no |
| Audit log | yes | yes |
| Free tier | yes | no |
```

`yes/true/y/✓/1` → bold ✓ in accent. `no/false/n/✗/0/—/-` → muted dash.

### `[image]`

```markdown
# Architecture [image]
![v2 stack diagram](diagrams/arch-v2.png "v2 stack overview")
```

Standalone `![alt](path "caption")` outside any heading creates an `image` slide named after the alt text. Alt text is **required**; lint fails on missing.

### `[video]` — placeholder frame

```markdown
# Demo [video]
![product demo poster](posters/demo.png "Click to play in talk track")
```

No actual video embed (avoids huge file size). Renders frame + play icon. Alt required.

### `[code:LANG]`

````markdown
# Sample [code:python]
```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```
> remind audience this is illustrative
````

`pygments` highlights if installed (in `requirements-extras.txt`). Fall-through is plain mono Consolas. Code fence language is parsed when `[code]` marker omitted.

### `[timeline]`

```markdown
# Roadmap [timeline]
## 2026-Q1: Public beta
## 2026-Q2: GA launch
## 2026-Q3: SOC 2 Type II
## 2026-Q4: Enterprise tier
```

Each `## date: label` becomes a node. Labels alternate above/below the axis.

### `[metric_grid]` — 4-up KPI tiles

```markdown
# Q3 KPIs [metric_grid]
## $1.2M | ARR | +34%
## 412 | Customers | +58
## 99.97% | Uptime |
## 4.8 / 5 | CSAT | +0.3
```

`value | label | delta`. Delta starting `+` renders accent; otherwise muted. Up to 4 tiles.

### `[agenda:N]` — TOC with current highlight

```markdown
# Agenda [agenda:1]
## Topline
## Risks
## Q4 plan
```

`[agenda:1]` highlights item index 1 (zero-based) — the current section. Omit `:N` for a plain TOC.

### `[pricing]`

```markdown
# Pricing [pricing]
## Starter | $0 | mo
- Up to 3 users
- Email support
## Pro | $49 | mo | featured
- Unlimited users
- Priority support
- API access
## Enterprise | Contact | sales
- SSO + SCIM
- 24/7 phone
```

Pipe-delimited: `name | price | period [| featured]`. Feature bullets follow as `-` items. The `featured` plan inverts colors (accent fill, bg text).

### `[before_after]`

```markdown
# Migration impact [before_after]
## before: 14 manual steps, 3-day cycle
- nightly batch
- engineer babysit
## after: API webhook, real-time
- self-serve
- audit log
```

`## before:` and `## after:` open the two columns. Bullets under each.

### Fenced slide blocks `:::kind`

Alternative to `# Title [kind]` — useful when the heading and kind syntax feels noisy.

```markdown
:::stat 73%
of customers renew within 30 days
:::

:::cta Start your trial
## sub: Free for 14 days
## contact: hello@acme.com
:::
```

`:::kind [optional title]` opens; bare `:::` closes. Identical semantics to `# Title [kind]`.

## Validation

The parser raises `MarkdownError` with a line number and suggestion when a slide is missing required content for its kind:

```
line 24: slide #5 'Compare' kind='comparison' missing required content
  suggestion: add a `| feature | a | b |` table with yes/no rows
```

Per-kind requirements:

| Kind | Required |
|---|---|
| `table`, `comparison` | header row + ≥1 body row |
| `chart` | `## categories: ...` and ≥1 `## series Name: ...` |
| `two-col` | exactly two `## ` blocks |
| `image`, `video` | `![alt](path)` line |

Other kinds degrade gracefully (e.g. `[bullets]` with no bullets uses the title).

## End-to-end example

A working example using ~all kinds is at `/tmp/feature-test.md` after running the smoke tests, or you can write one yourself and run:

```bash
pptx render outline.md -o deck.pptx
pptx inspect deck.pptx
pptx lint deck.pptx
```
