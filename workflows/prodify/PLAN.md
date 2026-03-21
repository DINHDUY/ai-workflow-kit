# Prodify Subagent Plan

Source workflow: `workflows/prodify/SPEC.md`

---

## Overview

Prodify transforms React prototypes into enterprise production-grade applications using a hybrid architecture (FSD + Bulletproof React + Clean Architecture). The system consists of 8 specialized agents orchestrated across 7 sequential phases, with one parallel quality-enforcement phase running concurrently with the refactoring phase.

---

## Pattern Selection

**Primary pattern:** Sequential Pipeline  
**Reason:** The 7-phase workflow has strict dependencies — each phase builds on the previous phase's output. Foundation setup requires completed audit, refactoring requires foundation, production hardening requires refactored features, etc.

**Secondary pattern:** Parallel Fan-Out (Phase 3 + Phase 4)  
**Reason:** Quality enforcement (testing, linting, clean code review) can run simultaneously with incremental feature refactoring without blocking progress. Both agents work on the same codebase but with different concerns.

---

## Workflow-to-Agent Mapping

| Workflow Step | Agent | Pattern Role |
|---|---|---|
| Phase 1 - Audit & Planning | `prodify.audit-planner` | Sequential stage 1 |
| Phase 2 - Foundation Setup | `prodify.foundation-setup` | Sequential stage 2 |
| Phase 3 - Incremental Architectural Refactor | `prodify.feature-refactor` | Sequential stage 3 (parallel worker A) |
| Phase 4 - Quality, Clean Code & Best Practices | `prodify.quality-enforcer` | Parallel worker B (runs with stage 3) |
| Phase 5 - Production-Ready Features | `prodify.production-hardener` | Sequential stage 4 |
| Phase 6 - CI/CD, Deployment & Monitoring | `prodify.cicd-deployer` | Sequential stage 5 |
| Phase 7 - Documentation, Processes & Ongoing Maintenance | `prodify.documenter` | Sequential stage 6 |
| - Orchestration & Coordination | `prodify.orchestrator` | Pipeline orchestrator |

---

## Pipeline

```
User Request
    ↓
prodify.orchestrator
    ↓
[Phase 1] prodify.audit-planner
    ↓ (audit report + ADR)
[Phase 2] prodify.foundation-setup
    ↓ (Vite + tooling configured)
[Phase 3 & 4] ┌─ prodify.feature-refactor (refactor features incrementally)
              │
              └─ prodify.quality-enforcer (test/lint/review in parallel)
    ↓ (refactored codebase + quality reports)
[Phase 5] prodify.production-hardener
    ↓ (auth, error handling, monitoring added)
[Phase 6] prodify.cicd-deployer
    ↓ (CI/CD pipeline + deployment configured)
[Phase 7] prodify.documenter
    ↓ (docs, ADRs, processes written)
Final Production-Grade App
```

---

## Agent Specifications

### `prodify.orchestrator`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** Task (subagent delegation), File Read/Write, Bash
- **Pattern Role:** Pipeline orchestrator
- **Role:** Coordinates the entire 7-phase transformation pipeline. Manages sequential stage transitions, triggers parallel execution of Phase 3 and Phase 4, collects intermediate outputs, and compiles the final production-ready application state.
- **Input:** User's prototype project path, architecture requirements, target stack preferences
- **Output:** Consolidated transformation report with all phase outputs, final codebase location, deployment URLs

### `prodify.audit-planner`
- **Model:** sonnet
- **Readonly:** true
- **Tools:** File Read, Grep, Glob, Bash (read-only commands like `tree`, `git log`)
- **Pattern Role:** Sequential stage 1
- **Role:** Analyzes the existing prototype to map features, identify mixed concerns (logic in components), detect technical debt, security/accessibility gaps, and missing tests. Creates an Architecture Decision Record (ADR) documenting the decision to use FSD + Clean Architecture hybrid approach.
- **Input:** Project root path, current stack info (package.json, tsconfig, etc.)
- **Output:** Audit report markdown file (`audit-report.md`) containing feature map, tech debt inventory, missing capabilities list, and ADR file (`architecture-decision.md`)

### `prodify.foundation-setup`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash (npm/yarn/pnpm commands), Grep, Glob
- **Pattern Role:** Sequential stage 2
- **Role:** Bootstraps or migrates the project to Vite + React 19 + TypeScript strict mode. Installs and configures all tooling: ESLint (with no-restricted-paths for layer enforcement), Prettier, Husky/lint-staged, Vitest, React Testing Library, MSW, Playwright, TanStack Query, React Router, Zod, React Hook Form, Zustand, Tailwind/shadcn-ui, Storybook. Sets up path aliases and public APIs.
- **Input:** Audit report, ADR, user preferences for package manager and UI library
- **Output:** Configured `package.json`, `vite.config.ts`, `tsconfig.json`, `eslint.config.js`, `.prettierrc`, Husky hooks, Vitest config, Playwright config, and scaffolded `src/` directory structure with foundation folders

### `prodify.feature-refactor`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash (git commands for feature branches), Grep, Semantic Search
- **Pattern Role:** Sequential stage 3 (runs as parallel worker A alongside quality-enforcer)
- **Role:** Implements incremental feature-by-feature migration using the strangler fig pattern. For each feature, creates FSD-compliant structure (`features/[name]/api|components|hooks|types|utils`), extracts domain entities, implements use-case hooks, builds repository adapters (TanStack Query), and creates presentational UI components. Enforces Clean Architecture principles with entities → use cases → adapters → presentation layers.
- **Input:** Foundation setup output, audit report feature map, prioritized feature list
- **Output:** Refactored features in `src/features/` with ESLint-enforced layer boundaries, each feature exposing a public API via `index.ts`, migration progress log

### `prodify.quality-enforcer`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash (test/lint commands), Grep, Glob
- **Pattern Role:** Parallel worker B (runs simultaneously with feature-refactor)
- **Role:** Enforces quality and clean code practices in parallel with feature refactoring. Runs continuous tests (unit with Vitest, component with RTL, integration with MSW, E2E with Playwright), executes lint checks, measures code coverage (targeting 80%+), verifies naming conventions, checks for proper colocation, validates accessibility with axe audits, and measures performance with Lighthouse CI. Reports issues back to orchestrator for retry coordination.
- **Input:** Current codebase state, ESLint/Prettier configs, test configs
- **Output:** Quality reports per feature (`quality-report-[feature].md`), coverage summaries, accessibility audit results, performance scores, list of clean code violations

### `prodify.production-hardener`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash, Grep
- **Pattern Role:** Sequential stage 4
- **Role:** Adds production-ready features to the refactored codebase. Implements secure authentication (TanStack Query interceptors, token refresh, protected routes), global error handling with error boundaries, integrates logging and monitoring (Sentry), configures environment variables, applies build optimizations, and optionally adds PWA/offline support.
- **Input:** Refactored codebase, quality enforcement reports
- **Output:** Production-hardened codebase with auth flows, error boundaries, Sentry integration, environment configs, optimized build configuration

### `prodify.cicd-deployer`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash (git, deployment CLIs), Grep
- **Pattern Role:** Sequential stage 5
- **Role:** Sets up CI/CD pipeline and deployment infrastructure. Creates GitHub Actions workflows (PR: lint → type-check → test → build; main: deploy preview or production), configures hosting on Vercel/Netlify or AWS S3+CloudFront, sets up monitoring dashboards (Sentry performance tracking), integrates bundle analyzer, and optionally configures Nx/Turborepo for monorepo scaling.
- **Input:** Production-hardened codebase, deployment preferences (Vercel/Netlify/AWS), environment secrets
- **Output:** `.github/workflows/` CI/CD configs, deployment configs (e.g., `vercel.json`), deployed preview and production URLs, monitoring dashboard links

### `prodify.documenter`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash (Storybook commands), Grep, Glob
- **Pattern Role:** Sequential stage 6
- **Role:** Creates comprehensive documentation and establishes ongoing maintenance processes. Builds Storybook as living component documentation (optionally integrates Chromatic), generates architecture diagrams (FSD layers, Clean Architecture circles), writes ADRs for major decisions, creates PR templates, sets up conventional commits enforcement, generates CODEOWNERS file, and documents weekly tech-debt review processes.
- **Input:** Final codebase, CI/CD configs, team structure info
- **Output:** Published Storybook, `docs/` folder with architecture diagrams and ADRs, `.github/PULL_REQUEST_TEMPLATE.md`, `commitlint.config.js`, `CODEOWNERS`, team process documentation

---

## Reused Agents

None — all agents are purpose-built for the prodify workflow.

---

## File Layout

```
.cursor/agents/
  prodify.orchestrator.md
  prodify.audit-planner.md
  prodify.foundation-setup.md
  prodify.feature-refactor.md
  prodify.quality-enforcer.md
  prodify.production-hardener.md
  prodify.cicd-deployer.md
  prodify.documenter.md
```

---

## Key Design Decisions

1. **Pattern choice** - Sequential pipeline chosen because each transformation phase depends critically on the previous phase's output (e.g., cannot refactor features without foundation tooling). Parallel fan-out integrated for quality enforcement to avoid blocking refactoring progress while maintaining quality gates.

2. **Phase 3 + 4 parallelization** - Feature refactoring and quality enforcement run simultaneously to maximize velocity. Quality-enforcer provides continuous feedback without blocking forward progress, enabling a fast feedback loop while keeping the strangler fig migration moving.

3. **Model selection uniformity** - All agents use `sonnet` due to the complex nature of enterprise-grade architectural transformations. Each phase requires nuanced decision-making beyond simple formatting or keyword extraction. The orchestrator in particular must handle sophisticated multi-phase coordination.

4. **Foundation-first approach** - Phase 2 (foundation-setup) is isolated as a dedicated agent because tooling configuration is a prerequisite for all downstream work. This ensures ESLint layer enforcement, testing infrastructure, and build tooling are in place before any refactoring begins.

5. **Strangler fig safety** - The feature-refactor agent explicitly uses git branching and incremental migration to ensure the app remains shippable at every step. This "never big-bang" approach is embedded in the agent's instructions to prevent risky rewrites.

6. **Quality gate enforcement** - While quality-enforcer runs in parallel, its reports feed back to the orchestrator which can trigger retry loops for feature-refactor if critical issues are detected (e.g., test failures, ESLint violations blocking build). This combines parallel efficiency with reviewer-loop safety.

---

## Dependencies

```bash
# Core dependencies installed by foundation-setup agent
npm install -D vite @vitejs/plugin-react typescript
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-plugin-prettier eslint-config-prettier
npm install -D husky lint-staged
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
npm install -D msw
npm install -D @playwright/test
npm install -D storybook @storybook/react-vite

npm install react@19 react-dom@19
npm install @tanstack/react-query @tanstack/react-query-devtools
npm install react-router-dom
npm install zod react-hook-form @hookform/resolvers
npm install zustand
npm install tailwindcss postcss autoprefixer
# or: npm install styled-components

# Production monitoring (added by production-hardener)
npm install @sentry/react

# Optional (CI/CD and scaling)
npm install -D nx  # or turborepo
```

---

## Invocation Examples

**Full pipeline:**
```
Transform my React prototype at ./my-prototype to a production-grade enterprise app using FSD + Clean Architecture. Use Vite, React 19, TypeScript strict mode, TanStack Query, Tailwind, and deploy to Vercel.
```

**Audit only:**
```
Run a prodify audit on my prototype at ./project-x to identify tech debt and architecture gaps. Save the audit report.
```

**Foundation setup only:**
```
Set up the prodify foundation (Vite + tooling + testing + project structure) for my app at ./my-app. Use pnpm and shadcn-ui.
```

**Incremental refactor:**
```
Refactor the authentication feature in ./src/components/auth to FSD + Clean Architecture structure. Run quality checks in parallel.
```

**Production hardening:**
```
Add production-ready features to my refactored app: Sentry monitoring, error boundaries, auth interceptors, and environment configs.
```

**CI/CD deployment:**
```
Set up GitHub Actions CI/CD for my app and deploy to Vercel with preview environments.
```

**Documentation:**
```
Generate full documentation for my prodified app: Storybook, architecture diagrams, ADRs, and team processes.
```
