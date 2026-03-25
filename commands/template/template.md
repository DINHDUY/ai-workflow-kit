---
# ─── Cursor Agent Command ────────────────────────────────────────────────────
# Install to: .cursor/commands/template.md
# Invoked as: /template <user input>
description: "Replace with a clear one-sentence description of what this command does and when to invoke it."
# alwaysApply: false   # Set to true to automatically apply this command in every session

# ─── GitHub Copilot Prompt File ──────────────────────────────────────────────
# Install to: .github/copilot/commands/template.prompt.md
# mode: agent          # agent | ask | edit  (default: ask)
# tools:
#   - codebase         # Search and read files in the workspace
#   - terminal         # Run shell commands
#   - githubRepo       # Query GitHub issues, PRs, and commits
#   - editor           # Read the currently open editor content
#   - extensions       # Use VS Code extension APIs
# ─────────────────────────────────────────────────────────────────────────────
---

# command-name

<!-- Replace "command-name" with your actual command name (lowercase, hyphens). -->

## Overview

A clear description of what this command does, why it exists, and when to use it. Keep it to two or three sentences so the agent understands purpose and scope at a glance.

> **Tip:** Be explicit about what this command does *not* handle so the agent avoids scope creep.

## Steps

1. **Gather information**
   - Read any details the user already provided after the `/command-name` invocation
   - Ask only for what is missing — do not re-ask what was already given:
     - **Required input** — description of what the user must supply (e.g. file path, topic, issue number)
     - **Optional input** — parameters that have safe defaults (document the defaults)

2. **Validate prerequisites**
   - Check for required tools, dependencies, or environment variables
   - Provide the exact install/setup command if a prerequisite is missing:
     ```bash
     # Example dependency check
     command -v my-tool &>/dev/null || echo "Install my-tool: https://example.com/install"
     ```

3. **Execute the task**
   - Describe the concrete actions the agent takes in order
   - Include exact commands, file paths, or API calls:
     ```bash
     # Primary command
     scripts/shell/template.sh --input "$INPUT" --output "$OUTPUT"
     ```
     ```bash
     # Alternative: Python script variant
     python scripts/python/template_script.py "$INPUT"
     ```
   - Document any branching logic (e.g. "if X then do Y, otherwise do Z")

4. **Verify the result**
   - State how to confirm success (exit code, output pattern, file existence)
   - Show expected output:
     ```
     ✓ Operation completed successfully.
     Output written to: <path>
     ```
   - On failure: describe how to diagnose (flags, logs, verbose mode) and what corrective action to suggest

5. **Report back**
   - Summarize what was done: files written, commands run, any warnings
   - Suggest logical next steps if applicable

## Configuration

| Setting | Required | Default | Description |
|---------|----------|---------|-------------|
| `INPUT` | Yes | — | Path or value to process |
| `OUTPUT` | No | `./output` | Where to write results |
| `VERBOSE` | No | `false` | Enable detailed logging |
| `DRY_RUN` | No | `false` | Preview actions without executing |

<!-- Remove this section if the command needs no configuration. -->

## Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--input <path>` | `-i` | — | Input file or value |
| `--output <path>` | `-o` | `./output` | Output destination |
| `--dry-run` | | `false` | Show what would happen without writing |
| `--verbose` | `-v` | `false` | Enable debug output |
| `--force` | `-f` | `false` | Overwrite existing files |

## Examples

See `examples/` for complete annotated examples. Quick reference:

### Basic usage

```
/command-name path/to/input.txt
```

### Specify output path

```
/command-name path/to/input.txt --output path/to/output.txt
```

### Dry run — preview without executing

```
/command-name path/to/input.txt --dry-run
```

### Verbose mode — show detailed progress

```
/command-name path/to/input.txt --verbose
```

## References

For detailed documentation, see:

- [`references/reference.md`](references/reference.md) — extended specifications, edge cases, and troubleshooting — loaded on demand

## Notes

- Keep this file focused on *what the agent should do*; move verbose technical specs to `references/`
- Scripts in `scripts/` are self-contained with `--help` flags and helpful error messages
- Examples in `examples/` use real-world inputs to illustrate expected behaviour
