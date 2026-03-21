# Pattern: Sequential (Pipeline)

**Source:** `docs/basic/5-subagents.md` - Section 02

---

## Overview

One agent finishes, its output feeds directly into the next. Use when stages have strict dependencies — each stage consumes the previous stage's output as its primary input.

```
Main Agent
 delegates task + context
→ agent-1        (e.g. planner)
 returns output
→ agent-2        (e.g. coder)
 returns output
→ agent-3        (e.g. reviewer)
 returns verdict
→ Final Result
```

---

## When to Use

- Output of step A is required input for step B
- Tasks must run in strict order (planning → coding → testing)
- Each stage transforms the artifact produced by the prior stage
- Domain: research pipelines, code generation pipelines, document processing chains

---

## YAML Pattern

```yaml
---
name: orchestrator
description: "Coordinates a multi-stage pipeline. Use for [domain] workflows."
model: sonnet
readonly: false
---

You are a pipeline orchestrator.

Sequence:
1. Use [agent-1] to [phase 1 task] — pass [inputs]
2. Pass [agent-1 output] → [agent-2] to [phase 2 task]
3. Pass [agent-2 output] → [agent-3] to [phase 3 task]
4. Compile and return consolidated output
```

---

## Context Passing Rules

- Pass ALL required context explicitly at each step — agents share no conversation history
- Include: topic, prior output (full text or file path), original inputs
- Never assume a downstream agent has seen previous messages

---

## Real-World Examples

- SSRN paper discovery: `keyword-definer` → `paper-searcher` → `citation-explorer` → `bulk-screener` → `paper-summarizer`
- PR review: `lint-agent` → `logic-reviewer` → `security-scanner` → `pr-summary`
- Doc pipeline: `researcher` → `planner` → `builder` → `documenter`

---

## Anti-Patterns

- Do NOT use sequential when stages are independent of each other → use **Parallel (Fan-Out)** instead
- Do NOT chain more than 6-8 agents in a single pipeline — split into sub-pipelines
