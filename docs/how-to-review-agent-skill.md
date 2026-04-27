# How to Review an Agent Skill

The full review checklist is maintained as part of the **reviewing-agent-skill** skill:

- **Checklist**: [`skills/reviewing-agent-skill/references/review-checklist.md`](../skills/reviewing-agent-skill/references/review-checklist.md)
- **Skill definition**: [`skills/reviewing-agent-skill/SKILL.md`](../skills/reviewing-agent-skill/SKILL.md)

## Quick Start

1. Open the skill you want to review
2. Ask the agent: *"Review this skill"* (the reviewing-agent-skill will activate automatically)
3. The agent will evaluate the skill against the checklist and produce a summary with issues categorized by severity

## Review Areas

The checklist covers:

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

See the [full checklist](../skills/reviewing-agent-skill/references/review-checklist.md) for all criteria.
