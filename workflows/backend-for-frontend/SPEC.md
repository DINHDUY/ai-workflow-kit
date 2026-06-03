# Backend-for-Frontend (BFF) Workflow Specification

## Overview

This multi-agent system automates the workflow for building a Backend-for-Frontend layer that bridges a visual frontend prototype (Figma or Google Stitch screens, user flows, interactions) and a fully functional backend. The system takes a Figma or Google Stitch prototype URL and requirements as input, and produces a complete, tested, and deployed BFF including data models, API contracts, server implementation, and integration.

The workflow follows the pattern used by senior full-stack engineers who combine careful requirements analysis, contract-first API design, parallel development with mocks, and iterative integration — now accelerated by AI-assisted code generation.

---

## Scope

**In Scope:**
- Analyzing Figma and Google Stitch prototype screens to extract user stories, data entities, and API requirements
- Designing ERDs, selecting tech stack, and defining architecture
- Creating OpenAPI/Swagger specs and mock servers for parallel frontend/backend development
- Implementing the full backend (routes, controllers, services, database, auth, validation)
- Integration, end-to-end testing, deployment configuration, and monitoring setup

**Out of Scope:**
- Frontend code generation (this workflow focuses on the BFF/backend layer)
- Infrastructure provisioning beyond configuration and scripts
- Product/UX design decisions (those come from the prototype)

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Prototype URL or screen exports | Required | Figma (`figma.com/file/…` or `figma.com/design/…`) or Google Stitch (`stitch.withgoogle.com/embed/…` or `stitch.withgoogle.com/edit/…`) URL, or exported screen images |
| Project name / slug | Required | Used for folder naming and namespacing |
| Tech stack preferences | Optional | Defaults to Node.js/Express + PostgreSQL + Prisma |
| Auth requirements | Optional | JWT, OAuth providers, session-based |
| Deployment target | Optional | Docker, Vercel, AWS, Railway, Supabase |
| Existing API contracts | Optional | If partially designed, pass to skip API design phase |

---

## Outputs

| Output | Agent | Description |
|--------|-------|-------------|
| `analysis/user-stories.md` | bff.analyzer | Structured user stories with acceptance criteria |
| `analysis/data-entities.md` | bff.analyzer | Identified data entities and relationships |
| `analysis/api-requirements.md` | bff.analyzer | API endpoints derived from UI flows |
| `architecture/erd.md` | bff.architect | Entity-relationship diagram (Mermaid) |
| `architecture/tech-stack.md` | bff.architect | Stack decisions with rationale |
| `architecture/architecture.md` | bff.architect | Overall system architecture document |
| `api/openapi.yaml` | bff.api-designer | Full OpenAPI 3.0 specification |
| `api/mock-server/` | bff.api-designer | Mock server for parallel frontend dev |
| `src/` | bff.implementer | Complete backend implementation |
| `tests/` | bff.integrator | Integration and E2E test suites |
| `deploy/` | bff.integrator | Docker, CI/CD, and deployment configs |

---

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `bff.orchestrator` | claude-sonnet-4-5 | Coordinates the full pipeline, validates inputs, manages handoffs |
| `bff.analyzer` | claude-sonnet-4-5 | Extracts requirements, user stories, entities, and API needs from prototype |
| `bff.architect` | claude-sonnet-4-5 | Designs data model (ERD), selects tech stack, defines architecture |
| `bff.api-designer` | claude-sonnet-4-5 | Creates OpenAPI spec, designs endpoints, builds mock server |
| `bff.implementer` | claude-sonnet-4-5 | Implements backend server, routes, services, database, auth |
| `bff.integrator` | claude-sonnet-4-5 | Wires integration, runs E2E tests, sets up deployment and monitoring |

---

## Pipeline

```
User provides Figma prototype URL + project requirements
    ↓
bff.orchestrator (validates inputs, creates project structure)
    ↓
bff.analyzer
    → Outputs: user-stories.md, data-entities.md, api-requirements.md
    ↓
bff.architect
    → Outputs: erd.md, tech-stack.md, architecture.md
    ↓
bff.api-designer
    → Outputs: openapi.yaml, mock-server/, HANDOFF_API.md
    ↓
bff.implementer
    → Outputs: src/ (complete backend), HANDOFF_IMPL.md
    ↓
bff.integrator
    → Outputs: tests/, deploy/, monitoring setup
    ↓
Production-ready BFF layer
```

---

## Pattern

**Primary Pattern:** Sequential / Hand-off (Pipeline)

Each phase depends on the output of the previous phase. Analysis drives architecture, architecture drives API design, API design drives implementation, and implementation drives integration.

**Secondary Pattern:** Parallel Development Gate

After `bff.api-designer` produces the OpenAPI spec and mock server, frontend development can proceed in parallel with `bff.implementer`. The integrator phase synchronizes both tracks.

---

## Tech Stack Defaults

| Layer | Default | Alternatives |
|-------|---------|--------------|
| Runtime | Node.js 20 LTS | Python/FastAPI, Go |
| Framework | Express 5 or Fastify | NestJS, Hono |
| Language | TypeScript (strict) | JavaScript, Python |
| ORM | Prisma | Drizzle, TypeORM, SQLAlchemy |
| Database | PostgreSQL 16 | MySQL, SQLite, MongoDB |
| Auth | JWT + Passport.js | Supabase Auth, Clerk, Auth0 |
| Validation | Zod | Joi, Yup |
| Testing | Vitest + Supertest | Jest, Mocha |
| E2E | Playwright | Cypress |
| Mocking | MSW + JSON Server | WireMock, MirageJS |
| Deployment | Docker + docker-compose | Railway, Render, Supabase |
