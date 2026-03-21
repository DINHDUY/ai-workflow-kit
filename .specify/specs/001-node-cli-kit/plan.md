# Implementation Plan: ai-workflow-kit Node.js CLI Package

**Feature ID:** 001-node-cli-kit
**Version:** 1.0.0
**Created:** 2026-03-21
**Spec:** [spec.md](./spec.md)
**Constitution:** [constitution.md](../../memory/constitution.md)
**Reference:** [docs/node-kit-features.md](../../../docs/node-kit-features.md)

---

## Implementation Plan

### Phase 1: Project Scaffolding & Configuration

Set up the foundational project structure, TypeScript configuration, and package metadata before writing any application code.

1. **Initialize `package.json`** with ESM module type, engine constraints, bin mappings, files whitelist, and dependency declarations.
2. **Create `tsconfig.json`** with `target: ES2022`, `module: NodeNext`, `moduleResolution: NodeNext`, `strict: true`, `outDir: ./dist`, `rootDir: ./node`.
3. **Install dependencies:** `commander@^12.0.0`, `chalk@^5.4.0` as production deps; `typescript@^5.5.0`, `tsx@^4.0.0`, `@types/node@^22.0.0` as dev deps.
4. **Create directory scaffold:** `node/tools/`, `node/tools/commands/`, `node/tools/lib/`, and the parallel `node/tools/__tests__/` tree.

### Phase 2: Shared Library Layer (TDD)

Build the infrastructure modules that all three commands depend on. Every module is developed test-first using the Node.js built-in test runner.

1. **`node/tools/lib/types.ts`** — Define shared types: `ResourcePath`, `CopyResult`, `CommandOptions` interface with `output`, `force`, and `dryRun` fields.
2. **`node/tools/lib/fs.ts`** — Implement `SKIP_DIRS` constant, `copyTree(src, dst)`, and `copyFile(src, dst)` using synchronous `node:fs` APIs. Tests use `mkdtempSync` for isolation.
3. **`node/tools/lib/resources.ts`** — Implement `getResourceDir(name)` with two-phase `import.meta.url` lookup, plus `getAvailableSkills()`, `getAvailableCommands()`, `getAvailableWorkflows()` discovery functions.

### Phase 3: CLI Entry Point & Command Registration

Wire the Commander.js program and register all three subcommands.

1. **`node/tools/cli.ts`** — Create the main entry point with shebang, Commander program setup, version from `process.env.npm_package_version`, and calls to `registerAddSkills`, `registerAddCommands`, `registerAddWorkflows`.
2. **Verify `tsx` dev runner** — Confirm `npm run dev -- add-skills --help` prints usage correctly.

### Phase 4: Command Implementations (TDD)

Implement each command following the shared execution flow: validate → dry-run → conflict-check → copy → report.

1. **`node/tools/commands/add-skills.ts`** — `registerAddSkills(program)` with skill name validation, `scripts/` special-casing, conflict detection, dry-run support, and coloured output.
2. **`node/tools/commands/add-commands.ts`** — `registerAddCommands(program)` with `findCommandMd()` helper, `.md` file placement, scripts merging, and conflict detection on the `.md` path.
3. **`node/tools/commands/add-workflows.ts`** — `registerAddWorkflows(program)` with flat agent file copy to output dir, remaining files to `docs/workflows/<name>/`, per-file conflict detection with consolidated error.

### Phase 5: End-to-End Testing & Build Verification

Validate the full pipeline from CLI invocation through filesystem mutations.

1. **E2E test suite for each command** — Cover: success path, `--dry-run` (assert no fs mutations), `--force` overwrite, `--output` custom dir, invalid resource name, `SKIP_DIRS` exclusion.
2. **Build pipeline** — Run `tsc`, verify `dist/` output, test compiled JS with `node dist/cli.js add-skills --help`.
3. **npx simulation** — `npm pack` and install from tarball to verify resource resolution in installed mode.

### Phase 6: Polish & Documentation

1. **Error message review** — Verify all error paths produce red, actionable messages with file paths and remediation hints.
2. **README.md** — Usage examples, installation instructions, development setup.
3. **Final coverage audit** — Confirm 100% line and branch coverage on core logic modules.

---

## Technical Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Runtime** | Node.js LTS | v22+ | Execution environment with built-in test runner |
| **Language** | TypeScript | v5.5+ | Type-safe development with strict mode |
| **Module System** | ESM | — | `"type": "module"` in package.json; `import.meta.url` for path resolution |
| **CLI Framework** | Commander.js | v12+ | Command registration, option parsing, help generation |
| **Terminal Output** | Chalk | v5+ | ESM-native coloured terminal output (green/yellow/red) |
| **File System** | `node:fs` (sync) | Built-in | `mkdirSync`, `copyFileSync`, `readdirSync`, `existsSync`, `statSync` |
| **Path Handling** | `node:path` | Built-in | `join`, `resolve`, `relative`, `basename`, `dirname` |
| **URL Resolution** | `node:url` | Built-in | `fileURLToPath` for ESM `import.meta.url` conversion |
| **Dev Runner** | tsx | v4+ | Direct TypeScript execution during development |
| **Test Runner** | `node:test` | Built-in | `describe`, `it`, `mock` — no external frameworks |
| **Assertions** | `node:assert/strict` | Built-in | Strict equality assertions |
| **Build** | `tsc` | v5.5+ | TypeScript compiler to ES2022 JavaScript |

### Key Technical Decisions

1. **Synchronous filesystem APIs throughout.** Scaffolding is a one-shot, local-disk operation. Sync calls produce simpler, linear code with no async overhead penalty.
2. **`import.meta.url` two-phase resource lookup.** Enables the same code to resolve bundled resource directories whether running from `node_modules` (installed) or a source checkout (development/linked).
3. **Single compiled entry point for all three bin commands.** Commander.js dispatches based on the invoked subcommand name, so `add-skills`, `add-commands`, and `add-workflows` all point to `dist/cli.js` in the `bin` field.
4. **No external test framework.** Node.js v22+ built-in test runner (`node --test`) provides `describe`/`it`/`mock` natively, eliminating Jest/Vitest/Mocha dependencies.
5. **Chalk confined to CLI layer only.** Domain and infrastructure modules never import Chalk; coloured output is applied exclusively at the presentation boundary.

---

## File Structure

```
ai-workflow-kit/
├── node/
│   └── tools/
│       ├── cli.ts                          # Main entry point (shebang, Commander program)
│       ├── commands/
│       │   ├── add-skills.ts               # registerAddSkills() — skill scaffolding command
│       │   ├── add-commands.ts             # registerAddCommands() — command scaffolding command
│       │   └── add-workflows.ts            # registerAddWorkflows() — workflow scaffolding command
│       ├── lib/
│       │   ├── types.ts                    # Shared types: ResourcePath, CopyResult, CommandOptions
│       │   ├── resources.ts                # getResourceDir(), getAvailable*() discovery functions
│       │   └── fs.ts                       # SKIP_DIRS, copyTree(), copyFile()
│       └── __tests__/
│           ├── cli.test.ts                 # CLI entry point integration tests
│           ├── commands/
│           │   ├── add-skills.test.ts      # add-skills unit + E2E tests
│           │   ├── add-commands.test.ts    # add-commands unit + E2E tests
│           │   └── add-workflows.test.ts   # add-workflows unit + E2E tests
│           └── lib/
│               ├── resources.test.ts       # Resource discovery tests
│               └── fs.test.ts              # copyTree / copyFile tests (temp dir isolation)
├── skills/                                 # Bundled skill templates (published in package)
│   └── <skill-name>/
│       ├── SKILL.md
│       └── scripts/                        # Optional helper scripts
├── commands/                               # Bundled command templates (published in package)
│   └── <command-name>/
│       ├── <command-name>.md
│       └── scripts/                        # Optional helper scripts
├── workflows/                              # Bundled workflow templates (published in package)
│   └── <workflow-name>/
│       ├── agents/                         # Agent definition files
│       └── docs/                           # Supporting documentation
├── dist/                                   # Compiled JS output (gitignored, published)
│   └── tools/
│       ├── cli.js                          # Compiled entry point (bin target)
│       ├── commands/
│       │   ├── add-skills.js
│       │   ├── add-commands.js
│       │   └── add-workflows.js
│       └── lib/
│           ├── types.js
│           ├── resources.js
│           └── fs.js
├── package.json                            # ESM config, bin mappings, files whitelist
├── tsconfig.json                           # TypeScript strict config
└── README.md                               # Usage, installation, development docs
```

### Module Dependency Graph

```
cli.ts
 ├─→ commands/add-skills.ts
 │     ├─→ lib/resources.ts   (getAvailableSkills, getResourceDir)
 │     ├─→ lib/fs.ts          (copyTree, copyFile)
 │     └─→ lib/types.ts       (CommandOptions, CopyResult)
 ├─→ commands/add-commands.ts
 │     ├─→ lib/resources.ts   (getAvailableCommands, getResourceDir)
 │     ├─→ lib/fs.ts          (copyTree, copyFile)
 │     └─→ lib/types.ts       (CommandOptions, CopyResult)
 └─→ commands/add-workflows.ts
       ├─→ lib/resources.ts   (getAvailableWorkflows, getResourceDir)
       ├─→ lib/fs.ts          (copyTree, copyFile)
       └─→ lib/types.ts       (CommandOptions, CopyResult)
```

Dependencies flow strictly inward: CLI → Commands → Lib. No circular references. Chalk is imported only in command modules for output formatting.

---

## Dependencies

### Production Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `commander` | `^12.0.0` | CLI framework: subcommand registration, option parsing, auto-generated help |
| `chalk` | `^5.4.0` | ESM-native terminal colour output (green success, yellow dry-run, red errors) |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `typescript` | `^5.5.0` | TypeScript compiler with strict mode and ES2022 target |
| `@types/node` | `^22.0.0` | Node.js type definitions (fs, path, url, test, assert) |
| `tsx` | `^4.0.0` | Run TypeScript directly during development without compilation |

### Built-in Node.js Modules (No Install Required)

| Module | Usage |
|--------|-------|
| `node:fs` | Synchronous file system operations: `mkdirSync`, `copyFileSync`, `readdirSync`, `existsSync`, `statSync` |
| `node:path` | Path construction: `join`, `resolve`, `relative`, `basename`, `dirname` |
| `node:url` | ESM path resolution: `fileURLToPath(import.meta.url)` |
| `node:test` | Built-in test runner: `describe`, `it`, `mock`, `beforeEach`, `afterEach` |
| `node:assert/strict` | Test assertions: `equal`, `deepEqual`, `throws`, `doesNotThrow` |
| `node:os` | `tmpdir()` for test isolation with `mkdtempSync` |

---

## API Design

### Shared Types (`lib/types.ts`)

```typescript
export type ResourcePath = string;

export interface CopyResult {
  copied: string[];
}

export interface CommandOptions {
  output: string;
  force: boolean;
  dryRun: boolean;
}
```

### Resource Discovery (`lib/resources.ts`)

| Function | Signature | Returns |
|----------|-----------|---------|
| `getResourceDir` | `(name: string) => string` | Absolute path to the resource category directory |
| `getAvailableSkills` | `() => string[]` | Sorted array of skill directory names |
| `getAvailableCommands` | `() => string[]` | Sorted array of command directory names |
| `getAvailableWorkflows` | `() => string[]` | Sorted array of workflow directory names |

### File Operations (`lib/fs.ts`)

| Function | Signature | Returns |
|----------|-----------|---------|
| `copyTree` | `(src: string, dst: string) => string[]` | Array of absolute paths of all written files |
| `copyFile` | `(src: string, dst: string) => string` | Absolute path of the written file |

### Command Registration

| Function | Module | Signature |
|----------|--------|-----------|
| `registerAddSkills` | `commands/add-skills.ts` | `(program: Command) => void` |
| `registerAddCommands` | `commands/add-commands.ts` | `(program: Command) => void` |
| `registerAddWorkflows` | `commands/add-workflows.ts` | `(program: Command) => void` |

---

## Configuration Files

### `package.json`

```jsonc
{
  "name": "ai-workflow-kit",
  "version": "1.0.0",
  "description": "Scaffold AI agent assets (skills, commands, workflows) into your project",
  "type": "module",
  "engines": { "node": ">=22.0.0" },
  "bin": {
    "add-skills":    "./dist/tools/cli.js",
    "add-commands":  "./dist/tools/cli.js",
    "add-workflows": "./dist/tools/cli.js"
  },
  "files": ["dist/", "skills/", "commands/", "workflows/"],
  "scripts": {
    "build": "tsc --project tsconfig.json",
    "dev": "tsx node/tools/cli.ts",
    "test": "node --import tsx --test 'node/tools/__tests__/**/*.test.ts'",
    "typecheck": "tsc --noEmit"
  },
  "keywords": ["ai", "agent", "workflow", "scaffold", "cli", "cursor"],
  "license": "MIT",
  "dependencies": {
    "chalk": "^5.4.0",
    "commander": "^12.0.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "typescript": "^5.5.0",
    "tsx": "^4.0.0"
  }
}
```

### `tsconfig.json`

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./node",
    "strict": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "esModuleInterop": false,
    "forceConsistentCasingInImports": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  },
  "include": ["node/**/*.ts"],
  "exclude": ["node/**/__tests__/**", "node/**/*.test.ts"]
}
```

---

## Command Execution Flow

All three commands follow the same five-step execution flow, enforced by the shared architecture:

```
┌─────────────────────────────────────────────────────────┐
│  1. VALIDATE resource name                              │
│     getAvailable*() → check name exists                 │
│     ✗ → print available list (chalk.red) → exit 1       │
├─────────────────────────────────────────────────────────┤
│  2. DRY-RUN check                                       │
│     if --dry-run → print planned ops (chalk.yellow)     │
│     → exit 0 (no fs mutations)                          │
├─────────────────────────────────────────────────────────┤
│  3. CONFLICT detection                                  │
│     check destination paths with existsSync             │
│     ✗ (no --force) → print conflicts (chalk.red)        │
│     → exit 1                                            │
├─────────────────────────────────────────────────────────┤
│  4. COPY operations                                     │
│     copyTree / copyFile → accumulate written paths      │
│     wrap in try/catch → actionable error on failure     │
├─────────────────────────────────────────────────────────┤
│  5. REPORT success                                      │
│     chalk.green summary with relative paths             │
│     → exit 0                                            │
└─────────────────────────────────────────────────────────┘
```

---

## Testing Strategy

### Test File Mapping

| Source Module | Test File | Key Test Cases |
|--------------|-----------|----------------|
| `lib/types.ts` | (type-only, no runtime tests) | TypeScript compilation validates types |
| `lib/fs.ts` | `__tests__/lib/fs.test.ts` | `copyTree` recursive copy, `SKIP_DIRS` filtering, `copyFile` single file, parent dir creation, empty source dir |
| `lib/resources.ts` | `__tests__/lib/resources.test.ts` | Two-phase lookup (installed vs dev), missing resource error, `getAvailable*` returns sorted names, empty resource dir |
| `commands/add-skills.ts` | `__tests__/commands/add-skills.test.ts` | Success path, `scripts/` merging, `--dry-run` no mutations, `--force` overwrite, `--output` custom dir, invalid name |
| `commands/add-commands.ts` | `__tests__/commands/add-commands.test.ts` | `.md` file placement, `findCommandMd` resolution, `scripts/` merging, conflict on `.md` path, `--dry-run`, `--force` |
| `commands/add-workflows.ts` | `__tests__/commands/add-workflows.test.ts` | Agent flat copy, docs directory copy, per-file conflict detection, consolidated conflict list, `--dry-run`, `--force` |
| `cli.ts` | `__tests__/cli.test.ts` | Program creation, all 3 commands registered, `--version` output, `--help` output |

### Test Patterns

- **Filesystem isolation:** Every test that touches the filesystem creates a temp directory via `mkdtempSync(path.join(os.tmpdir(), 'awkit-'))` and cleans it in an `after` hook.
- **No mocking fs for unit tests:** Since the operations are synchronous and local, tests use real temp directories for correctness confidence.
- **Mock `import.meta.url`:** Resource resolution tests mock the URL to simulate both installed-package and development-checkout scenarios.
- **Exit code assertions:** E2E tests capture `process.exitCode` and stdout/stderr to validate error paths.

### Coverage Targets

| Module Category | Line Coverage | Branch Coverage |
|----------------|--------------|-----------------|
| `lib/fs.ts` | 100% | 100% |
| `lib/resources.ts` | 100% | 100% |
| `commands/*.ts` | 100% | 100% |
| `cli.ts` | 100% | 100% |

---

## Error Handling Strategy

| Error Scenario | Exit Code | Output Colour | Message Pattern |
|---------------|-----------|---------------|-----------------|
| Invalid resource name | 1 | Red | `Error: Skill '<name>' not found. Available skills: <list>` |
| Destination conflict (no --force) | 1 | Red | `Error: Destination already exists: <path>. Use --force to overwrite.` |
| Filesystem permission denied | 1 | Red | `Error: Permission denied writing to <path>. Check directory permissions.` |
| Missing `.md` in command bundle | 1 | Red | `Error: No '<name>.md' found in command bundle at <path>.` |
| Resource directory not found | 1 | Red | `Error: Resource directory '<name>' not found. Package may be corrupted.` |
| Usage/argument error | 2 | Red | Commander.js built-in error handling |

---

## Build & Distribution Pipeline

### Build Steps

```bash
# 1. Type-check without emitting
npm run typecheck

# 2. Compile TypeScript to JavaScript
npm run build
# Output: dist/tools/cli.js, dist/tools/commands/*.js, dist/tools/lib/*.js

# 3. Run all tests
npm test

# 4. Pack for distribution
npm pack
# Creates: ai-workflow-kit-1.0.0.tgz containing dist/, skills/, commands/, workflows/
```

### Compiled Output Structure

```
dist/
└── tools/
    ├── cli.js                    # Entry point with shebang
    ├── cli.d.ts
    ├── commands/
    │   ├── add-skills.js
    │   ├── add-skills.d.ts
    │   ├── add-commands.js
    │   ├── add-commands.d.ts
    │   ├── add-workflows.js
    │   └── add-workflows.d.ts
    └── lib/
        ├── types.js
        ├── types.d.ts
        ├── resources.js
        ├── resources.d.ts
        ├── fs.js
        └── fs.d.ts
```

### Import Path Convention

All TypeScript imports use `.js` extensions to match compiled output:

```typescript
import { copyTree } from '../lib/fs.js';
import { getResourceDir } from '../lib/resources.js';
import type { CommandOptions } from '../lib/types.js';
```

This is required by `"module": "NodeNext"` — TypeScript resolves `.js` imports to the corresponding `.ts` source files during compilation, and the extensions are correct at runtime.

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `import.meta.url` resolution differs between tsx and compiled JS | Medium | High | Test both modes explicitly; E2E test against `npm pack` tarball |
| Commander.js subcommand routing with shared `bin` entry | Low | Medium | Validate `process.argv` handling for all three bin names |
| Chalk v5 ESM-only breaks in CJS contexts | Low | Low | Entire project is ESM; enforce `"type": "module"` |
| `SKIP_DIRS` set misses platform-specific artifacts | Low | Low | Set is configurable; add entries as discovered |
| Test temp directories not cleaned on assertion failure | Medium | Low | Use `after` hooks (not `afterEach`) with unconditional cleanup |
