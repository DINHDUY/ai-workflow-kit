# ai-workflow-kit Constitution

## Core Principles

### I. Test-Driven Development (NON-NEGOTIABLE)

- TDD is mandatory for every module: write tests first, watch them fail, then implement.
- Red-Green-Refactor cycle strictly enforced — no production code without a failing test.
- All tests use the Node.js built-in test runner (`node --test`) exclusively — no external test frameworks.
- Every source module (`src/**/*.ts`) must have a corresponding test file (`tests/**/*.test.ts`).
- Tests must cover: unit (individual functions), integration (CLI command end-to-end), and edge cases (missing dirs, permission errors, existing files).
- Target 100% line and branch coverage for core logic; file system operations must use temp directories for isolation.
- `--dry-run` behavior must be validated by asserting no file system mutations occur.

### II. SOLID Principles

- **Single Responsibility**: Each module handles one concern — argument parsing, file copying, output formatting, and option validation are separate modules.
- **Open/Closed**: New commands (e.g., `add-workflows`) are added by composing existing utilities, not modifying them.
- **Liskov Substitution**: Shared interfaces (e.g., `CommandOptions`, `CopyResult`) must be substitutable across all three CLI commands.
- **Interface Segregation**: Consumers depend only on the interfaces they use; CLI entry points do not import internals of other commands.
- **Dependency Inversion**: Higher-level command modules depend on shared library interfaces, not on each other's internals. Testability is achieved through temp directory isolation, not DI abstractions over `node:fs` (synchronous scaffolding operations do not benefit from filesystem indirection).

### III. DRY (Don't Repeat Yourself)

- Shared logic for `--output`, `--force`, and `--dry-run` handling is extracted into reusable utilities.
- Common file-copy operations live in a single shared module used by all three commands.
- Option definitions, validation, and error messages are centralized — not duplicated per command.
- Template directory resolution logic is defined once and parameterized by resource type.

### IV. Clean Code & Clean Architecture

- Functions are small, focused, and named to reveal intent — no comments needed to explain what code does.
- No nested callbacks or deeply indented logic; prefer early returns and guard clauses.
- Layered architecture: CLI layer (Commander.js) → Application layer (command orchestration) → Domain layer (copy logic, validation) → Infrastructure layer (file system operations).
- Dependencies flow inward only: CLI depends on Application, Application depends on Domain, Domain depends on Infrastructure abstractions.
- No business logic in CLI entry points; they parse arguments and delegate to application services.

### V. Simplicity & YAGNI

- Build only what the three commands require — no speculative abstractions.
- Start with synchronous `node:fs` APIs as specified; do not introduce async complexity unless proven necessary.
- Prefer composition over inheritance; prefer plain functions over classes where no state is needed.
- Every abstraction must justify its existence by serving at least two consumers or enabling testability.

## Technology Constraints

### Runtime & Language
- **Node.js**: LTS v22+ required. Use built-in modules (`node:fs`, `node:path`, `node:test`, `node:assert`) wherever possible.
- **TypeScript**: v5.5+ with strict mode enabled (`"strict": true`). No `any` types unless explicitly justified with a comment.
- **Module System**: ESM exclusively (`"type": "module"` in `package.json`). No CommonJS `require()` calls. All imports use `.js` extensions in compiled output.

### Dependencies
- **Commander.js**: v12+ for CLI argument parsing and command registration.
- **Chalk**: v5+ (ESM-native) for terminal output styling. Used only in the CLI/presentation layer, never in domain logic.
- **tsx**: Development-only dependency for running TypeScript directly during development.
- Minimize external dependencies. Every new dependency must be justified by significant complexity reduction.

### File System
- Use synchronous `node:fs` APIs (`mkdirSync`, `copyFileSync`, `readdirSync`, `existsSync`, `statSync`) for all file operations.
- All paths constructed via `node:path` (`join`, `resolve`, `relative`, `basename`, `dirname`) — no string concatenation for paths.
- Never use `__dirname` or `__filename` — use `import.meta.url` with `node:url` (`fileURLToPath`) for ESM compatibility.

### Package Standards
- Proper `package.json` metadata: `name`, `version`, `description`, `keywords`, `author`, `license`, `repository`, `engines`, `bin`, `files`, `type`.
- `bin` field maps three executables: `add-skills`, `add-commands`, `add-workflows`.
- Use `files` whitelist in `package.json` (preferred over `.npmignore`) to control published package contents.
- Include `engines` field specifying `"node": ">=22.0.0"`.

## Quality Standards

### Code Quality
- TypeScript strict mode with no suppressions (`@ts-ignore`, `@ts-expect-error`) unless documented with justification.
- No `console.log` in library code — use structured output functions that respect `--dry-run` and `--force` flags.
- All functions have explicit return types. Exported functions have JSDoc descriptions.
- Maximum function length: 30 lines. Maximum file length: 200 lines. Violations require refactoring.
- Error handling: all file system operations wrapped in try/catch with meaningful error messages including the file path that caused the error.

### Code Organization
```
node/
└── tools/
    ├── cli.ts                  # Main entry — registers all commands
    ├── commands/
    │   ├── add-skills.ts       # add-skills command implementation
    │   ├── add-commands.ts     # add-commands command implementation
    │   └── add-workflows.ts    # add-workflows command implementation
    ├── lib/
    │   ├── types.ts            # Shared TypeScript types
    │   ├── resources.ts        # Resource discovery & resolution
    │   └── fs.ts               # copyTree / copyFile helpers
    └── __tests__/
        ├── types.test.ts
        ├── resources.test.ts
        ├── fs.test.ts
        ├── add-skills.test.ts
        ├── add-commands.test.ts
        └── add-workflows.test.ts
```

### Output & UX
- All commands provide clear, colored terminal output using Chalk.
- `--dry-run` prints what would be copied without performing mutations, prefixed with a clear indicator.
- `--force` overwrites existing files; without it, the command exits with code `1` and a list of conflicting paths.
- Exit codes: `0` for success, `1` for operational errors, `2` for usage/argument errors.
- Error messages are actionable: include what went wrong, which file/path, and what the user can do.

## Testing Standards

### Test Infrastructure
- **Runner**: Node.js built-in test runner (`node --test`) — no Mocha, Jest, Vitest, or other frameworks.
- **Assertions**: `node:assert/strict` exclusively.
- **Mocking**: `node:test` built-in `mock` API for function mocking and spying.
- **Test script**: `"test": "node --test tests/**/*.test.ts"` (using tsx or `--loader` for TypeScript).

### Test Requirements
- Every source file in `src/` has a corresponding test file in `tests/` mirroring the directory structure.
- Test file naming: `{module-name}.test.ts`.
- Each test file uses `describe` and `it` blocks with descriptive names following "should [expected behavior] when [condition]" pattern.
- Tests are independent and isolated — no shared mutable state between test cases.
- File system tests use `mkdtempSync` for temporary directories, cleaned up in `after` hooks.
- No network calls in tests. No reliance on external state.

### Coverage & CI
- All three CLI commands must have end-to-end tests verifying: successful copy, `--dry-run` behavior, `--force` overwrite, `--output` custom directory, missing source directory error handling.
- Regression tests added for every bug fix.
- Tests must pass with zero warnings before any code is considered complete.

## Governance

- This constitution supersedes all ad-hoc decisions. Any deviation requires explicit justification documented in the relevant spec or plan.
- All code reviews must verify compliance with these principles. Non-compliant code must not be merged.
- Amendments to this constitution require: (1) a written proposal, (2) impact analysis on existing code, (3) a migration plan for affected modules.
- When principles conflict, priority order is: Correctness → Testability → Simplicity → Performance → Extensibility.

**Version**: 1.0.0 | **Ratified**: 2026-03-21 | **Last Amended**: 2026-03-21
