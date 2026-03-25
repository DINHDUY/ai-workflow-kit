# TEMPLATE Command

A full-featured template for creating new AI agent commands that work with both **Cursor** and **GitHub Copilot**.

## Structure

```
template/
├── template.md             # Main command definition — copy and rename this (required)
├── README.md               # This file (for humans, not loaded by agents)
├── examples/               # Annotated input/output examples (optional)
│   ├── example-basic.md    # Simple, common use case
│   └── example-advanced.md # Complex use case with all options
├── references/             # Extended documentation loaded on demand (optional)
│   └── reference.md        # Detailed specs, edge cases, troubleshooting
└── scripts/                # Executable helper scripts (optional)
    ├── python/
    │   └── template_script.py
    └── shell/
        └── template.sh
```

## Quick Start

1. **Copy** this `template/` folder to your commands directory:
   ```bash
   # Via the kit CLI (recommended)
   npx @dtranllc/ai-workflow-kit add-commands template

   # Or manually
   cp -r path/to/ai-workflow-kit/commands/template my-command
   ```

2. **Rename** the folder to your command name (lowercase, hyphens only):
   ```bash
   mv template my-command
   ```

3. **Rename** `template.md` to match the folder name:
   ```bash
   mv my-command/template.md my-command/my-command.md
   ```

4. **Edit** `my-command.md`:
   - Replace `command-name` with your actual command name
   - Update `description` in the frontmatter
   - Fill in the Overview, Steps, and Examples sections
   - Remove unused sections

5. **Install** to your project:
   ```bash
   npx @dtranllc/ai-workflow-kit add-commands my-command
   ```

---

## Platform Installation Paths

### Cursor

```bash
# Project-level (recommended)
.cursor/commands/<command-name>.md

# Invoked with:
/command-name <user input>
```

### GitHub Copilot

```bash
# Project-level prompt files
.github/copilot/<command-name>.prompt.md

# Or VS Code workspace prompts
.vscode/<command-name>.prompt.md

# Invoked via the Copilot chat command picker
```

---

## Frontmatter Reference

### Cursor (`template.md`)

```yaml
---
description: "One-sentence description shown in the command palette."
alwaysApply: false   # true = auto-apply in every session; false = on-demand only
---
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Shown in Cursor's command palette; used for discovery |
| `alwaysApply` | boolean | No (default `false`) | Auto-inject this command context every session |

### GitHub Copilot (`.prompt.md`)

```yaml
---
mode: agent             # agent | ask | edit
description: "One-sentence description shown in the prompt picker."
tools:
  - codebase            # Semantic search + file read
  - terminal            # Run shell commands
  - githubRepo          # GitHub issues, PRs, commits
  - editor              # Currently open editor content
  - extensions          # VS Code extension APIs
---
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mode` | string | No (default `ask`) | `agent` = autonomous multi-step; `ask` = single response; `edit` = inline edit |
| `description` | string | Yes | Shown in the Copilot prompt picker |
| `tools` | array | No | Tools the agent may use in `agent` mode |

---

## Command File Conventions

- **Name**: match the folder name — lowercase, hyphens only (e.g. `my-command`)
- **`template.md`**: keep focused on agent instructions — 100–200 lines is ideal
- **`references/`**: move verbose specs, API docs, and troubleshooting here — loaded only when needed
- **`scripts/`**: self-contained with `--help` flags and clear error messages
- **`examples/`**: real-world inputs that illustrate expected behavior, not just syntax
- **`README.md`**: for humans only — agents do not read this file by default

## Conventions for Agent Instructions

- Write steps as imperative actions: **"Check"**, **"Run"**, **"Verify"** — not "you should check"
- Use numbered lists for sequential steps; bullet lists for parallel or optional steps
- Include exact commands in fenced code blocks with the language tag
- Document every flag/option in a Markdown table
- Limit scope explicitly: tell the agent what it *does not* handle

## Learn More

- [Cursor Agent Commands](https://docs.cursor.com/context/rules)
- [GitHub Copilot Prompt Files](https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-files-experimental)
- [GitHub Copilot Instructions](https://code.visualstudio.com/docs/copilot/copilot-customization#_use-instructionfiles-to-add-context)
