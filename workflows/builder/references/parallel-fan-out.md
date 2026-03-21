# Pattern: Parallel (Fan-Out)

**Source:** `docs/basic/5-subagents.md` - Section 02

---

## Overview

Main agent spawns multiple subagents simultaneously via the Task tool. All run at the same time; results are merged when all complete. Use when subtasks are independent and can proceed without each other's output.

```
Main Agent (fan-out)
├─────────────────┐
↓                 ↓                ↓
agent-A       agent-B          agent-C
(tests)       (docs)           (lint)
└─────────────────┘
      Merge Results
```

---

## When to Use

- Subtasks are fully independent of each other
- Speed matters — parallel cuts total time by the number of branches
- Same operation applied to different targets (e.g. different modules, different files)
- Domain: parallel analysis, multi-module processing, simultaneous reporting

---

## YAML Pattern

```yaml
---
name: orchestrator
description: "Runs [tasks] in parallel. Use when [domain] subtasks are independent."
model: sonnet
readonly: false
---

Run the following in parallel (all at once via Task tool):
- [agent-A] on [target-1]
- [agent-B] for [target-2]
- [agent-C] on [target-3]

Merge all results and report any blocking issues.
```

---

## Context Passing Rules

- Each parallel agent receives its own full context — do not assume they share anything
- Define a merge strategy: how to combine outputs (union, first-wins, ranked, aggregated table)
- Wait for ALL agents to complete before merging

---

## Git Worktrees (for file-writing agents)

For parallel agents that modify files in the same repo, use git worktrees to avoid merge conflicts:

```bash
git worktree add ../branch-a feature/module-a
git worktree add ../branch-b feature/module-b
# Each agent works in its own worktree, merge after all complete
```

---

## Real-World Examples

- Feature scaffold: `backend-agent` + `frontend-agent` + `db-agent` all building simultaneously
- Doc generator: `readme-agent` + `api-doc-agent` + `example-agent` writing in parallel
- Security audit: `auth-scanner` + `payment-scanner` + `data-access-scanner` running together

---

## Anti-Patterns

- Do NOT use parallel when agent B needs agent A's output → use **Sequential** instead
- Do NOT spawn more than 8 concurrent agents — performance degrades beyond this
- Do NOT use parallel for file-writing agents on the same files without git worktrees
