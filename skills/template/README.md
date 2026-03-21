# TEMPLATE Skill

A template for creating new Cursor/Claude/Codex agent skills following the [Agent Skills](https://agentskills.io) open standard.

## Structure

```
TEMPLATE/
├── SKILL.md              # Main skill definition (required)
├── README.md             # This file (for humans, not loaded by agents)
├── scripts/              # Executable scripts (optional)
│   ├── example.sh        # Bash script example
│   └── validate.py       # Python script example
├── references/           # Extended documentation (optional)
│   └── REFERENCE.md      # Loaded on demand by agents
└── assets/               # Static resources (optional)
    └── config-template.json
```

## Usage

1. Copy this TEMPLATE folder to your skills directory:
   - `.cursor/skills/` (project-level)
   - `~/.cursor/skills/` (user-level global)

2. Rename the folder to match your skill name (lowercase, hyphens only)

3. Edit `SKILL.md`:
   - Update the `name` field to match the folder name
   - Write a clear `description` for agent discovery
   - Add detailed instructions for the agent

4. Add scripts, references, and assets as needed

## Conventions

- **name**: Lowercase letters, numbers, and hyphens only. Must match folder name.
- **description**: Used by agents to determine when the skill is relevant.
- **SKILL.md**: Keep focused; move detailed docs to `references/`.
- **scripts/**: Self-contained with helpful error messages.
- **disable-model-invocation**: Set to `true` for explicit `/skill-name` invocation only.

## Skill Directories

Skills are auto-discovered from:

| Location | Scope |
|----------|-------|
| `.cursor/skills/` | Project-level |
| `.claude/skills/` | Project-level (Claude compatibility) |
| `.codex/skills/` | Project-level (Codex compatibility) |
| `~/.cursor/skills/` | User-level (global) |
| `~/.claude/skills/` | User-level (global) |
| `~/.codex/skills/` | User-level (global) |

## Learn More

- [Cursor Skills Documentation](https://cursor.com/docs/context/skills)
- [Agent Skills Standard](https://agentskills.io)
