# How to Use the Workflow Builder to Generate New Workflows

So you have a routine -- something you and your teammates do over and over -- and you would love an AI assistant to handle the boring parts. Good news: that is exactly what the **Workflow Builder** is for. You describe the routine in plain English, and the Builder creates a small team of AI agents in Cursor that will run it for you.

This guide walks you from zero to a working multi-agent workflow. No AI engineering background required.

## What is the Workflow Builder?

The Workflow Builder is a **meta-workflow** -- it is a workflow that builds other workflows. Think of it as a small factory inside Cursor. You tell it what you want automated, and it produces a complete set of specialized AI agents tailored to that task.

It runs in **four phases**:

1. **Research** -- studies how people actually do the work today (tools, steps, gotchas).
2. **Plan** -- designs the team of agents needed to automate it.
3. **Build** -- writes the agent files and drops them into your project.
4. **Document** -- creates a README so your teammates know how to use them.

Under the hood, five agents do the work:

| Agent | What it does |
|---|---|
| `workflow.orchestrator` | The foreman. Runs the whole pipeline end-to-end. |
| `workflow.researcher` | Searches the web and writes up the domain workflow. |
| `workflow.planner` | Designs the agent team and their responsibilities. |
| `workflow.builder` | Writes the actual agent files. |
| `workflow.documenter` | Writes the README. |

You usually only need to talk to the orchestrator. It talks to the others.

## Before You Begin

You will need:

- **Cursor IDE** installed and signed in.
- A **project folder** open in Cursor (can be empty -- a new folder is fine).
- **`uv`** installed (a Python tool installer). If you do not have it: [Install uv](https://docs.astral.sh/uv/getting-started/installation/).
- An **internet connection** (the researcher agent uses web search).

That is it. You do not need to know Python, YAML, or anything about agent frameworks.

## Step 1 -- Install the Builder into Your Project

Open Cursor''s integrated terminal (`` Ctrl + ` `` on Windows, `` Cmd + ` `` on Mac) and run:

```bash
uvx --from git+https://github.com/DINHDUY/ai-workflow-kit-py ^
    add-workflows builder --output .cursor/agents
```

> **Mac/Linux users:** replace the trailing `^` (a Windows line-continuation character) with a backslash `\`, or just put the whole command on one line.

This downloads five agent files into `.cursor/agents/`:

```
.cursor/agents/
  workflow.orchestrator.md
  workflow.researcher.md
  workflow.planner.md
  workflow.builder.md
  workflow.documenter.md
```

Cursor detects them automatically -- no restart needed.

## Step 2 -- A Quick Primer on Talking to Subagents in Cursor

Before we run the Builder, here is how Cursor subagents work. You have **two ways** to invoke one from the chat:

**Option A -- the slash shortcut (explicit):**

Type `/` in the chat input, then start typing the agent name. Cursor pops up a picker. Select it and type your request.

```
/workflow.orchestrator Research and build agents for monitoring equity factor performance
```

**Option B -- natural language (Cursor picks the right one):**

Just describe what you want and mention the agent by name. Cursor delegates automatically.

```
Use the workflow.orchestrator subagent to research and build agents for
monitoring equity factor performance.
```

Both work. The slash form is tidier when you know exactly which agent you want. The natural-language form is friendlier when you are not sure.

> **Good to know:** Each subagent runs in its **own isolated context window**. That means your main chat stays clean -- only the final summary bubbles back up to you.

## Step 3 -- Run the Full Pipeline

This is the easy path, and it is the one we recommend for your first try. Just tell the orchestrator what you want.

**The template:**

```
/workflow.orchestrator Research and build agents for [what the workflow does and who uses it]
Project name: [short-identifier], Output: workflows/[folder]/
```

**A real example** -- let us build a workflow for quant researchers who search SSRN for academic papers:

```
/workflow.orchestrator Research and build agents for quant researchers searching SSRN papers
Project name: ssrn, Output: workflows/ssrn/
```

Hit Enter and sit back. The orchestrator will:

1. Kick off the **researcher** -- it searches the web and writes `workflows/ssrn/ssrn.md`.
2. Hand off to the **planner** -- it designs the agents and writes `workflows/ssrn/ssrn-plan.md`.
3. Hand off to the **builder** -- it creates files in `.cursor/agents/` like `ssrn.orchestrator.md`, `ssrn.searcher.md`, etc.
4. Hand off to the **documenter** -- it writes `workflows/ssrn/README.md`.

Along the way, you will see phase summaries in the chat. When it finishes, you have a brand-new workflow ready to use.

**Try your shiny new workflow:**

```
/ssrn.orchestrator Find recent papers on machine learning in factor investing
```

## What You Get

After a successful run, your project looks like this:

```
workflows/ssrn/
  |-- ssrn.md            # Research document (the "how it is done today" writeup)
  |-- ssrn-plan.md       # Agent architecture plan
  `-- README.md          # Usage documentation

.cursor/agents/
  |-- ssrn.orchestrator.md
  |-- ssrn.searcher.md
  |-- ssrn.ranker.md
  `-- ...                # One file per agent the planner designed
```

The markdown files are **yours to edit**. If the researcher missed a nuance or the planner picked an agent name you do not love, open the file and change it. They are just text.

## Running Individual Phases (When You Want More Control)

Sometimes you do not need the whole pipeline. Maybe you already have a research write-up and just want agents built from it. Each phase is available as its own agent.

### Research only

Good for scoping: "I want to understand this workflow before committing."

```
/workflow.researcher Research the workflow that data engineers use to build RAG pipelines
Save to: workflows/rag/rag.md
```

### Plan from an existing research doc

You wrote (or edited) the research yourself and want a plan.

```
/workflow.planner Read workflows/rag/rag.md and design an agent system
Save plan to: workflows/rag/rag-plan.md
```

### Build from an existing plan

You hand-wrote or tuned a plan and just want the files generated.

```
/workflow.builder Read plan from workflows/rag/rag-plan.md
Create agents in: .cursor/agents/
```

### Document an existing set of agents

You already have the agents but need a friendly README.

```
/workflow.documenter Read plan from workflows/rag/rag-plan.md
Create README at: workflows/rag/README.md
```

## Worked Example -- Building a Workflow from Scratch

Let us pretend you are a portfolio analyst and you want to automate the monthly ritual of pulling factor performance, writing commentary, and drafting a client memo.

**1. Ask the orchestrator:**

```
/workflow.orchestrator Research and build agents for portfolio analysts who
produce monthly factor-performance client memos
Project name: factor-memo, Output: workflows/factor-memo/
```

**2. Watch the phases scroll by** (typically 2-5 minutes total):

- Researcher: "Investigating factor performance reporting workflows..."
- Planner: "Proposing 4 agents: `factor-memo.data-puller`, `factor-memo.commentary-writer`, `factor-memo.qa-reviewer`, `factor-memo.compiler`..."
- Builder: "Writing 5 files to `.cursor/agents/`..."
- Documenter: "Generated `workflows/factor-memo/README.md`."

**3. Review the output.** Open the README and the plan. If something looks off -- maybe an agent should be read-only, or a step is missing -- edit the plan file and re-run just the builder:

```
/workflow.builder Read plan from workflows/factor-memo/factor-memo-plan.md
Create agents in: .cursor/agents/
```

**4. Use it:**

```
/factor-memo.orchestrator Draft the March factor memo using last month''s returns
```

## Tips for Great Results

- **Be specific about the audience.** "for quant researchers searching SSRN" is better than "for researchers."
- **Include the purpose.** Say *why* the workflow exists ("to find recent papers on X for literature reviews"), not just *what* it does.
- **Pick a short project name.** Lowercase, hyphens, no spaces. It becomes the prefix on every agent name (`ssrn.orchestrator`, `factor-memo.compiler`, etc.).
- **Edit freely.** The generated markdown files are drafts, not sacred texts. Open them, tweak them, commit them.
- **Iterate.** If the first build misses the mark, edit the plan file and re-run `/workflow.builder`. It is fast.

## Troubleshooting

| Symptom | What to try |
|---|---|
| `/workflow.orchestrator` does not autocomplete | Confirm files exist in `.cursor/agents/`. Restart Cursor once if needed. |
| The researcher''s output feels thin | Re-run `/workflow.researcher` with a more specific prompt, then re-plan and re-build. |
| Agent names are not what you wanted | Edit the `*-plan.md` file, then re-run `/workflow.builder` against it. |
| Cursor picks the wrong agent | Use the explicit `/name` form instead of natural language. |
| You do not see phase summaries | Scroll up in the chat -- each subagent reports when it finishes, and some phases are quick. |

## Where to Go Next

- Browse existing workflows under [`workflows/`](../workflows/) for inspiration (look at `ipo/`, `ssrn/`, `uv-monorepo/`, `mcp-py2ts/`).
- Read the Builder''s own [`README.md`](../workflows/builder/README.md) for the full command reference.
- Try building a tiny workflow first -- something you do weekly that takes 15 minutes. Those are the best candidates.

Now go automate something delightful.
