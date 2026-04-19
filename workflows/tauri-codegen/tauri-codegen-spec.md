# Tauri Codegen — Workflow Specification

> **Purpose**: Reference document for the `tauri-codegen` workflow, which scaffolds a full
> Tauri v2 desktop application with a separated frontend (React, Svelte, Blazor WASM, NiceGUI,
> etc.), a separated backend MCP server (Node.js/Express, Python/FastAPI, C#/ASP.NET Core), and
> a Rust `src-tauri` core. Frontend ↔ Backend communication uses **Model Context Protocol (MCP)**
> over either `stdio` or HTTP SSE / Streamable-HTTP transport.
>
> **Audience**: Desktop app developers and fullstack engineers building Tauri v2 apps.
>
> **Scope**: Full project scaffold, stack-specific code generation, MCP wiring, Tauri sidecar
> configuration, build/test verification — sufficient for fully automated code generation.

---

## 1. Overview

### What This Workflow Builds

A multi-layer Tauri desktop application with four primary concerns kept cleanly separated:

| Layer | Directory | Responsibility |
|---|---|---|
| **Frontend** | `frontend/` | User interface (configurable stack) |
| **Backend** | `backend/` | Business logic + MCP server (configurable stack) |
| **Rust core** | `src-tauri/` | Tauri v2 configuration, Rust commands, event bridge |
| **Workspace root** | `/` | Orchestration scripts, package.json / Makefile / justfile |

### Communication Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Tauri Desktop App                        │
│                                                             │
│  ┌──────────────┐   MCP (stdio or HTTP SSE)  ┌───────────┐ │
│  │   frontend/  │ ◄────────────────────────► │ backend/  │ │
│  │  (UI Layer)  │                            │(MCP Server│ │
│  └──────┬───────┘                            └─────┬─────┘ │
│         │  Tauri IPC / JS API                      │       │
│         │                                    sidecar spawn │
│  ┌──────▼───────────────────────────────────────────────┐  │
│  │                  src-tauri/ (Rust core)               │  │
│  │   tauri.conf.json · Cargo.toml · main.rs · commands  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### MCP Transport Options

| Transport | Mechanism | Best For |
|---|---|---|
| **stdio** | Backend spawned as child process sidecar; messages over stdin/stdout | Fully embedded offline apps |
| **HTTP SSE** | Backend runs on `localhost:<port>`; frontend connects via `EventSource` | Dev mode, multi-client, hot-reload |
| **Streamable HTTP** | Single HTTP POST endpoint with streaming response body | Modern MCP SDK default (replaces SSE) |

---

## 2. User Input

### Required Parameters

| Parameter | Description | Example |
|---|---|---|
| `appName` | Application name (kebab-case) | `my-tauri-app` |
| `frontendStack` | UI technology | `react-vite` \| `svelte-vite` \| `blazor-wasm` \| `nicegui` |
| `backendStack` | Business logic technology | `node-express` \| `python-fastapi` \| `csharp-aspnet` |
| `mcpTransport` | MCP wire protocol | `stdio` \| `http-sse` \| `streamable-http` |

### Optional Parameters

| Parameter | Default | Description |
|---|---|---|
| `mcpTools` | `[]` | List of MCP tool names to scaffold (e.g., `["query_data","run_script"]`) |
| `tauriVersion` | `2` | Tauri major version |
| `packageManager` | `npm` | Root package manager (`npm` \| `pnpm` \| `yarn` \| `bun`) |
| `addLinting` | `true` | Add ESLint / Clippy / dotnet-format configs |
| `addTesting` | `true` | Add Vitest / pytest / xUnit stubs |

---

## 3. Expected Output File Structure

```
{appName}/
├── frontend/                        # UI layer
│   ├── src/
│   │   ├── main.tsx                 # React/Svelte entry  (or Program.cs for Blazor)
│   │   ├── App.tsx
│   │   └── mcp/
│   │       ├── client.ts            # MCP client singleton
│   │       └── hooks.ts             # useMcpTool() React/Svelte hooks
│   ├── index.html
│   ├── vite.config.ts               # (React/Svelte only)
│   ├── package.json                 # (React/Svelte/NiceGUI Node wrapper)
│   └── tsconfig.json
│
├── backend/                         # MCP server / business logic
│   ├── src/
│   │   ├── index.ts                 # (Node) or main.py (Python) or Program.cs (C#)
│   │   ├── server.ts                # MCP Server bootstrap
│   │   └── tools/
│   │       ├── query-data.ts        # One file per MCP tool
│   │       └── run-script.ts
│   ├── package.json                 # (Node)  or pyproject.toml (Python) or *.csproj (C#)
│   └── tsconfig.json                # (Node only)
│
├── src-tauri/                       # Rust core (Tauri v2)
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── capabilities/
│   │   └── default.json             # Tauri v2 capability permissions
│   └── src/
│       ├── main.rs
│       └── lib.rs                   # Tauri commands + sidecar spawn logic
│
├── package.json                     # Workspace root (npm workspaces or scripts)
├── Makefile                         # or justfile — top-level dev/build targets
├── .gitignore
└── README.md
```

---

## 4. Workflow Steps

### Step 1 — Scaffold Project Structure

**Goal**: Create directory skeleton, root config files, and workspace manifests.

```bash
mkdir -p {appName}/{frontend,backend,src-tauri}
cd {appName}
```

**Root `package.json`** (npm workspaces, adjust for pnpm/yarn):
```json
{
  "name": "{appName}",
  "private": true,
  "workspaces": ["frontend", "backend"],
  "scripts": {
    "dev":   "concurrently \"npm run dev -w frontend\" \"npm run dev -w backend\" \"npm run tauri dev\"",
    "build": "npm run build -w frontend && npm run build -w backend && npm run tauri build",
    "tauri": "tauri"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2",
    "concurrently": "^9"
  }
}
```

**Root `.gitignore`**:
```
node_modules/
dist/
target/
__pycache__/
*.pyc
.env
*.local
```

**Validation**:
- `frontend/`, `backend/`, `src-tauri/` directories exist
- `package.json` present at root

---

### Step 2 — Generate Frontend Code

Generate stack-specific frontend source files. See **Section 6** for per-stack details.

**Common tasks regardless of stack**:
1. Create `frontend/src/mcp/` directory
2. Install MCP client SDK for the frontend language
3. Write `frontend/src/mcp/client.ts` (or `.cs` / `.py`)
4. Write a sample page component that calls at least one MCP tool

**React + Vite scaffold command**:
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

**Svelte + Vite scaffold command**:
```bash
cd frontend
npm create vite@latest . -- --template svelte-ts
npm install
```

**Validation**:
- Frontend dev server starts (`npm run dev` in `frontend/`)
- MCP client file exists at `frontend/src/mcp/client.ts`

---

### Step 3 — Configure Frontend MCP Client

Connect the frontend to the backend using the chosen MCP transport.

#### 3a. stdio Transport (Tauri Shell Plugin)

The frontend does **not** communicate directly with the process via stdio — it calls Tauri commands that forward requests to the sidecar.

```typescript
// frontend/src/mcp/client.ts  (stdio path)
import { invoke } from "@tauri-apps/api/core";

export async function callMcpTool<T>(
  toolName: string,
  args: Record<string, unknown>
): Promise<T> {
  // Tauri command bridges to the sidecar backend
  return invoke<T>("call_mcp_tool", { toolName, args });
}
```

#### 3b. HTTP SSE Transport

```typescript
// frontend/src/mcp/client.ts  (HTTP SSE path)
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

const BACKEND_URL = "http://localhost:3001";

let _client: Client | null = null;

export async function getMcpClient(): Promise<Client> {
  if (_client) return _client;
  const transport = new SSEClientTransport(
    new URL(`${BACKEND_URL}/sse`)
  );
  _client = new Client({ name: "tauri-frontend", version: "1.0.0" });
  await _client.connect(transport);
  return _client;
}

export async function callMcpTool<T>(
  toolName: string,
  args: Record<string, unknown>
): Promise<T> {
  const client = await getMcpClient();
  const result = await client.callTool({ name: toolName, arguments: args });
  return result.content as T;
}
```

#### 3c. Streamable HTTP Transport

```typescript
// frontend/src/mcp/client.ts  (Streamable HTTP path)
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const transport = new StreamableHTTPClientTransport(
  new URL("http://localhost:3001/mcp")
);
const client = new Client({ name: "tauri-frontend", version: "1.0.0" });
await client.connect(transport);
```

**React hook example**:
```typescript
// frontend/src/mcp/hooks.ts
import { useState, useCallback } from "react";
import { callMcpTool } from "./client";

export function useMcpTool<T>(toolName: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const call = useCallback(
    async (args: Record<string, unknown>) => {
      setLoading(true);
      setError(null);
      try {
        const result = await callMcpTool<T>(toolName, args);
        setData(result);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    },
    [toolName]
  );

  return { data, loading, error, call };
}
```

**Validation**:
- MCP client module exports `callMcpTool`
- Hook compiles without TypeScript errors

---

### Step 4 — Generate Backend Code

Generate stack-specific backend server with HTTP or stdio entry point. See **Section 7** for per-stack details.

**Common tasks regardless of stack**:
1. Create `backend/src/tools/` directory
2. Create one stub file per tool listed in `mcpTools`
3. Write server bootstrap that registers all tools
4. Add `dev` and `build` scripts

**Node.js scaffold**:
```bash
cd backend
npm init -y
npm install express @modelcontextprotocol/sdk
npm install -D typescript @types/node @types/express tsx
```

**Python scaffold**:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install fastmcp fastapi uvicorn
```

**C# scaffold**:
```bash
cd backend
dotnet new webapi -n Backend --no-https
cd Backend
dotnet add package ModelContextProtocol
dotnet add package ModelContextProtocol.AspNetCore
```

**Validation**:
- Backend server starts without errors
- `/health` endpoint returns `200 OK` (HTTP transports)
- MCP `tools/list` returns declared tools

---

### Step 5 — Implement MCP Server in the Backend

Define all MCP tools, resources, and prompts for the backend.

#### MCP Tool Schema

Every tool must declare:
```json
{
  "name": "query_data",
  "description": "Query structured data from the local database",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "SQL or filter expression"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum rows to return",
        "default": 100
      }
    },
    "required": ["query"]
  }
}
```

#### Example Tools to Scaffold

| Tool Name | Description | Input Fields |
|---|---|---|
| `query_data` | Query local database | `query: string`, `limit?: number` |
| `run_script` | Execute a safe shell script | `script: string`, `timeout?: number` |
| `get_system_info` | Return OS/hardware info | _(none)_ |
| `read_file` | Read a file from allowed paths | `path: string` |
| `write_file` | Write content to allowed paths | `path: string`, `content: string` |

#### Node.js Tool Implementation Pattern

```typescript
// backend/src/tools/query-data.ts
import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

export function registerQueryData(server: McpServer) {
  server.tool(
    "query_data",
    "Query structured data from the local database",
    {
      query: z.string().describe("SQL or filter expression"),
      limit: z.number().int().positive().default(100),
    },
    async ({ query, limit }) => {
      // Implementation
      return {
        content: [{ type: "text", text: JSON.stringify({ rows: [], query, limit }) }],
      };
    }
  );
}
```

#### Python Tool Implementation Pattern (fastmcp)

```python
# backend/tools/query_data.py
from fastmcp import FastMCP

mcp = FastMCP("tauri-backend")

@mcp.tool()
def query_data(query: str, limit: int = 100) -> dict:
    """Query structured data from the local database."""
    # Implementation
    return {"rows": [], "query": query, "limit": limit}
```

#### C# Tool Implementation Pattern

```csharp
// backend/Tools/QueryDataTool.cs
using ModelContextProtocol.Server;
using System.ComponentModel;

[McpServerToolType]
public static class QueryDataTool
{
    [McpServerTool, Description("Query structured data from the local database")]
    public static async Task<string> QueryData(
        [Description("SQL or filter expression")] string query,
        [Description("Maximum rows to return")] int limit = 100)
    {
        // Implementation
        return System.Text.Json.JsonSerializer.Serialize(new { rows = Array.Empty<object>(), query, limit });
    }
}
```

**Validation**:
- All tools listed in `mcpTools` are registered
- `tools/list` MCP call returns correct tool schemas
- Each tool handler returns `{ content: [{ type: "text", text: "..." }] }`

---

### Step 6 — Generate Tauri Core (`src-tauri/`)

Scaffold the Rust core with Tauri v2 configuration, commands, and sidecar bridge.

#### Initialize Tauri

```bash
# From workspace root
npm run tauri init
# OR using cargo-tauri directly
cargo tauri init --app-name {appName} --window-title "{App Title}"
```

#### `src-tauri/Cargo.toml`

```toml
[package]
name = "app"
version = "0.1.0"
edition = "2021"

[lib]
name = "app_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri           = { version = "2", features = [] }
tauri-plugin-shell = "2"
serde           = { version = "1", features = ["derive"] }
serde_json      = "1"

[profile.release]
panic   = "abort"
codegen-units = 1
lto     = true
opt-level = "s"
strip   = true
```

#### `src-tauri/tauri.conf.json` (Streamable HTTP transport)

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "{appName}",
  "version": "0.1.0",
  "identifier": "com.example.{appName}",
  "build": {
    "frontendDist": "../frontend/dist",
    "devUrl": "http://localhost:5173",
    "beforeDevCommand": "npm run dev -w frontend",
    "beforeBuildCommand": "npm run build -w frontend"
  },
  "app": {
    "windows": [
      {
        "title": "{App Title}",
        "width": 1280,
        "height": 800
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "externalBin": ["binaries/backend"]
  },
  "plugins": {
    "shell": {
      "open": true
    }
  }
}
```

#### `src-tauri/tauri.conf.json` — stdio sidecar variant

When using stdio transport, remove `externalBin` from bundle and configure shell scope:

```json
{
  "plugins": {
    "shell": {
      "open": true,
      "scope": [
        {
          "name": "backend-sidecar",
          "cmd": "binaries/backend",
          "args": true,
          "sidecar": true
        }
      ]
    }
  }
}
```

#### `src-tauri/capabilities/default.json`

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capability set",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "shell:allow-execute",
    "shell:allow-spawn"
  ]
}
```

#### `src-tauri/src/lib.rs` — Sidecar spawn + Tauri command bridge

```rust
use tauri::Manager;
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn call_mcp_tool(
    app: tauri::AppHandle,
    tool_name: String,
    args: serde_json::Value,
) -> Result<serde_json::Value, String> {
    // For stdio transport: forward to sidecar process via stdin/stdout
    // For HTTP transport: make a local HTTP request to the backend
    // This example shows the HTTP approach (simpler Rust side):
    let client = reqwest::Client::new();
    let response = client
        .post("http://localhost:3001/mcp")
        .json(&serde_json::json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": tool_name, "arguments": args }
        }))
        .send()
        .await
        .map_err(|e| e.to_string())?;

    response
        .json::<serde_json::Value>()
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
async fn start_backend(app: tauri::AppHandle) -> Result<(), String> {
    let shell = app.shell();
    let (_rx, _child) = shell
        .sidecar("backend")
        .map_err(|e| e.to_string())?
        .spawn()
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![call_mcp_tool, start_backend])
        .setup(|app| {
            // Auto-start backend sidecar on app launch (stdio transport)
            // For HTTP transport, launch backend separately via beforeDevCommand
            #[cfg(not(debug_assertions))]
            {
                let handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    let _ = start_backend(handle).await;
                });
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**Validation**:
- `cargo build` in `src-tauri/` succeeds
- Tauri commands are registered in `invoke_handler!`
- Capabilities file grants required shell permissions

---

### Step 7 — Wire Everything Together

#### 7a. Backend as Sidecar (stdio / production)

1. Build the backend to a single binary:
   - **Node**: `pkg` or `nexe` to bundle to `binaries/backend`
   - **Python**: `pyinstaller` to `binaries/backend`
   - **C#**: `dotnet publish -r {rid} --self-contained` to `binaries/backend`
2. Place binary at `src-tauri/binaries/backend-{target-triple}` (Tauri naming convention)
3. Add to `tauri.conf.json` → `bundle.externalBin`
4. Grant `shell:allow-spawn` capability

**Tauri binary naming convention**:
```
src-tauri/binaries/
├── backend-x86_64-unknown-linux-gnu
├── backend-x86_64-apple-darwin
├── backend-aarch64-apple-darwin
└── backend-x86_64-pc-windows-msvc.exe
```

Use `tauri-build`'s `try_build()` with resource paths, or symlink for local dev:
```bash
# Local dev symlink (macOS/Linux)
ln -sf "$(which backend-dev)" src-tauri/binaries/backend-$(rustc -Vv | grep host | awk '{print $2}')
```

#### 7b. Backend as Standalone Dev Server (HTTP transport)

Add `backend` start command to `tauri.conf.json`:
```json
{
  "build": {
    "beforeDevCommand": "concurrently \"npm run dev -w frontend\" \"npm run dev -w backend\""
  }
}
```

Backend must set `CORS` headers to allow Tauri's webview origin:
```typescript
// Node/Express example
app.use(cors({ origin: ["http://localhost:5173", "tauri://localhost"] }));
```

#### 7c. Environment Configuration

```typescript
// frontend/src/config.ts
export const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL ?? "http://localhost:3001";

export const MCP_TRANSPORT =
  (import.meta.env.VITE_MCP_TRANSPORT as "stdio" | "http-sse" | "streamable-http")
  ?? "streamable-http";
```

**Validation**:
- `npm run dev` from workspace root starts all three layers
- Frontend can call a backend MCP tool end-to-end
- Tauri window opens and displays the frontend

---

### Step 8 — Build & Test Verification

#### Build Steps

```bash
# 1. Build frontend
npm run build -w frontend          # outputs to frontend/dist/

# 2. Build backend binary (example: Node + pkg)
cd backend && npx pkg . --target node20 --output ../src-tauri/binaries/backend-$(rustc -Vv | grep host | awk '{print $2}')

# 3. Build Tauri app
npm run tauri build                # outputs to src-tauri/target/release/bundle/
```

#### Automated Test Checklist

| Check | Command | Expected |
|---|---|---|
| Frontend unit tests | `npm test -w frontend` | All pass |
| Backend unit tests | `npm test -w backend` or `pytest backend/` | All pass |
| MCP tool schema validation | `node scripts/validate-mcp-tools.js` | No schema errors |
| Rust lint | `cargo clippy --manifest-path src-tauri/Cargo.toml -- -D warnings` | No warnings |
| Full build | `npm run build` | Zero errors |
| App smoke test | Launch built binary, open DevTools, call one MCP tool | Returns valid JSON |

#### MCP Tool Smoke Test Script

```typescript
// scripts/validate-mcp-tools.js
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const client = new Client({ name: "validator", version: "1.0.0" });
await client.connect(new StreamableHTTPClientTransport(new URL("http://localhost:3001/mcp")));
const { tools } = await client.listTools();
console.log(`Found ${tools.length} tools:`);
tools.forEach(t => console.log(` - ${t.name}: ${t.description}`));
await client.close();
```

---

## 5. Companion Tools

### Tauri / Rust

| Tool | Purpose | Install |
|---|---|---|
| `@tauri-apps/cli` | Tauri v2 CLI (`tauri init`, `tauri dev`, `tauri build`) | `npm install -D @tauri-apps/cli@^2` |
| `cargo` | Rust package manager + build tool | `rustup` |
| `cargo-tauri` | Alternative Tauri CLI via cargo | `cargo install tauri-cli` |
| `tauri-plugin-shell` | Sidecar spawn + shell command execution | `cargo add tauri-plugin-shell` |
| `tauri-build` | Build-script helper for Tauri codegen | `cargo add --build tauri-build` |
| `rustup` | Rust toolchain installer + target management | https://rustup.rs |

### Frontend

| Tool | Purpose | Install |
|---|---|---|
| `vite` | Frontend dev server + bundler (React/Svelte) | `npm create vite@latest` |
| `@tauri-apps/api` | Tauri JS/TS API (invoke, events, etc.) | `npm install @tauri-apps/api` |
| `@modelcontextprotocol/sdk` | TypeScript MCP client + server SDK | `npm install @modelcontextprotocol/sdk` |
| `dotnet` CLI | .NET SDK for Blazor WASM scaffold | https://dot.net |
| `ModelContextProtocol` NuGet | .NET MCP client SDK | `dotnet add package ModelContextProtocol` |
| `nicegui` | Python-based UI server (acts as MCP client) | `pip install nicegui` |

### Backend

| Tool | Purpose | Install |
|---|---|---|
| `@modelcontextprotocol/sdk` | TypeScript MCP server SDK | `npm install @modelcontextprotocol/sdk` |
| `express` | Node.js HTTP framework | `npm install express` |
| `zod` | Runtime schema validation for MCP tools | `npm install zod` |
| `mcp[cli]` | Python MCP SDK (official) | `pip install mcp[cli]` |
| `fastmcp` | High-level Python MCP server framework | `pip install fastmcp` |
| `fastapi` | Python HTTP framework for HTTP transport | `pip install fastapi uvicorn` |
| `ModelContextProtocol` NuGet | .NET MCP server SDK | `dotnet add package ModelContextProtocol` |
| `ModelContextProtocol.AspNetCore` NuGet | .NET MCP HTTP integration | `dotnet add package ModelContextProtocol.AspNetCore` |

### Build / Packaging

| Tool | Purpose | Install |
|---|---|---|
| `pkg` | Bundle Node.js app to standalone binary | `npm install -g @vercel/pkg` |
| `nexe` | Alternative Node.js bundler | `npm install -g nexe` |
| `pyinstaller` | Bundle Python app to standalone binary | `pip install pyinstaller` |
| `dotnet publish` | Publish self-contained .NET binary | Built into `dotnet` SDK |
| `concurrently` | Run multiple npm scripts in parallel | `npm install -D concurrently` |
| `just` | Command runner (alternative to Make) | `cargo install just` |

**Total companion tools listed: 27**

---

## 6. Frontend Stack Variants

### 6.1 React + Vite (TypeScript) — Default

**Scaffold**:
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install @tauri-apps/api @modelcontextprotocol/sdk
```

**Key files**:
- `frontend/src/App.tsx` — root component
- `frontend/src/mcp/client.ts` — MCP client (see Step 3)
- `frontend/src/mcp/hooks.ts` — `useMcpTool()` hook
- `frontend/vite.config.ts` — add `@tauri-apps/vite-plugin`

**Vite config**:
```typescript
// frontend/vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { internalIpV4 } from "internal-ip";

export default defineConfig(async () => ({
  plugins: [react()],
  clearScreen: false,
  server: {
    port: 5173,
    strictPort: true,
    host: await internalIpV4() || "localhost",
  },
  envPrefix: ["VITE_", "TAURI_"],
  build: {
    target: "chrome105",
    minify: !process.env.TAURI_DEBUG ? "esbuild" : false,
    sourcemap: !!process.env.TAURI_DEBUG,
  },
}));
```

---

### 6.2 Svelte + Vite (TypeScript)

**Scaffold**:
```bash
cd frontend
npm create vite@latest . -- --template svelte-ts
npm install @tauri-apps/api @modelcontextprotocol/sdk
```

**Key difference from React**:
- Use Svelte stores instead of React hooks
- `frontend/src/mcp/store.ts`:

```typescript
// frontend/src/mcp/store.ts
import { writable } from "svelte/store";
import { callMcpTool } from "./client";

export function createToolStore<T>(toolName: string) {
  const { subscribe, set } = writable<{ data: T | null; loading: boolean; error: string | null }>({
    data: null, loading: false, error: null,
  });
  return {
    subscribe,
    call: async (args: Record<string, unknown>) => {
      set({ data: null, loading: true, error: null });
      try {
        const data = await callMcpTool<T>(toolName, args);
        set({ data, loading: false, error: null });
      } catch (err) {
        set({ data: null, loading: false, error: String(err) });
      }
    },
  };
}
```

---

### 6.3 Blazor WASM (.NET)

**Scaffold**:
```bash
cd frontend
dotnet new blazorwasm -n Frontend
dotnet add Frontend package ModelContextProtocol
```

**MCP Client service** (`frontend/Frontend/Services/McpClientService.cs`):
```csharp
using ModelContextProtocol.Client;
using ModelContextProtocol.Protocol.Transport;

public class McpClientService
{
    private IMcpClient? _client;

    public async Task<IMcpClient> GetClientAsync()
    {
        if (_client is not null) return _client;

        var transport = new SseClientTransport(
            new SseClientTransportOptions
            {
                Endpoint = new Uri("http://localhost:3001/sse"),
            }
        );
        _client = await McpClientFactory.CreateAsync(transport);
        return _client;
    }

    public async Task<string> CallToolAsync(string toolName, object args)
    {
        var client = await GetClientAsync();
        var result = await client.CallToolAsync(toolName,
            System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, object>>(
                System.Text.Json.JsonSerializer.Serialize(args))!);
        return string.Join("\n", result.Content.Select(c => c.Text ?? ""));
    }
}
```

**`Program.cs` registration**:
```csharp
builder.Services.AddScoped<McpClientService>();
```

**Note**: Blazor WASM runs in the browser sandbox. It communicates with the backend only via HTTP SSE or Streamable HTTP — stdio transport is not available for Blazor WASM.

---

### 6.4 NiceGUI (Python)

NiceGUI acts as both the UI server and the MCP client. Tauri points its webview at `http://localhost:8080`.

**Scaffold**:
```bash
cd frontend
python -m venv .venv && source .venv/bin/activate
pip install nicegui mcp[cli]
```

**`frontend/main.py`**:
```python
from nicegui import ui
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio, json

MCP_BACKEND_CMD = ["python", "../backend/main.py"]

async def call_mcp_tool(tool_name: str, args: dict):
    params = StdioServerParameters(command=MCP_BACKEND_CMD[0], args=MCP_BACKEND_CMD[1:])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, args)
            return result.content

@ui.page("/")
def index():
    result_label = ui.label("Result: —")

    async def on_query():
        data = await call_mcp_tool("query_data", {"query": "SELECT 1"})
        result_label.set_text(f"Result: {json.dumps(data)}")

    ui.button("Query Data", on_click=on_query)

ui.run(host="0.0.0.0", port=8080, reload=False)
```

**`tauri.conf.json` for NiceGUI**:
```json
{
  "build": {
    "devUrl": "http://localhost:8080",
    "beforeDevCommand": "cd frontend && python main.py"
  }
}
```

---

## 7. Backend Stack Variants

### 7.1 Node.js + Express + TypeScript

**Bootstrap** (`backend/src/server.ts`):
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import express from "express";
import cors from "cors";
import { registerQueryData } from "./tools/query-data.js";
import { registerRunScript } from "./tools/run-script.js";

const app = express();
app.use(express.json());
app.use(cors({ origin: ["http://localhost:5173", "tauri://localhost"] }));

const server = new McpServer({ name: "tauri-backend", version: "1.0.0" });
registerQueryData(server);
registerRunScript(server);

// Streamable HTTP transport (recommended)
app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

// SSE transport (legacy)
app.get("/sse", async (req, res) => {
  const transport = new SSEServerTransport("/messages", res);
  await server.connect(transport);
});
app.post("/messages", async (req, res) => {
  // handle SSE messages
});

// Health check
app.get("/health", (_, res) => res.json({ status: "ok" }));

app.listen(3001, () => console.log("Backend MCP server running on :3001"));
```

**stdio transport entry point**:
```typescript
// backend/src/stdio-server.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerQueryData } from "./tools/query-data.js";

const server = new McpServer({ name: "tauri-backend", version: "1.0.0" });
registerQueryData(server);

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

### 7.2 Python + FastAPI + fastmcp

**Bootstrap** (`backend/main.py`):
```python
from fastmcp import FastMCP
from fastmcp.server.http import create_sse_app
import uvicorn

mcp = FastMCP("tauri-backend")

# Register tools
from tools.query_data import query_data
from tools.run_script import run_script

mcp.add_tool(query_data)
mcp.add_tool(run_script)

if __name__ == "__main__":
    import sys
    if "--stdio" in sys.argv:
        # stdio transport for sidecar mode
        mcp.run()
    else:
        # HTTP SSE transport for dev mode
        app = create_sse_app(mcp, path="/sse", post_path="/messages")
        uvicorn.run(app, host="0.0.0.0", port=3001)
```

**Tool file** (`backend/tools/query_data.py`):
```python
def query_data(query: str, limit: int = 100) -> dict:
    """Query structured data from the local database."""
    # Implementation here
    return {"rows": [], "query": query, "limit": limit}
```

**Streamable HTTP with official `mcp` SDK**:
```python
from mcp.server.fastmcp import FastMCP
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Route

mcp = FastMCP("tauri-backend")

@mcp.tool()
def query_data(query: str, limit: int = 100) -> dict:
    """Query structured data."""
    return {"rows": [], "query": query}

session_manager = StreamableHTTPSessionManager(app=mcp._mcp_server)
starlette_app = Starlette(routes=[Route("/mcp", session_manager.handle_request, methods=["POST"])])
```

---

### 7.3 C# + ASP.NET Core

**`Program.cs`**:
```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddMcpServer()
    .WithHttpTransport()
    .WithToolsFromAssembly();

builder.Services.AddCors(options =>
    options.AddPolicy("Tauri", p =>
        p.WithOrigins("http://localhost:5173", "tauri://localhost")
         .AllowAnyHeader().AllowAnyMethod()));

var app = builder.Build();
app.UseCors("Tauri");
app.MapMcp("/mcp");
app.MapGet("/health", () => Results.Ok(new { status = "ok" }));
app.Run("http://localhost:3001");
```

**Tool class** (`backend/Tools/QueryDataTool.cs`):
```csharp
using ModelContextProtocol.Server;
using System.ComponentModel;

[McpServerToolType]
public static class QueryDataTool
{
    [McpServerTool, Description("Query structured data from the local database")]
    public static Task<string> QueryData(
        [Description("SQL or filter expression")] string query,
        [Description("Maximum rows to return")] int limit = 100)
    {
        var result = new { rows = Array.Empty<object>(), query, limit };
        return Task.FromResult(System.Text.Json.JsonSerializer.Serialize(result));
    }
}
```

**stdio sidecar mode** (add alongside HTTP mode):
```csharp
// Detect if running as sidecar (no console, or --stdio flag)
if (args.Contains("--stdio"))
{
    var server = new McpServer(new McpServerOptions { ServerInfo = new() { Name = "tauri-backend", Version = "1.0.0" } });
    server.RegisterToolsFromAssembly(Assembly.GetExecutingAssembly());
    var transport = new StdioServerTransport();
    await server.ConnectAsync(transport);
    await server.RunAsync();
    return;
}
```

---

## 8. Tauri Sidecar Configuration (Deep Dive)

### 8.1 Binary Naming Convention

Tauri v2 requires sidecar binaries to include the Rust target triple in their filename:
```
src-tauri/binaries/{name}-{target-triple}[.exe]
```

Supported targets:
```
x86_64-unknown-linux-gnu
x86_64-apple-darwin
aarch64-apple-darwin
x86_64-pc-windows-msvc
```

Build script to place binary in the correct location:
```makefile
# Makefile
TARGET := $(shell rustc -Vv | grep host | awk '{print $$2}')

.PHONY: build-backend-sidecar
build-backend-sidecar:
    cd backend && npx pkg . --target node20 \
        --output ../src-tauri/binaries/backend-$(TARGET)
    chmod +x src-tauri/binaries/backend-$(TARGET)
```

### 8.2 Tauri v2 Capability System

Tauri v2 replaced the old allowlist with a **capability + permission** system.

**`src-tauri/capabilities/default.json`** (full shell sidecar permissions):
```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default app capabilities",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "shell:allow-execute",
    "shell:allow-spawn",
    "shell:default"
  ]
}
```

> **Security note**: `shell:allow-spawn` must be scoped to the specific binary. Do not grant `args: true` to shell without a strict scope definition.

### 8.3 Sidecar Spawn in Rust (`lib.rs` full pattern)

```rust
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandChild;
use std::sync::Mutex;

struct BackendState(Mutex<Option<CommandChild>>);

#[tauri::command]
async fn start_backend(app: tauri::AppHandle, state: tauri::State<'_, BackendState>) -> Result<(), String> {
    let mut guard = state.0.lock().map_err(|e| e.to_string())?;
    if guard.is_some() {
        return Ok(()); // already running
    }

    let (mut rx, child) = app
        .shell()
        .sidecar("backend")
        .map_err(|e| e.to_string())?
        .args(["--stdio"])
        .spawn()
        .map_err(|e| e.to_string())?;

    *guard = Some(child);

    // Forward stdout lines to frontend as Tauri events
    let app_handle = app.clone();
    tauri::async_runtime::spawn(async move {
        use tauri_plugin_shell::process::CommandEvent;
        while let Some(event) = rx.recv().await {
            if let CommandEvent::Stdout(line) = event {
                let _ = app_handle.emit("backend-stdout", String::from_utf8_lossy(&line).to_string());
            }
        }
    });

    Ok(())
}

#[tauri::command]
async fn stop_backend(state: tauri::State<'_, BackendState>) -> Result<(), String> {
    let mut guard = state.0.lock().map_err(|e| e.to_string())?;
    if let Some(child) = guard.take() {
        child.kill().map_err(|e| e.to_string())?;
    }
    Ok(())
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(BackendState(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![
            start_backend,
            stop_backend,
            call_mcp_tool,
        ])
        .setup(|app| {
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                let state = handle.state::<BackendState>();
                let _ = start_backend(handle.clone(), state).await;
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 8.4 MCP over stdio — Message Framing

When the frontend calls a Tauri command to invoke a backend tool (stdio transport), the Rust layer must send a valid JSON-RPC request to the sidecar's stdin and read the response from stdout. The MCP SDK handles framing (newline-delimited JSON), so the Rust side needs to:

1. Write `{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"...","arguments":{...}}}\n` to child stdin
2. Read one line from child stdout
3. Parse and return the JSON-RPC response

For production use, prefer the HTTP transport approach where the backend process runs as a local HTTP server — this avoids complex stdio plumbing in Rust.

---

## 9. MCP Integration Details

### 9.1 Transport Comparison

| Feature | stdio | HTTP SSE | Streamable HTTP |
|---|---|---|---|
| **MCP SDK support** | Full | Full (legacy) | Full (recommended) |
| **Dev hot-reload** | Requires restart | Supported | Supported |
| **Multi-client** | No (1:1) | Yes | Yes |
| **Production bundle** | Single binary sidecar | Separate server process | Separate server process |
| **Rust integration** | Complex (stdin/stdout) | Simple (HTTP client) | Simple (HTTP client) |
| **Blazor WASM** | Not supported | Supported | Supported |
| **NiceGUI** | Supported | Supported | Supported |
| **Firewall / port** | No port needed | Requires localhost port | Requires localhost port |

### 9.2 Complete MCP Tool Definition Schema

```typescript
interface McpToolDefinition {
  name: string;              // kebab-case or snake_case identifier
  description: string;       // Human-readable description for the LLM/client
  inputSchema: {
    type: "object";
    properties: Record<string, {
      type: "string" | "number" | "integer" | "boolean" | "array" | "object";
      description?: string;
      default?: unknown;
      enum?: unknown[];
      minimum?: number;
      maximum?: number;
      items?: { type: string };
    }>;
    required?: string[];
    additionalProperties?: boolean;
  };
}
```

### 9.3 MCP Resources and Prompts

Beyond tools, MCP supports **resources** (readable data) and **prompts** (templated messages):

**Resource example** (Node.js):
```typescript
server.resource(
  "app://config",
  "Application configuration",
  async (uri) => ({
    contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify(appConfig) }]
  })
);
```

**Prompt example** (Node.js):
```typescript
server.prompt(
  "analyze-data",
  "Prompt template for data analysis",
  {
    dataset: z.string().describe("Dataset name or path"),
  },
  ({ dataset }) => ({
    messages: [{
      role: "user",
      content: { type: "text", text: `Analyze the dataset: ${dataset}` }
    }]
  })
);
```

### 9.4 Security Considerations

| Risk | Mitigation |
|---|---|
| Arbitrary shell execution via `run_script` tool | Whitelist allowed commands; sandbox with `child_process` options |
| Path traversal via `read_file` / `write_file` tools | Validate paths against an allowed-paths allowlist |
| CORS misconfiguration | Restrict `origin` to Tauri webview origin only |
| Sidecar binary tampering | Verify binary hash at startup; use Tauri's `updater` signature verification |
| Stdio injection via tool args | Sanitize args; use typed schemas (Zod / Pydantic) not raw string interpolation |

---

## 10. Programmatic Access

### Fully Automatable Steps

| Step | Automatable | Notes |
|---|---|---|
| 1. Scaffold project structure | **Yes** | Given `appName`, all dirs/files are deterministic |
| 2. Generate frontend code | **Yes** (after stack choice) | Stack CLI commands are deterministic |
| 3. Configure MCP client | **Yes** (after transport choice) | Template files, no user decisions |
| 4. Generate backend code | **Yes** (after stack choice) | Stack CLI + boilerplate |
| 5. Implement MCP tools | **Yes** (after `mcpTools` list) | One file per tool, schema-driven |
| 6. Generate Tauri core | **Yes** | Config files are templated from `appName` |
| 7. Wire everything | **Yes** | Script-driven, deterministic |
| 8. Build & test | **Yes** | Scripted via `make` / `npm` |

### Requires User Input

| Decision | Options | When Asked |
|---|---|---|
| `appName` | Any valid identifier | Before Step 1 |
| `frontendStack` | `react-vite` \| `svelte-vite` \| `blazor-wasm` \| `nicegui` | Before Step 2 |
| `backendStack` | `node-express` \| `python-fastapi` \| `csharp-aspnet` | Before Step 4 |
| `mcpTransport` | `stdio` \| `http-sse` \| `streamable-http` | Before Step 3 |
| `mcpTools` | Comma-separated list of tool names | Before Step 5 (optional) |
| `packageManager` | `npm` \| `pnpm` \| `yarn` \| `bun` | Before Step 1 (optional) |

**Programmatic access available: Yes** — all 8 workflow steps are fully automatable once the 4 required user inputs are collected upfront.

### Recommended Input Collection Strategy

Collect all required inputs in a single upfront prompt before executing any steps:

```
Required inputs:
1. App name (e.g., "my-tauri-app"):
2. Frontend stack [react-vite / svelte-vite / blazor-wasm / nicegui]:
3. Backend stack [node-express / python-fastapi / csharp-aspnet]:
4. MCP transport [stdio / http-sse / streamable-http]:
5. MCP tools to scaffold (comma-separated, e.g. "query_data,run_script") [optional]:
```

Once collected, the entire workflow executes without further interruption.

---

## Summary

| Metric | Value |
|---|---|
| **Workflow steps** | 8 |
| **Companion tools** | 27 |
| **Frontend stack variants** | 4 (React+Vite, Svelte+Vite, Blazor WASM, NiceGUI) |
| **Backend stack variants** | 3 (Node/Express, Python/FastAPI, C#/ASP.NET) |
| **MCP transport variants** | 3 (stdio, HTTP SSE, Streamable HTTP) |
| **Programmatic access** | Yes — after 4 required inputs |
| **Tauri version** | v2 |
| **MCP protocol version** | 2025-03-26 (latest) |
