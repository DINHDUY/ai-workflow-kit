# Kit Features — Node.js / TypeScript Edition

**Source reference:** [docs/kit-features.md](./kit-features.md) (Python original)

This document describes how the `ai-workflow-kit` CLI — originally implemented in Python using `click` — is redesigned for Node.js and TypeScript. The feature set is identical: three installable commands (`add-skills`, `add-commands`, `add-workflows`) that scaffold AI agent assets into a target project. All implementation choices follow the Node.js LTS (v22+) and TypeScript (v5.x) conventions and best practices.

---

## Table of Contents

1. [Technology Choices](#technology-choices)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [Shared Infrastructure](#shared-infrastructure)
5. [CLI Commands](#cli-commands)
   - [add-skills](#add-skills)
   - [add-commands](#add-commands)
   - [add-workflows](#add-workflows)
6. [Common Behavioural Patterns](#common-behavioural-patterns)
7. [Resource Resolution Strategy](#resource-resolution-strategy)
8. [File Layout Conventions](#file-layout-conventions)
9. [Build & Distribution](#build--distribution)

---

## Technology Choices

| Concern | Python original | Node.js replacement | Rationale |
|---------|-----------------|---------------------|-----------|
| CLI framework | `click` | [`commander`](https://github.com/tj/commander.js) v12+ | De-facto standard; composable sub-commands; built-in `--version`, `--help` |
| Terminal colour | `click.secho` | [`chalk`](https://github.com/chalk/chalk) v5+ | ESM-native; zero-dependency-like ergonomics |
| File system | `pathlib.Path` | `node:fs/promises` + `node:path` | Native async API; no added dependency |
| Module system | Python packages | ESM (`"type": "module"`) | Node.js LTS default; compatible with `import.meta.url` resource resolution |
| TypeScript runtime (dev) | — | [`tsx`](https://github.com/privatenumber/tsx) | Fast TS execution without a separate compile step during development |
| Distribution entry | `pyproject.toml` `[project.scripts]` | `package.json` `"bin"` field | npm/npx ecosystem standard |
| Package manager | `uv` / `pip` | `npm` / `npx` | Standard Node.js toolchain |

---

## Project Structure

```
node/
└── tools/
    ├── cli.ts                  # Main entry point — registers all commands
    ├── commands/
    │   ├── add-skills.ts       # add-skills command implementation
    │   ├── add-commands.ts     # add-commands command implementation
    │   └── add-workflows.ts    # add-workflows command implementation
    └── lib/
        ├── resources.ts        # Resource discovery & resolution
        ├── fs.ts               # copy_tree / copy_file helpers
        └── types.ts            # Shared TypeScript types
```

`cli.ts` is the file referenced in `package.json`'s `"bin"` field. Each command lives in its own module, keeping the entry point thin.

---

## Architecture Overview

```
cli.ts
│
├── lib/resources.ts        # getResourceDir(), available*() helpers
├── lib/fs.ts               # copyTree(), copyFile()
├── lib/types.ts            # ResourcePath, CopyResult
│
├── commands/add-skills.ts
│   ├── getAvailableSkills()
│   └── program.command("add-skills")
│
├── commands/add-commands.ts
│   ├── getAvailableCommands()
│   ├── findCommandMd()
│   └── program.command("add-commands")
│
└── commands/add-workflows.ts
    ├── getAvailableWorkflows()
    └── program.command("add-workflows")
```

All three commands share the same three options (`--output`, `--force`, `--dry-run`) and follow an identical validation → dry-run → conflict-check → copy → report flow.

---

## Shared Infrastructure

### `lib/types.ts`

```typescript
import type { PathLike } from 'node:fs';

/** A resolved filesystem path (always an absolute string in Node.js). */
export type ResourcePath = string;

/** Result returned by copyTree / copyFile. */
export interface CopyResult {
  copied: string[];   // absolute paths of written files
}
```

Unlike Python which needs a `Union[Path, Traversable]` shim to bridge installed and development modes, Node.js ESM resolves all resource paths to plain `string`s via `import.meta.url`, so a single `string` type suffices throughout.

---

### `lib/resources.ts`

#### `getResourceDir(name: string): string`

Locates a top-level bundled resource directory (`skills/`, `commands/`, or `workflows/`) using a **two-phase lookup**:

| Phase | Mode | Mechanism |
|-------|------|-----------|
| 1 | Installed package (`node_modules`) | `fileURLToPath(new URL(`../../${name}`, import.meta.url))` — resolves relative to the compiled output inside the package |
| 2 | Development (source checkout) | Walks up from `import.meta.url` to the repository root and checks for the directory |

```typescript
import { fileURLToPath } from 'node:url';
import { existsSync } from 'node:fs';
import path from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

export function getResourceDir(name: string): string {
  // Phase 1 — installed package: resources sit two levels above lib/
  const pkgDir = path.resolve(__dirname, '..', '..', name);
  if (existsSync(pkgDir)) return pkgDir;

  // Phase 2 — development: repository root is three levels up from node/tools/lib/
  const devDir = path.resolve(__dirname, '..', '..', '..', name);
  if (existsSync(devDir)) return devDir;

  throw new Error(`Resource directory '${name}' not found`);
}
```

> **Why `import.meta.url` instead of `__dirname`?**
> Node.js ESM modules do not expose `__dirname` natively. The `fileURLToPath(import.meta.url)` pattern is the idiomatic ESM replacement, supported since Node.js 10.12 and required under `"type": "module"`.

#### `getAvailableSkills() / getAvailableCommands() / getAvailableWorkflows(): string[]`

Each function calls `getResourceDir(category)`, reads the directory entries with `fs.readdirSync`, filters to directories only, and returns the names sorted alphabetically — matching the Python `sorted(item.name for item in dir.iterdir() if item.is_dir())` pattern.

```typescript
import { readdirSync } from 'node:fs';

export function getAvailableSkills(): string[] {
  const dir = getResourceDir('skills');
  return readdirSync(dir, { withFileTypes: true })
    .filter(e => e.isDirectory())
    .map(e => e.name)
    .sort();
}
```

Using the synchronous `readdirSync` here is intentional: discovery is a fast, local operation that runs once at command startup; async overhead adds no benefit.

---

### `lib/fs.ts`

#### `SKIP_DIRS`

```typescript
const SKIP_DIRS = new Set(['__pycache__', '.git', 'node_modules', 'dist', '.turbo']);
```

The Node.js set adds `dist` and `.turbo` to the Python original's exclusion list, reflecting common Node.js build artefact directories.

#### `copyTree(src: string, dst: string): string[]`

Recursively copies a source directory tree to `dst`.

- Uses `fs.mkdirSync(dst, { recursive: true })` to create the destination and all intermediate directories in a single call.
- Iterates entries with `fs.readdirSync(src, { withFileTypes: true })`, filtering via `SKIP_DIRS`.
- Copies files with `fs.copyFileSync` for atomic, buffered transfer.
- Returns a flat `string[]` of all written absolute paths.

```typescript
import { mkdirSync, readdirSync, copyFileSync } from 'node:fs';
import path from 'node:path';

export function copyTree(src: string, dst: string): string[] {
  mkdirSync(dst, { recursive: true });
  const copied: string[] = [];

  for (const entry of readdirSync(src, { withFileTypes: true })) {
    if (SKIP_DIRS.has(entry.name)) continue;
    const srcPath = path.join(src, entry.name);
    const dstPath = path.join(dst, entry.name);
    if (entry.isFile()) {
      copyFileSync(srcPath, dstPath);
      copied.push(dstPath);
    } else if (entry.isDirectory()) {
      copied.push(...copyTree(srcPath, dstPath));
    }
  }
  return copied;
}
```

#### `copyFile(src: string, dst: string): string`

Copies a single file, creating parent directories as needed, and returns the destination path.

```typescript
import { mkdirSync, copyFileSync } from 'node:fs';
import path from 'node:path';

export function copyFile(src: string, dst: string): string {
  mkdirSync(path.dirname(dst), { recursive: true });
  copyFileSync(src, dst);
  return dst;
}
```

> **Sync vs async:** All filesystem helpers are synchronous. These are scaffolding operations — invoked once, on local disk, with no concurrency. Synchronous calls produce simpler, linear code without sacrificing any real-world performance.

---

## CLI Commands

The top-level `cli.ts` wires the three commands into a single `Commander` program:

```typescript
#!/usr/bin/env node
import { Command } from 'commander';
import { registerAddSkills }    from './commands/add-skills.js';
import { registerAddCommands }  from './commands/add-commands.js';
import { registerAddWorkflows } from './commands/add-workflows.js';

const program = new Command()
  .name('ai-workflow-kit')
  .description('Scaffold AI agent assets into your project')
  .version(process.env.npm_package_version ?? '0.0.0');

registerAddSkills(program);
registerAddCommands(program);
registerAddWorkflows(program);

program.parse();
```

> Each `register*` function receives the root `Command` instance and calls `.command(name).description(...).option(...).action(...)` on it, keeping command definitions co-located with their implementation.

---

### `add-skills`

**Purpose:** Install a named skill template — a directory bundle — into the project.

**Signature:**
```
add-skills [options] <skillName>
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output <path>` | `./skills` | Directory where the skill folder will be created |
| `-f, --force` | `false` | Overwrite an existing skill directory |
| `--dry-run` | `false` | Print the planned file operations without writing |
| `-V, --version` | — | Print the package version and exit |

**Implementation sketch:**

```typescript
interface AddSkillsOptions {
  output: string;
  force: boolean;
  dryRun: boolean;
}

export function registerAddSkills(program: Command): void {
  program
    .command('add-skills <skillName>')
    .description('Copy skill template files to your project')
    .option('-o, --output <path>', 'Output directory', 'skills')
    .option('-f, --force', 'Overwrite existing files', false)
    .option('--dry-run', 'Show what would be copied without actually copying', false)
    .action((skillName: string, opts: AddSkillsOptions) => {
      // ... implementation
    });
}
```

**Discovery:** `getAvailableSkills()` enumerates all child directories under `skills/` and returns their names sorted alphabetically.

**Copy contract:**

| Source path | Destination |
|-------------|-------------|
| `skills/<name>/**` (excluding `scripts/`) | `<output>/<name>/` |
| `skills/<name>/scripts/**` | `scripts/` at project root |

The `scripts/` subdirectory inside the skill bundle is special-cased: its contents are merged into a top-level `scripts/` directory so that helper scripts are always available at a predictable path regardless of which skill they originated from.

**Error handling:**
- Prints the list of available skills when the requested name is not found (exits with code `1` via `process.exitCode = 1; return`).
- Without `--force`, rejects the operation if the destination directory already exists (checked with `fs.existsSync`).
- All errors are caught in a top-level `try/catch`; the error message is printed in red and `process.exit(1)` is called.

---

### `add-commands`

**Purpose:** Install a named AI-agent command — a `.md` file plus optional scripts — into the project.

**Signature:**
```
add-commands [options] <commandName>
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output <path>` | `.cursor/commands` | Directory where the `.md` file is placed |
| `-f, --force` | `false` | Overwrite an existing `.md` file |
| `--dry-run` | `false` | Print the planned file operations without writing |
| `-V, --version` | — | Print the package version and exit |

**Discovery:** `getAvailableCommands()` enumerates all child directories under `commands/`. `findCommandMd(cmdDir, commandName)` then locates `<commandName>.md` inside that bundle:

```typescript
function findCommandMd(cmdDir: string, commandName: string): string {
  const mdFile = path.join(cmdDir, `${commandName}.md`);
  if (!existsSync(mdFile)) {
    throw new Error(`No '${commandName}.md' found in command bundle`);
  }
  return mdFile;
}
```

**Copy contract:**

| Source path | Destination |
|-------------|-------------|
| `commands/<name>/<name>.md` | `<output>/<name>.md` |
| `commands/<name>/scripts/**` | `scripts/` at project root |

Placing the `.md` file under `.cursor/commands/` (the default) makes the command appear as `/<command-name>` in Cursor chat. Any bundled scripts are co-located with skill scripts under the project-root `scripts/` tree.

**Conflict detection:** Only the destination `.md` file path is checked against `fs.existsSync` before writing. Script files are silently overwritten when `--force` is active.

---

### `add-workflows`

**Purpose:** Install a named multi-agent workflow — agent definition files plus documentation — into the project.

**Signature:**
```
add-workflows [options] <workflowName>
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output <path>` | `.cursor/agents` | Directory where agent definition files are placed |
| `-f, --force` | `false` | Overwrite existing agent files and docs directory |
| `--dry-run` | `false` | Print the planned file operations without writing |
| `-V, --version` | — | Print the package version and exit |

**Discovery:** `getAvailableWorkflows()` enumerates all child directories under `workflows/`.

**Copy contract:**

| Source path | Destination |
|-------------|-------------|
| `workflows/<name>/agents/**` (files only, flat) | `<output>/` |
| `workflows/<name>/**` (everything except `agents/`) | `docs/workflows/<name>/` |

The `agents/` subdirectory feeds exclusively into the live AI agent configuration directory. All other files (README, diagrams, reference docs) are preserved under `docs/workflows/<name>/`.

**Conflict detection:** Checks each individual agent file path and the `docs/workflows/<name>/` output directory with `fs.existsSync`. Presents a consolidated list of conflicting paths and exits `1` if any conflict is found and `--force` is not set.

---

## Common Behavioural Patterns

All three commands share the following execution model:

```
1. Validate <name> against getAvailable*() list           → exit 1 + available list if missing
2. If --dry-run → print planned operations and return
3. Check destination conflicts with fs.existsSync         → exit 1 + conflict list if found (no --force)
4. Perform copy operations; accumulate written paths
5. Print summary (chalk.green success + file list)
   or chalk.red error + process.exit(1)
```

**Dry-run output** mirrors the real copy plan and prints each operation group with its intended destination, making it safe to inspect before committing changes.

**Colour convention** (via `chalk` v5+):

| Colour | Meaning |
|--------|---------|
| `chalk.green` | Successful operation |
| `chalk.yellow` | Dry-run informational output |
| `chalk.red` | Error / validation failure |

**Relative path display:** All printed file paths use `path.relative(process.cwd(), absPath)` to stay concise, matching the Python `f.relative_to(Path.cwd())` output.

---

## Resource Resolution Strategy

The two-phase lookup in `getResourceDir` makes the package work correctly in both deployment contexts:

- **Installed via `npm install -g` or `npx`:** The compiled JS files live inside `node_modules/ai-workflow-kit/dist/`. Resource directories (`skills/`, `commands/`, `workflows/`) are published alongside them and resolved by walking up from `import.meta.url`.
- **Running from source (`npm link`, local `tsx node/tools/cli.ts`):** The same upward traversal finds the directories at the repository root.

This means:
```bash
# No installation required — runs directly from the registry or a git URL
npx ai-workflow-kit add-skills TEMPLATE --output .cursor/skills

# Also works after a local link during development
npm link && add-skills TEMPLATE
```

> **`import.meta.url` is essential here.** It always points to the *current module's* location, whether that is inside `node_modules` or in a local source tree — unlike `process.cwd()` which reflects the user's working directory and would produce incorrect paths.

---

## File Layout Conventions

| Bundle type | Bundle root | Key file / dir | Installed to |
|-------------|-------------|----------------|--------------|
| Skill | `skills/<name>/` | Any files + optional `scripts/` | `<output>/<name>/`, `scripts/` |
| Command | `commands/<name>/` | `<name>.md` + optional `scripts/` | `<output>/<name>.md`, `scripts/` |
| Workflow | `workflows/<name>/` | `agents/` + docs | `<agents-output>/`, `docs/workflows/<name>/` |

All three bundle types share the `SKIP_DIRS` exclusion set (`__pycache__`, `.git`, `node_modules`, `dist`, `.turbo`) during recursive copy operations.

---

## Build & Distribution

### `package.json` excerpt

```jsonc
{
  "name": "ai-workflow-kit",
  "version": "1.0.0",
  "type": "module",                          // ESM throughout
  "bin": {
    "add-skills":    "./dist/cli.js",        // installed global binary
    "add-commands":  "./dist/cli.js",
    "add-workflows": "./dist/cli.js"
  },
  "files": [
    "dist/",
    "skills/",
    "commands/",
    "workflows/"
  ],
  "scripts": {
    "build": "tsc --project tsconfig.json",
    "dev":   "tsx node/tools/cli.ts",
    "lint":  "eslint node/",
    "test":  "node --test"
  },
  "dependencies": {
    "chalk":     "^5.4.0",
    "commander": "^12.0.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "typescript":  "^5.5.0",
    "tsx":         "^4.0.0"
  }
}
```

### `tsconfig.json` key settings

```jsonc
{
  "compilerOptions": {
    "target":          "ES2022",
    "module":          "NodeNext",    // correct ESM resolution for Node.js
    "moduleResolution":"NodeNext",
    "outDir":          "./dist",
    "rootDir":         "./node",
    "strict":          true,
    "declaration":     true,
    "esModuleInterop": false          // not needed with native ESM
  }
}
```

> `"module": "NodeNext"` is the correct TypeScript setting for Node.js ESM. It enforces explicit `.js` extensions on relative imports (which resolve to the compiled `.js` output files at runtime) and enables `import.meta` support.

### Running without installation

```bash
# From git URL (equivalent to Python's uvx --from <git-url>)
npx --yes ai-workflow-kit add-skills TEMPLATE --output .cursor/skills

# From local source during development
npm run dev -- add-skills TEMPLATE --output .cursor/skills
```
