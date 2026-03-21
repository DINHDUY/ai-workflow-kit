# Pattern: Hand-off

**Source:** `docs/basic/5-subagents.md` - Section 03

---

## Overview

One specialized agent completes its task and passes a structured "handoff document" with full context to the next agent. Clean role boundaries — each agent owns one domain entirely and exits cleanly.

The handoff document is the contract between agents. It must be structured and machine-readable so the receiving agent has zero ambiguity.

---

## When to Use

- Clear role boundaries exist between stages (planning vs. coding vs. reviewing)
- Each phase requires deep specialization with different context or tools
- The transition between phases needs an explicit, auditable artifact
- Domain: planning → implementation → verification; research → drafting → editing

---

## YAML Pattern

```yaml
---
name: [phase-1]-agent
description: "Plans [task]. Hands off to [phase-2]-agent when plan is ready."
model: sonnet
readonly: true
---

You are a [role] specialist.

Steps:
1. [Perform phase work]
2. Output a structured HANDOFF DOCUMENT:

## HANDOFF TO: [next-agent-name]
### Context: [summary of what was done]
### Inputs for next phase: [structured list]
### Files to work on: [list]
### Acceptance criteria: [list]
### Risks / constraints: [list]

Signal [next-agent-name] to begin.
```

---

## Handoff Document Structure

Always include in the handoff document:
- **Context**: brief summary of what the current agent produced
- **Inputs**: exact data, file paths, or content the next agent needs
- **Scope**: what is in/out of scope for the next phase
- **Acceptance criteria**: how the next agent knows it succeeded
- **Risks**: anything the next agent should watch out for

---

## Real-World Examples

- `handoff-planner` → `coder-agent`: planner produces spec, coder implements
- `workflow.researcher` → `workflow.planner`: research doc handed off as file path + summary
- `data-extractor` → `report-writer`: extracted data handed off as structured JSON

---

## Anti-Patterns

- Do NOT use vague handoff documents ("implement the thing") — be explicit and structured
- Do NOT skip the handoff document and rely on conversation history — agents don't share context
- Do NOT chain more than 4-5 hand-offs without intermediate checkpoints
