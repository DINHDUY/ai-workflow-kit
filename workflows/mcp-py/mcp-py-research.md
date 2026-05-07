**Systematic, production-quality workflow for building an MCP (Model Context Protocol) server using the latest Microsoft-supported Python patterns, deployed as Azure Functions (serverless or containerized).** This follows **Test-Driven Development (TDD)** with unit and integration tests, adheres to Python conventions (PEP 8, type hints, modern tooling), and supports any requested feature through repeatable steps. It targets **Python ≥ 3.11** (ideally 3.12+ for Azure Functions compatibility as of 2026).

MCP is an open protocol (originally associated with Anthropic, now broadly adopted) for exposing **tools**, **resources**, and **prompts** to LLM clients (e.g., Claude Desktop, GitHub Copilot, Azure AI Foundry agents, VS Code) in a standardized, secure way.

### Two Primary Hosting Approaches on Azure Functions
Microsoft provides first-class support via the **Azure Functions MCP extension** (recommended for native integration) and self-hosted options using the official **MCP Python SDK** (`mcp` package with `FastMCP`).

1. **MCP Extension Approach (Preferred for Azure-native)**: Use `@app.mcp_tool()` and related decorators from `azure-functions >= 2.0`. Tools/resources are inferred from function signatures and type hints. Built-in support for Streamable HTTP (`/runtime/webhooks/mcp`), authentication (Entra ID + system keys), and MCP Apps (interactive UIs via `ui://` resources). Excellent for serverless scaling.

2. **Self-Hosted SDK Approach**: Build with `mcp.server.fastmcp.FastMCP`, mount as ASGI (Starlette/FastAPI) or use custom handler. Deploy via Azure Functions custom handlers or as a container. Use for full SDK flexibility (lifespan, advanced context, OAuth). Microsoft provides hosting samples.

**Recommendation**: Start with the **MCP Extension template** (`azure-samples/remote-mcp-functions-python`) for simplicity and Azure integration. Fall back to **self-hosted FastMCP** for complex shared state or custom transports. Both support **Consumption/Flex Consumption** plans (serverless) or **containerized** deployment (e.g., via Docker + Functions or Azure Container Apps as alternative).

Use **Azure Developer CLI (`azd`)** for IaC, provisioning, and deployment.

### Modern Toolchain & Project Setup (Production-Grade)
- **Dependency Management**: `uv` (preferred, fast resolver) or `poetry`/`pip` with `pyproject.toml`. Pin exact versions.
- **Runtime**: Python 3.12+ (Azure Functions supports it; check latest for 3.13). Use isolated worker model.
- **Linting/Formatting**: `ruff` (fast replacement for flake8/black/isort), `mypy` for strict typing.
- **Testing**: `pytest`, `pytest-asyncio`, `httpx` for integration, `pytest-mock` or `unittest.mock`.
- **IaC/Deployment**: `azd` + Bicep (in `infra/`), GitHub Actions or Azure DevOps for CI/CD.
- **Secrets/Config**: Azure Key Vault + `azure-identity`, environment variables via `local.settings.json` / App Settings.
- **Logging/Monitoring**: Azure Application Insights (auto-enabled in Functions).
- **Security**: Entra ID (Microsoft Entra), least-privilege RBAC, VNet integration (Flex Consumption), API Management optional for policies/rate limiting.
- **Other**: `pre-commit` hooks, `dependabot` or Renovate, semantic versioning.

**Initial Project Bootstrap** (repeatable for any feature):

```bash
# 1. Create project
uv init mcp-myfeature-server --python 3.12
cd mcp-myfeature-server
uv venv
uv add "azure-functions>=2.0" "mcp[cli]" pytest pytest-asyncio httpx pydantic ruff mypy

# Or use official template
azd init --template remote-mcp-functions-python  # or clone https://github.com/Azure-Samples/remote-mcp-functions-python
```

Structure (scalable for multiple features):
```
mcp-myfeature-server/
├── src/                    # or root for simple projects
│   ├── __init__.py
│   ├── tools/              # Feature modules: weather.py, db_query.py, etc.
│   ├── resources/
│   ├── prompts/
│   ├── main.py             # Function app entry (decorators)
│   └── context.py          # Shared lifespan/context if self-hosted
├── tests/
│   ├── unit/               # Pure unit tests (mock dependencies)
│   └── integration/        # HTTP/MCP client tests against local or deployed endpoint
├── infra/                  # Bicep for resources (Function App, Storage, Key Vault, etc.)
├── .vscode/                # mcp.json for local/remote MCP connections
├── pyproject.toml
├── host.json
├── azure.yaml              # azd config
├── requirements.txt        # or pyproject.toml dependencies
└── Dockerfile              # For container option
```

Configure `host.json` for MCP extension (server name, version, auth level).

### TDD Workflow (Red-Green-Refactor) — Repeatable for Any Feature
This workflow ensures **production quality**: high test coverage, regression safety, and clear specifications before implementation.

1. **Feature Definition (Specification)**:
   - Define the MCP primitive: **Tool** (action with side effects), **Resource** (data fetch), or **Prompt** (reusable template).
   - Write acceptance criteria: inputs/outputs, error cases, performance, security.
   - Example: "Add a `get_weather(city: str) -> WeatherData` tool using NWS API, returning Pydantic model."

2. **Write Failing Tests First (Red)**:
   - **Unit Tests** (`tests/unit/`): Test business logic in isolation (mock external APIs, DBs).
     ```python
     # tests/unit/test_weather.py
     import pytest
     from src.tools.weather import get_weather
     from unittest.mock import patch

     @pytest.mark.asyncio
     async def test_get_weather_success():
         with patch('src.tools.weather.make_nws_request') as mock_req:
             mock_req.return_value = {...}  # mocked data
             result = await get_weather("Boston")
             assert result.temperature == 22.5
             assert isinstance(result, WeatherData)
     ```
   - **Integration Tests** (`tests/integration/`): Test full MCP flow using `httpx` or official MCP client against local Functions runtime or deployed endpoint. Test discovery, tool calling, authentication, error handling, and end-to-end with a mock MCP client.
     - Use `mcp` SDK client for session-based testing.
     - Test against `/runtime/webhooks/mcp` (Streamable HTTP).
     - Include negative cases (invalid input, auth failures, rate limits).

3. **Implement Minimal Code to Pass Tests (Green)**:
   - Use decorators:
     - **MCP Extension**: `@app.mcp_tool()` (or `@app.mcp_resource()`). Inference from type hints/Pydantic.
     - **Self-Hosted FastMCP**:
       ```python
       from mcp.server.fastmcp import FastMCP, Context
       from pydantic import BaseModel

       mcp = FastMCP("MyFeatureServer")

       class WeatherData(BaseModel):
           temperature: float
           # ...

       @mcp.tool()
       async def get_weather(city: str, ctx: Context) -> WeatherData:
           # Implementation + ctx.info(), progress, etc.
           ...
       ```
   - Add **lifespan** for shared resources (DB connections, clients) using `@asynccontextmanager`.
   - Use structured output via Pydantic/Dataclasses for automatic schema generation.
   - Handle context injection for logging/progress/elicit.

4. **Refactor**:
   - Improve readability, extract helpers, optimize (async where possible), add error handling/retry.
   - Ensure no blocking calls in async paths (critical for Functions scaling).
   - Run `ruff check --fix`, `ruff format`, `mypy`.

5. **Run Full Test Suite**:
   ```bash
   uv run pytest tests/unit -v
   uv run pytest tests/integration -v --asyncio-mode=auto
   ```
   - Aim for >80-90% coverage on core logic.
   - Integration tests should hit the local Functions host (`func start`) or deployed URL.

6. **Local MCP Verification**:
   - Run with MCP Inspector, VS Code (`mcp.json`), or `uv run mcp dev`.
   - Test discovery of tools/resources/prompts and invocation.

**For any new feature**: Repeat steps 1-6. Modularize (one file/module per major capability) so tests remain independent.

### Deployment to Azure Functions (Serverless or Container)
**Serverless (Recommended)**:
- Use **Consumption** (low traffic) or **Flex Consumption** (better VNet/memory control, GA ~2025/2026).
- `azd up` (provisions Function App, Storage, etc. via Bicep).
- Remote build (recommended for Python to optimize cold starts/package size).
- Configure App Settings: secrets, Python version (`PYTHON_VERSION`), Always On (if needed).
- Enable Application Insights.

**Containerized**:
- Add `Dockerfile` (multi-stage for slim image).
- Deploy as **Azure Functions on Linux with custom container** or use **Azure Container Apps** (alternative for full container control, with MCP tutorials available).
- Push to ACR, reference in Function App or Container App.

**CI/CD**:
- GitHub Actions: `azd deploy` on push to main; run tests + `ruff`/`mypy` in PRs.
- Include `azd env` management for multiple environments (dev/staging/prod).

**Post-Deployment**:
- Retrieve system key (`mcp_extension`) for clients.
- Connect via `https://<funcapp>.azurewebsites.net/runtime/webhooks/mcp` with Entra login or key.
- Monitor scaling, cold starts (optimize package size, use async), and costs.
- Enable VNet for private resources.

### Best Practices & Production Considerations
- **Performance**: Async everywhere; avoid large packages; use remote build. Multiple worker processes for CPU-bound work.
- **Security**: Entra ID/OAuth for protected resources; never hardcode secrets; use managed identities. Implement token verification if needed.
- **Observability**: Structured logging + Application Insights; context-based progress reporting in tools.
- **Scalability**: Stateless where possible (`stateless_http=True`); use lifespan carefully (Functions are ephemeral).
- **Error Handling**: Graceful failures with meaningful MCP responses; retries for external calls.
- **Versioning**: Semantic versioning for server; document capabilities.
- **Testing in CI**: Matrix for Python versions; integration against staging deployment.
- **Compliance**: Follow Azure Well-Architected Framework (reliability, security, cost optimization).

### Resources for Latest Templates & Docs
- Official MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk (FastMCP examples, lifespan, transports).
- Azure Remote MCP Functions Python Template: https://github.com/Azure-Samples/remote-mcp-functions-python (use `azd`).
- MCP Extension Docs: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-mcp.
- Self-hosted hosting sample: https://github.com/Azure-Samples/mcp-sdk-functions-hosting-python.
- Azure MCP Server (for Azure resources): Microsoft Learn docs.

This workflow is **feature-agnostic**—add a new tool/resource by writing its tests first, implementing minimally, refactoring, and deploying via `azd`. It produces maintainable, testable, secure MCP servers ready for production LLM agent use on Azure.

Start by cloning the Microsoft template and running the TDD cycle on a simple "hello" tool to validate your setup. For custom needs (e.g., specific integrations), provide the feature spec for tailored code/examples.