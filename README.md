# agent-skills

Curated collection of [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) skills. Drop one into `~/.claude/skills/` and Claude auto-discovers it via the `SKILL.md` frontmatter.

## What is a Claude skill?

A skill is a directory containing a `SKILL.md` file plus any supporting code, templates, or data. Claude reads the YAML frontmatter at the top of `SKILL.md` (name, description, trigger phrases) and loads the skill on matching requests — no manual invocation required. See [Anthropic's skill authoring docs](https://docs.claude.com/en/docs/claude-code/skills) for the format.

## Skills in this collection

| Skill | What it does | Trigger phrases |
|---|---|---|
| [pptx-create](skills/pptx-create/) | Generate `.pptx` decks programmatically with `python-pptx`. 13 prebuilt themes (Stripe, Linear, McKinsey, Apple, healthcare, pitch-noir, etc.), 10 worked examples spanning business and healthcare verticals, markdown→pptx converter, structure inspector. | "make a deck", "create slides", "build a powerpoint", "generate pptx" |

## Install a skill

Clone the repo somewhere stable, then symlink the skill directory into `~/.claude/skills/`:

```bash
git clone git@github.com:sirhco/agent-skills.git ~/code/agent-skills
mkdir -p ~/.claude/skills
ln -s ~/code/agent-skills/skills/pptx-create ~/.claude/skills/pptx-create
```

Open a new Claude Code session — the skill is now discoverable.

To install every skill in the collection:

```bash
for d in ~/code/agent-skills/skills/*/; do
  ln -s "$d" ~/.claude/skills/"$(basename "$d")"
done
```

To uninstall, remove the symlink: `rm ~/.claude/skills/pptx-create`.

## Repo layout

```
agent-skills/
├── README.md
├── LICENSE
└── skills/
    └── pptx-create/
        ├── SKILL.md
        ├── copilot-prompt.md
        ├── helpers/
        ├── templates/
        ├── themes/
        └── examples/
```

Each skill lives in its own directory under `skills/`. New skills follow the same pattern.

## Contributing a new skill

1. Create `skills/<your-skill>/SKILL.md` with YAML frontmatter — at minimum `name`, `description`, and trigger phrases in the description.
2. Add supporting files (helpers, templates, examples) alongside it.
3. Add a row to the **Skills in this collection** table above.
4. Open a PR.

Keep skills self-contained — no cross-skill imports. A user should be able to install a single skill via one symlink without pulling in dependencies from other skills.

## License

Apache 2.0 — see [LICENSE](LICENSE).
