# Pattern: Hierarchical (Nested Agents)

**Source:** `docs/basic/5-subagents.md` - Section 03

---

## Overview

A subagent itself acts as an orchestrator and spawns its own sub-subagents. Creates a tree of agents with clear domain ownership at each tier.

```
Tier 1: project-manager (top orchestrator)
  ├── Tier 2: backend-lead (domain orchestrator)
  │     ├── Tier 3: db-schema-agent
  │     ├── Tier 3: api-designer
  │     └── Tier 3: auth-specialist
  └── Tier 2: frontend-lead (domain orchestrator)
        ├── Tier 3: component-builder
        └── Tier 3: stylist-agent
```

---

## When to Use

- The problem is too large for a flat set of agents
- Clear domain boundaries exist at multiple levels (project → module → task)
- Different domains can proceed independently (backend team vs. frontend team)
- Domain: large codebase refactors, multi-module builds, cross-team coordination simulations

---

## YAML Pattern

```yaml
---
name: domain-lead
description: "Coordinates [domain] work. Spawns specialized agents for each [domain] subtask."
model: sonnet
---

You are the [domain] lead coordinator.

1. Spawn in parallel:
   - [specialist-agent-1] for [subtask-1]
   - [specialist-agent-2] for [subtask-2]
   - [specialist-agent-3] for [subtask-3]

2. Merge results from all specialists
3. Return consolidated [domain] output to parent orchestrator
```

---

## Depth Limits

- **Maximum 2-3 tiers** — performance degrades beyond this
- **Maximum 8 concurrent subagents** at any single tier
- Keep the top orchestrator thin — it should coordinate, not do domain work

---

## Context Passing

- Each tier passes its own context to its children explicitly
- The top orchestrator passes high-level topic/goal
- Each domain lead enriches context with domain-specific details before passing to specialists
- Results bubble back up tier by tier

---

## Real-World Examples

- Codebase refactor: `refactor-lead` → `[module]-lead` × N → `refactor-worker` × M per module
- Multi-language docs: `docs-lead` → `[language]-lead` → `[section]-writer` per language
- Security audit: `audit-lead` → `[layer]-auditor` (auth/data/network) → `[component]-checker`

---

## Anti-Patterns

- Do NOT go deeper than 3 tiers — exponential context explosion
- Do NOT make every tier an orchestrator — leaf agents should specialize, not coordinate
- Do NOT use hierarchical when a flat sequential or parallel pattern is sufficient
