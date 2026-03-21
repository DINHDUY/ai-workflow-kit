# Pattern: Reviewer / Verifier Loop

**Source:** `docs/basic/5-subagents.md` - Section 03

---

## Overview

A dedicated verification agent checks the output of a worker agent and either approves it or triggers a retry cycle with specific fix instructions. Ensures quality gates are enforced automatically.

```
main-agent
    ↓
worker-agent  (implements / produces)
    ↓
verifier-agent  (checks)
    ↓
APPROVED → done
REJECTED → RETRY-INSTRUCTION → worker-agent (loop)
```

---

## When to Use

- Quality must be verified before accepting output
- Work may need multiple iterations to meet standards
- The verification criteria are well-defined and checkable
- Domain: code review, test validation, data quality checks, content moderation

---

## YAML Pattern

```yaml
---
name: verifier
description: "Validates completed work. Use after tasks are marked done to confirm implementations work."
model: sonnet
readonly: true
tools: [Read, Bash, Grep, Glob]
---

You are a verification specialist.

For each completed task:
1. Read the implementation files
2. Run tests: `npm test` or equivalent
3. Check edge cases manually
4. Output one of:
   ✅ APPROVED - [reason]
   ❌ REJECTED - [specific issue]
      RETRY-INSTRUCTION: [exact fix needed]
```

---

## Loop Control

The orchestrator manages the retry loop:
- Maximum retries: set a limit (e.g. 3) to prevent infinite loops
- Pass RETRY-INSTRUCTION verbatim to the worker agent for the next attempt
- On max retries exceeded: escalate to user with full context

```yaml
# Orchestrator loop logic:
1. Call worker-agent with task
2. Call verifier with worker output
3. If REJECTED and retries < 3:
     Pass RETRY-INSTRUCTION back to worker-agent (go to step 1)
   If REJECTED and retries >= 3:
     Report failure to user with last RETRY-INSTRUCTION
4. If APPROVED: continue pipeline
```

---

## Real-World Examples

- Code generation: `coder-agent` → `verifier` (runs tests) → retry if tests fail
- Data extraction: `extractor-agent` → `quality-checker` → retry if schema invalid
- PR review: `implementer` → `pr-reviewer` (checks all criteria) → request changes loop

---

## Anti-Patterns

- Do NOT use an open-ended retry loop without a maximum — set a hard limit
- Do NOT make the verifier also fix the issue — keep verification and fixing separate roles
- Do NOT accept vague REJECTED messages — the RETRY-INSTRUCTION must be actionable
