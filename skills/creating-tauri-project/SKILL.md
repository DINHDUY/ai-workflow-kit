---
name: creating-tauri-project
description: >
  Generates a complete, production-ready Tauri 2.x project scaffold with a separated
  frontend, backend sidecar, and Rust core. Use this skill whenever the user asks to:
  scaffold, create, initialize, bootstrap, or generate a Tauri app or project; set up
  a Tauri + sidecar architecture; create a desktop app with Tauri and Python/FastAPI/.NET/
  Go backends; build a cross-platform desktop app using Tauri; or structure a Tauri
  monorepo. Trigger even for vague requests like "set up my Tauri app", "help me start
  a Tauri project", or "create a Tauri + React + Python app". Always use this skill
  before writing any Tauri-related files — do not improvise the structure from memory.
---

# Tauri Project Generator

Generates a complete `my-tauri-app/` scaffold with:
- A web frontend (Vite + React/Svelte/Vue/Next.js/Blazor)
- A separated backend (Python/FastAPI, .NET, Go, Node, etc.)
- A thin Tauri Rust core with sidecar support
- CI/CD via GitHub Actions

---

## Step 0 — Gather Requirements

Before generating anything, ask the user for:

1. **Project name** (default: `my-tauri-app`)
2. **Frontend framework**: React, Svelte, Vue, Next.js, Blazor, Vanilla
3. **Backend language/framework**: Python/FastAPI, .NET, Go, Node/Express, none
4. **Package manager**: pnpm (recommended), npm, yarn
5. **Target platforms**: Windows, macOS, Linux (default: all three)

If the user has already provided these details, skip asking and proceed directly.

---

## Step 1 — Determine Platform Targets & Binary Names

For each enabled platform, the sidecar binary must be named with its **Rust target triple** suffix.
Read `references/target-triples.md` for the full mapping.

Common triples:
| Platform        | Triple                            |
|-----------------|-----------------------------------|
| Windows x64     | `x86_64-pc-windows-msvc`          |
| macOS ARM       | `aarch64-apple-darwin`            |
| macOS x64       | `x86_64-apple-darwin`             |
| Linux x64       | `x86_64-unknown-linux-gnu`        |

Binary names follow: `<backend-name>-<triple>[.exe on Windows]`

---

## Step 2 — Generate the Full File Tree

Create ALL files listed below. Use the templates in `references/` for file contents.

```
<project-name>/
├── frontend/
│   ├── src/
│   │   ├── main.<ext>           # Entry point (tsx/svelte/vue/jsx)
│   │   └── App.<ext>
│   ├── index.html
│   ├── vite.config.<ext>
│   ├── tsconfig.json            # if TypeScript
│   └── package.json
├── backend/
│   ├── src/                     # Python: main.py here; .NET: Program.cs; Go: main.go
│   ├── requirements.txt         # Python only
│   ├── <name>.csproj            # .NET only
│   ├── go.mod                   # Go only
│   └── tests/
├── src-tauri/
│   ├── binaries/                # gitignored — holds built sidecar executables
│   │   └── .gitkeep
│   ├── capabilities/
│   │   └── default.json
│   ├── icons/                   # placeholder icons note
│   ├── src/
│   │   └── main.rs
│   ├── tauri.conf.json
│   ├── Cargo.toml
│   └── build.rs
├── .github/
│   └── workflows/
│       └── release.yml
├── .gitignore
├── package.json                 # root — scripts for dev/build + sidecar
├── pnpm-workspace.yaml          # if pnpm
└── README.md
```

---

## Step 3 — File Contents

### `package.json` (root)

```json
{
  "name": "<project-name>",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "tauri dev",
    "build": "tauri build",
    "build:backend": "<see backend section>",
    "frontend:dev": "cd frontend && <pm> run dev",
    "tauri": "tauri"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2"
  }
}
```

### `pnpm-workspace.yaml`

```yaml
packages:
  - 'frontend'
```

### `src-tauri/tauri.conf.json`

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "<ProjectName>",
  "version": "0.1.0",
  "identifier": "com.<author>.<project-name>",
  "build": {
    "frontendDist": "../frontend/dist",
    "devUrl": "http://localhost:5173",
    "beforeDevCommand": "cd frontend && <pm> run dev",
    "beforeBuildCommand": "cd frontend && <pm> run build"
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "externalBin": [
      "binaries/<backend-name>"
    ]
  },
  "app": {
    "windows": [
      {
        "title": "<ProjectName>",
        "width": 1200,
        "height": 800
      }
    ]
  }
}
```

> **Key**: `externalBin` paths are prefix-only — Tauri appends the target triple at runtime.

### `src-tauri/capabilities/default.json`

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capability set",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-execute",
    "shell:allow-open"
  ]
}
```

> For sidecar permissions, also add:
> ```json
> { "identifier": "shell:allow-execute", "allow": [{ "name": "<backend-name>", "sidecar": true }] }
> ```

### `src-tauri/src/main.rs`

```rust
// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;
use tauri_plugin_shell::ShellExt;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Spawn the backend sidecar
            let sidecar_command = app.shell().sidecar("<backend-name>").unwrap();
            let (_rx, _child) = sidecar_command.spawn().expect("Failed to spawn sidecar");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### `src-tauri/Cargo.toml`

```toml
[package]
name = "<project-name>"
version = "0.1.0"
edition = "2021"

[lib]
name = "<project_name>_lib"
crate-type = ["lib", "cdylib", "staticlib"]

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri = { version = "2", features = [] }
tauri-plugin-shell = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

### `src-tauri/build.rs`

```rust
fn main() {
    tauri_build::build()
}
```

### `.gitignore`

```
node_modules/
dist/
target/
src-tauri/binaries/*
!src-tauri/binaries/.gitkeep
*.pyc
__pycache__/
.env
```

---

## Step 4 — Backend-Specific Files

Read `references/backends.md` for language-specific templates.

| Backend       | Entry file              | Build command output                           |
|---------------|-------------------------|------------------------------------------------|
| Python/FastAPI | `backend/src/main.py`  | PyInstaller → `src-tauri/binaries/`            |
| .NET          | `backend/src/Program.cs`| `dotnet publish -r <rid> -o src-tauri/binaries/` |
| Go            | `backend/src/main.go`  | `go build -o src-tauri/binaries/<name>-<triple>`|
| Node          | `backend/src/index.js` | `pkg` or `nexe` → `src-tauri/binaries/`       |

---

## Step 5 — Frontend-Specific Files

Read `references/frontends.md` for framework-specific templates.

| Framework | vite.config | Entry ext | Notes                        |
|-----------|-------------|-----------|------------------------------|
| React     | `.ts`       | `.tsx`    | `@vitejs/plugin-react`       |
| Svelte    | `.ts`       | `.svelte` | `@sveltejs/vite-plugin-svelte`|
| Vue       | `.ts`       | `.vue`    | `@vitejs/plugin-vue`         |
| Vanilla   | `.js`       | `.js`     | No framework plugin          |

Always set `server.port: 5173` and `clearScreen: false` in vite config for Tauri compatibility.

---

## Step 6 — GitHub Actions CI/CD

See `references/cicd.md` for the full multi-platform `release.yml` template.

Key jobs:
1. **build-backend** — matrix: `[ubuntu, macos, windows]` → compiles sidecar for each target
2. **build-tauri** — depends on build-backend, uses `tauri-apps/tauri-action@v0`
3. **Artifacts** uploaded per platform, then bundled in a GitHub Release

---

## Step 7 — README.md

Generate a README with:
- Project description
- Prerequisites (Node, Rust, backend runtime)
- `## Development` section: steps to install and run
- `## Building` section: steps to compile backend + `pnpm build`
- `## Architecture` section: brief explanation of the sidecar pattern

---

## Step 8 — Post-Generation Checklist

After creating all files, remind the user:

- [ ] Run `<pm> install` in root and `frontend/`
- [ ] Run `cargo add tauri-plugin-shell` in `src-tauri/`
- [ ] Replace `com.<author>.<name>` identifier in `tauri.conf.json`
- [ ] Add app icons to `src-tauri/icons/` (use `tauri icon` CLI)
- [ ] Build the backend binary at least once before `tauri dev`
- [ ] Add backend binary name to `capabilities/default.json` permissions

---

## Important Notes

- **`src-tauri/binaries/` is gitignored** — binaries are built artifacts, not committed
- The `externalBin` array in `tauri.conf.json` uses **prefix paths** — Tauri resolves the full triple-suffixed filename at runtime
- Sidecar processes inherit no environment — pass config via args or stdin
- On macOS, codesigning is required for distribution; set `APPLE_*` env vars in CI
- Tauri 2.x uses a **capabilities-based permission system** — the shell plugin must be explicitly allowed
