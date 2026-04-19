# Contributing to ai-workflow-kit

Thank you for contributing! This guide covers everything needed to get started.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/DINHDUY/ai-workflow-kit.git
cd ai-workflow-kit

# Install dependencies (Node >=22 required)
npm install

# Run in dev mode (no build step needed)
npm run dev -- add-skills --help

# Type check
npm run typecheck

# Build to dist/
npm run build

# Run tests
npm test

# Lint
npm run lint
npm run lint:fix

# Format
npm run format
npm run format:check
```

## Commit Message Convention

This project uses **Conventional Commits** enforced by semantic-release. Your commit message determines the version bump — please follow the format precisely.

### Format

```
<type>(<optional scope>): <short description>

[optional body]

[optional footer(s)]
```

### Types and Their Effect on Versioning

| Type | Release | Description |
|------|---------|-------------|
| `feat` | **minor** | A new feature |
| `fix` | **patch** | A bug fix |
| `perf` | **patch** | A performance improvement |
| `revert` | **patch** | Reverts a previous commit |
| `docs` | none | Documentation only changes |
| `style` | none | Formatting, missing semicolons, etc. |
| `refactor` | none | Code refactoring (no feature/fix) |
| `test` | none | Adding or correcting tests |
| `build` | none | Changes to the build system |
| `ci` | none | Changes to CI configuration |
| `chore` | none | Maintenance tasks |

### Breaking Changes → Major Bump

Add `BREAKING CHANGE:` in the commit **footer**, or use `!` after the type:

```
feat!: remove --output flag alias

BREAKING CHANGE: The -o shorthand has been removed. Use --output instead.
```

```
fix(add-skills)!: change default output directory

BREAKING CHANGE: Default output changed from skills/ to .cursor/rules/
```

### Examples

```bash
# New feature (minor bump: 1.1.0 → 1.2.0)
git commit -m "feat(add-workflows): support --flatten flag to copy agents to a single dir"

# Bug fix (patch bump: 1.1.0 → 1.1.1)
git commit -m "fix(resources): resolve skill path lookup on Windows"

# Performance improvement (patch bump)
git commit -m "perf(fs): use streams for large file copies"

# No release
git commit -m "docs: update README with installation examples"
git commit -m "test(add-commands): add dry-run edge case coverage"
git commit -m "chore: upgrade tsx devDependency"
git commit -m "ci: add format:check step to CI workflow"

# Major breaking change (major bump: 1.1.0 → 2.0.0)
git commit -m "feat!: rename add-commands to add-rules

BREAKING CHANGE: The add-commands CLI command and binary have been renamed to add-rules."
```

## Pull Request Process

1. Fork the repo and create a feature branch from `master`
2. Ensure all checks pass: `npm run typecheck && npm run lint && npm run build && npm test`
3. Open a PR against `master`
4. PR title should also follow the Conventional Commits format (it's used as the squash commit message)
5. A maintainer will review and merge — semantic-release will handle versioning and publishing automatically

## Project Structure

```
src/ai-workflow-kit/
  cli.ts              # Entry point, registers subcommands
  commands/           # add-skills, add-commands, add-workflows
  lib/
    fs.ts             # File system utilities
    resources.ts      # Resource discovery (skills/commands/workflows)
    types.ts          # Shared TypeScript types
  __tests__/          # Node built-in test runner tests

skills/               # Bundled skill templates
commands/             # Bundled command templates
workflows/            # Bundled workflow templates
```

## Running Tests

Tests use the Node.js built-in `node:test` runner (no Jest):

```bash
npm test
```

Tests are co-located under `src/ai-workflow-kit/__tests__/` and use temp directories for isolation. They are excluded from the compiled output.
