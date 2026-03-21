# Workflow Builder

Source workflow: [`SPEC.md`](SPEC.md)

---

## Overview

5 Cursor subagents that automate the 4-phase meta-workflow for building domain-specific multi-agent systems: **research → plan → build agents → document**. A fifth orchestrator agent coordinates all phases end-to-end.

---

## Workflow-to-Agent Mapping

| Workflow Step | Agent |
|---|---|
| Step 1 - Research a domain workflow | ``workflow.researcher`` |
| Step 2 - Plan subagents | ``workflow.planner`` |
| Step 3 - Build the agent files | ``workflow.builder`` |
| Step 4 - Create README | ``workflow.documenter`` |
| All phases - Pipeline coordination | ``workflow.orchestrator`` |

---

## Pipeline

```
User: "for [who] using [purpose]" + project name + output folder
        |
        v
workflow.researcher
  - WebSearch + WebFetch to research the domain workflow
  - Structured output: step-by-step workflow, companion tools, API access
  - Saves: workflows/[project]/[name].md
        |
        v
workflow.planner
  - Reads research markdown
  - Maps workflow steps to specialized agents
  - Designs orchestrator + subagent specs (model, readonly, tools, I/O)
  - Saves: workflows/[project]/[name]-plan.md
        |
        v
workflow.builder
  - Reads plan markdown
  - Creates .cursor/agents/[name].md files with YAML frontmatter + full instructions
  - Follows existing agent file patterns
        |
        v
workflow.documenter
  - Reads plan + agent list
  - Creates workflows/[project]/README.md
  - Includes: what it does, agent list, invocation examples
```

---

## Agent Specifications

### ``workflow.orchestrator``
- **Model:** sonnet
- **Readonly:** false
- **Role:** Single entry point. Accepts a topic/purpose description, project name, and output folder. Sequences all 4 phases explicitly, passes context between agents, and presents phase summaries.
- **Input:** "for [who] using [purpose]", project name, output folder
- **Output:** Populated docs folder + built agents + README

---

### ``workflow.researcher``
- **Model:** sonnet
- **Readonly:** false
- **Tools:** WebSearch, WebFetch
- **Role:** Researches the target domain's workflow using web search and fetching. Produces a structured deep-dive markdown document.
- **Output structure:**
  - Step-by-step workflow with sub-steps
  - Companion tools table (tool, what it does, access)
  - Programmatic/API access section with code examples
  - Best practices and tips
- **Saves to:** `workflows/[project]/[name].md`

---

### ``workflow.planner``
- **Model:** sonnet
- **Readonly:** false
- **Role:** Reads the research markdown and decomposes the workflow into a set of specialized agents plus one orchestrator. Specifies model, readonly setting, tools, inputs, outputs, and key design decisions for each.
- **Output structure:**
  - Workflow-to-agent mapping table
  - Pipeline ASCII diagram
  - Per-agent specification (model, readonly, role, input, output)
  - Key design decisions
  - Dependencies
  - Invocation examples
- **Saves to:** `workflows/[project]/[name]-plan.md`

---

### ``workflow.builder``
- **Model:** sonnet
- **Readonly:** false
- **Role:** Reads the plan markdown and creates each `.cursor/agents/[name].md` file. Follows the established pattern of existing agents in the project.
- **Agent file pattern:**
  ```yaml
  ---
  name: [agent-name]
  description: "[one-sentence description for agent discovery]"
  model: [fast|sonnet]
  readonly: [true|false]
  ---

  [Full instruction body with H2 sections for each major task]
  ```
- **Creates:** one file per agent specified in the plan

---

### ``workflow.documenter``
- **Model:** fast
- **Readonly:** false
- **Role:** Creates a concise, user-friendly README.md for the agent system. Covers what the system is for, the agent list with descriptions, and practical invocation examples.
- **Output structure:**
  - Project title and one-paragraph summary
  - What it does
  - Agent list with descriptions
  - How to use (full pipeline + individual agents)
  - Example invocations
- **Saves to:** `workflows/[project]/README.md`

---

## File Layout

```
.cursor/agents/
  workflow.orchestrator.md
  workflow.researcher.md
  workflow.planner.md
  workflow.builder.md
  workflow.documenter.md
```

---

## Key Design Decisions

1. **File-based handoff** - Each phase saves its output to a `.md` file; the next agent reads from that file path. This is the reliable context transfer mechanism since agents share no conversation history.
2. **Explicit context passing** - The orchestrator always passes topic, file paths, and prior outputs explicitly to each downstream agent.
3. **Builder follows existing patterns** - ``workflow.builder`` is explicitly instructed to match the YAML frontmatter and instruction style of existing `.cursor/agents/*.md` files in the project.
4. **Researcher scopes deeply** - Output should match the depth and structure of `workflows/lei/ssrn.md` (companion tools, programmatic access, step-by-step details).
5. **Orchestrator is the single entry point** - Users invoke ``workflow.orchestrator`` with a one-liner; all file naming, folder creation, and sequencing is handled automatically.

---

## Invocation Examples

**Full pipeline:**
```
Use workflow.orchestrator to create agents for the workflow that quant researchers use to monitor equity factor performance
```

**Research only:**
```
Use workflow.researcher to research the workflow that data engineers use to build RAG pipelines
```

**Plan from existing research:**
```
Use workflow.planner to plan agents from the research at workflows/my-project/my-research.md
```

**Build from existing plan:**
```
Use workflow.builder to build agents from the plan at workflows/my-project/my-plan.md
```

**Document existing agents:**
```
Use workflow.documenter to create a README for the agents described in workflows/my-project/my-plan.md
```