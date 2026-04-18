# Claude Packager — Agent Plan

**Date**: 2026-04-17  
**Spec**: `workflows/claude-packager/claude-packager-spec.md`  
**Output agents dir**: `workflows/claude-packager/agents/`  
**Generated code target**: `src/<workflow_name>/`

---

## Overview

The `claude-packager` system converts any `workflows/<name>/agents/*.md` directory into a deployable Python application using the Anthropic Claude SDK. It is composed of **six agents** operating in strict sequence:

```
claude-packager.orchestrator
├── phase 1 → claude-packager.parser
├── phase 2 → claude-packager.builder
├── phase 3 → claude-packager.tester
├── phase 4 → claude-packager.simulator
└── phase 5 → claude-packager.deployer
```

---

## Agent Roster

| Agent | Role | Model | Tools |
|-------|------|-------|-------|
| `claude-packager.orchestrator` | Pipeline coordinator | sonnet | Read, Bash, delegate_to_parser, delegate_to_builder, delegate_to_tester, delegate_to_simulator, delegate_to_deployer |
| `claude-packager.parser` | Parse agent markdown files | haiku | Read, Glob, Write |
| `claude-packager.builder` | Generate Claude SDK Python code | sonnet | Read, Write, Bash, Glob |
| `claude-packager.tester` | Generate pytest test suite | sonnet | Read, Write, Bash, Glob |
| `claude-packager.simulator` | Generate simulator + mock fixtures | sonnet | Read, Write, Bash, Glob |
| `claude-packager.deployer` | Generate deployment artifacts | haiku | Read, Write, Bash |

---

## Phase Details

### Phase 0 — Orchestrator Pre-Flight

**Agent**: `claude-packager.orchestrator`

**Inputs** (from user message):
- `workflow_name` — the target workflow (e.g. `nextjs`, `scrapy`)
- `agents_dir` — default `workflows/<workflow_name>/agents/`
- `output_dir` — default `src/<workflow_name>/`

**Pre-flight checks**:
1. Verify `agents_dir` exists and contains `*.md` files
2. Verify `<workflow_name>.orchestrator.md` exists in that dir
3. Create `src/<workflow_name>/ORCHESTRATION_LOG.md` tracking all phase statuses

**Handoff to Phase 1**: `workflow_name` + `agents_dir` + `output_dir`

---

### Phase 1 — Parser

**Agent**: `claude-packager.parser`

**Input**: `workflow_name`, `agents_dir`

**Actions**:
1. Glob all `*.md` files in `agents_dir`
2. For each file, parse YAML frontmatter block (`---\n...\n---`)
3. Extract: `name`, `description`, `model`, `tools`, `readonly`
4. Resolve model alias: `sonnet` → `claude-sonnet-4-5-20250929`, `opus` → `claude-opus-4-7`, `haiku` → `claude-haiku-3-5-20241022`
5. Extract body (everything after the closing `---`) as `instructions`
6. Identify which agent is the orchestrator (filename ends with `.orchestrator.md`)
7. Validate required fields (name, description, model) — error on missing
8. Write `src/<workflow_name>/parse-manifest.json`

**Output artifact**: `src/<workflow_name>/parse-manifest.json`
```json
{
  "workflow_name": "nextjs",
  "agents_dir": "workflows/nextjs/agents/",
  "orchestrator": "nextjs.orchestrator",
  "agents": [
    {
      "name": "nextjs.orchestrator",
      "description": "...",
      "model": "claude-sonnet-4-5-20250929",
      "tools": ["Read", "Bash", "delegate_to_nextjs.builder"],
      "readonly": false,
      "instructions": "You are ...",
      "source_file": "workflows/nextjs/agents/nextjs.orchestrator.md"
    }
  ]
}
```

---

### Phase 2 — Builder

**Agent**: `claude-packager.builder`

**Input**: `src/<workflow_name>/parse-manifest.json`

**Generated files** (all in `src/<workflow_name>/`):

#### `__init__.py`
Empty module marker.

#### `config.py`
Frozen dataclasses only — no logic, no imports except stdlib:
- `AgentConfig(name, description, model, instructions, tools, readonly)`
- `WorkflowConfig(workflow_name, agents_dir, output_dir, agents, orchestrator_name)`

#### `loader.py`
`AgentMarkdownLoader` class:
- `load_agent(path: Path) -> AgentConfig` — parse one file
- `load_all(agents_dir: Path) -> list[AgentConfig]` — load all .md files sorted
- `find_orchestrator(agents_dir, workflow_name) -> AgentConfig | None`
- `_resolve_model(alias: str) -> str` — private, maps aliases to full model IDs
- Uses `re` and `yaml.safe_load` — no external I/O beyond reading the path

#### `tools/__init__.py`
Re-exports `ToolRegistry`, `BUILTIN_TOOLS`.

#### `tools/registry.py`
`ToolRegistry` class:
- `__init__(tools: dict[str, Callable])` — injected, not hardcoded
- `build_for_agent(agent_config: AgentConfig) -> list[Callable]` — returns callables matching agent's tool list
- `register(name: str, fn: Callable) -> None` — extend registry
- Only raises `KeyError` for unknown tool names when `strict=True`

#### `tools/builtin.py`
All tools decorated with `@beta_tool`, one function per tool:
- `Read(path: str) -> str` — reads file, raises `ToolError` on missing
- `Write(path: str, content: str) -> str` — writes file, creates parents
- `Bash(command: str, working_dir: str = ".") -> str` — subprocess with timeout, returns combined stdout+stderr
- `Glob(pattern: str, base_dir: str = ".") -> str` — json list of matched paths
- `Grep(pattern: str, path: str, recursive: bool = False) -> str` — regex search, returns matches
- `WebFetch(url: str, timeout: int = 30) -> str` — httpx GET, returns text
- `TodoRead() -> str` — reads `.todo.json` in cwd
- `TodoWrite(todos: str) -> str` — writes `.todo.json` (todos is JSON string)

#### `tools/subagent.py`
`build_subagent_tool(agent_config: AgentConfig, agent_runner: "AgentRunner") -> Callable`:
- Creates a `@beta_tool`-decorated function named `delegate_to_<name>` (sanitised)
- Description is the agent's `description` field
- Single `task: str` parameter
- Internally calls `agent_runner.run(task)` and returns the result string

#### `agent.py`
`AgentRunner` class:
- `__init__(config: AgentConfig, client: Anthropic, tool_registry: ToolRegistry)`
- `run(user_message: str, *, stream: bool = False) -> str`
  - Builds tool list via `tool_registry.build_for_agent(config)`
  - Creates `tool_runner` with `system=config.instructions`
  - Returns `runner.until_done().content[0].text`
- `run_streaming(user_message: str) -> Iterator[str]` — yields text chunks

#### `runner.py`
`WorkflowRunner` class:
- `__init__(config: WorkflowConfig, client: Anthropic)`
- `load() -> None` — loads all agents from manifest, builds subagent tools, wires tool registry
- `run(task: str) -> str` — delegates to orchestrator agent
- `_build_registry() -> ToolRegistry` — builds `ToolRegistry` from builtins + subagent tools
- Raises `WorkflowError` (custom exception) on configuration issues

`WorkflowError(Exception)` — domain exception.

#### `simulator.py`
`WorkflowSimulator` class (drop-in replacement for `WorkflowRunner`):
- `__init__(config: WorkflowConfig, mock_responses: dict[str, str])`
  - `mock_responses` maps `agent_name -> response_text`
- `load() -> None` — no-op (no real API calls)
- `run(task: str) -> str` — returns `mock_responses[orchestrator_name]`
- `run_agent(agent_name: str, task: str) -> str` — returns `mock_responses[agent_name]`
- Tracks calls in `self.call_log: list[tuple[str, str]]`

#### `main.py`
CLI using `click`:
```
claude-packager run <workflow_name> [--agents-dir PATH] [--output-dir PATH] [--stream]
claude-packager simulate <workflow_name> [--agents-dir PATH]
claude-packager parse <workflow_name> [--agents-dir PATH]
```
- Reads `ANTHROPIC_API_KEY` from environment (never hardcoded)
- Exits with code 1 on error, prints structured error message

#### `pyproject.toml`
```toml
[project]
name = "<workflow_name>"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.96.0",
    "pyyaml>=6.0",
    "click>=8.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-mock>=3.12",
    "pytest-cov>=5.0",
    "pytest-asyncio>=0.23",
]
```

---

### Phase 3 — Tester

**Agent**: `claude-packager.tester`

**Input**: Generated source files from Phase 2

**Test files** (all in `tests/<workflow_name>/`):

#### `conftest.py`
Shared fixtures:
- `sample_agent_config()` — `AgentConfig` with known values
- `sample_workflow_config(tmp_path)` — `WorkflowConfig` with fixtures dir
- `mock_anthropic_client(mocker)` — stubs `Anthropic` client
- `fixture_agents_dir()` — path to `tests/<wf>/fixtures/`

#### `fixtures/`
- `sample_agent.md` — single valid agent with all fields
- `sample_orchestrator.md` — orchestrator with subagent delegation tool
- `mock_workflow/mock.orchestrator.md` — minimal orchestrator
- `mock_workflow/mock.worker.md` — minimal worker

#### `test_config.py`
- Frozen dataclass immutability
- Default values
- Type checking

#### `test_loader.py`
- `load_agent()` with valid file
- `load_agent()` with missing frontmatter → `ValueError`
- `load_agent()` with unknown model alias → passthrough
- `load_all()` sorts alphabetically
- `find_orchestrator()` found / not found
- `_resolve_model()` for all aliases

#### `test_tools/test_registry.py`
- `build_for_agent()` returns correct tools
- `build_for_agent()` with strict=True raises on unknown tool
- `register()` adds new tool
- Empty tools list

#### `test_tools/test_builtin.py`
- `Read()` reads existing file
- `Read()` raises `ToolError` for missing file
- `Write()` creates file + parent dirs
- `Bash()` returns stdout
- `Bash()` returns stderr on error
- `Glob()` returns JSON list
- `Grep()` finds matches
- `WebFetch()` (mocked httpx) returns text
- `TodoRead()` / `TodoWrite()` roundtrip

#### `test_tools/test_subagent.py`
- `build_subagent_tool()` creates callable with correct name
- Calling the tool calls `agent_runner.run(task)`
- Tool description matches agent description

#### `test_agent.py`
- `run()` calls `tool_runner.until_done()`, returns text
- `run()` with streaming calls streaming path
- Empty content returns empty string
- Tool registry errors propagate

#### `test_runner.py`
- `load()` creates agents for all parsed agents
- `run()` delegates to orchestrator agent
- `run()` raises `WorkflowError` when no orchestrator
- `_build_registry()` includes builtins + subagent tools

#### `test_simulator.py`
- `run()` returns mock response without API call
- `run_agent()` returns specific agent mock
- `call_log` records all calls
- Missing agent in mock_responses → `KeyError`

#### `test_main.py`
- CLI `run` command invokes `WorkflowRunner`
- CLI `simulate` command invokes `WorkflowSimulator`
- CLI `parse` command invokes parser
- Missing `ANTHROPIC_API_KEY` → error message, exit code 1
- Invalid workflow name → error message

**Coverage target**: 100% (`--fail-under=100`)  
**Run command**: `pytest tests/<workflow_name>/ --cov=src/<workflow_name> --cov-report=term-missing --fail-under=100`

---

### Phase 4 — Simulator

**Agent**: `claude-packager.simulator`

**Input**: Generated source from Phase 2

**Actions**:
1. Create `tests/<workflow_name>/fixtures/mock_workflow/` with two agent markdown files
2. Create `tests/<workflow_name>/conftest.py` simulator fixtures
3. Create `tests/<workflow_name>/functional/` directory
4. Write `tests/<workflow_name>/functional/test_full_pipeline.py` — exercises `WorkflowSimulator` end-to-end
5. Write sample mock dataset JSON: `tests/<workflow_name>/fixtures/mock_datasets.json`

**Mock dataset format** (`mock_datasets.json`):
```json
{
  "scenarios": [
    {
      "name": "basic_delegation",
      "task": "Perform task X",
      "mock_responses": {
        "<wf>.orchestrator": "Task completed: delegated to worker, result: ...",
        "<wf>.worker": "Worker result: processed successfully"
      },
      "expected_final": "Task completed"
    }
  ]
}
```

**Functional test scenarios**:
- Happy path: orchestrator delegates to worker, gets result
- Error path: worker returns error, orchestrator handles it
- Multi-step: orchestrator calls multiple agents in sequence
- Empty task: graceful handling

---

### Phase 5 — Deployer

**Agent**: `claude-packager.deployer`

**Input**: Generated source from Phase 2

**Generated files**:

#### `src/<workflow_name>/deploy/Dockerfile`
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .
COPY src/<workflow_name>/ ./src/<workflow_name>/
CMD ["python", "-m", "<workflow_name>.main", "run", "${WORKFLOW_NAME}"]
```
Multi-stage: `base` → `test` (installs dev deps, runs tests) → `production`.

#### `src/<workflow_name>/deploy/.env.example`
```
ANTHROPIC_API_KEY=your_api_key_here
WORKFLOW_NAME=<workflow_name>
LOG_LEVEL=INFO
```

#### `src/<workflow_name>/deploy/docker-compose.yml`
```yaml
services:
  agent:
    build: ../..
    env_file: .env
    volumes:
      - ../../workflows:/app/workflows:ro
```

#### `.github/workflows/<workflow_name>-ci.yml`
GitHub Actions:
- Trigger: push/PR to main
- Steps: checkout, setup Python 3.12, install deps, run tests with coverage, build Docker image

#### `src/<workflow_name>/deploy/README.md`
Deployment instructions with Quick Start, Environment Variables, Docker, CI/CD sections.

---

## Context Passing Between Phases

Each phase outputs a structured artifact that the next phase reads:

```
Phase 1 → parse-manifest.json
Phase 2 → all source files (loader reads them)
Phase 3 → test files (tester reads source)
Phase 4 → functional test files + fixtures
Phase 5 → deployment artifacts
```

All intermediate artifacts written to `src/<workflow_name>/`.

---

## Error Handling

| Error | Response |
|-------|----------|
| Missing `agents_dir` | Stop, report path, suggest fix |
| No `*.md` files found | Stop, list what was found instead |
| Missing orchestrator | Stop, list available agents, ask which is orchestrator |
| YAML parse error | Stop, report file and line number |
| Missing required field | Stop, report which field and which file |
| Phase failure | Report phase name + error, ask user to retry or skip |
