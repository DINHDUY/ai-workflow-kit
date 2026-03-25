# MAF — Microsoft Agent Framework Port Workflow

Converts an existing multi-platform agent system (`.cursor/agents`, `.claude/agents`, `.copilot/agents`, or any custom path) into a running **Microsoft Agent Framework** (Python) workflow backed by **Azure OpenAI**. Each source agent `*.md` file becomes an MAF `Agent` object; the full team is wired into a `MagenticBuilder` workflow that dynamically selects the right agent per subtask.

## Agents

| Agent | Role |
|-------|------|
| `maf.environment-setup` | Installs dependencies, creates `.env`, bootstraps `AzureOpenAIResponsesClient`, runs smoke test |
| `maf.parser` | Parses `*.md` agent files from any platform, auto-detects global instructions (`CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`), builds the agent registry |
| `maf.tool-mapper` | Maps `tools:` frontmatter values (`Read`, `Write`, `Grep`, `Bash`, `WebFetch`, …) to typed Python `@tool` functions; writes `tools.py` |
| `maf.agent-builder` | Constructs MAF `Agent` objects from the registry with composed instructions, resolved tools, and per-agent model selection; writes `agents.py` |
| `maf.orchestrator` | Assembles the `MagenticBuilder` (or GroupChat / Sequential / Concurrent) workflow; writes `workflow.py` |
| `maf.runner` | Writes `main.py` — the streaming async entry point; supports `--agents-dir`, `--platform`, `--task`, and `--repl` |
| `maf.productionizer` | Adds sessions, checkpointing, human-in-the-loop review, FastAPI server wrapper, and Azure Container App deployment |

## Platform Support

All platforms share the same YAML frontmatter schema (`name`, `description`, `tools`, `model`).

| Source platform | Agents directory | Global instructions file |
|---|---|---|
| Cursor | `.cursor/agents/` | `.cursorrules` |
| Claude Code | `.claude/agents/` | `CLAUDE.md` |
| GitHub Copilot | `.copilot/agents/` | `.github/copilot-instructions.md` |
| Custom | any path | `AGENTS.md` / `AGENT.md` |

Platform is **auto-detected** from the directory path. Pass `--platform` to override.

## How to Use

### Full pipeline

Invoke `maf.environment-setup` first, then run agents in order:

```
@maf.environment-setup Set up the MAF environment. Azure endpoint: https://my-resource.openai.azure.com/
```

```
@maf.parser Parse .cursor/agents/
```

```
@maf.tool-mapper Generate tools.py from the registry above
```

```
@maf.agent-builder Build agents.py from the registry and tools
```

```
@maf.orchestrator Assemble workflow.py using MagenticBuilder
```

```
@maf.runner Write main.py and run a test: "Summarize what each agent does"
```

### maf.orchestrator — detailed usage

**Default (MagenticBuilder, auto-detect agents dir):**

```
@maf.orchestrator Assemble workflow.py from .cursor/agents/
```

**Explicit agents directory and platform:**

```
@maf.orchestrator Build workflow.py — agents_dir: /path/to/my-project/.cursor/agents, platform: cursor
```

**Swap orchestration pattern:**

```
@maf.orchestrator Assemble workflow.py using GroupChatBuilder — agents review each other's output before finalising
```

```
@maf.orchestrator Build a SequentialBuilder pipeline: researcher → writer → editor (fixed order)
```

```
@maf.orchestrator Use ConcurrentBuilder to fan out analysis tasks to all agents in parallel
```

**Tune round limits and enable human plan review:**

```
@maf.orchestrator Assemble workflow.py, max_round_count=25, max_stall_count=5, enable_plan_review=True
```

**Wrap the workflow as a single agent (for nesting or session use):**

```
@maf.orchestrator Assemble workflow.py and add a workflow.as_agent() wrapper named "ResearchTeam"
```

After `workflow.py` is generated, run it with `maf.runner` or call `build_workflow()` directly:

```python
from workflow import build_workflow

wf = build_workflow(
    agents_dir=".cursor/agents",
    platform="cursor",
    max_round_count=20,
    enable_plan_review=True,
)
```

### Explicit agents directory

Pass any path — `maf.parser`, `maf.agent-builder`, `maf.orchestrator`, and `maf.runner` all accept an `agents_dir` argument:

```
@maf.parser Parse /path/to/my-project/.cursor/agents/
```

```
@maf.runner Run workflow with --agents-dir /path/to/my-project/.cursor/agents/ "Your task here"
```

### Single-agent usage

Run individual agents when only one step is needed — e.g. regenerate tools after adding a new `tools:` entry:

```
@maf.tool-mapper Re-generate tools.py — I added WebSearch to two agents
```

```
@maf.agent-builder Rebuild agents.py after updating instructions in my-researcher.md
```

### CLI (after main.py is generated)

```bash
# Auto-detect agents dir
python main.py "Analyze the codebase and produce a summary report"

# Explicit Cursor agents path
python main.py --agents-dir .cursor/agents "task"

# Claude agents path
python main.py --agents-dir .claude/agents "task"

# Custom path with platform override
python main.py --agents-dir /path/to/agents --platform generic "task"

# Read task from file
python main.py --task task.txt

# Interactive REPL
python main.py --repl
```

## Generated File Layout

```
project/
├── .env                  # Azure OpenAI credentials (not committed)
├── client.py             # AzureOpenAIResponsesClient singleton
├── parser.py             # Registry builder — platform-agnostic
├── tools.py              # @tool function implementations
├── agents.py             # MAF Agent objects (ms_agents dict)
├── workflow.py           # MagenticBuilder workflow
└── main.py               # Async entry point with streaming output
```

## Orchestration Patterns

`maf.orchestrator` defaults to `MagenticBuilder` (dynamic agent selection). Override when needed:

| Pattern | MAF Builder | Best for |
|---|---|---|
| Dynamic selection (default) | `MagenticBuilder` | Most multi-agent workflows |
| Collaborative review | `GroupChatBuilder` | Code review, debate, consensus |
| Fixed pipeline | `SequentialBuilder` | ETL, phase-by-phase transformation |
| Parallel fan-out | `ConcurrentBuilder` | Independent analyses, map-reduce |
