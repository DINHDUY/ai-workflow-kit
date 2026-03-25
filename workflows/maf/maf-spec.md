# MAF (Microsoft Agent Framework)

**Here is the complete, practical step-by-step workflow to port a Claude Code subagent system** (the `.claude/agents/*.md` files + optional root `CLAUDE.md`) into **Microsoft Agent Framework** (Python) using **Azure OpenAI** models. Everything runs locally in your Python process — only LLM calls go to Azure.

Claude Code subagents are specialist Claude instances defined in Markdown with YAML frontmatter (name, description, tools list, optional model) + body as system instructions. Microsoft Agent Framework achieves the exact same modular, dynamic multi-agent behavior using **single Agents + Workflows** (especially **Magentic** orchestration, which dynamically selects agents just like Claude spawning subagents via the Task/Agent tool).

### Step 1: Prepare Your Environment (same as before)
```bash
pip install agent-framework --pre pyyaml python-frontmatter azure-identity python-dotenv
```

Use the same `.env` + `AzureOpenAIResponsesClient` setup from the previous example.

### Step 2: Parse All `.claude/agents/*.md` Files
Write a small parser (run once or on startup):

```python
import frontmatter
from pathlib import Path
from typing import Dict

def load_claude_agents(agents_dir: str = ".claude/agents") -> Dict[str, dict]:
    agents = {}
    for md_file in Path(agents_dir).glob("*.md"):
        post = frontmatter.load(md_file)
        name = post.metadata.get("name")
        if not name:
            continue
        agents[name] = {
            "name": name,
            "description": post.metadata.get("description", ""),
            "tools": post.metadata.get("tools", []),          # e.g. ["Read", "Grep", "Glob"]
            "instructions": post.content.strip(),             # the body
            "model": post.metadata.get("model")               # optional — ignore or handle
        }
    return agents
```

(You can also parse the root `CLAUDE.md` as global instructions to inject into every agent or a top-level supervisor.)

### Step 3: Map Each Claude Subagent → Microsoft Agent + Implement Tools
For every parsed agent:

```python
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework import tool, Agent
from azure.identity import AzureCliCredential
import os

client = AzureOpenAIResponsesClient(credential=AzureCliCredential())

# Example custom tools that match common Claude tools
@tool
def read_file(path: str) -> str:
    """Read file content (Claude 'Read' tool)."""
    return Path(path).read_text(encoding="utf-8")

@tool
def grep(pattern: str, path: str = ".") -> str:
    """Grep-like search (Claude 'Grep' tool)."""
    # Implement with grep, rg, or simple os.walk — example omitted for brevity
    ...

# Create MS Agent for each Claude subagent
def create_ms_agent(claude_data: dict) -> Agent:
    instructions = f"{claude_data['description']}\n\n{claude_data['instructions']}"
    tool_list = [read_file, grep] if "Read" in claude_data["tools"] or "Grep" in claude_data["tools"] else None
    
    return client.as_agent(
        name=claude_data["name"],
        instructions=instructions,
        tools=tool_list,
        # description=claude_data["description"]  # used by orchestrator
    )
```

Run:
```python
claude_agents = load_claude_agents()
ms_agents = {name: create_ms_agent(data) for name, data in claude_agents.items()}
```

### Step 4: Orchestrate with a Workflow (Recommended: Magentic for Dynamic Subagent Behavior)
Claude auto-spawns subagents dynamically → use **Magentic orchestration** (manager decides who acts next, exactly like Claude).

```python
from agent_framework.orchestrations import MagenticBuilder

# Create a lightweight manager agent (or use one of your existing ones)
manager = client.as_agent(
    name="Orchestrator",
    instructions="You coordinate a team of specialized agents to solve the task efficiently."
)

workflow = MagenticBuilder(
    participants=list(ms_agents.values()),   # all your subagents
    manager_agent=manager,
    intermediate_outputs=True,               # stream partial results
    max_round_count=15,
    max_stall_count=3,
    enable_plan_review=False                 # set True for human-in-the-loop like Claude
).build()
```

**Alternatives** (choose based on your Claude workflow):
- **Group Chat** → collaborative back-and-forth (great for review teams).
- **SequentialBuilder** or **ConcurrentBuilder** → fixed pipeline.
- Wrap the whole workflow as one agent: `workflow_agent = workflow.as_agent(name="ClaudePortedAgent")` — then call it exactly like a single Claude agent.

### Step 5: Run the Ported Workflow (Local Execution)
```python
import asyncio

async def main():
    task = "Your original prompt that would trigger multiple subagents in Claude Code"
    
    async for event in workflow.run(task, stream=True):
        if event.type == "output" and hasattr(event.data, "text"):
            print(event.data.text, end="", flush=True)
        # Optional: handle human review events if enable_plan_review=True

asyncio.run(main())
```

### Step 6: Polish & Productionize
- **Inject root CLAUDE.md** instructions into every agent or the manager.
- **Tool restrictions** — only attach the tools listed in each `.md` (same security model as Claude).
- **Sessions & memory** — use `session = await workflow_agent.create_session()` for multi-turn.
- **Checkpointing / human-in-the-loop** — built-in (same as Claude interactive mode).
- **Testing** — start with 1–2 agents, then scale. Magentic + intermediate_outputs=True gives you the same real-time visibility Claude Code provides.
- **Deployment** — same local script, or deploy the workflow as an Azure Container App / Foundry endpoint later.

### Mapping Summary Table
| Claude Code Feature          | Microsoft Agent Framework Equivalent                  |
|------------------------------|-------------------------------------------------------|
| `.claude/agents/*.md`        | One `Agent` per file (parsed)                         |
| YAML `name` / `description`  | `Agent(name=..., description=...)`                    |
| Body text                    | `instructions=`                                       |
| `tools:` list                | `@tool` functions attached to that Agent only         |
| Dynamic subagent spawning    | **MagenticBuilder** (manager picks next agent)        |
| Root `CLAUDE.md`             | Global instructions injected into manager or all agents |
| Interactive / Task tool      | Workflow events + streaming + human review            |

This port preserves the exact modular specialist-agent design of Claude Code while giving you full Python control, type safety, checkpointing, and Azure OpenAI integration.
