# Reviewing Agent Skill

An agent skill that reviews other agent skills for conventions, best practices, and platform compatibility.

## Purpose

This skill teaches the AI agent how to systematically review SKILL.md files and skill directories against the Agent Skills Standard and platform-specific conventions (Cursor, Claude Code, etc.).

## Structure

```
reviewing-agent-skill/
├── SKILL.md                        # Main skill definition (agent-facing)
├── README.md                       # This file (human-facing)
└── references/
    └── review-checklist.md         # Full review checklist
```

## What Gets Reviewed

The skill evaluates agent skills across these areas:

| Area | What's Checked |
|------|---------------|
| Metadata | Name format, description quality, trigger keywords |
| Content | Conciseness, terminology, examples |
| Structure | Progressive disclosure, file organization |
| Freedom | Specificity matches task fragility |
| Workflows | Steps, checklists, validation loops |
| Scripts | Error handling, portability, documentation |
| Anti-patterns | Backslashes, vague names, nested refs |
| Compatibility | Cross-platform, Agent Skills Standard |

## Output Format

The skill produces a narrative review summary with:
- Issues categorized by severity (Critical / Suggestion / Minor)
- Positive observations
- Prioritized recommendations
- Platform compatibility assessment

## Full Checklist

The complete detailed review checklist is at [`references/review-checklist.md`](references/review-checklist.md).

## Usage

This skill activates automatically when a user asks to review, audit, evaluate, or check an agent skill. It can also be invoked explicitly.
