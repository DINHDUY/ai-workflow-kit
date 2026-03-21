# Prodify - React Prototype to Enterprise Production-Grade App

Prodify transforms scrappy React prototypes into enterprise-ready applications using a hybrid architecture of Feature-Sliced Design, Bulletproof React, and Clean Architecture principles. It automates the tedious work of setting up tooling, refactoring mixed concerns, enforcing quality gates, adding production features, and establishing CI/CD pipelines. Designed for teams who need to ship fast but can't sacrifice maintainability, security, or scalability when moving from MVP to production.

## What It Does

1. **Audits your prototype** and maps features, technical debt, security gaps, and missing tests — then creates an Architecture Decision Record documenting the transformation plan
2. **Bootstraps production tooling** with Vite, React 19, TypeScript strict mode, ESLint with layer enforcement, Vitest/Playwright testing, and optional UI libraries (Tailwind/shadcn)
3. **Refactors features incrementally** using the strangler fig pattern, extracting domain entities, implementing use-case hooks, and building Clean Architecture layers with FSD structure
4. **Enforces quality standards** in parallel with refactoring — runs unit/component/E2E tests, measures coverage (80%+ target), audits accessibility, and scores performance with Lighthouse
5. **Hardens for production** by adding secure auth flows, global error boundaries, Sentry monitoring, environment configs, and build optimizations
6. **Deploys with CI/CD** on Vercel/Netlify/AWS with automated PR checks (lint → test → build) and production deployment workflows
7. **Documents everything** with Storybook, architecture diagrams, ADRs, PR templates, conventional commits, and team maintenance processes

## Agents

| Agent | Role |
|-------|------|
| `prodify.orchestrator` | Coordinates the 7-phase transformation pipeline, manages sequential stage transitions, and triggers parallel quality enforcement |
| `prodify.audit-planner` | Analyzes existing prototype to map features, identify tech debt, detect security/accessibility gaps, and create an ADR |
| `prodify.foundation-setup` | Bootstraps or migrates project to Vite + React 19 with full tooling: ESLint, Prettier, Husky, testing frameworks, and scaffolded directory structure |
| `prodify.feature-refactor` | Implements incremental feature-by-feature migration with FSD-compliant structure and Clean Architecture layers |
| `prodify.quality-enforcer` | Runs continuous tests, lint checks, coverage reports, accessibility audits, and performance scoring in parallel with refactoring |
| `prodify.production-hardener` | Adds production-ready features: secure authentication, error boundaries, logging/monitoring, environment configs, and build optimizations |
| `prodify.cicd-deployer` | Sets up GitHub Actions CI/CD pipelines and deployment infrastructure on Vercel/Netlify/AWS with monitoring dashboards |
| `prodify.documenter` | Creates comprehensive documentation with Storybook, architecture diagrams, ADRs, PR templates, and team processes |

## How to Use

### Full Pipeline

Invoke `prodify.orchestrator` with your prototype project path and architecture requirements:

```
@prodify.orchestrator Transform my React prototype at ~/projects/my-app into a production-grade application. Use Vite + React 19, deploy to Vercel, and include auth with error monitoring.
```

### Individual Agents

**Audit Phase** - Use `prodify.audit-planner` when you only need to assess readiness:
```
@prodify.audit-planner Analyze the prototype at ~/projects/my-app and create an audit report with feature map and ADR
```

**Foundation Setup** - Use `prodify.foundation-setup` to bootstrap tooling for an existing prototype:
```
@prodify.foundation-setup Set up Vite, TypeScript strict mode, ESLint with FSD enforcement, Vitest, and Playwright for ~/projects/my-app
```

**Quality Enforcement** - Use `prodify.quality-enforcer` to audit an already-refactored codebase:
```
@prodify.quality-enforcer Run full quality audit on ~/projects/my-app with test coverage, accessibility checks, and Lighthouse performance scoring
```

**CI/CD Setup** - Use `prodify.cicd-deployer` when foundation and features are ready but deployment is missing:
```
@prodify.cicd-deployer Create GitHub Actions workflows and deploy ~/projects/my-app to Vercel with Sentry monitoring
```

## Setup

```bash
# No pre-installation required — agents install dependencies during execution
# Ensure you have Node.js 18+ and your preferred package manager (npm/yarn/pnpm)

# Optional: Set up Sentry project for production monitoring (provide DSN to orchestrator)
# Optional: Configure deployment platform credentials (Vercel/Netlify/AWS)
```

## Output

The orchestrator creates a transformed codebase in the original project directory with FSD structure (`src/app`, `src/features/`, `src/entities/`, `src/shared/`), full tooling configuration, CI/CD workflows in `.github/workflows/`, comprehensive documentation in `docs/`, and deployed preview/production URLs. Each phase produces intermediate reports (`audit-report.md`, quality reports, architecture diagrams) saved in the project root or `docs/` folder.

## Examples

```
@prodify.orchestrator Convert ~/projects/ecommerce-mvp to production using shadcn-ui and deploy to AWS S3+CloudFront
```

```
@prodify.orchestrator Transform ~/projects/dashboard-app with monorepo setup using Nx and deploy to Netlify
```

```
@prodify.audit-planner Audit ~/projects/social-app and generate migration plan for FSD + Clean Architecture
```

---

DOCUMENTATION COMPLETE
Output: /Users/duy/repos/SDD/agentic‑workflow‑kit/workflows/prodify/README.md
Agents documented: 8
Word count (approx): 475
