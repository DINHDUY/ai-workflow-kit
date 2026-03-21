# Feature Specification: ai-workflow-kit Node.js CLI Package

**Feature ID:** 001-node-cli-kit
**Version:** 1.0.0
**Created:** 2026-03-21
**Status:** Draft
**Constitution:** [.specify/memory/constitution.md](../../../.specify/memory/constitution.md)
**Reference:** [docs/node-kit-features.md](../../../docs/node-kit-features.md)

---

## Overview

The `ai-workflow-kit` CLI package is a Node.js/TypeScript tool that scaffolds AI agent assets (skills, commands, and workflows) into target projects. It exposes three installable CLI commands—`add-skills`, `add-commands`, and `add-workflows`—each copying bundled resource templates into a user's project with support for output directory customization, force-overwrite, and dry-run preview.

---

## User Stories

### US1: Install a Skill Template

As a **developer integrating AI agent capabilities**, I want to run `add-skills <skillName>` so that the skill's template files are copied into my project's skills directory without manual file management.

**Details:**
- The command locates the named skill from the bundled `skills/` directory.
- Files are copied recursively to `./skills/<skillName>/` by default.
- A special-cased `scripts/` subdirectory within the skill bundle is merged into the project-root `scripts/` directory.
- The developer sees a green success summary listing all files written.

### US2: Install a Command Template

As a **developer setting up AI-agent slash commands**, I want to run `add-commands <commandName>` so that the command's `.md` file is placed into `.cursor/commands/` and any bundled scripts are installed, making the command available in Cursor chat.

**Details:**
- The command locates `<commandName>.md` inside the bundled `commands/<commandName>/` directory.
- The `.md` file is copied to `.cursor/commands/<commandName>.md` by default.
- Any `scripts/` subdirectory contents are merged into the project-root `scripts/` directory.

### US3: Install a Workflow Template

As a **developer configuring multi-agent workflows**, I want to run `add-workflows <workflowName>` so that agent definition files land in `.cursor/agents/` and supporting documentation goes to `docs/workflows/<workflowName>/`.

**Details:**
- Agent files from the `agents/` subdirectory are copied flat into the output directory (`.cursor/agents/` by default).
- All remaining files (README, diagrams, reference docs) are copied to `docs/workflows/<workflowName>/`.

### US4: Customize Output Directory

As a **developer with a non-standard project layout**, I want to specify `--output <path>` on any command so that scaffolded files land in my preferred directory instead of the default.

**Details:**
- `add-skills --output ./my-skills TEMPLATE` copies to `./my-skills/TEMPLATE/` instead of `./skills/TEMPLATE/`.
- `add-commands --output ./my-commands TEMPLATE` copies the `.md` file to `./my-commands/TEMPLATE.md`.
- `add-workflows --output ./my-agents TEMPLATE` copies agent files to `./my-agents/`.

### US5: Preview Changes with Dry Run

As a **cautious developer**, I want to pass `--dry-run` to any command so that I see exactly which files would be created or overwritten without any filesystem mutations.

**Details:**
- Dry-run output mirrors the real copy plan, listing each source → destination pair.
- Output is displayed in yellow to distinguish it from actual operations.
- No files or directories are created, modified, or deleted.
- The exit code is `0` on successful dry-run preview.

### US6: Force Overwrite Existing Files

As a **developer updating previously scaffolded assets**, I want to pass `--force` so that existing files are overwritten with the latest template versions instead of the command aborting on conflict.

**Details:**
- Without `--force`, the command checks for existing destination paths and exits with code `1` plus a conflict list if any exist.
- With `--force`, all destination files are overwritten silently.

### US7: Discover Available Resources

As a **developer exploring what's available**, I want to see a helpful error message listing all available resource names when I request a name that doesn't exist.

**Details:**
- If `<skillName>`, `<commandName>`, or `<workflowName>` is not found in the bundled resources, the command prints the list of valid names and exits with code `1`.

### US8: Run without Installation

As a **developer who wants to try the tool quickly**, I want to run commands via `npx ai-workflow-kit add-skills TEMPLATE` without a global install so that I can scaffold assets from a registry or git URL in a single command.

**Details:**
- The `package.json` `bin` field maps all three commands to the compiled entry point.
- Resource resolution via `import.meta.url` works both from `node_modules` (installed) and from a source checkout (development/linked).

---

## Functional Requirements

### FR1: CLI Entry Point and Command Registration

- A single entry point (`cli.ts`) registers three subcommands via Commander.js v12+.
- The entry point includes a shebang (`#!/usr/bin/env node`) for direct execution.
- Package version is read from `process.env.npm_package_version` with a `'0.0.0'` fallback.
- Each command is registered by a dedicated `register*` function that receives the root `Command` instance.

### FR2: Shared CLI Options

All three commands support the following options:

| Option | Flag | Default | Description |
|--------|------|---------|-------------|
| Output | `-o, --output <path>` | Command-specific | Target directory for scaffolded files |
| Force | `-f, --force` | `false` | Overwrite existing files on conflict |
| Dry Run | `--dry-run` | `false` | Preview without filesystem mutations |
| Version | `-V, --version` | — | Print package version and exit |

Default output directories:
- `add-skills`: `./skills`
- `add-commands`: `.cursor/commands`
- `add-workflows`: `.cursor/agents`

### FR3: Resource Discovery and Resolution

- `getResourceDir(name)` implements a two-phase lookup using `import.meta.url`:
  - **Phase 1 (installed):** Resolves relative to the compiled output inside `node_modules`.
  - **Phase 2 (development):** Walks up from the module location to find the repository root.
- Throws a descriptive `Error` if neither phase finds the directory.
- `getAvailableSkills()`, `getAvailableCommands()`, and `getAvailableWorkflows()` each call `getResourceDir`, read directory entries with `readdirSync`, filter to directories only, and return sorted names.

### FR4: File Copy Operations

- `copyTree(src, dst)` recursively copies a directory tree, creating destination directories with `mkdirSync({ recursive: true })` and copying files with `copyFileSync`.
- `copyFile(src, dst)` copies a single file, creating parent directories as needed.
- Both functions skip entries in `SKIP_DIRS`: `__pycache__`, `.git`, `node_modules`, `dist`, `.turbo`.
- Both functions return the absolute paths of all written files.
- All filesystem operations use synchronous `node:fs` APIs.

### FR5: add-skills Command

- Accepts a required positional argument `<skillName>`.
- Validates the skill name against `getAvailableSkills()`.
- Copies `skills/<name>/**` (excluding `scripts/`) to `<output>/<name>/`.
- Copies `skills/<name>/scripts/**` to `scripts/` at the project root.
- Checks for destination directory conflicts before writing (unless `--force`).

### FR6: add-commands Command

- Accepts a required positional argument `<commandName>`.
- Validates the command name against `getAvailableCommands()`.
- Locates `<commandName>.md` inside the command bundle via `findCommandMd()`.
- Copies the `.md` file to `<output>/<commandName>.md`.
- Copies `commands/<name>/scripts/**` to `scripts/` at the project root.
- Checks for destination `.md` file conflict before writing (unless `--force`).

### FR7: add-workflows Command

- Accepts a required positional argument `<workflowName>`.
- Validates the workflow name against `getAvailableWorkflows()`.
- Copies `workflows/<name>/agents/**` (flat, files only) to `<output>/`.
- Copies `workflows/<name>/**` (everything except `agents/`) to `docs/workflows/<name>/`.
- Checks each agent file path and the docs output directory individually for conflicts.
- Presents a consolidated conflict list and exits `1` if conflicts found without `--force`.

### FR8: Common Execution Flow

All commands follow this sequence:

1. Validate `<name>` against the available resource list → exit `1` with available list if not found.
2. If `--dry-run` → print planned operations in yellow and return with exit `0`.
3. Check destination conflicts with `fs.existsSync` → exit `1` with conflict list if found and `--force` not set.
4. Perform copy operations; accumulate written file paths.
5. Print success summary in green with the list of written files (displayed as relative paths via `path.relative(process.cwd(), absPath)`).

### FR9: Error Handling

- All filesystem operations are wrapped in `try/catch` with meaningful error messages that include the file path causing the error.
- Exit codes: `0` success, `1` operational error, `2` usage/argument error.
- Error messages are printed in red via Chalk and are actionable (what went wrong, which path, what to do).
- No `console.log` in library code; all output goes through structured output functions that respect `--dry-run`.

---

## Non-Functional Requirements

### NFR1: Technology Stack

- **Runtime:** Node.js LTS v22+ (`"engines": { "node": ">=22.0.0" }`).
- **Language:** TypeScript v5.5+ with strict mode enabled.
- **Module System:** ESM exclusively (`"type": "module"` in `package.json`); no CommonJS `require()`.
- **CLI Framework:** Commander.js v12+.
- **Terminal Output:** Chalk v5+ (ESM-native), used only in CLI/presentation layer.
- **Dev Runtime:** tsx for running TypeScript directly during development.

### NFR2: Code Quality

- TypeScript strict mode with no `@ts-ignore` or `@ts-expect-error` suppressions (unless documented).
- All functions have explicit return types; exported functions have JSDoc descriptions.
- Maximum function length: 30 lines. Maximum file length: 200 lines.
- No `any` types unless explicitly justified with a comment.
- Paths constructed exclusively via `node:path` functions; no string concatenation for paths.
- `import.meta.url` used instead of `__dirname`/`__filename` throughout.

### NFR3: Architecture

- Layered architecture: CLI layer → Application layer → Domain layer → Infrastructure layer.
- Dependencies flow inward only; no business logic in CLI entry points.
- Single Responsibility: each module handles one concern.
- Open/Closed: new commands added by composing existing utilities, not modifying them.
- Shared logic for options, file operations, and validation centralized in reusable modules.

### NFR4: Package Distribution

- `package.json` includes proper metadata: `name`, `version`, `description`, `keywords`, `author`, `license`, `repository`, `engines`, `bin`, `files`, `type`, `exports`.
- `bin` field maps `add-skills`, `add-commands`, `add-workflows` to the compiled entry point.
- `files` whitelist in `package.json` controls published contents: `dist/`, `skills/`, `commands/`, `workflows/`.
- `tsconfig.json`: `target: ES2022`, `module: NodeNext`, `moduleResolution: NodeNext`, `strict: true`.

### NFR5: Testing

- All tests use the Node.js built-in test runner (`node --test`) exclusively; no external test frameworks.
- Assertions via `node:assert/strict`; mocking via `node:test` built-in `mock` API.
- Every source module has a corresponding test file mirroring the source directory structure.
- Test naming convention: `{module-name}.test.ts` with `describe`/`it` blocks following "should [behavior] when [condition]".
- File system tests use `mkdtempSync` for isolated temporary directories, cleaned in `after` hooks.
- End-to-end tests for each command cover: successful copy, `--dry-run`, `--force` overwrite, `--output` custom directory, missing resource error handling.
- TDD cycle strictly enforced: red-green-refactor.
- Target 100% line and branch coverage for core logic.

### NFR6: Performance

- Synchronous filesystem APIs used throughout (scaffolding is a single-run, local-disk operation).
- Resource discovery runs once at command startup.
- No unnecessary async overhead.

---

## Acceptance Criteria

### AC1: add-skills Success Path

- **Given** a valid skill name exists in the bundled `skills/` directory
- **When** the user runs `add-skills <skillName>`
- **Then** the skill's files are copied to `./skills/<skillName>/`, scripts go to `./scripts/`, and a green success summary is printed listing all written files as relative paths.

### AC2: add-commands Success Path

- **Given** a valid command name exists in the bundled `commands/` directory
- **When** the user runs `add-commands <commandName>`
- **Then** `<commandName>.md` is copied to `.cursor/commands/<commandName>.md`, scripts go to `./scripts/`, and a green success summary is printed.

### AC3: add-workflows Success Path

- **Given** a valid workflow name exists in the bundled `workflows/` directory
- **When** the user runs `add-workflows <workflowName>`
- **Then** agent files from `agents/` are copied to `.cursor/agents/`, other files go to `docs/workflows/<workflowName>/`, and a green success summary is printed.

### AC4: Custom Output Directory

- **Given** any command is run with `--output <customPath>`
- **When** the copy operation executes
- **Then** files are placed under `<customPath>` instead of the default directory, and the summary reflects the custom paths.

### AC5: Dry Run Produces No Side Effects

- **Given** any command is run with `--dry-run`
- **When** the command completes
- **Then** no files or directories are created, modified, or deleted on disk; the output is displayed in yellow showing the planned operations; the exit code is `0`.

### AC6: Force Overwrite

- **Given** destination files already exist and the user passes `--force`
- **When** the copy operation executes
- **Then** existing files are overwritten with the new template versions and a success summary is printed.

### AC7: Conflict Detection Without Force

- **Given** destination files already exist and `--force` is NOT passed
- **When** the command runs
- **Then** the command exits with code `1`, prints a red error listing all conflicting paths, and does not modify any files.

### AC8: Invalid Resource Name

- **Given** the user specifies a resource name that does not exist in the bundled directory
- **When** the command runs
- **Then** the command exits with code `1` and prints a red error message listing all available resource names.

### AC9: Resource Resolution Works in Both Modes

- **Given** the package is either installed via npm/npx or run from a source checkout
- **When** any command is invoked
- **Then** resource directories are correctly located via the two-phase `import.meta.url` lookup without errors.

### AC10: SKIP_DIRS Are Excluded

- **Given** source resource directories contain entries matching `SKIP_DIRS` (`__pycache__`, `.git`, `node_modules`, `dist`, `.turbo`)
- **When** a copy operation runs
- **Then** those directories and their contents are not present in the destination.

### AC11: Error Messages Are Actionable

- **Given** a filesystem error occurs (e.g., permission denied, missing directory)
- **When** the error is caught
- **Then** the error message includes what went wrong, the specific file path, and guidance for the user; exit code is `1`.

### AC12: npx Execution Without Global Install

- **Given** the package is published to npm
- **When** a user runs `npx ai-workflow-kit add-skills <name>`
- **Then** the command executes successfully, resolving resources from within the `node_modules` package structure.

### AC13: Test Coverage

- **Given** the complete source codebase
- **When** `node --test` is executed
- **Then** all tests pass with zero warnings, every source module has a corresponding test, and core logic achieves 100% line and branch coverage.

---

## Out of Scope

- **Authentication or network operations:** The CLI is purely local; no API calls, no registry authentication beyond npm's own.
- **Interactive prompts:** All input is via command-line arguments; no interactive TUI or prompts.
- **Template variable substitution:** Files are copied verbatim; no mustache/handlebars templating.
- **Watch mode or hot-reload:** Scaffolding is a one-shot operation.
- **Windows-specific path handling:** Target is Node.js LTS on macOS/Linux; Windows compatibility is not a first-class requirement in v1.0.
- **Plugin system:** No mechanism for user-defined resource types or custom commands beyond the three built-in ones.
- **Async filesystem operations:** Synchronous APIs are used by design for simplicity; async migration is deferred unless performance profiling demands it.

---

## Glossary

| Term | Definition |
|------|------------|
| **Skill** | A directory bundle of AI agent template files (prompts, configs, optional scripts) |
| **Command** | A `.md` file that defines a Cursor slash command, plus optional helper scripts |
| **Workflow** | A multi-agent orchestration bundle containing agent definitions and documentation |
| **Resource** | Generic term for any bundled template (skill, command, or workflow) |
| **Scaffolding** | The process of copying template files into a target project structure |
| **Two-phase lookup** | The `getResourceDir` strategy: first check installed package path, then development source path |
| **SKIP_DIRS** | Set of directory names excluded from recursive copy: `__pycache__`, `.git`, `node_modules`, `dist`, `.turbo` |
