# Next.js Subagent Plan

Source workflow: `workflows/nextjs/spec.md`

---

## Overview

This multi-agent system automates the workflow for converting Google Stitch UI sketches into production-ready enterprise React applications using the modern 2026 stack (Next.js 15+, Tailwind, shadcn/ui, TanStack Query). The system consists of 8 specialized agents that handle everything from design token extraction through deployment configuration.

---

## Pattern Selection

**Primary pattern:** Sequential / Hand-off (Pipeline)

**Reason:** Each workflow phase depends on the output of the previous phase — design tokens feed component building, components feed page assembly, pages feed data integration, etc. This is a clear transformation pipeline where stage A's output is stage B's required input.

**Secondary pattern(s):** None needed for initial implementation. Could add Reviewer Loop at component-builder and test-deployer phases in future iterations for automated quality gates.

---

## Workflow-to-Agent Mapping

| Workflow Step | Agent | Pattern Role |
|---|---|---|
| Step 1 - Generate/Refine in Stitch | _Manual user action_ | N/A (external tool) |
| Step 2 - Import & Tokenize | `nextjs.design-processor` | Sequential stage 1 |
| Step 3 - Set Up Next.js Project | `nextjs.project-scaffolder` | Sequential stage 2 |
| Step 4 - Build Atomic Components | `nextjs.component-builder` | Sequential stage 3 |
| Step 5 - Assemble Pages with Server Components | `nextjs.page-assembler` | Sequential stage 4 |
| Step 6 - Add Data Layer | `nextjs.data-layer-integrator` | Sequential stage 5 |
| Step 7 - Polish for Enterprise | `nextjs.quality-polish` | Sequential stage 6 |
| Step 8 - Test & Deploy | `nextjs.test-deployer` | Sequential stage 7 |
| _Overall coordination_ | `nextjs.orchestrator` | Pipeline orchestrator |

---

## Pipeline

```
User provides Stitch export (HTML/CSS or Figma URL)
    ↓
nextjs.orchestrator
    ↓
nextjs.design-processor
    → Outputs: tailwind.config.js, globals.css, design-tokens.json
    ↓
nextjs.project-scaffolder
    → Outputs: Next.js project structure, package.json, tsconfig.json
    ↓
nextjs.component-builder
    → Outputs: shadcn/ui components in components/ui/, Storybook stories
    ↓
nextjs.page-assembler
    → Outputs: app/ directory pages with Server Components, layouts
    ↓
nextjs.data-layer-integrator
    → Outputs: API routes, TanStack Query setup, forms with RHF + Zod
    ↓
nextjs.quality-polish
    → Outputs: Accessibility fixes, i18n setup, dark mode, security headers
    ↓
nextjs.test-deployer
    → Outputs: Test configs, CI/CD workflows, deployment setup
    ↓
Production-ready application
```

---

## Agent Specifications

### `nextjs.orchestrator`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File operations, shell execution
- **Pattern Role:** Pipeline orchestrator
- **Role:** Coordinates the full Stitch-to-production pipeline. Validates user inputs (Stitch export format, project requirements), orchestrates the sequence of specialized agents, and ensures each handoff contains complete context. Compiles the final summary showing all generated files and next steps for deployment.
- **Input:** 
  - Stitch export (HTML/CSS files, Figma URL, or pasted HTML)
  - Project name and requirements
  - Target deployment platform (Vercel, self-hosted, etc.)
  - Authentication needs (NextAuth, Clerk, etc.)
- **Output:** 
  - Orchestration log showing each phase completion
  - Final summary document: `PROJECT_SUMMARY.md` with file inventory, setup instructions, and deployment checklist

---

### `nextjs.design-processor`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File read/write
- **Pattern Role:** Sequential stage 1
- **Role:** Processes Stitch HTML/CSS exports or Figma designs to extract design tokens (colors, spacing, typography, shadows, border radii). Generates Tailwind configuration and CSS variables that match the Stitch design system exactly. Analyzes component patterns in the Stitch output to identify reusable primitives.
- **Input:** 
  - Stitch HTML/CSS export files or Figma URL
  - Project root directory path
- **Output:** 
  - `tailwind.config.ts` with custom theme extending Stitch design tokens
  - `app/globals.css` with CSS custom properties for theming
  - `design-tokens.json` with structured token data
  - `HANDOFF_DESIGN.md` documenting extracted tokens and component patterns identified

---

### `nextjs.project-scaffolder`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File operations, shell execution
- **Pattern Role:** Sequential stage 2
- **Role:** Initializes a Next.js 15+ project with TypeScript, Tailwind CSS, and shadcn/ui. Configures the full modern stack including Biome/ESLint, package manager (pnpm/npm), and integrates the design tokens from design-processor. Sets up project structure following Next.js App Router conventions.
- **Input:** 
  - Project name
  - `tailwind.config.ts` and `design-tokens.json` from design-processor
  - Package manager preference (pnpm/npm/yarn)
  - Optional: authentication provider choice
- **Output:** 
  - Initialized Next.js 15+ project with:
    - `package.json` with all dependencies (Next.js 15+, React 19, Tailwind 4+, shadcn/ui, TanStack Query, React Hook Form, Zod, Biome)
    - `app/` directory structure
    - `components/` directory with ui/ subdirectory prepared
    - `lib/` directory with utility functions
    - Configuration files: `tsconfig.json`, `next.config.js`, `biome.json`, `.gitignore`
  - `HANDOFF_SCAFFOLD.md` listing created directories, installed packages, and configuration details

---

### `nextjs.component-builder`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File operations, shell execution (for shadcn/ui CLI)
- **Pattern Role:** Sequential stage 3
- **Role:** Builds atomic UI components matching Stitch designs using shadcn/ui primitives. Installs needed shadcn components via CLI, customizes them to match design tokens exactly, and creates composite components for repeated patterns. Sets up Storybook or Ladle for component development and documentation. Ensures components are accessible (ARIA labels, keyboard navigation).
- **Input:** 
  - `HANDOFF_DESIGN.md` with component patterns
  - Stitch HTML/CSS structure
  - Project directory from scaffolder
  - Design tokens already integrated in Tailwind config
- **Output:** 
  - `components/ui/` with shadcn/ui primitives (button.tsx, card.tsx, input.tsx, etc.)
  - `components/` with custom composite components matching Stitch patterns
  - `.storybook/` configuration and `*.stories.tsx` files for each component
  - `HANDOFF_COMPONENTS.md` listing all created components, their props, usage examples, and Storybook links

---

### `nextjs.page-assembler`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File operations
- **Pattern Role:** Sequential stage 4
- **Role:** Assembles full application pages using Server Components from Next.js 15 App Router. Composes atomic components into organisms, templates, and pages following the Stitch screen flows. Implements layouts, navigation, routing structure, and Suspense boundaries for streaming. Wires up initial data fetching patterns using fetch in Server Components.
- **Input:** 
  - `HANDOFF_COMPONENTS.md` with component inventory
  - Stitch screen flows and navigation structure
  - Project directory with components ready
  - User requirements for routing structure
- **Output:** 
  - `app/` directory with:
    - `layout.tsx` (root layout with providers)
    - `page.tsx` files for each route
    - `loading.tsx` for Suspense fallbacks
    - `error.tsx` for error boundaries
    - Nested route groups as needed
  - `components/layouts/` with reusable layout components
  - `HANDOFF_PAGES.md` documenting route structure, page components, and data requirements identified

---

### `nextjs.data-layer-integrator`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File operations, shell execution
- **Pattern Role:** Sequential stage 5
- **Role:** Integrates TanStack Query v5+ for data fetching and caching, creates React Hook Form + Zod schemas for forms, and sets up Next.js Server Actions for mutations. Implements API routes or tRPC endpoints as needed. Adds client-side state management with Zustand if needed. Wires up authentication with NextAuth/Auth.js v5 or user's chosen provider.
- **Input:** 
  - `HANDOFF_PAGES.md` with data requirements
  - API specifications or backend endpoint documentation
  - Authentication provider choice (NextAuth, Clerk, Auth0, etc.)
  - Forms identified in Stitch design
- **Output:** 
  - `lib/api/` with TanStack Query setup and query functions
  - `lib/schemas/` with Zod validation schemas
  - `app/api/` with API routes or Server Actions
  - `lib/auth/` with authentication configuration
  - `hooks/` with custom data hooks
  - Forms wired with React Hook Form + Zod in page components
  - `HANDOFF_DATA.md` documenting API structure, query keys, form schemas, and auth setup

---

### `nextjs.quality-polish`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File operations, shell execution
- **Pattern Role:** Sequential stage 6
- **Role:** Applies enterprise-grade polish for production readiness. Implements comprehensive accessibility (ARIA, semantic HTML, keyboard nav), sets up internationalization (next-intl or react-i18next), configures dark mode with Tailwind, adds performance optimizations (React Compiler if enabled, memoization, image optimization), implements security headers and CSP, adds error monitoring (Sentry), and configures SEO metadata.
- **Input:** 
  - `HANDOFF_DATA.md` with current application state
  - Complete application codebase
  - User requirements for i18n (supported languages)
  - Target Lighthouse score requirements
- **Output:** 
  - Accessibility improvements: semantic HTML tags, ARIA labels, focus management, color contrast fixes
  - `lib/i18n/` with internationalization setup and translation files
  - Dark mode implementation with theme toggle component
  - `next.config.js` updated with security headers, CSP
  - `lib/monitoring/` with Sentry or error tracking setup
  - `app/layout.tsx` with comprehensive metadata and SEO
  - Performance optimizations applied throughout
  - `HANDOFF_POLISH.md` documenting all polish work, Lighthouse scores, and remaining recommendations

---

### `nextjs.test-deployer`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File operations, shell execution
- **Pattern Role:** Sequential stage 7
- **Role:** Sets up comprehensive testing infrastructure (Vitest + Testing Library for unit, Playwright for E2E) with example tests. Creates CI/CD workflows (GitHub Actions or GitLab CI) for automated testing and deployment. Configures deployment for target platform (Vercel deployment config, or Docker + Kubernetes manifests for self-hosted). Sets up environment variable management and deployment checklist.
- **Input:** 
  - `HANDOFF_POLISH.md` with production-ready application
  - Complete application codebase
  - Target deployment platform (Vercel, self-hosted, AWS, etc.)
  - CI/CD platform preference (GitHub Actions, GitLab CI, etc.)
- **Output:** 
  - `vitest.config.ts` and test setup files
  - `__tests__/` or `*.test.tsx` files with unit tests for critical components
  - `e2e/` directory with Playwright tests and `playwright.config.ts`
  - `.github/workflows/ci.yml` or equivalent CI/CD configuration
  - `Dockerfile` and `docker-compose.yml` (if self-hosted)
  - `vercel.json` or deployment configuration for target platform
  - `.env.example` with required environment variables documented
  - `DEPLOYMENT.md` with deployment instructions, environment setup guide, and post-deployment checklist
  - Final handoff to user with complete production-ready application

---

## Reused Agents

None. All agents are new and specific to the Next.js workflow.

---

## File Layout

```
.cursor/agents/
  nextjs.orchestrator.md
  nextjs.design-processor.md
  nextjs.project-scaffolder.md
  nextjs.component-builder.md
  nextjs.page-assembler.md
  nextjs.data-layer-integrator.md
  nextjs.quality-polish.md
  nextjs.test-deployer.md
```

---

## Key Design Decisions

1. **Pattern choice** - Sequential/Hand-off pipeline chosen over parallel fan-out because each phase strictly depends on the previous phase's output. Design tokens must exist before scaffolding, scaffold must complete before component building, components before pages, pages before data integration, etc. Clean handoff documents ensure each agent receives complete context without shared conversation history.

2. **Model selection** - All agents use `sonnet` because they all require complex reasoning (parsing design tokens, generating TypeScript, wiring React hooks), and several need shell execution for package management and scaffolding commands. No simple keyword extraction or formatting tasks that would warrant `fast` model.

3. **Readonly=false for all agents** - Every agent in the pipeline creates or modifies files. Even the orchestrator needs to write the final PROJECT_SUMMARY.md. No agents are purely analytical.

4. **No background agents** - All phases are user-blocking and time-sensitive. The user waits for the full pipeline to complete to get their production-ready app. No long-running monitoring or async tasks.

5. **Storybook in component-builder phase** - Component isolation and documentation is critical for enterprise teams. Storybook setup happens during component building so components can be developed and verified in isolation before page assembly.

6. **Auth integration in data-layer phase** - Authentication is tightly coupled with data fetching (protecting routes, API calls). Integrating it during data layer setup rather than as separate phase reduces complexity and ensures auth + data work together from the start.

7. **Quality polish as dedicated phase** - Accessibility, i18n, performance, security are often afterthoughts but critical for enterprise. Dedicating a full agent ensures these are systematically addressed with proper tooling and verification.

8. **Testing + deployment combined** - Both are final production-readiness concerns. Combining them in one agent ensures tests are written with deployment environment in mind (environment variables, API endpoints, etc.) and CI/CD can run tests before deployment.

---

## Dependencies

```bash
# Core framework and React
npm install next@latest react@latest react-dom@latest

# TypeScript
npm install -D typescript @types/node @types/react @types/react-dom

# Styling
npm install tailwindcss@latest postcss autoprefixer
npm install class-variance-authority clsx tailwind-merge

# shadcn/ui (installed via CLI, adds to package.json)
npx shadcn-ui@latest init  # Adds Radix UI primitives as needed

# Data & State
npm install @tanstack/react-query @tanstack/react-query-devtools
npm install zustand  # Optional, for client state
npm install nuqs  # URL state sync

# Forms & Validation
npm install react-hook-form zod @hookform/resolvers

# Authentication (choose one)
npm install next-auth  # Auth.js v5
# OR npm install @clerk/nextjs
# OR npm install @supabase/supabase-js @supabase/ssr

# Testing
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
npm install -D playwright @playwright/test

# Dev Tools
npm install -D @biomejs/biome  # Linting + formatting
# OR npm install -D eslint prettier eslint-config-next

# Storybook (optional but recommended)
npx storybook@latest init

# Monitoring (optional)
npm install @sentry/nextjs

# i18n (optional)
npm install next-intl
# OR npm install react-i18next i18next
```

---

## Invocation Examples

**Full pipeline:**
```
@nextjs.orchestrator I have a Stitch export (HTML/CSS attached) for a SaaS dashboard. 
Project name: "acme-dashboard". 
Need NextAuth with Google OAuth. 
Deploy to Vercel. 
Target: fully accessible, dark mode, E2E tests for critical flows.
```

**Design processing only:**
```
@nextjs.design-processor Extract design tokens from this Stitch HTML export 
(see stitch-export.html) and generate Tailwind config. Project root: ./acme-dashboard
```

**Component building phase only (after design + scaffold):**
```
@nextjs.component-builder Build shadcn/ui components matching the Stitch patterns 
in HANDOFF_DESIGN.md. Project: ./acme-dashboard. Set up Storybook.
```

**Data layer integration only (after pages assembled):**
```
@nextjs.data-layer-integrator Add TanStack Query for API calls, React Hook Form 
for the login/signup forms. Backend: REST API at https://api.acme.com. 
Use NextAuth with Google provider.
```

**Quality polish only (before deployment):**
```
@nextjs.quality-polish Add full accessibility (target WCAG AA), dark mode toggle, 
i18n for en/es/fr, security headers, Sentry monitoring. Current codebase: ./acme-dashboard
```

**Testing + deployment only:**
```
@nextjs.test-deployer Set up Vitest + Playwright tests, GitHub Actions CI/CD, 
deploy to Vercel. Project: ./acme-dashboard. Critical flows to test: auth, dashboard load, create item.
```
