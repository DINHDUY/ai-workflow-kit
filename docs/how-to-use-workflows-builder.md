## Multi-agent Workflow Builder

Automated system for creating domain-specific multi-agent workflows. Transforms workflow descriptions into fully functional agent systems through a four-phase pipeline: research, planning, implementation, and documentation.

## What It Does

Automates the end-to-end creation of multi-agent workflows:

1. **Research** — Investigates domain workflows and tools
2. **Plan** — Designs agent architecture and specifications  
3. **Build** — Generates agent files with complete instructions
4. **Document** — Creates usage documentation and examples

## Get it 

**For Cursor:**
```bash
uvx --from git+https://github.com/DINHDUY/ai-workflow-kit-py ^
    add-workflows builder --output .cursor/agents
```

**For Claude:**
```bash
uvx --from git+https://github.com/DINHDUY/ai-workflow-kit-py ^
    add-workflows builder --output .claude/agents
```

## Use it

Before we run the Builder, here is how Cursor subagents work. You have **multiple ways** to invoke one from the chat:

**Use the slash shortcut (explicit):**

Type `/` in the chat input, then start typing the agent name. Cursor pops up a picker. Select it and type your request.

```
/workflow.orchestrator Research and build agents for monitoring equity factor performance
```

**Use natural language (Cursor picks the right one):**

Just describe what you want and mention the agent by name. Cursor delegates automatically.

```
Use the workflow.orchestrator subagent to research and build agents for
monitoring equity factor performance.
```

Both work. The slash form is tidier when you know exactly which agent you want. The natural-language form is friendlier when you are not sure.


**For more control over the output**

Provide project name, what you want to name your new workflow, and output folder - where your workflow will be written to.

```
Run agent /workflow.orchestrator for [domain description] Project name: [identifier], Output: workflows/[folder]/".
```


> **Good to know:** Each subagent runs in its **own isolated context window**. That means your main chat stays clean -- only the final summary bubbles back up to you.


## More

- [docs/how-to-use-workflow-builder-to-generate-new-workflows.md](how-to-use-workflow-builder-to-generate-new-workflows.md)

- [workflows/builder/README.md](workflows/builder/README.md)