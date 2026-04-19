# Tauri Codegen

A multi-agent workflow that scaffolds a production-ready **Tauri v2 desktop application** from four user inputs, generating all three layers — frontend UI, MCP backend server, and Rust core — fully wired together.

---

## What It Generates

```
{appName}/
├── context.json              # codegen configuration
├── package.json              # npm workspace root
├── Makefile                  # dev/build/test/clean targets
├── .gitignore
├── README.md
├── frontend/                 # UI layer (stack-specific)
│   └── src/mcp/
│       ├── client.ts         # MCP client (transport-specific)
│       └── hooks.ts          # React hooks / Svelte stores
├── backend/                  # MCP server (stack-specific)
│   └── src/tools/            # query_data, run_script, get_system_info
└── src-tauri/                # Rust core
    ├── Cargo.toml
    ├── tauri.conf.json
    ├── capabilities/default.json
    └── src/
        ├── main.rs
        └── lib.rs
```

| Layer | Directory | Technology |
|-------|-----------|------------|
| Frontend (UI) | `frontend/` | React+Vite, Svelte+Vite, Blazor WASM, or NiceGUI |
| Backend (MCP server) | `backend/` | Node/Express, Python/FastAPI, or C#/ASP.NET Core |
| Rust core | `src-tauri/` | Tauri v2, tauri-plugin-shell, sidecar bridge |

Frontend ↔ Backend communication uses the **Model Context Protocol (MCP)** over one of three transports: `stdio`, `http-sse`, or `streamable-http`.

---

## Prerequisites

| Tool | Install |
|------|---------|
| Rust + Cargo | [rustup.rs](https://rustup.rs) |
| Node.js 18+ and npm | [nodejs.org](https://nodejs.org) |
| Tauri CLI v2 | `cargo install tauri-cli --version "^2"` |
| .NET SDK | Required for `blazor-wasm` or `csharp-aspnet` stacks |
| Python 3.11+ | Required for `nicegui` or `python-fastapi` stacks |

---

## Required Inputs

| Input | Options |
|-------|---------|
| `appName` | Any valid kebab-case string (e.g., `my-tauri-app`) |
| `frontendStack` | `react-vite` \| `svelte-vite` \| `blazor-wasm` \| `nicegui` |
| `backendStack` | `node-express` \| `python-fastapi` \| `csharp-aspnet` |
| `mcpTransport` | `stdio` \| `http-sse` \| `streamable-http` |

---

## Stack Matrix

✅ = supported | ⚠️ = supported with caveat | ❌ = not supported

| `frontendStack` | `backendStack` | `stdio` | `http-sse` | `streamable-http` |
|-----------------|----------------|:-------:|:----------:|:-----------------:|
| `react-vite` | `node-express` | ✅ | ✅ | ✅ |
| `react-vite` | `python-fastapi` | ✅ | ✅ | ✅ |
| `react-vite` | `csharp-aspnet` | ✅ | ✅ | ✅ |
| `svelte-vite` | `node-express` | ✅ | ✅ | ✅ |
| `svelte-vite` | `python-fastapi` | ✅ | ✅ | ✅ |
| `svelte-vite` | `csharp-aspnet` | ✅ | ✅ | ✅ |
| `blazor-wasm` | `node-express` | ❌ | ✅ | ✅ |
| `blazor-wasm` | `python-fastapi` | ❌ | ✅ | ✅ |
| `blazor-wasm` | `csharp-aspnet` | ❌ | ✅ | ✅ |
| `nicegui` | `node-express` | ✅ | ✅ | ⚠️ |
| `nicegui` | `python-fastapi` | ✅ | ✅ | ⚠️ |
| `nicegui` | `csharp-aspnet` | ✅ | ✅ | ⚠️ |

**Caveats**:
- `blazor-wasm` + `stdio`: Blazor WASM runs in the browser sandbox and cannot use the Tauri IPC bridge. HTTP transport required.
- `nicegui` + `streamable-http`: Requires `mcp>=1.6`; flagged as experimental.

---

## Quick Start

```
Use tauri-codegen.orchestrator to create my-app with react-vite frontend,
python-fastapi backend, and streamable-http MCP transport
```

---

## Agent Pipeline

Agents execute sequentially. The orchestrator collects all inputs upfront before dispatching sub-agents.

```
[1] tauri-codegen.orchestrator      Collects inputs, writes context.json, runs final smoke-check
         │
         ▼
[2] tauri-codegen.scaffolder        Creates root directory skeleton, workspace manifests, empty layer dirs
         │
         ▼
[3] tauri-codegen.frontend-generator   Generates frontend layer + MCP client for chosen stack/transport
         │
         ▼ (may run in parallel with step 3)
[4] tauri-codegen.backend-generator    Generates MCP server + tool stubs for chosen backend stack
         │
         ▼
[5] tauri-codegen.tauri-core-generator  Generates src-tauri/ (Cargo.toml, tauri.conf.json, Rust source)
         │
         ▼
[6] tauri-codegen.wirer             Reconciles all layers, finalizes Makefile, writes validation report
```

| Agent | Responsibility |
|-------|---------------|
| `tauri-codegen.orchestrator` | Entry point; validates inputs, writes `context.json`, orchestrates the pipeline, runs final smoke-check |
| `tauri-codegen.scaffolder` | Creates directory tree, root `package.json`, `Makefile`, `.gitignore`, skeleton `README.md` |
| `tauri-codegen.frontend-generator` | Full frontend source, transport-specific MCP client (`client.ts`), React hooks / Svelte stores |
| `tauri-codegen.backend-generator` | MCP server bootstrap, one file per tool (`query_data`, `run_script`, `get_system_info`), health endpoint |
| `tauri-codegen.tauri-core-generator` | `Cargo.toml`, `tauri.conf.json`, `main.rs`/`lib.rs`, `capabilities/default.json`, sidecar config for stdio |
| `tauri-codegen.wirer` | Reconciles `tauri.conf.json` paths, configures CORS, finalizes `Makefile` targets, writes `.codegen-validation.json` |

---

## MCP Transport Guide

| Transport | Description |
|-----------|-------------|
| **stdio** | Backend runs as a Tauri sidecar process; frontend communicates through Tauri IPC → Rust stdin/stdout bridge. Best for offline/embedded apps. |
| **http-sse** | Backend runs as a local HTTP server; frontend uses `SSEClientTransport` to connect. Good for development and simple integrations. |
| **streamable-http** | Backend uses `StreamableHTTP` transport for bidirectional streaming. Best for complex tool interactions requiring real-time updates. |

---

## Post-Generation Commands

```bash
cd {appName}
make dev          # start frontend + backend + tauri in dev mode
make build        # build production bundles + tauri installer
make test         # run all tests
make clean        # remove build artifacts
```

---

## Files Reference

| File | Description |
|------|-------------|
| [tauri-codegen-spec.md](tauri-codegen-spec.md) | Research document with full workflow details |
| [tauri-codegen-plan.md](tauri-codegen-plan.md) | Agent decomposition plan |
| `.cursor/agents/tauri-codegen.*.md` | Individual agent instruction files |
