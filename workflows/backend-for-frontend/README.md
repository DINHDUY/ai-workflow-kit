# Backend-for-Frontend (BFF) Development Pipeline

Automates the full workflow for building a Backend-for-Frontend layer that bridges a frontend prototype and a production-ready backend. Starting from a **Figma** or **Google Stitch** URL and project requirements, the system extracts user stories and data entities, designs the architecture and ERD, creates an OpenAPI contract with a mock server (so frontend dev can proceed in parallel), implements the complete TypeScript backend, and wires up integration tests and deployment configuration.

Designed for full-stack engineers, tech leads, and startup teams who want to accelerate prototype-to-backend development while maintaining clean architecture, type safety, and API-first best practices.

---

## What It Does

1. **Analyzes the prototype** (Figma or Google Stitch) — walks every screen, flow, and interaction to extract user stories with acceptance criteria, data entities and relationships, and the full list of API endpoints the UI requires
2. **Designs the architecture** — produces an ERD (Mermaid diagram), selects and justifies the tech stack, plans authentication/authorization strategy and service boundaries
3. **Creates the API contract** — generates a complete OpenAPI 3.0 specification with request/response schemas, error codes, and security definitions; spins up a mock server so the frontend team is unblocked immediately
4. **Implements the backend** — scaffolds a TypeScript project with Express/Fastify, generates Prisma schema from the ERD, builds routes/controllers/services, adds JWT auth middleware, Zod validation, structured logging, and error handling
5. **Integrates and deploys** — writes integration and E2E tests against the real backend, creates Docker and docker-compose configs, generates a GitHub Actions CI/CD workflow, and sets up health checks and error tracking

---

## Agents

| Agent | Role |
|-------|------|
| `bff.orchestrator` | Coordinates the full pipeline, validates inputs, manages handoffs between agents, and compiles the final summary |
| `bff.analyzer` | Analyzes Figma or Google Stitch screens and user flows to extract user stories, data entities, API requirements, auth needs, and edge cases |
| `bff.architect` | Designs the ERD, selects tech stack, defines authentication strategy, and produces the overall architecture blueprint |
| `bff.api-designer` | Creates the OpenAPI 3.0 spec, designs all endpoints and schemas, and sets up a mock server for parallel frontend development |
| `bff.implementer` | Implements the full backend: TypeScript project setup, Prisma schema, routes, controllers, services, auth, validation, and logging |
| `bff.integrator` | Wires frontend-to-backend integration, writes tests, creates Docker/CI/CD configs, and configures monitoring |

---

## How to Use

### Full Pipeline

Invoke `bff.orchestrator` with your Figma URL and project requirements:

```
@bff.orchestrator I have a Figma prototype for a task management SaaS app.
Prototype URL: https://www.figma.com/file/abc123/TaskApp
Project name: task-manager
Tech stack: Node.js + Express + PostgreSQL + Prisma
Auth: JWT with email/password + Google OAuth
Deploy to: Docker + Railway
```

Or with a **Google Stitch** prototype:

```
@bff.orchestrator I have a Google Stitch prototype for a task management SaaS app.
Prototype URL: https://stitch.withgoogle.com/embed/abc123
Project name: task-manager
Tech stack: Node.js + Express + PostgreSQL + Prisma
Auth: JWT with email/password
Deploy to: Docker + Railway
```

### Individual Agents

**Prototype Analysis Only** — use `bff.analyzer` when you just need requirements extracted:
```
@bff.analyzer Analyze this prototype and extract all user stories,
data entities, and API requirements.
Prototype URL: https://stitch.withgoogle.com/embed/abc123
Prototype tool: stitch
Project: task-manager
```

**Architecture Design Only** — use `bff.architect` when analysis is complete:
```
@bff.architect Design the ERD and architecture for this project.
Read the analysis from: analysis/user-stories.md, analysis/data-entities.md
Tech preference: PostgreSQL + Prisma, Node.js
```

**API Contract Only** — use `bff.api-designer` when architecture is ready:
```
@bff.api-designer Generate the OpenAPI spec and mock server.
Architecture: architecture/erd.md, architecture/tech-stack.md
Output the spec to: api/openapi.yaml
Set up JSON Server mock at: api/mock-server/
```

**Backend Implementation Only** — use `bff.implementer` with an existing API spec:
```
@bff.implementer Implement the backend from this OpenAPI spec.
Spec: api/openapi.yaml
Architecture: architecture/erd.md
Stack: Node.js + Express + TypeScript + Prisma + PostgreSQL
```

**Integration & Deployment Only** — use `bff.integrator` when implementation is done:
```
@bff.integrator Set up tests and deployment for the implemented backend.
Source: src/
API spec: api/openapi.yaml
Deploy target: Docker + GitHub Actions
```

---

## Project Structure

After the pipeline runs, your project will have this structure:

```
{project-name}/
├── analysis/
│   ├── user-stories.md          # User stories with acceptance criteria
│   ├── data-entities.md         # Entity definitions and relationships
│   └── api-requirements.md      # API endpoints per user flow
├── architecture/
│   ├── erd.md                   # Entity-Relationship Diagram (Mermaid)
│   ├── tech-stack.md            # Stack decisions with rationale
│   └── architecture.md          # Overall system architecture
├── api/
│   ├── openapi.yaml             # OpenAPI 3.0 specification
│   ├── postman-collection.json  # Postman collection for manual testing
│   └── mock-server/             # JSON Server mock for frontend dev
│       ├── db.json              # Seed data
│       ├── routes.json          # Route mappings
│       └── package.json
├── src/
│   ├── app.ts                   # Express app factory
│   ├── server.ts                # Entry point
│   ├── routes/                  # Route definitions
│   ├── controllers/             # Request handlers
│   ├── services/                # Business logic
│   ├── middleware/              # Auth, validation, error handling
│   ├── lib/                     # Database client, logger, config
│   └── types/                   # TypeScript types and schemas
├── prisma/
│   └── schema.prisma            # Database schema
├── tests/
│   ├── integration/             # Supertest API integration tests
│   └── e2e/                     # Playwright E2E tests
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions pipeline
├── .env.example
├── package.json
├── tsconfig.json
└── README.md
```

---

## Prerequisites

- Node.js 20 LTS or later
- pnpm (or npm/yarn)
- Docker (for local database and deployment)
- Figma account (for prototype access)
- PostgreSQL 16 (or Docker image)

---

## Tech Stack Defaults

The pipeline defaults to a modern TypeScript-first stack:

| Layer | Default |
|-------|---------|
| Runtime | Node.js 20 LTS |
| Framework | Express 5 + TypeScript strict |
| ORM | Prisma 5 |
| Database | PostgreSQL 16 |
| Auth | JWT + Passport.js |
| Validation | Zod |
| Testing | Vitest + Supertest + Playwright |
| Mock Server | JSON Server + Faker.js |
| Deployment | Docker + docker-compose |
| CI/CD | GitHub Actions |

Override any of these by specifying your preferences when invoking `bff.orchestrator`.

---

## Parallel Development

One of the core benefits of this workflow is enabling parallel frontend/backend development. After `bff.api-designer` completes:

1. **Start the mock server** so the frontend team can develop immediately:
   ```bash
   cd api/mock-server
   npm install
   npm start
   # Mock API running at http://localhost:3001
   ```

2. **Frontend connects to mock** — update the frontend's API base URL to `http://localhost:3001`

3. **Backend development proceeds** — `bff.implementer` builds the real backend while frontend uses the mock

4. **Cutover** — when the real backend is ready, update the frontend's API base URL to `http://localhost:3000`

---

## Handoff Documents

The pipeline produces structured handoff documents between phases. These are useful for reviewing progress or resuming from a specific phase:

| File | From | To |
|------|------|----|
| `HANDOFF_ANALYSIS.md` | bff.analyzer | bff.architect |
| `HANDOFF_ARCHITECTURE.md` | bff.architect | bff.api-designer |
| `HANDOFF_API.md` | bff.api-designer | bff.implementer |
| `HANDOFF_IMPL.md` | bff.implementer | bff.integrator |
| `ORCHESTRATION_LOG.md` | bff.orchestrator | All agents |
