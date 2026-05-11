# Frontend-Stitch Pipeline Plan

## Overview

This plan defines a multi-agent system that automates the conversion of Google Stitch exports (rough HTML/CSS + PNG screenshots) into production-quality frontend code. The pipeline follows a sequential 5-phase workflow inspired by the 11-step research document.

## Workflow Steps (from Research)

1. Generate & refine in Stitch
2. Export artifacts (HTML + PNG)
3. Define architecture & tokens
4. Model components
5. Rebuild UI
6. Add responsiveness & accessibility
7. Wire data & state
8. Harden with tests & CI/CD
9. Iterate with designers/product

## Agents

### Orchestrator: frontend-stitch.orchestrator

- **Role**: Coordinates the full Stitch-to-production pipeline
- **Model**: claude-sonnet-4-5
- **Responsibilities**:
  - Validate inputs (Stitch artifacts, project name, target stack)
  - Initialize project structure and orchestration log
  - Execute phases sequentially, delegating to subagents
  - Track handoff documents between phases
  - Present phase completion summaries to the user
  - Produce final pipeline summary

### Subagent 1: frontend-stitch.analyzer

- **Role**: Analyzes Stitch export artifacts (HTML + PNG)
- **Model**: claude-sonnet-4-5
- **Tools**: read_file, vision (PNG analysis), list_dir
- **Inputs**: Stitch HTML export file, PNG screenshot(s), project name
- **Outputs**:
  - `analysis/ANALYSIS_REPORT.md` — artifact survey, structural analysis, visual assessment
  - `analysis/component-inventory.md` — atoms, molecules, organisms catalog
  - `analysis/design-tokens-extracted.md` — colors, typography, spacing, radii, shadows
  - `analysis/gaps.md` — identified responsiveness and accessibility gaps
- **Phase Mapping**: Phase 1 (Artifact Analysis) of the orchestrator

### Subagent 2: frontend-stitch.architect

- **Role**: Designs the target architecture and component model
- **Model**: claude-sonnet-4-5
- **Tools**: read_file, create_file, list_dir
- **Inputs**: Analysis report, component inventory, design tokens, target stack preference
- **Outputs**:
  - `architecture/ARCHITECTURE_SPEC.md` — framework setup, project structure, routing strategy
  - `architecture/DESIGN_TOKENS.md` — finalized token specification (Tailwind config or theme file)
  - `architecture/COMPONENT_MODEL.md` — detailed component API contracts with props/interfaces
  - `architecture/PAGE_ROUTES.md` — page and layout hierarchy
  - `architecture/HANDOFF_ARCHITECTURE.md` — summary handoff for the builder agent
- **Phase Mapping**: Phase 2 (Architecture Design) of the orchestrator

### Subagent 3: frontend-stitch.builder

- **Role**: Implements the complete frontend based on architecture
- **Model**: claude-sonnet-4-5
- **Tools**: read_file, create_file, list_dir, run_terminal
- **Inputs**: Handoff architecture, architecture specs, design tokens, component model, page routes, analysis report
- **Outputs**:
  - `src/` — complete component implementation (atoms, molecules, organisms, layouts, pages)
  - `package.json`, `tsconfig.json` — project configuration
  - Framework config files (next.config, etc.)
  - `tailwind.config.ts` or equivalent theme file
  - `public/` — static assets
- **Phase Mapping**: Phase 3 (Component Building) of the orchestrator

### Subagent 4: frontend-stitch.hardener

- **Role**: Hardens the built frontend for production
- **Model**: claude-sonnet-4-5
- **Tools**: read_file, create_file, list_dir, run_terminal
- **Inputs**: Built source, architecture spec, page routes
- **Outputs**:
  - Updated `src/` — responsive breakpoints, accessibility fixes applied
  - `tests/unit/` — component-level unit tests (React Testing Library)
  - `tests/e2e/` — E2E test scaffolding (Playwright)
  - `.eslintrc`, `.prettierrc` — linting and formatting configs
  - `.github/workflows/ci.yml` — CI/CD pipeline
  - `tests/screenshots/` — visual regression baseline
- **Phase Mapping**: Phase 4 (Production Hardening) of the orchestrator

## Phase-to-Agent Mapping

| Phase | Agent | Key Output |
|-------|-------|-----------|
| 1. Artifact Analysis | analyzer | ANALYSIS_REPORT.md, component inventory, design tokens |
| 2. Architecture Design | architect | ARCHITECTURE_SPEC.md, COMPONENT_MODEL.md, DESIGN_TOKENS.md |
| 3. Component Building | builder | Complete src/ implementation, framework config |
| 4. Production Hardening | hardener | Tests, linting, CI/CD, accessibility, responsiveness |
| 5. Quality Review | orchestrator (direct) | REVIEW_REPORT.md, visual regression comparison |

## Data Flow

```
Stitch HTML + PNG
        |
        v
   [analyzer] -----> analysis/ANALYSIS_REPORT.md
                   -----> analysis/component-inventory.md
                   -----> analysis/design-tokens-extracted.md
        |
        v
   [architect] -----> architecture/ARCHITECTURE_SPEC.md
                    -----> architecture/COMPONENT_MODEL.md
                    -----> architecture/DESIGN_TOKENS.md
                    -----> architecture/HANDOFF_ARCHITECTURE.md
        |
        v
    [builder] -------> src/ (complete implementation)
                    -----> package.json, tsconfig.json
                    -----> tailwind.config.ts
        |
        v
   [hardener] -----> tests/unit/
                   -----> tests/e2e/
                   -----> .eslintrc, .prettierrc
                   -----> .github/workflows/ci.yml
        |
        v
   [orchestrator] --> REVIEW_REPORT.md (Phase 5 quality review)
```

## Default Stack

- Framework: Next.js 15 (App Router)
- Language: TypeScript
- Styling: Tailwind CSS
- Testing: React Testing Library + Playwright
- Linting: ESLint + Prettier
