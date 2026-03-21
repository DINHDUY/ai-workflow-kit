# Pattern: Background (Non-blocking)

**Source:** `docs/basic/5-subagents.md` - Section 02

---

## Overview

Runs independently while you continue working. Does not block the main thread. State is persisted to disk at `~/.cursor/subagents/`. Used for long-running monitoring, analysis, or generation tasks that shouldn't interrupt the user.

---

## When to Use

- Task is long-running and doesn't require synchronous response
- User should be able to continue working while the agent runs
- Monitoring, watching, or periodic checking tasks
- Domain: test watchers, log analyzers, CI monitors, doc generators running on save

---

## YAML Pattern

```yaml
---
name: bg-monitor
description: "Monitors [target] and logs [events]. Use immediately after [trigger condition]."
model: fast
is_background: true
readonly: true
---

You run [task] silently and report [output] via a summary.
Never block the main thread.

Checkpoint progress to ~/.cursor/subagents/[agent-name]-state.json after each [unit of work].
```

---

## State Location

Background agents write state to `~/.cursor/subagents/` during execution. Read from this location to check progress or resume.

---

## Invocation

```bash
# CLI spawn (headless)
cursor-agent "monitor test suite" --agent bg-monitor --headless

# Capture agent ID for status checks
cursor-agent "run analysis" --agent bg-monitor --output-id > agent_id.txt
```

---

## Real-World Examples

- `test-watcher`: runs tests after each file save, logs failures silently
- `ci-assistant`: monitors CI output, maps failures to source files
- `log-analyzer`: tails application logs and surfaces anomaly patterns
- `doc-generator`: regenerates docs on file change events

---

## Anti-Patterns

- Do NOT use background for tasks that the main workflow needs to synchronously depend on
- Do NOT forget to checkpoint — if the agent crashes without state, all progress is lost
- Do NOT use expensive models (sonnet/opus) for background agents — prefer `fast`
