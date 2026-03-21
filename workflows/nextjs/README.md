# Next.js Enterprise Development Pipeline

Automates the conversion of Google Stitch UI sketches into production-ready enterprise React applications using the modern 2026 stack (Next.js 15+, Tailwind CSS 4+, shadcn/ui, TanStack Query v5, React 19). The system guides you through design token extraction, project scaffolding, component building, page assembly, data integration, quality polish (accessibility, i18n, dark mode, security), and deployment configuration. Designed for full-stack developers and teams who want to accelerate the design-to-production workflow while maintaining enterprise-grade code quality and best practices.

## What It Does

1. **Extracts design tokens** from Stitch HTML/CSS exports or Figma designs, generating Tailwind configuration and CSS variables that match your design system exactly
2. **Scaffolds a complete Next.js 15+ project** with TypeScript, Tailwind CSS, shadcn/ui, and modern tooling (Biome/ESLint, TanStack Query, React Hook Form, Zod)
3. **Builds atomic UI components** using shadcn/ui primitives, customized to match your design tokens, with Storybook documentation for component development
4. **Assembles full application pages** using Next.js 15 App Router Server Components, implementing layouts, routing, navigation, and Suspense boundaries
5. **Integrates the data layer** with TanStack Query for data fetching, React Hook Form + Zod for forms, Server Actions for mutations, and authentication (NextAuth/Clerk/Auth0)
6. **Applies enterprise polish** including comprehensive accessibility (WCAG AA), internationalization, dark mode, performance optimizations, security headers, SEO metadata, and error monitoring
7. **Sets up testing and deployment** with Vitest + Testing Library for unit tests, Playwright for E2E tests, CI/CD workflows (GitHub Actions), and deployment configuration for Vercel or self-hosted platforms

## Agents

| Agent | Role |
|-------|------|
| `nextjs.orchestrator` | Coordinates the full Stitch-to-production pipeline, validates inputs, orchestrates specialized agents, and compiles final summary |
| `nextjs.design-processor` | Extracts design tokens from Stitch exports, generates Tailwind configuration and CSS variables |
| `nextjs.project-scaffolder` | Initializes Next.js 15+ project with TypeScript, Tailwind, shadcn/ui, and modern development stack |
| `nextjs.component-builder` | Builds atomic UI components using shadcn/ui primitives, sets up Storybook for component documentation |
| `nextjs.page-assembler` | Assembles application pages with Server Components, implements routing structure and navigation |
| `nextjs.data-layer-integrator` | Integrates TanStack Query, React Hook Form + Zod schemas, Server Actions, and authentication |
| `nextjs.quality-polish` | Applies enterprise polish: accessibility, i18n, dark mode, security headers, performance optimization, SEO |
| `nextjs.test-deployer` | Sets up testing infrastructure (Vitest, Playwright), CI/CD workflows, and deployment configuration |

## How to Use

### Full Pipeline

Invoke `nextjs.orchestrator` with your Stitch export and project requirements:

```
@nextjs.orchestrator I have a Stitch export (HTML/CSS attached) for a SaaS dashboard. 
Project name: "acme-dashboard". 
Need NextAuth with Google OAuth. 
Deploy to Vercel. 
Target: fully accessible, dark mode, E2E tests for critical flows.
```

### Individual Agents

**Design Token Extraction** - Use `nextjs.design-processor` when you only need to extract design tokens from a Stitch export:
```
@nextjs.design-processor Extract design tokens from this Stitch HTML export 
(see stitch-export.html) and generate Tailwind config. Project root: ./acme-dashboard
```

**Component Building** - Use `nextjs.component-builder` when you already have a scaffolded project and want to generate components:
```
@nextjs.component-builder Build shadcn/ui components matching the Stitch patterns 
in HANDOFF_DESIGN.md. Project: ./acme-dashboard. Set up Storybook.
```

**Data Layer Integration** - Use `nextjs.data-layer-integrator` when pages are assembled and you need to wire up data fetching:
```
@nextjs.data-layer-integrator Add TanStack Query for API calls, React Hook Form 
for the login/signup forms. Backend: REST API at https://api.acme.com. 
Use NextAuth with Google provider.
```

**Quality Polish** - Use `nextjs.quality-polish` before deployment to add enterprise features:
```
@nextjs.quality-polish Add full accessibility (target WCAG AA), dark mode toggle, 
i18n for en/es/fr, security headers, Sentry monitoring. Current codebase: ./acme-dashboard
```

## Setup

The pipeline automatically installs dependencies during the scaffolding phase. Core packages include:

```bash
# Automatically installed by the scaffolder agent
# Next.js 15+, React 19, TypeScript
# Tailwind CSS 4+, shadcn/ui (Radix UI primitives)
# TanStack Query v5+, Zustand, nuqs
# React Hook Form, Zod
# Vitest, Testing Library, Playwright
# Biome (linting + formatting)
# Optional: Storybook, Sentry, next-intl
```

Authentication options (choose during orchestration):
- **NextAuth** (Auth.js v5) - OAuth providers, credentials
- **Clerk** - Complete auth + user management
- **Supabase Auth** - Open-source auth solution

## Output

The system creates a complete Next.js application in your specified project directory with:
- `app/` directory with pages, layouts, API routes, and Server Components using Next.js 15 App Router conventions
- `components/` with shadcn/ui primitives and custom composite components, plus optional Storybook stories
- `lib/` with API clients, authentication configuration, validation schemas, and utility functions
- `__tests__/` and `e2e/` with comprehensive test suites for unit and end-to-end testing
- Configuration files for TypeScript, Tailwind, testing, CI/CD, and deployment
- `PROJECT_SUMMARY.md` documenting all generated files, setup instructions, and deployment checklist

## Examples

**SaaS Dashboard with Multi-tenant Auth:**
```
@nextjs.orchestrator Convert this Stitch export (attached) to a multi-tenant SaaS dashboard. 
Project: "tenant-portal". Auth: Clerk with organization support. 
Backend: tRPC API at /api/trpc. Deploy: Vercel with Preview deployments.
Target: i18n (en/es), dark mode, Lighthouse 95+ score.
```

**E-commerce Storefront:**
```
@nextjs.orchestrator Build an e-commerce product catalog from Stitch designs. 
Project: "shop-frontend". Auth: NextAuth with email/password + Google. 
API: REST at https://api.shop.com. Deploy: Docker + Kubernetes (self-hosted).
Features: product search, cart, checkout flow, admin dashboard.
```

**Marketing Site with CMS:**
```
@nextjs.orchestrator Create a marketing site from Figma designs (link: figma.com/file/xyz). 
Project: "marketing-site". No auth. Content: headless CMS integration (Sanity). 
Deploy: Vercel Edge. Features: blog, case studies, contact forms, newsletter signup.
```
