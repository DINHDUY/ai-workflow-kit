# Pattern: Resumable (Stateful)

**Source:** `docs/basic/5-subagents.md` - Section 03

---

## Overview

Long-running agents that checkpoint their progress and can be paused and resumed using a persistent agent ID. Designed for multi-hour or multi-day tasks that may be interrupted.

---

## When to Use

- Task spans too much work for a single session (large codebase analysis, bulk processing)
- Work must survive interruptions (system restarts, context window limits)
- You need to inspect intermediate state before continuing
- Domain: database migrations, large-scale refactors, bulk data processing, long research tasks

---

## YAML Pattern

```yaml
---
name: [agent-name]
description: "Analyzes [target]. Long-running. Resumes from last checkpoint if given an agent ID."
model: sonnet
is_background: true
---

Checkpoint your progress after each [unit of work].
Write status to ~/.cursor/subagents/[agent-name]-state.json:
{
  "last_completed": "[item identifier]",
  "processed_count": N,
  "results_so_far": [...],
  "next_item": "[item identifier]"
}

On startup: check if ~/.cursor/subagents/[agent-name]-state.json exists.
If yes: resume from last_completed. If no: start from beginning.
```

---

## CLI Usage

```bash
# Spawn and capture agent ID
cursor-agent "run migration analysis" \
  --agent migration-analyst \
  --output-id > agent_id.txt

# Check status (read state file)
cat ~/.cursor/subagents/migration-analyst-state.json

# Resume with preserved context
cursor-agent "continue where you left off" \
  --resume $(cat agent_id.txt)
```

---

## Checkpoint Design

Good checkpoint state includes:
- **last_completed**: identifier of the last successfully processed item
- **processed_count**: progress counter
- **results_so_far**: accumulated results (or file path to results file for large data)
- **next_item**: what to process next on resume

---

## Real-World Examples

- `migration-analyst`: analyzes 1000+ DB migration files, checkpoints after each file
- `bulk-pdf-processor`: processes a folder of PDFs, resumes from last processed file
- `codebase-archaeologist`: maps all usages of deprecated patterns across large monorepo

---

## Anti-Patterns

- Do NOT store large result sets in the checkpoint JSON — write to a separate file and store the path
- Do NOT rely on resumable pattern for short tasks (< 5 minutes) — unnecessary overhead
- Do NOT skip the startup checkpoint check — without it, resume is meaningless
