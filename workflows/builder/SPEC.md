# Workflow Builder - Workflow

Step by step workflow to build new multi-agent workflows

## Step 1 - Ask AI Agent (Cursor, Claude, Copilot,...) (**ASK** Mode/High Think Model) research a workflow 

> **Template**: Research a workflow  that [for who are the users of this workflow] use [for what purposes]

**Examples**

```prompt
Research a workflow that quant researchers use to search on SSRN website for relate papers
```

```prompt
Research a workflow that desktop support engineers use to provide support for Windows applications
```

> **Best Practices**: Save the research output to a *.md to review and manual edit if needed (workflows/lei/ssrn.md).

## Step 2 - Ask AI Agent (Cursor, Claude, Copilot,...) (**PLAN** Mode/High Thinking Model) for a plan to create subagents

> **Template**: Plan for creating subagents for the workflow describe in [the research output to a *.md]

```prompt
Plan for creating subagents for the workflow describes in workflows/lei/ssrn.md
```

## Step 3 - Ask AI Agent (Cursor, Claude, Copilot,...) (**AGENT** Mode/High Thinking Model) to write the plan first and then build the agents

> **Template**: First write the plan to [plan output], and then build the agents

```prompt
First write the plan to workflows/ssrn/PLAN.md, and then build the agents
```

## Step 4 - Ask AI Agent (Cursor, Claude, Copilot,...) to create a (**AGENT** Mode/High Thinking Model) README.md file project

> **Template**: Add a README.md for the project, include that it is for and how to use it with some simple examples. Keep it simple and concise.

```prompt
Add a README.md for the project, include that it is for and how to use it with some simple examples. Keep it simple and concise.
```

## Step 5 - TEST TEST and TEST the workflow

> **Refine** the workflow until objectives are sastified.

EOF