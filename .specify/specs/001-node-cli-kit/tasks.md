# Tasks: ai-workflow-kit Node.js CLI Package

**Feature ID:** 001-node-cli-kit
**Generated:** 2026-03-21
**Plan:** [plan.md](./plan.md)
**Spec:** [spec.md](./spec.md)

---

## Phase 1: Project Scaffolding & Configuration

### Task 1 — Initialize `package.json`

- [ ] Create `package.json` with:
  - `"name": "ai-workflow-kit"`, `"version": "1.0.0"`
  - `"type": "module"` for ESM
  - `"engines": { "node": ">=22.0.0" }`
  - `"bin"` mapping `add-skills`, `add-commands`, `add-workflows` → `./dist/tools/cli.js`
  - `"files": ["dist/", "skills/", "commands/", "workflows/"]`
  - `"scripts"`: `build`, `dev`, `test`, `typecheck`
  - `"keywords"`, `"license": "MIT"`, `"description"`
- **File:** `package.json`
- **Dependencies:** None (first task)
- **Acceptance:** `npm install` succeeds; `node -e "JSON.parse(require('fs').readFileSync('package.json','utf8'))"` parses without error

### Task 2 — Create `tsconfig.json`

- [ ] Create `tsconfig.json` with:
  - `target: ES2022`, `module: NodeNext`, `moduleResolution: NodeNext`
  - `strict: true`, `outDir: ./dist`, `rootDir: ./node`
  - `declaration: true`, `declarationMap: true`, `sourceMap: true`
  - `include: ["node/**/*.ts"]`, `exclude: ["node/**/__tests__/**", "node/**/*.test.ts"]`
- **File:** `tsconfig.json`
- **Depends on:** Task 1 (TypeScript dev dependency must be declared)
- **Acceptance:** `npx tsc --noEmit` runs without config errors (no source files needed yet)

### Task 3 — Install dependencies

- [ ] Install production deps: `commander@^12.0.0`, `chalk@^5.4.0`
- [ ] Install dev deps: `typescript@^5.5.0`, `tsx@^4.0.0`, `@types/node@^22.0.0`
- [ ] Verify `node_modules/` is populated and `package-lock.json` created
- **Depends on:** Task 1 (package.json must exist)
- **Acceptance:** `npm ls --depth=0` lists all 5 packages without errors

### Task 4 — Create directory scaffold

- [ ] Create directory structure:
  - `node/tools/commands/`
  - `node/tools/lib/`
  - `node/tools/__tests__/commands/`
  - `node/tools/__tests__/lib/`
- **Depends on:** Task 1
- **Acceptance:** All directories exist; `find node -type d` shows expected tree

---

## Phase 2: Shared Library Layer (TDD)

### Task 5 — Define shared types in `lib/types.ts`

- [ ] Create `node/tools/lib/types.ts` with:
  - `ResourcePath` type alias (`string`)
  - `CopyResult` interface with `copied: string[]`
  - `CommandOptions` interface with `output: string`, `force: boolean`, `dryRun: boolean`
- **File:** `node/tools/lib/types.ts`
- **Depends on:** Task 4 (directory must exist)
- **Acceptance:** `npx tsc --noEmit` passes; types are importable from other modules

### Task 6 — Write tests for `lib/fs.ts`

- [ ] Create `node/tools/__tests__/lib/fs.test.ts` with test cases:
  - `copyTree` recursively copies a directory tree
  - `copyTree` skips entries in `SKIP_DIRS` (`__pycache__`, `.git`, `node_modules`, `dist`, `.turbo`)
  - `copyTree` creates destination directories as needed
  - `copyTree` handles empty source directory
  - `copyFile` copies a single file
  - `copyFile` creates parent directories if missing
  - `SKIP_DIRS` constant contains expected values
- [ ] Use `mkdtempSync` for filesystem isolation; cleanup in `after` hooks
- **File:** `node/tools/__tests__/lib/fs.test.ts`
- **Depends on:** Task 4, Task 5 (types needed for return type assertions)
- **Acceptance:** Tests exist and fail (red phase of TDD)

### Task 7 — Implement `lib/fs.ts`

- [ ] Create `node/tools/lib/fs.ts` with:
  - `SKIP_DIRS` constant: `Set<string>` with `__pycache__`, `.git`, `node_modules`, `dist`, `.turbo`
  - `copyTree(src: string, dst: string): string[]` — recursive sync copy via `readdirSync`/`mkdirSync`/`copyFileSync`, skipping `SKIP_DIRS`, returning absolute paths of written files
  - `copyFile(src: string, dst: string): string` — single file copy with parent directory creation, returning absolute path of written file
- [ ] Use only `node:fs` sync APIs and `node:path` for path construction
- **File:** `node/tools/lib/fs.ts`
- **Depends on:** Task 5 (types), Task 6 (tests must exist first — TDD)
- **Acceptance:** All tests from Task 6 pass (green phase); `npx tsc --noEmit` passes

### Task 8 — Write tests for `lib/resources.ts`

- [ ] Create `node/tools/__tests__/lib/resources.test.ts` with test cases:
  - `getResourceDir('skills')` returns path to `skills/` directory
  - `getResourceDir('commands')` returns path to `commands/` directory
  - `getResourceDir('workflows')` returns path to `workflows/` directory
  - `getResourceDir` throws descriptive error for missing resource directory
  - Two-phase lookup: resolves from installed package path (Phase 1) and dev checkout path (Phase 2)
  - `getAvailableSkills()` returns sorted array of skill directory names
  - `getAvailableCommands()` returns sorted array of command directory names
  - `getAvailableWorkflows()` returns sorted array of workflow directory names
  - `getAvailable*()` returns empty array for empty resource directory
- [ ] Mock `import.meta.url` for installed vs development scenarios
- **File:** `node/tools/__tests__/lib/resources.test.ts`
- **Depends on:** Task 4
- **Acceptance:** Tests exist and fail (red phase)

### Task 9 — Implement `lib/resources.ts`

- [ ] Create `node/tools/lib/resources.ts` with:
  - `getResourceDir(name: string): string` — two-phase `import.meta.url` lookup (installed package, then dev checkout)
  - `getAvailableSkills(): string[]` — reads `skills/` directory, filters to dirs, returns sorted names
  - `getAvailableCommands(): string[]` — reads `commands/` directory, filters to dirs, returns sorted names
  - `getAvailableWorkflows(): string[]` — reads `workflows/` directory, filters to dirs, returns sorted names
- [ ] Use `fileURLToPath(import.meta.url)` from `node:url`
- [ ] Throw descriptive `Error` if resource directory not found in either phase
- **File:** `node/tools/lib/resources.ts`
- **Depends on:** Task 5 (types), Task 8 (tests — TDD)
- **Acceptance:** All tests from Task 8 pass; `npx tsc --noEmit` passes

---

## Phase 3: CLI Entry Point & Command Registration

### Task 10 — Write tests for `cli.ts`

- [ ] Create `node/tools/__tests__/cli.test.ts` with test cases:
  - Program is created with name `ai-workflow-kit`
  - Program version is set from `process.env.npm_package_version` (with `'0.0.0'` fallback)
  - All three subcommands are registered: `add-skills`, `add-commands`, `add-workflows`
  - `--help` output includes all three command names
  - `--version` outputs the version string
- **File:** `node/tools/__tests__/cli.test.ts`
- **Depends on:** Task 4
- **Acceptance:** Tests exist and fail (red phase)

### Task 11 — Implement `cli.ts` entry point

- [ ] Create `node/tools/cli.ts` with:
  - Shebang line: `#!/usr/bin/env node`
  - Commander program setup with name, description, version from `process.env.npm_package_version ?? '0.0.0'`
  - Import and call `registerAddSkills(program)`, `registerAddCommands(program)`, `registerAddWorkflows(program)`
  - `program.parse()` at the end
- **File:** `node/tools/cli.ts`
- **Depends on:** Task 10 (tests — TDD), Task 9 (resources module), Task 7 (fs module)
- **Acceptance:** All tests from Task 10 pass; `npx tsc --noEmit` passes

### Task 12 — Verify tsx dev runner

- [ ] Confirm `npm run dev -- add-skills --help` prints usage correctly
- [ ] Confirm `npm run dev -- add-commands --help` prints usage correctly
- [ ] Confirm `npm run dev -- add-workflows --help` prints usage correctly
- [ ] Confirm `npm run dev -- --version` prints version string
- **Depends on:** Task 11, Task 3 (tsx must be installed)
- **Acceptance:** All four help/version outputs display correctly without errors

---

## Phase 4: Command Implementations (TDD)

### Task 13 — Write tests for `add-skills` command

- [ ] Create `node/tools/__tests__/commands/add-skills.test.ts` with test cases:
  - Success path: copies skill files to `./skills/<name>/`
  - `scripts/` subdirectory contents are merged to project-root `scripts/`
  - `--dry-run` prints planned operations in yellow, creates no files
  - `--force` overwrites existing files
  - `--output <path>` copies to custom directory
  - Invalid skill name prints available list and exits with code 1
  - Conflict detection exits with code 1 listing conflicting paths (no `--force`)
  - `SKIP_DIRS` entries are excluded from copy
- [ ] Use temp directories for isolation
- **File:** `node/tools/__tests__/commands/add-skills.test.ts`
- **Depends on:** Task 7 (fs module), Task 9 (resources module), Task 5 (types)
- **Acceptance:** Tests exist and fail (red phase)

### Task 14 — Implement `add-skills.ts` command

- [ ] Create `node/tools/commands/add-skills.ts` with:
  - `registerAddSkills(program: Command): void`
  - Subcommand `add-skills <skillName>` with `-o, --output`, `-f, --force`, `--dry-run` options
  - Default output: `./skills`
  - Execution flow: validate → dry-run → conflict-check → copy → report
  - Skill name validation against `getAvailableSkills()`
  - `scripts/` special-casing: merge to project-root `scripts/` directory
  - Coloured output via Chalk: green (success), yellow (dry-run), red (errors)
  - Conflict detection with `existsSync` on destination paths
- **File:** `node/tools/commands/add-skills.ts`
- **Depends on:** Task 13 (tests — TDD), Task 7, Task 9, Task 5
- **Acceptance:** All tests from Task 13 pass; `npx tsc --noEmit` passes

### Task 15 — Write tests for `add-commands` command

- [ ] Create `node/tools/__tests__/commands/add-commands.test.ts` with test cases:
  - Success path: copies `<name>.md` to `.cursor/commands/<name>.md`
  - `findCommandMd()` locates the `.md` file inside the command bundle
  - `scripts/` subdirectory contents are merged to project-root `scripts/`
  - `--dry-run` prints planned operations, creates no files
  - `--force` overwrites existing `.md` file
  - `--output <path>` copies `.md` to custom directory
  - Invalid command name prints available list and exits with code 1
  - Conflict detection on `.md` path exits with code 1 (no `--force`)
  - Missing `.md` in command bundle produces actionable error
- [ ] Use temp directories for isolation
- **File:** `node/tools/__tests__/commands/add-commands.test.ts`
- **Depends on:** Task 7, Task 9, Task 5
- **Acceptance:** Tests exist and fail (red phase)

### Task 16 — Implement `add-commands.ts` command

- [ ] Create `node/tools/commands/add-commands.ts` with:
  - `registerAddCommands(program: Command): void`
  - Subcommand `add-commands <commandName>` with `-o, --output`, `-f, --force`, `--dry-run` options
  - Default output: `.cursor/commands`
  - `findCommandMd(bundlePath: string, commandName: string): string` helper to locate the `.md` file
  - `.md` file placement to `<output>/<commandName>.md`
  - `scripts/` merging to project-root `scripts/`
  - Conflict detection on the `.md` destination path
  - Coloured output via Chalk
- **File:** `node/tools/commands/add-commands.ts`
- **Depends on:** Task 15 (tests — TDD), Task 7, Task 9, Task 5
- **Acceptance:** All tests from Task 15 pass; `npx tsc --noEmit` passes

### Task 17 — Write tests for `add-workflows` command

- [ ] Create `node/tools/__tests__/commands/add-workflows.test.ts` with test cases:
  - Success path: agent files from `agents/` copied flat to `.cursor/agents/`, remaining files to `docs/workflows/<name>/`
  - `--dry-run` prints planned operations, creates no files
  - `--force` overwrites existing agent and doc files
  - `--output <path>` copies agent files to custom directory
  - Invalid workflow name prints available list and exits with code 1
  - Per-file conflict detection on individual agent files and docs directory
  - Consolidated conflict error message listing all conflicts
  - `SKIP_DIRS` entries excluded
- [ ] Use temp directories for isolation
- **File:** `node/tools/__tests__/commands/add-workflows.test.ts`
- **Depends on:** Task 7, Task 9, Task 5
- **Acceptance:** Tests exist and fail (red phase)

### Task 18 — Implement `add-workflows.ts` command

- [ ] Create `node/tools/commands/add-workflows.ts` with:
  - `registerAddWorkflows(program: Command): void`
  - Subcommand `add-workflows <workflowName>` with `-o, --output`, `-f, --force`, `--dry-run` options
  - Default output: `.cursor/agents`
  - Agent files from `agents/` subdirectory copied flat (files only) to output directory
  - Remaining files copied to `docs/workflows/<workflowName>/`
  - Per-file conflict detection with consolidated error list
  - Coloured output via Chalk
- **File:** `node/tools/commands/add-workflows.ts`
- **Depends on:** Task 17 (tests — TDD), Task 7, Task 9, Task 5
- **Acceptance:** All tests from Task 17 pass; `npx tsc --noEmit` passes

---

## Phase 5: End-to-End Testing & Build Verification

### Task 19 — E2E test suite for `add-skills`

- [ ] Add E2E tests to `node/tools/__tests__/commands/add-skills.test.ts` (or separate E2E file):
  - Full CLI invocation via `tsx node/tools/cli.ts add-skills <name>` with child process
  - Verify filesystem state after successful run
  - `--dry-run` assert zero filesystem mutations
  - `--force` overwrite existing files
  - `--output` custom directory
  - Invalid resource name returns exit code 1
  - `SKIP_DIRS` entries excluded from output
- **Depends on:** Task 14, Task 11
- **Acceptance:** All E2E tests pass

### Task 20 — E2E test suite for `add-commands`

- [ ] Add E2E tests to `node/tools/__tests__/commands/add-commands.test.ts` (or separate E2E file):
  - Full CLI invocation via `tsx node/tools/cli.ts add-commands <name>`
  - `.md` file placed correctly
  - `scripts/` merged to project root
  - `--dry-run`, `--force`, `--output` scenarios
  - Invalid name error
- **Depends on:** Task 16, Task 11
- **Acceptance:** All E2E tests pass

### Task 21 — E2E test suite for `add-workflows`

- [ ] Add E2E tests to `node/tools/__tests__/commands/add-workflows.test.ts` (or separate E2E file):
  - Full CLI invocation via `tsx node/tools/cli.ts add-workflows <name>`
  - Agent files in output dir, docs in `docs/workflows/<name>/`
  - `--dry-run`, `--force`, `--output` scenarios
  - Consolidated conflict error
  - Invalid name error
- **Depends on:** Task 18, Task 11
- **Acceptance:** All E2E tests pass

### Task 22 — TypeScript build pipeline

- [ ] Run `npm run build` (`tsc --project tsconfig.json`)
- [ ] Verify `dist/` output structure matches plan:
  - `dist/tools/cli.js` (with shebang preserved)
  - `dist/tools/commands/add-skills.js`, `add-commands.js`, `add-workflows.js`
  - `dist/tools/lib/types.js`, `resources.js`, `fs.js`
  - Corresponding `.d.ts` and `.js.map` files
- [ ] Test compiled JS: `node dist/tools/cli.js add-skills --help` works
- [ ] Test compiled JS: `node dist/tools/cli.js --version` outputs version
- **Depends on:** Task 11, Task 14, Task 16, Task 18
- **Acceptance:** `tsc` compiles without errors; compiled entry point runs correctly

### Task 23 — npx simulation test

- [ ] Run `npm pack` to create `ai-workflow-kit-1.0.0.tgz`
- [ ] Install tarball in a temporary directory: `npm install <path-to-tgz>`
- [ ] Verify resource resolution works from `node_modules`: `npx add-skills --help`
- [ ] Verify `import.meta.url` two-phase lookup resolves bundled resources from installed location
- **Depends on:** Task 22
- **Acceptance:** Commands execute correctly from installed tarball; resources are found

---

## Phase 6: Polish & Documentation

### Task 24 — Error message review

- [ ] Audit all error paths across all three commands:
  - Invalid resource name → red message listing available names
  - Destination conflict → red message listing conflicting paths with `--force` hint
  - Permission denied → red message with path and remediation
  - Missing `.md` in command bundle → red message with bundle path
  - Resource directory not found → red message suggesting package corruption
- [ ] Verify all error messages include: what went wrong, which path, what to do
- [ ] Verify exit codes: `0` success, `1` operational error, `2` usage/argument error
- **Depends on:** Task 14, Task 16, Task 18
- **Acceptance:** Manual review confirms all error messages are red, actionable, and include file paths

### Task 25 — Write `README.md`

- [ ] Create `README.md` with:
  - Project description and purpose
  - Installation instructions (`npm install`, `npx` usage)
  - Usage examples for all three commands with flags
  - `--dry-run`, `--force`, `--output` option documentation
  - Development setup (clone, install, test, build)
  - Project structure overview
  - License
- **File:** `README.md`
- **Depends on:** Task 22 (build must work for accurate instructions)
- **Acceptance:** README is comprehensive and all code examples are accurate

### Task 26 — Final coverage audit

- [ ] Run `npm test` with coverage enabled
- [ ] Verify 100% line and branch coverage for:
  - `node/tools/lib/fs.ts`
  - `node/tools/lib/resources.ts`
  - `node/tools/commands/add-skills.ts`
  - `node/tools/commands/add-commands.ts`
  - `node/tools/commands/add-workflows.ts`
  - `node/tools/cli.ts`
- [ ] Fix any coverage gaps by adding missing test cases
- [ ] Confirm all tests pass with zero warnings
- **Depends on:** Task 19, Task 20, Task 21
- **Acceptance:** `npm test` passes; coverage report shows 100% line/branch on core modules

---

## Dependency Graph

```
Task 1 (package.json)
├── Task 2 (tsconfig.json)
├── Task 3 (install deps)
│   └── Task 12 (verify tsx)
└── Task 4 (directory scaffold)
    ├── Task 5 (types.ts)
    │   ├── Task 6 (fs tests) → Task 7 (fs.ts)
    │   ├── Task 8 (resources tests) → Task 9 (resources.ts)
    │   ├── Task 13 (add-skills tests) → Task 14 (add-skills.ts)
    │   ├── Task 15 (add-commands tests) → Task 16 (add-commands.ts)
    │   └── Task 17 (add-workflows tests) → Task 18 (add-workflows.ts)
    └── Task 10 (cli tests) → Task 11 (cli.ts)
                                  ├── Task 12 (verify tsx)
                                  ├── Task 19 (E2E add-skills)
                                  ├── Task 20 (E2E add-commands)
                                  ├── Task 21 (E2E add-workflows)
                                  └── Task 22 (build pipeline)
                                        └── Task 23 (npx simulation)

Task 14, 16, 18 → Task 24 (error review)
Task 22 → Task 25 (README)
Task 19, 20, 21 → Task 26 (coverage audit)
```

## Summary

| Phase | Tasks | IDs |
|-------|-------|-----|
| Phase 1: Scaffolding | 4 | 1–4 |
| Phase 2: Shared Library (TDD) | 5 | 5–9 |
| Phase 3: CLI Entry Point | 3 | 10–12 |
| Phase 4: Commands (TDD) | 6 | 13–18 |
| Phase 5: E2E & Build | 5 | 19–23 |
| Phase 6: Polish & Docs | 3 | 24–26 |
| **Total** | **26** | **1–26** |
