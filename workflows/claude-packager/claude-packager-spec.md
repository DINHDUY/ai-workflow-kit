# Claude Packager — Specification

**Date**: 2026-04-17  
**Author**: workflow.researcher  
**Purpose**: Document the domain knowledge and API patterns required to wrap any `workflows/<name>/agents/*.md` directory into a production-ready, deployable Python application using the Claude SDK.

---

## 1. Problem Statement

Agent systems are commonly authored as structured Markdown files with YAML frontmatter that declare `name`, `description`, `model`, `tools`, and `readonly` flag, with the agent's system-prompt body in the Markdown content block. These files are portable and human-readable, but they are not executable.

The **claude-packager** workflow bridges that gap: given a directory of agent Markdown files, it generates a complete Python package that runs those agents as a live multi-agent system via the Anthropic Claude SDK.

---

## 2. Agent Markdown File Format

Each agent file follows this structure:

```markdown
---
name: <workflow>.<role>           # required — used as agent id
description: "..."               # required — one-line purpose used in subagent tool description
model: sonnet | opus | haiku     # required — alias resolved at load time
readonly: true | false           # optional, default true
tools:                           # optional — list of tool names the agent may call
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebFetch
  - delegate_to_<subagent_name>  # special: spawns a subagent call
---

<System prompt / instructions body in Markdown>
```

### Model Aliases (Claude SDK v0.96.0)

| Alias    | Resolved Model              |
|----------|-----------------------------|
| `opus`   | `claude-opus-4-7`           |
| `sonnet` | `claude-sonnet-4-5-20250929`|
| `haiku`  | `claude-haiku-3-5-20241022` |

If the value is already a full model ID, it is used verbatim.

### Naming Convention for Orchestrator

The orchestrator is identified by filename: `<workflow_name>.orchestrator.md`.  
Its tool list may include `delegate_to_<subagent_name>` entries which are auto-generated as subagent tools.

---

## 3. Claude SDK — Key APIs (anthropic >= 0.96.0)

### 3.1 Synchronous Client

```python
from anthropic import Anthropic
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
```

### 3.2 Tool Definition (`@beta_tool`)

```python
from anthropic import beta_tool

@beta_tool
def get_weather(location: str, unit: str = "fahrenheit") -> str:
    """Get the current weather in a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA
        unit: Temperature unit, either 'celsius' or 'fahrenheit'
    """
    return json.dumps({"temperature": "20°C", "condition": "Sunny"})
```

The decorator extracts a JSON Schema from type hints and docstring. The function must return a `str` (or content block). Use `json.dumps()` to return structured data.

### 3.3 Tool Runner (Agentic Loop)

```python
runner = client.beta.messages.tool_runner(
    model="claude-opus-4-7",
    max_tokens=8192,
    system="You are ...",
    tools=[get_weather, calculate_sum],
    messages=[{"role": "user", "content": "What is the weather in Paris?"}],
)

# Iterate through intermediate messages (stops when no tool_use)
for message in runner:
    print(message)

# Or get only the final message
final = runner.until_done()
print(final.content[0].text)
```

**Streaming:**
```python
runner = client.beta.messages.tool_runner(..., stream=True)
for message_stream in runner:
    for event in message_stream:
        pass
    final_msg = message_stream.get_final_message()
```

### 3.4 ToolError (Structured Error Response)

```python
from anthropic.lib.tools import ToolError

@beta_tool
def risky_tool(path: str) -> str:
    """Reads a file safely."""
    if not Path(path).exists():
        raise ToolError(f"File not found: {path}")
    return Path(path).read_text()
```

### 3.5 Async Support

Replace `@beta_tool` with `@beta_async_tool` and use `AsyncAnthropic` client:

```python
from anthropic import AsyncAnthropic, beta_async_tool

client = AsyncAnthropic()

@beta_async_tool
async def fetch_url(url: str) -> str:
    """Fetches content from a URL."""
    async with httpx.AsyncClient() as http:
        resp = await http.get(url)
        return resp.text
```

### 3.6 Advanced Runner Control

```python
for message in runner:
    tool_response = runner.generate_tool_call_response()
    if tool_response:
        # inspect / modify tool result
        for block in tool_response["content"]:
            if block.get("is_error"):
                raise RuntimeError(f"Tool error: {block['content']}")
        # add cache_control for large results
        for block in tool_response["content"]:
            if block["type"] == "tool_result":
                block["cache_control"] = {"type": "ephemeral"}
        runner.append_messages(message, tool_response)
```

---

## 4. Multi-Agent Orchestration Pattern

The standard pattern for Claude SDK multi-agent systems:

1. Each subagent is wrapped as a `@beta_tool` callable
2. The orchestrator's `tool_runner` calls these tools when delegating
3. Each subagent tool internally creates its own `tool_runner` loop
4. Results flow back up as tool results

```
User Task
    │
    ▼
Orchestrator (tool_runner)
    │  calls delegate_to_<worker> tool
    ▼
Worker Agent (tool_runner)
    │  calls built-in tools (Read, Write, Bash, etc.)
    ▼
Result → back to orchestrator as tool_result
    │
    ▼
Final Answer
```

---

## 5. Built-in Tool Implementations

The following tool names appear in agent Markdown files and must be implemented:

| Tool Name  | Description                                   |
|------------|-----------------------------------------------|
| `Read`     | Read file content from a path                 |
| `Write`    | Write content to a file path                  |
| `Bash`     | Execute a shell command, return stdout/stderr  |
| `Glob`     | List files matching a glob pattern            |
| `Grep`     | Search file(s) with a regex pattern           |
| `WebFetch` | Fetch content from a URL                      |
| `TodoRead` | Read the current todo list                    |
| `TodoWrite`| Write/update the todo list                    |

---

## 6. Generated Package Structure

```
src/<workflow_name>/
├── __init__.py
├── config.py               # AgentConfig, WorkflowConfig dataclasses
├── loader.py               # AgentMarkdownLoader — parse frontmatter + body
├── tools/
│   ├── __init__.py
│   ├── registry.py         # ToolRegistry — maps tool names to callables
│   ├── builtin.py          # Built-in tool implementations (@beta_tool)
│   └── subagent.py         # SubAgentTool factory — wraps agents as tools
├── agent.py                # AgentRunner — runs a single agent via tool_runner
├── runner.py               # WorkflowRunner — orchestrates multi-agent system
├── simulator.py            # WorkflowSimulator — mock runner for testing
├── main.py                 # CLI entry point
└── deploy/
    ├── Dockerfile
    ├── .env.example
    └── docker-compose.yml
tests/<workflow_name>/
├── conftest.py
├── fixtures/
│   ├── sample_agent.md
│   ├── sample_orchestrator.md
│   └── mock_workflow/
│       ├── mock.orchestrator.md
│       └── mock.worker.md
├── test_config.py
├── test_loader.py
├── test_tools/
│   ├── __init__.py
│   ├── test_registry.py
│   ├── test_builtin.py
│   └── test_subagent.py
├── test_agent.py
├── test_runner.py
├── test_simulator.py
└── test_main.py
pyproject.toml
```

---

## 7. Design Principles

### SOLID
- **S** — `config.py` only holds data, `loader.py` only parses, `tools/` only implements tools, `agent.py` only runs one agent, `runner.py` only orchestrates.
- **O** — `ToolRegistry` is extended by registering new functions; no existing code is modified.
- **L** — `WorkflowSimulator` and `WorkflowRunner` are interchangeable via `WorkflowRunnerProtocol`.
- **I** — Tools are independent callables; `AgentRunner` does not depend on all tools existing.
- **D** — `WorkflowRunner` depends on `AnthropicClientProtocol` (abstract), not `Anthropic` (concrete).

### DRY
- Model alias resolution: done once in `loader.py::_resolve_model()`.
- Tool wiring: done once in `ToolRegistry.build_for_agent()`.
- Agentic loop: done once in `AgentRunner.run()`.

### Clean Architecture (layers)
```
Domain Layer:    config.py (AgentConfig, WorkflowConfig)
Use Case Layer:  loader.py, tools/registry.py, agent.py, runner.py
Infrastructure:  tools/builtin.py (I/O), tools/subagent.py (API calls)
Interface Layer: main.py (CLI)
```

---

## 8. Testing Strategy

- **Unit tests**: Each module tested in isolation using `pytest-mock` to stub external calls.
- **100% coverage**: Enforced via `pytest-cov` with `--fail-under=100`.
- **Fixtures**: Reusable mock agent markdown files in `tests/<wf>/fixtures/`.
- **Functional tests**: `WorkflowSimulator` stubs the Anthropic API and exercises the full pipeline with mock agent responses.
- **Edge cases**: Missing orchestrator, malformed frontmatter, tool errors, empty workflow.

---

## 9. Deployment Artifacts

- **`Dockerfile`**: Multi-stage build, `python:3.12-slim`, sets `ANTHROPIC_API_KEY` via env var.
- **`.env.example`**: Documents required environment variables.
- **`docker-compose.yml`**: Local run with env file mount.
- **`pyproject.toml`**: PEP 517 build, `anthropic>=0.96.0`, `pyyaml>=6.0`, `click>=8.0` for CLI.
