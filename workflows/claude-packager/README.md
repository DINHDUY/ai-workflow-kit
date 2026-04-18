# claude-packager

A multi-agent workflow that wraps agents in any `workflows/<workflow-name>/agents` directory into a production-ready, deployable Python package using the Anthropic Claude SDK (v0.96.0+).

## What It Does

Given a folder of agent markdown files (each with YAML frontmatter declaring `name`, `description`, `model`, and `tools`), `claude-packager` generates:

- A complete Python package with clean architecture (domain → use case → infrastructure → interface)
- A pytest test suite with 100% code coverage
- Functional simulation tests using mock datasets (no API calls required)
- Docker, docker-compose, and GitHub Actions CI/CD artifacts

## Agent Roster

| Agent | Model | Role |
|-------|-------|------|
| `claude-packager.orchestrator` | sonnet | Coordinates all phases; the main entry point |
| `claude-packager.parser` | haiku | Discovers and parses `*.md` files, emits `parse-manifest.json` |
| `claude-packager.builder` | sonnet | Generates the full Python package from the manifest |
| `claude-packager.tester` | sonnet | Generates pytest unit tests with 100% coverage |
| `claude-packager.simulator` | sonnet | Generates functional simulation tests and mock datasets |
| `claude-packager.deployer` | haiku | Generates Dockerfile, docker-compose, and GitHub Actions CI |

## Quick Start

### Requirements

- Python 3.12+
- `anthropic>=0.96.0`
- An Anthropic API key

### Install

```bash
pip install anthropic>=0.96.0 pyyaml click
export ANTHROPIC_API_KEY=your_key_here
```

### Invoke

Point the orchestrator at any agents directory:

```
Use claude-packager.orchestrator to wrap workflows/nextjs/agents/ into a Python package
```

```
Use claude-packager.orchestrator to wrap workflows/scrapy/agents/ into a ready-to-deploy package
```

```
Use claude-packager.orchestrator to wrap workflows/prodify/agents/ with output at src/prodify/
```

### What Gets Generated

For a workflow named `my-workflow`:

```
src/my-workflow/
├── __init__.py
├── config.py          # frozen dataclasses: AgentConfig, WorkflowConfig
├── loader.py          # AgentMarkdownLoader — parses .md files
├── agent.py           # AgentRunner — wraps a single agent with tool_runner
├── runner.py          # WorkflowRunner — orchestrates the full pipeline
├── simulator.py       # WorkflowSimulator — runs without API calls
├── main.py            # click CLI: parse | run | simulate
├── pyproject.toml
├── parse-manifest.json  # emitted by parser, consumed by builder/runner
├── tools/
│   ├── __init__.py
│   ├── registry.py    # ToolRegistry — maps names to @beta_tool callables
│   ├── builtin.py     # 8 built-in tools: Read, Write, Bash, Glob, Grep, WebFetch, TodoRead, TodoWrite
│   └── subagent.py    # build_subagent_tool — factory for delegate_to_* tools
└── deploy/
    ├── Dockerfile
    ├── .env.example
    ├── docker-compose.yml
    └── README.md

tests/my-workflow/
├── conftest.py
├── test_config.py
├── test_loader.py
├── test_agent.py
├── test_runner.py
├── test_simulator.py
├── test_main.py
├── tools/
│   ├── test_registry.py
│   ├── test_builtin.py
│   └── test_subagent.py
└── fixtures/
    ├── sample_agent.md
    ├── sample_orchestrator.md
    ├── mock_datasets.json
    └── mock_workflow/
        ├── mock.orchestrator.md
        └── mock.worker.md
    functional/
    └── test_full_pipeline.py

.github/workflows/
└── my-workflow-ci.yml
```

## Agent Markdown Format

Input agent files must follow this format:

```markdown
---
name: my-workflow.worker          # required: dot-separated agent name
description: "Does X and Y."     # required: used as tool description for delegation
model: sonnet                     # required: sonnet | haiku | opus | full model ID
readonly: true                    # optional: default true
tools:                            # optional: list of tool names
  - Read
  - Glob
  - delegate_to_my-workflow.other-agent
---

Your agent's system instructions go here.
Everything below the closing --- is the instruction body.
```

### Model Aliases

| Alias | Resolved Model |
|-------|---------------|
| `sonnet` | `claude-sonnet-4-5-20250929` |
| `haiku` | `claude-haiku-3-5-20241022` |
| `opus` | `claude-opus-4-7` |

### Built-in Tools

| Tool Name | Description |
|-----------|-------------|
| `Read` | Read file contents |
| `Write` | Write content to a file |
| `Bash` | Execute a shell command |
| `Glob` | List files matching a pattern |
| `Grep` | Search for text in files |
| `WebFetch` | Fetch content from a URL |
| `TodoRead` | Read the current todo list |
| `TodoWrite` | Write/update the todo list |

### Subagent Delegation

Use `delegate_to_<agent-name>` in the tools list to enable an agent to call another agent as a tool. The builder generates a `build_subagent_tool` factory call that wires the delegating agent at runtime.

## Running the Generated Package

After generation:

```bash
# Parse agent files (required once)
python -m src.my-workflow.main parse my-workflow

# Run the full pipeline
ANTHROPIC_API_KEY=sk-... python -m src.my-workflow.main run my-workflow \
  --task "Your task here"

# Simulate without API calls
python -m src.my-workflow.main simulate my-workflow \
  --task "Your task here"
```

## Running Tests

```bash
python -m pytest tests/my-workflow/ \
  --cov=src/my-workflow \
  --cov-report=term-missing \
  --fail-under=100 \
  -v
```

## Deploying with Docker

```bash
cd src/my-workflow/deploy
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY

docker compose up agent
```
