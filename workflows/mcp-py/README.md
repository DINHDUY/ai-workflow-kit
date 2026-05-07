# MCP-Py Server Builder

A multi-agent system that generates production-quality MCP (Model Context Protocol) servers in Python, deployed as Azure Functions. It is designed for developers who need a serverless-ready, TDD-verified MCP server — complete with tools, resources, and/or prompts — without the manual overhead of setting up async patterns, Pydantic schemas, integration tests, and IaC scaffolding. The system researches the latest Azure Functions MCP extension and FastMCP patterns, distills them into a coding constitution, writes all tests before any source code, then iteratively implements and verifies the feature through two targeted feedback loops — producing a deployable server, a full test suite, and a complete provenance trail.

## What It Does

1. Researches the Azure Functions MCP extension API, FastMCP patterns, Streamable HTTP transport, and authentication best practices
2. Generates a constitution (coding rule-set) covering async-first design, Pydantic I/O models, security, and MCP-specific error handling
3. Authors a complete test suite (unit + integration) using pytest, pytest-asyncio, and httpx — all tests written RED before any source code
4. Produces a TDD implementation plan ordered by: Pydantic models → business logic → MCP decorator wiring → error handling → config → infra stubs
5. Decomposes the plan into atomic, dependency-ordered tasks (each under 30 lines of code)
6. Implements all tasks and iteratively fixes failures through an inner correctness loop (Loop A, up to 5 retries)
7. Optionally re-runs from spec onward through an outer quality loop (Loop B, up to 2 iterations) — only triggered when acceptance criteria are not met
8. Performs a local MCP verification step (`mcp dev` or MCP Inspector) to confirm tool/resource/prompt discovery and invocation

## Agents

| Agent | Role |
|-------|------|
| `mcp-py.orchestrator` | Coordinates the full pipeline and controls the outer quality loop (Loop B) |
| `mcp-py.researcher` | Reads the primary research doc and supplements with web searches on MCP extension API, FastMCP, auth, and testing patterns |
| `mcp-py.constitution-writer` | Distills research into a compact rule-set injected into all downstream agents |
| `mcp-py.spec-writer` | Converts the feature request into a formal spec and authors all unit + integration test files (RED first) |
| `mcp-py.planner` | Produces a TDD implementation plan with step-by-step build order and test-to-step mappings |
| `mcp-py.task-decomposer` | Breaks the plan into atomic tasks and outputs a dependency graph (DAG) as `task-graph.json` |
| `mcp-py.implementer` | Writes source code task-by-task following constitution rules; fixes failing tasks on retry |
| `mcp-py.test-runner` | Executes all pytest suites, ruff, and mypy; produces a structured JSON report (read-only) |
| `mcp-py.loop-controller` | Manages the inner implement/test cycle (Loop A), enforcing retry limits |

## How to Use

### Full Pipeline

Invoke `mcp-py.orchestrator` with your feature request, hosting approach, and acceptance criteria:

```
@mcp-py.orchestrator Build an MCP server with a get_weather tool that fetches current conditions from the NWS API. Hosting: Azure Functions MCP Extension. Input: city name (str). Output: WeatherData Pydantic model with temperature, humidity, and conditions. Auth: system key. Coverage target: 80%.
```

```
@mcp-py.orchestrator Build an MCP server with a list_documents resource that paginates documents from Azure Blob Storage. Hosting: Self-hosted FastMCP. Auth: Entra ID. Return: DocumentList Pydantic model with items and next_cursor. Coverage: 85%.
```

### Individual Agents

**Research only** — Use `mcp-py.researcher` when you need current MCP extension or FastMCP patterns:
```
@mcp-py.researcher Research the Azure Functions MCP Extension decorator API as of Python 3.12. Focus on: @app.mcp_tool() signature inference, Pydantic v2 schema generation, system key auth, and Streamable HTTP transport endpoint.
```

**Spec and tests only** — Use `mcp-py.spec-writer` when you already have a constitution and research report:
```
@mcp-py.spec-writer Create a spec and test suite for an MCP get_stock_price tool. Constitution: workflows/mcp-py/outputs/stock-price/constitution.md. Research: workflows/mcp-py/outputs/stock-price/mcp-research-report.md.
```

**Inner loop only** — Use `mcp-py.loop-controller` to run the implement/test cycle on an existing task graph:
```
@mcp-py.loop-controller Execute the implementation/test loop for task graph at workflows/mcp-py/outputs/get-weather/task-graph.json. Constitution: constitution.md. Spec: spec.md.
```

## Nested Loop Structure

The system uses two targeted feedback loops. Use them sparingly — loops are a tool for genuine blockers, not a default.

**Loop A (inner — correctness, mandatory):** After all tasks are implemented, the test runner executes the full pytest suite plus ruff and mypy checks. If any tests fail or linting errors remain, the loop controller sends failure details back to the implementer, which fixes only the failing tasks. This repeats up to 5 times or until all tests are green. Loop A always runs.

**Loop B (outer — quality, optional):** After Loop A succeeds, the orchestrator checks whether acceptance criteria from the spec are met (all functional requirements satisfied, coverage ≥ target). If criteria ARE met, Loop B is SKIPPED entirely. If criteria are NOT met, the pipeline re-runs from Stage 3 (spec-writer) onward with learnings from the test report injected into each agent. Loop B runs at most 2 times. Do not trigger it for minor issues that a targeted fix can resolve.

```
User Feature Request
       |
       v
mcp-py.orchestrator  ────────────────────────────────────────────┐
       |                                                          |
       v                                                          |
  mcp-py.researcher                                               |
    (mcp-research-report.md)                                      |
       |                                                          |
       v                                                          |
  mcp-py.constitution-writer                                      |
    (constitution.md)                                             |
       |                                                          |
       v                                                          |
  mcp-py.spec-writer                                        LOOP B (optional)
    (spec.md + tests/)                                      re-runs stages 3-7
       |                                                    max 2 iterations
       v                                                    only if acceptance
  mcp-py.planner                                           criteria NOT met
    (implementation-plan.md)                                      |
       |                                                          |
       v                                                          |
  mcp-py.task-decomposer                                          |
    (task-graph.json)                                             |
       |                                                          |
       v                                                          |
  mcp-py.loop-controller ────────┐                                |
       |                         |                                |
       v               LOOP A (mandatory)                         |
  mcp-py.implementer     repeats until                            |
    (src/ code)          all tests pass                           |
       |                 max 5 retries                            |
       v                         |                                |
  mcp-py.test-runner             |                                |
    (test-report.json)           |                                |
       |                         |                                |
       ├── FAIL ─────────────────┘                                |
       |                                                          |
       v                                                          |
     PASS                                                         |
       |                                                          |
  MCP Verification step                                           |
  (mcp dev / Inspector)                                           |
       |                                                          |
       ├── Acceptance criteria NOT met ──────────────────────────┘
       |
       v
  Acceptance criteria MET (or Loop B max reached)
       |
       v
  Final Output:
    - Deployed-ready source in src/
    - Full test suite in tests/
    - constitution.md, spec.md, task-graph.json
    - test-report.json, loop-a-summary.json
    - Infra stubs in infra/
```

## Setup

```bash
# Install toolchain
uv init mcp-myfeature-server --python 3.12
cd mcp-myfeature-server
uv venv
uv add "azure-functions>=2.0" "mcp[cli]" pydantic ruff mypy
uv add --dev pytest pytest-asyncio httpx pytest-mock

# Or use the official Azure template
azd init --template remote-mcp-functions-python
```

No additional infrastructure is required for local development. All agents use built-in tools (file read/write, shell execution, web search). For deployment, `azd up` provisions the Azure Functions app via Bicep templates in `infra/`.

## Output

All artifacts are saved to `workflows/mcp-py/outputs/[feature-name]/`:

```
outputs/[feature-name]/
  tests/
    unit/          # Isolated unit tests with mocked dependencies
    integration/   # httpx / MCP SDK client tests via Streamable HTTP
  src/
    tools/         # MCP tool implementations
    resources/     # MCP resource implementations
    prompts/       # MCP prompt implementations
    main.py        # Azure Functions entry point with decorators
  infra/           # Bicep stubs for Function App, Storage, Key Vault
  constitution.md
  spec.md
  implementation-plan.md
  task-graph.json
  mcp-research-report.md
  test-report.json
  loop-a-summary.json
  loop-b-state.json
```

Every intermediate artifact is preserved, making the entire workflow auditable and reproducible.

## Examples

```
@mcp-py.orchestrator Build an MCP server with a search_arxiv tool that queries the arXiv API by keyword, returns top-5 papers as a PaperList Pydantic model. Hosting: Azure Functions MCP Extension. Auth: system key.
```

```
@mcp-py.orchestrator Build a self-hosted FastMCP server with a run_sql_query tool that executes parameterized SQL against Azure SQL Database using pyodbc. Include connection pooling via lifespan. Auth: Managed Identity.
```

```
@mcp-py.orchestrator Build an MCP server with a daily_brief resource (uri: brief://today) that fetches a morning summary from Azure Blob Storage. Hosting: MCP Extension. Pydantic output: DailyBrief model.
```
