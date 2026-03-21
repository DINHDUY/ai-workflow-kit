# Pattern Selection Guide

**Source:** `docs/basic/5-subagents.md` - Section 07

Use this decision tree to select the right pattern(s) when designing a multi-agent system.

---

## Decision Tree

```
Is the task complex with multiple steps?
├── YES → Does it require isolated context / specialized knowledge per step?
│         ├── YES → Are subtasks independent of each other?
│         │         ├── YES → PARALLEL (fan-out, simultaneous execution)
│         │         │         See: parallel-fan-out.md
│         │         └── NO  → Does output of A feed into B?
│         │                   ├── YES → SEQUENTIAL / HAND-OFF (pipeline)
│         │                   │         See: sequential-pipeline.md or handoff.md
│         │                   └── NO  → HIERARCHICAL (orchestrator spawns sub-orchestrators)
│         │                             See: hierarchical-nested.md
│         └── NO  → Is it a repeatable one-purpose action?
│                   ├── YES → Use a SKILL (.cursor/skills/) not a subagent
│                   └── NO  → Single subagent with clear scoped prompt
└── NO  → Is it a single, one-off action?
          ├── YES → Is it repeatable/reusable?
          │         ├── YES → Use a SKILL or slash command
          │         └── NO  → Handle inline in main agent
          └── NO  → Is it long-running / non-blocking?
                    ├── YES → BACKGROUND subagent (is_background: true)
                    │         See: background-non-blocking.md
                    └── NO  → RESUMABLE subagent (with agent ID for continuation)
                              See: resumable-stateful.md
```

---

## Pattern Quick-Reference

| Pattern | Best For | Key Signal |
|---------|----------|------------|
| **Sequential** | Staged pipelines, transformations | Output of A → input of B |
| **Parallel** | Independent tasks, speed | Subtasks don't need each other |
| **Hand-off** | Clean role boundaries | One agent exits, next takes over |
| **Reviewer Loop** | Quality gates, iteration | Work needs verification + retry |
| **Hierarchical** | Large problems, domain teams | Too big for flat agents |
| **Background** | Monitoring, non-blocking work | Should not interrupt user |
| **Resumable** | Long-running, interruptible | May span hours or be paused |

---

## Combining Patterns

Most real workflows combine patterns. Common combinations:

- **Sequential + Parallel**: pipeline where one phase fans out (e.g. research → parallel analysis → synthesis)
- **Sequential + Reviewer Loop**: pipeline with a quality gate at one or more stages
- **Hierarchical + Parallel**: top orchestrator fans out to domain leads, each lead fans out to specialists
- **Hand-off + Background**: long planning phase hands off to background implementation

---

## Pattern Count Guidelines

- Start with **2-3 agents**. Add more only when there is a genuinely distinct use case.
- **5-8 agents** is the typical range for a complete domain workflow system.
- **Max 8 concurrent agents** at any single fan-out point.
- **Max 2-3 tiers** for hierarchical patterns.

---

## Model Selection by Pattern Role

| Role | Model | Reason |
|------|-------|--------|
| Orchestrator | `sonnet` | Complex coordination, multi-step reasoning |
| Web researcher / browser | `sonnet` | Browsing, page parsing, synthesis |
| Keyword extractor / formatter | `fast` | Simple reasoning, no web access |
| Verifier / quality checker | `sonnet` | Needs to run tests and reason about results |
| Background monitor | `fast` | Long-running, cost-sensitive |
| Planner / architect | `sonnet` | Complex design decisions |
