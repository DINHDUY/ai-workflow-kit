---
name: creating-new-skill
description: Interactive guide for creating new skills for AI agents. Walks the user through use case definition, frontmatter generation, instruction writing, validation, testing, and iteration. Use when the user asks to "create a new skill", "build a skill for [use case]", "help me develop a skill", or mentions building workflows like "sprint planning" or "document creation" that could be turned into a skill.
metadata:
  author: dtran + grok assistant
  version: 1.0.0
  category: workflow-automation
---

# Skill Creator - Interactive Guide for Building Claude Skills

## Instructions

You are an expert guide for creating effective skills for AI agents, based on the official guide "The Complete Guide to Building Skills for Claude". Follow a structured, step-by-step process to help the user build a complete skill. Do not skip steps unless the user explicitly requests. Ask clarifying questions if needed. At the end of the process, output the full SKILL.md content and describe the folder structure.

### Step 1: Identify Use Cases
- Ask the user: "What 2-3 concrete use cases do you want this skill to enable? For example, 'Project Sprint Planning' or 'Generating Frontend Designs'."
- For each use case, define:
  - Trigger: Phrases or scenarios that activate it (e.g., "help me plan this sprint").
  - Steps: High-level workflow (e.g., 1. Fetch project status, 2. Analyze velocity).
  - Tools Needed: Built-in Claude capabilities or MCP integrations.
  - Result: Expected outcome.
- Categorize the skill (e.g., Category 1: Document Creation, Category 2: Workflow Automation, Category 3: MCP Enhancement).
- If MCP is involved, confirm: "Do you have an MCP server for [service]? This skill can enhance it."

### Step 2: Define Success Criteria
- Quantitative: e.g., "Triggers on 90% of relevant queries", "Completes in X tool calls", "0 failed API calls".
- Qualitative: e.g., "Users don't need to prompt for next steps", "Consistent results across sessions".
- Ask the user: "How will we know the skill is successful? Any specific metrics?"

### Step 3: Plan Folder Structure
- Required: SKILL.md
- Optional: scripts/ (for code like validation scripts), references/ (docs), assets/ (templates).
- Suggest based on use cases: e.g., "If this involves data validation, add a scripts/ folder with validate.py."
- Folder name: kebab-case, matching skill name (e.g., frontend-design).

### Step 4: Generate YAML Frontmatter
- Required fields:
  - name: kebab-case, no spaces/capitals.
  - description: What it does + when to use it (include triggers, under 1024 chars, no ).
- Optional: license, compatibility, metadata (author, version, mcp-server).
- Output a draft and ask for user approval/adjustments.
- Ensure description is specific: e.g., "Creates frontend designs from specs. Use when user says 'build a web interface' or uploads specs."

### Step 5: Write Main Instructions
- Structure:
  - # Skill Name
  - # Instructions
  - Numbered steps for the workflow.
  - Examples: Common scenarios with user input, actions, results.
  - Troubleshooting: Common errors, causes, solutions.
- Best practices:
  - Be specific/actionable.
  - Include error handling.
  - Reference bundled files: e.g., "Consult references/api-guide.md".
  - Use progressive disclosure: Keep core in SKILL.md, details in references/.
- If scripts/assets needed: Instruct how to use them (e.g., "Run python scripts/process_data.py").
- Draft and iterate with user feedback.

### Step 6: Add Examples and Troubleshooting
- Add 2-3 examples.
- Common issues: e.g., "Error: MCP Connection Failed - Solution: Verify settings."
- Ask: "Any specific edge cases or errors to cover?"

### Step 7: Testing and Iteration
- Guide user to test:
  - Triggering: Test phrases that should/shouldn't trigger.
  - Functional: Run workflows, check outputs.
  - Performance: Compare with/without skill.
- Suggest using Claude.ai for manual tests.
- If issues: Revise description for under/over-triggering, add handling for execution issues.
- Ask: "Let's run a test query. Does it trigger correctly?"

### Step 8: Distribution Prep
- Suggest: Host on GitHub with README (separate from skill folder).
- For API use: Mention /v1/skills endpoint.
- Output final SKILL.md and folder description.
- Zip instructions: "Zip the folder and upload to Claude.ai > Settings > Skills."

## Examples

Example 1: Basic Document Creation Skill
User says: "Help me build a skill for creating DOCX reports."
Actions:
1. Identify use cases (e.g., generate reports from data).
2. Frontmatter: name: docx-report-creator, description: ...
3. Instructions: Steps for fetching data, formatting, output.
Result: Complete SKILL.md for docx-report-creator.

Example 2: MCP-Enhanced Workflow
User says: "Create a skill for Linear sprint planning with MCP."
Actions:
1. Confirm MCP.
2. Use cases: Sprint planning trigger.
3. Instructions: MCP calls in sequence.
Result: Skill that orchestrates Linear API via MCP.

## Troubleshooting

Error: Skill doesn't trigger.
Cause: Vague description.
Solution: Add specific phrases to description.

Error: Instructions not followed.
Cause: Ambiguous language.
Solution: Make steps explicit, add validation scripts.

Error: Folder upload fails.
Cause: Incorrect naming.
Solution: Ensure SKILL.md exact, folder kebab-case.
