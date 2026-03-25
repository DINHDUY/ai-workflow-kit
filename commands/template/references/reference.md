# Extended Reference Documentation

This file contains detailed reference material loaded on demand by the agent. The main `template.md` stays focused on agent steps; this file holds verbose specs, edge-case behavior, and troubleshooting guides.

---

## Full CLI Reference

### `scripts/python/template_script.py`

```
usage: template_script.py [-h] [-o OUTPUT] [-v] [--dry-run] [-f] input

positional arguments:
  input                 Path to the input file to process

options:
  -h, --help            Show this help message and exit
  -o, --output OUTPUT   Output file path (default: ./output/<input-name>)
  -v, --verbose         Enable verbose/debug output to stderr
  --dry-run             Preview actions without writing any files
  -f, --force           Overwrite output if it already exists
```

### `scripts/shell/template.sh`

```
usage: template.sh [--input <path>] [--output <path>] [--dry-run] [--verbose] [--force]

Options:
  --input   <path>   Input file (required)
  --output  <path>   Output path (default: ./output/<basename>)
  --dry-run          Preview without writing
  --verbose          Enable debug output
  --force            Overwrite existing output
  --help             Show this message
```

---

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `INPUT` | string | — | Path to the input file (required) |
| `OUTPUT` | string | `./output/<basename>` | Path for the output file |
| `VERBOSE` | boolean | `false` | Write debug info to stderr |
| `DRY_RUN` | boolean | `false` | Preview without writing |
| `FORCE` | boolean | `false` | Overwrite existing output |
| `ENCODING` | string | `utf-8` | File encoding for read/write |

---

## Behavior Specification

### Input resolution

1. If `INPUT` is a relative path, resolve it from the current working directory.
2. If `INPUT` is an absolute path, use it as-is.
3. If `INPUT` does not exist, exit with code `1` and print an error to stderr.

### Output resolution

1. If `--output` is specified, use that path exactly.
2. If not specified, derive the output path: `./output/<stem><ext>` where `<stem>` and `<ext>` come from the input filename.
3. Create parent directories automatically if they do not exist.
4. If the output file already exists:
   - Without `--force`: exit with code `1` and print an error.
   - With `--force`: overwrite and log `[WARN] Overwriting existing file: <path>` to stderr.

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | User error (bad input, missing file, overwrite conflict) |
| `2` | Internal / unexpected error |

---

## Cursor Frontmatter — Complete Reference

```yaml
---
description: "Shown in the Cursor command palette. Keep under 120 characters."
alwaysApply: false
---
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | — | Displayed in the `/` command picker |
| `alwaysApply` | boolean | `false` | `true` injects the command context into every chat automatically |

**When to use `alwaysApply: true`:**
- Commands that define global coding conventions or style guides
- Commands that set persistent project context (architecture decision records, coding standards)

**When to leave it `false` (default):**
- Task-specific commands invoked only for particular workflows
- Commands that make changes or run scripts (prefer explicit invocation)

---

## GitHub Copilot Frontmatter — Complete Reference

```yaml
---
mode: agent
description: "Shown in the Copilot prompt picker. Aim for one clear sentence."
tools:
  - codebase
  - terminal
  - githubRepo
  - editor
  - extensions
---
```

### `mode` values

| Value | Description |
|-------|-------------|
| `ask` | Single-turn response. Agent reads context, answers, stops. **(default)** |
| `edit` | Inline edit mode. Agent modifies the currently open file. |
| `agent` | Multi-turn autonomous mode. Agent can call tools, run commands, iterate. |

### Available `tools`

| Tool | Description | Requires |
|------|-------------|---------|
| `codebase` | Semantic search + file read across the workspace | — |
| `terminal` | Execute shell commands | User approval per command |
| `githubRepo` | Read GitHub issues, PRs, commits, and repo metadata | Authenticated GitHub session |
| `editor` | Read content of the currently open editor tab | — |
| `extensions` | Call VS Code extension APIs | Specific extension installed |

> **Security note:** Only include `terminal` if your command genuinely needs to run shell commands. Prompt files with `terminal` access require user confirmation before each command runs.

---

## Prompt File Locations

### GitHub Copilot

| Path | Scope | Notes |
|------|-------|-------|
| `.github/copilot/<name>.prompt.md` | Repository | Tracked in git; shared with team |
| `.vscode/<name>.prompt.md` | Workspace | Tracked in git if workspace is committed |
| `~/.vscode/<name>.prompt.md` | User (global) | Not shared; personal prompts |

### Cursor

| Path | Scope | Notes |
|------|-------|-------|
| `.cursor/commands/<name>.md` | Project | Tracked in git; shared with team |
| `~/.cursor/commands/<name>.md` | User (global) | Not shared; personal commands |

---

## Troubleshooting

### Command not appearing in the picker

**Cursor:** Ensure the `.md` file is in `.cursor/commands/` and the file is saved. Reload the Cursor window (`Cmd+Shift+P` → `Developer: Reload Window`).

**Copilot:** Ensure the file ends in `.prompt.md` and is in a supported location. Reload VS Code. Check that the GitHub Copilot extension is version 1.x or later.

### Frontmatter not parsed correctly

- Verify the `---` delimiters are on their own lines with no leading spaces.
- YAML is whitespace-sensitive; use 2-space indentation for nested values.
- Quote strings that contain colons (`:`) or special YAML characters.

### Script exits with code 1 unexpectedly

1. Run with `--verbose` to see debug output.
2. Check that the input file exists and is readable.
3. Check that the output directory is writable.
4. Use `--dry-run` to preview without side effects.

### Agent ignores parts of the instruction

- Move critical constraints to the top of the instructions body (agents read top-to-bottom).
- Use `>` blockquotes or `**Bold**` to emphasize must-follow rules.
- Keep the total token count reasonable; extremely long command files may be truncated in context.

---

## Additional Resources

- [Cursor Rules & Commands Documentation](https://docs.cursor.com/context/rules)
- [GitHub Copilot Prompt Files](https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-files-experimental)
- [GitHub Copilot Instructions Files](https://code.visualstudio.com/docs/copilot/copilot-customization#_use-instructionfiles-to-add-context)
- [YAML Specification](https://yaml.org/spec/1.2-old/spec.html)

---

## Changelog

### v1.0.0 — 2026-03-24

- Initial template release with Cursor + GitHub Copilot frontmatter support
- Added Python and shell script stubs
- Added basic and advanced examples
