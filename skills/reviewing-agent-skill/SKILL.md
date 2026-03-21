---
name: reviewing-agent-skill
description: Review agent skills for conventions, best practices, and platform compatibility following the Agent Skills Standard. Use when the user asks to review, audit, evaluate, or check an agent skill, SKILL.md file, or skill directory for quality, correctness, or compliance.
---

# Reviewing Agent Skills

Review agent skills for quality, conventions, and best practices across platforms (Cursor, Claude Code, and other Agent Skills Standard-compliant clients).

## When to Use

- User asks to review, audit, or evaluate an agent skill
- User wants to check a SKILL.md file for correctness
- User submits a new or updated skill for quality review
- User asks if a skill follows conventions or best practices

## Instructions

### Step 1: Locate and Read the Skill

1. Identify the skill directory and read `SKILL.md`
2. Read any referenced files (`scripts/`, `references/`, `templates/`)
3. Note the target platform(s) if specified

### Step 2: Review Against Key Areas

Evaluate the skill across these areas, noting issues found:

#### A. Metadata & Frontmatter

- **name**: Present, max 64 chars, lowercase/numbers/hyphens only, matches directory name, no reserved words ("anthropic", "claude")
- **description**: Present, max 1024 chars, third person, specific, includes WHAT it does and WHEN to use it, has trigger keywords

#### B. Content Quality

- SKILL.md body under 500 lines
- Concise — assumes agent intelligence, no over-explanation
- Consistent terminology (no mixing synonyms)
- No time-sensitive information (or properly marked as deprecated)
- Examples are concrete, not abstract

#### C. Structure & Organization

- Progressive disclosure: SKILL.md is the overview, details in separate files
- File references one level deep (no deeply nested chains)
- Forward slashes in all file paths (no backslashes)
- Standard subdirectories: `scripts/`, `references/`, `templates/`, `examples/`
- Descriptive file names

#### D. Degrees of Freedom

- High freedom (text instructions) for flexible tasks
- Medium freedom (pseudocode/templates) for preferred patterns
- Low freedom (exact scripts) for fragile/critical operations
- Specificity matches task fragility

#### E. Workflows & Validation

- Complex tasks broken into clear sequential steps
- Copyable checklists for progress tracking
- Feedback loops for critical operations (validate → fix → repeat)
- Conditional workflows guide decision points clearly

#### F. Scripts & Code (if applicable)

- Scripts solve problems (not punting to agent)
- Error handling is explicit and helpful
- No magic numbers or undocumented constants
- Required packages explicitly listed
- Clear execution intent: "run this" vs "read this for reference"
- Platform-agnostic, portable paths

#### G. Anti-Patterns (verify NONE present)

- No Windows-style paths (backslashes)
- No overwhelming number of options without a default
- No vague or generic names/descriptions
- No deeply nested file references
- No inconsistent terminology
- Directory name doesn't start with `.` or `_`

#### H. Platform Compatibility

- Agent Skills Standard compliant SKILL.md format
- Description enables semantic intent matching
- Name is unique in skill registry
- No hardcoded platform assumptions
- Relative, portable file paths

### Step 3: Produce the Review Summary

Write a narrative review summary using this structure:

```
## Skill Review: [skill-name]

### Overview
Brief description of the skill's purpose and scope.

### Issues Found

**Critical** (must fix):
- [Issue description and recommended fix]

**Suggestions** (should fix):
- [Issue description and recommended improvement]

**Minor** (nice to have):
- [Issue description and optional enhancement]

### What's Done Well
- [Positive observations about the skill]

### Recommendations
Prioritized list of next steps to improve the skill.

### Platform Compatibility
- Single-platform / Multi-platform / Agent Skills Standard compliant
- Notes on platform-specific considerations
```

If no issues are found in a severity category, omit that category.

### Step 4: Offer to Fix

After presenting the review, ask the user if they'd like help fixing any of the identified issues.

## Review Depth

Adjust review depth based on context:

- **Quick review**: Metadata + anti-patterns + content quality (for small/simple skills)
- **Standard review**: All areas A through H (default)
- **Deep review**: Standard + cross-platform testing recommendations + evaluation-driven development suggestions

## Full Checklist Reference

For the complete detailed checklist with all review criteria, see [references/review-checklist.md](references/review-checklist.md).
