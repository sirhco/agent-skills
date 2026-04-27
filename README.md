# agent-skills

Curated collection of [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) skills. Drop one into `~/.claude/skills/` and Claude auto-discovers it via the `SKILL.md` frontmatter.

## What is a Claude skill?

A skill is a directory containing a `SKILL.md` file plus any supporting code, templates, or data. Claude reads the YAML frontmatter at the top of `SKILL.md` (name, description, trigger phrases) and loads the skill on matching requests — no manual invocation required. See [Anthropic's skill authoring docs](https://docs.claude.com/en/docs/claude-code/skills) for the format.

## Skills in this collection

| Skill | What it does | Trigger phrases |
|---|---|---|
| [pptx-create](skills/pptx-create/) | Generate `.pptx` decks programmatically with `python-pptx`. 13 prebuilt themes (Stripe, Linear, McKinsey, Apple, healthcare, pitch-noir, etc.), 10 worked examples spanning business and healthcare verticals, markdown→pptx converter, structure inspector. | "make a deck", "create slides", "build a powerpoint", "generate pptx" |

## Install a skill

Clone the repo somewhere stable, then run the installer.

**macOS / Linux**

```bash
git clone git@github.com:sirhco/agent-skills.git ~/code/agent-skills
cd ~/code/agent-skills
./install.sh --list                   # show available skills
./install.sh --skill pptx-create      # install one
./install.sh --all                    # install everything
```

**Windows (PowerShell)**

```powershell
git clone git@github.com:sirhco/agent-skills.git $HOME\code\agent-skills
cd $HOME\code\agent-skills
.\install.ps1 --list
.\install.ps1 --skill pptx-create
```

The installer symlinks each skill into `~/.claude/skills/` (directory junction on Windows when symlinks aren't permitted). If the skill ships a `requirements.txt`, you'll be prompted before any `pip install --user` runs — pass `--no-deps` to skip.

You can also install a single skill from inside its own directory:

```bash
./skills/pptx-create/install.sh
```

Open a new Claude Code session — the skill is now discoverable.

**Other flags**

- `--copy` — copy files instead of linking (snapshot, repo edits won't propagate).
- `--force` — overwrite existing entries without prompting.
- `--target <path>` — install somewhere other than `~/.claude/skills`.
- `--uninstall <name>` / `--uninstall all` — remove a skill (link/junction only; never deletes the cloned repo).

If Python isn't installed, the wrappers will tell you. The installer itself uses only the standard library.

## Repo layout

```
agent-skills/
├── README.md
├── LICENSE
├── install.py            # cross-platform installer
├── install.sh            # bash wrapper
├── install.ps1           # PowerShell wrapper
└── skills/
    └── pptx-create/
        ├── SKILL.md
        ├── requirements.txt
        ├── install.sh    # delegates to root installer
        ├── install.ps1
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
3. If the skill has Python deps, add a `skills/<your-skill>/requirements.txt`. The installer will offer to `pip install --user` from it.
4. Optionally drop `install.sh` / `install.ps1` shims in the skill dir that delegate to the root installer (see `skills/pptx-create/` for the pattern).
5. Add a row to the **Skills in this collection** table above.
6. Open a PR.

Keep skills self-contained — no cross-skill imports. A user should be able to install a single skill without pulling in dependencies from other skills.

## License

Apache 2.0 — see [LICENSE](LICENSE).
