# maf-packager

`maf-packager` is a code-generation workflow that takes a `workflows/<workflow-name>/agents/` folder of Cursor/Copilot-style markdown agent definition files and generates a complete, production-ready Python package that wraps those agents into a deployable Microsoft Agent Framework (MAF) multi-agent application. Six specialized agents — coordinated by a central orchestrator — each own a distinct layer of the generated package (parsing, factory, workflow, tests, and packaging), and the orchestrator verifies each stage's output with `pytest --cov` before proceeding, retrying the responsible agent up to three times on failure.

## Prerequisites

- Python 3.11+
- Azure OpenAI credentials (endpoint, API key, and deployment name)
- [Cursor IDE](https://cursor.sh/) — agents are invoked as Cursor agent rules

## Agents

| Agent | Role | Model | Key Responsibilities |
|---|---|---|---|
| `maf-packager.orchestrator` | Pipeline coordinator | `sonnet-4.5` | Scans `agents/*.md`, builds `manifest.json`, delegates to each subagent in order, runs `pytest --cov` verification gates, retries failing stages (≤3×) |
| `maf-packager.parser-agent` | Stage 1 — Data layer | `sonnet-4.5` | Generates `parser.py` (YAML frontmatter extraction) and `types.py` (`AgentConfig`, `WorkflowConfig` dataclasses) |
| `maf-packager.factory-agent` | Stage 2 — DI layer | `sonnet-4.5` | Generates `factory.py` (`AgentFactory`, `ToolRegistry`) and `config.py` (multi-provider client construction for Foundry / Azure OpenAI / OpenAI) |
| `maf-packager.workflow-agent` | Stage 3 — Orchestration layer | `sonnet-4.5` | Generates `workflow.py` (`MAFLoader`, `build_magentic_workflow`) and `runner.py` (`run_workflow`, `run_workflow_streaming`) |
| `maf-packager.test-agent` | Stage 4 — Test suite | `sonnet-4.5` | Generates `simulator.py` (mock-mode execution) and the full `tests/` suite targeting 100% coverage |
| `maf-packager.packager` | Stage 5 — Package scaffold | `sonnet-4.5` | Generates `__init__.py`, `pyproject.toml`, `.env.example`, and `README.md` for the output package |

## How to Use

### Full Pipeline

Invoke `maf-packager.orchestrator` in Cursor with the path to your workflow directory:

```
Use maf-packager.orchestrator to build the maf-packager package from workflows/maf-packager/

workflow_dir: workflows/maf-packager/
output_dir: ./output/maf-packager-pkg/
```

The orchestrator will:
1. Scan `workflow_dir/agents/*.md` and write `output_dir/manifest.json`
2. Run each subagent in sequence (parser → factory → workflow → tests → packager)
3. Verify each stage with a Python import check and `pytest --cov`
4. Print `✅ DONE` with the output directory and coverage report, or `❌ FAILED` with the exact error

### Individual Agents

Use subagents directly when iterating on a specific layer without re-running the full pipeline.

**Stage 1 — Parser** — regenerate the data layer:
```
Use maf-packager.parser-agent to generate parser.py and types.py

manifest_path: ./output/maf-packager-pkg/manifest.json
output_dir: ./output/maf-packager-pkg/
```

**Stage 2 — Factory** — regenerate dependency injection:
```
Use maf-packager.factory-agent to generate factory.py and config.py

manifest_path: ./output/maf-packager-pkg/manifest.json
output_dir: ./output/maf-packager-pkg/
existing_modules: [maf_loader/parser.py, maf_loader/types.py]
```

**Stage 3 — Workflow** — regenerate orchestration:
```
Use maf-packager.workflow-agent to generate workflow.py and runner.py

manifest_path: ./output/maf-packager-pkg/manifest.json
output_dir: ./output/maf-packager-pkg/
existing_modules: [maf_loader/parser.py, maf_loader/types.py, maf_loader/factory.py, maf_loader/config.py]
```

**Stage 4 — Tests** — regenerate the test suite:
```
Use maf-packager.test-agent to generate simulator.py and all tests

output_dir: ./output/maf-packager-pkg/
```

**Stage 5 — Packager** — regenerate package metadata:
```
Use maf-packager.packager to generate __init__.py, pyproject.toml, .env.example, and README.md

output_dir: ./output/maf-packager-pkg/
```

## Output Structure

The orchestrator writes the following package to `output_dir/`:

```
maf_loader/
  __init__.py       # Public API exports
  types.py          # AgentConfig, WorkflowConfig dataclasses
  parser.py         # YAML frontmatter parser, discover_agent_files
  config.py         # ClientConfig, get_client_config (multi-provider)
  factory.py        # AgentFactory, ToolRegistry
  workflow.py       # MAFLoader, build_magentic_workflow
  runner.py         # run_workflow, run_workflow_streaming
  simulator.py      # Mock-mode execution for tests
tests/
  __init__.py
  conftest.py       # sample_workflow_dir fixture
  helpers/
    __init__.py
    mocks.py        # MockChatClient, MockAgent
  test_parser.py
  test_factory.py
  test_workflow.py
  test_runner.py
  test_simulator.py
manifest.json       # Generated agent manifest
pyproject.toml      # Hatchling build, dependencies, pytest config
.env.example        # Required environment variables
README.md           # Generated package README
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `AZURE_OPENAI_ENDPOINT` | Yes (Azure) | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | Yes (Azure) | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Yes (Azure) | Model deployment name |
| `OPENAI_API_KEY` | Yes (OpenAI) | OpenAI API key (if not using Azure) |
| `AZURE_AI_FOUNDRY_PROJECT` | Optional | Foundry project connection string |

The `config.py` module auto-detects the provider from which variables are set. `AZURE_OPENAI_ENDPOINT` takes precedence over `OPENAI_API_KEY`.

## Testing

Install the package in development mode and run the test suite:

```bash
cd output/maf-packager-pkg/
pip install -e ".[dev]"
pytest --cov=maf_loader --cov-report=term-missing
```

The packager configures `pyproject.toml` to enforce 100% coverage via `--cov-fail-under=100`. All tests use `MockChatClient` and `MockAgent` — no live API calls are made during the test run.
