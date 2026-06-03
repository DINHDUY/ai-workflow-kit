# Backend-for-Frontend (BFF) Agent Decomposition Plan

Source workflow: `workflows/backend-for-frontend/SPEC.md`

---

## Overview

This multi-agent system automates the full BFF development workflow — from analyzing a Figma prototype to a production-ready backend. It consists of 6 specialized agents that handle requirements extraction, architecture design, API contract design, implementation, and integration/deployment.

---

## Pattern Selection

**Primary pattern:** Sequential / Hand-off (Pipeline)

**Reason:** Each phase depends entirely on the previous phase's output. User stories and entity analysis must come before architecture decisions, which must come before API design, which must come before implementation, which must come before integration. There are no phases that can be parallelized within the pipeline itself.

**Secondary pattern:** Parallel Development Gate (at API design completion)

Once `bff.api-designer` produces a mock server and OpenAPI spec, frontend teams can develop against the mock while `bff.implementer` builds the real backend. This is a well-known BFF best practice (parallel development with mocks). The integrator phase resolves the two tracks.

---

## Workflow-to-Agent Mapping

| Workflow Step | Agent | Pattern Role |
|---|---|---|
| Step 1 - Analyze prototype for requirements | `bff.analyzer` | Sequential stage 1 |
| Step 2 - Define data model & architecture | `bff.architect` | Sequential stage 2 |
| Step 3 - Design APIs (contract-first) | `bff.api-designer` | Sequential stage 3 + parallel gate |
| Step 4 - Implement backend | `bff.implementer` | Sequential stage 4 |
| Step 5 - Integrate, test, and deploy | `bff.integrator` | Sequential stage 5 |
| _Overall coordination_ | `bff.orchestrator` | Pipeline orchestrator |

---

## Pipeline

```
User provides Figma URL or screen exports + project name + requirements
    ↓
bff.orchestrator
    → Validates inputs, creates project directory structure, initializes ORCHESTRATION_LOG.md
    ↓
bff.analyzer
    → Reads Figma screens, user flows, interactions
    → Outputs: analysis/user-stories.md, analysis/data-entities.md, analysis/api-requirements.md
    → Produces: HANDOFF_ANALYSIS.md (summary for bff.architect)
    ↓
bff.architect
    → Reads HANDOFF_ANALYSIS.md + analysis/ files
    → Outputs: architecture/erd.md, architecture/tech-stack.md, architecture/architecture.md
    → Produces: HANDOFF_ARCHITECTURE.md (summary for bff.api-designer)
    ↓
bff.api-designer
    → Reads HANDOFF_ARCHITECTURE.md + architecture/ files
    → Outputs: api/openapi.yaml, api/mock-server/, api/postman-collection.json
    → Produces: HANDOFF_API.md (summary for bff.implementer)
    ↓ [Parallel gate: frontend can connect to mock server here]
bff.implementer
    → Reads HANDOFF_API.md + api/openapi.yaml + architecture/ files
    → Outputs: src/ (complete TypeScript backend), prisma/, package.json, .env.example
    → Produces: HANDOFF_IMPL.md (summary for bff.integrator)
    ↓
bff.integrator
    → Reads HANDOFF_IMPL.md + src/ structure + api/openapi.yaml
    → Outputs: tests/, deploy/ (Dockerfile, docker-compose, CI/CD), monitoring setup
    → Produces: Final summary report
    ↓
Production-ready BFF
```

---

## Agent Specifications

### `bff.orchestrator`
- **Model:** claude-sonnet-4-5
- **Readonly:** false
- **Tools:** File system, shell execution
- **Pattern Role:** Pipeline orchestrator
- **Role:** Validates user inputs (Figma URL, project name, tech preferences), creates project directory structure, orchestrates the full sequential pipeline, passes complete context to each agent, and compiles the final delivery summary.
- **Input:** Figma prototype URL or screen exports, project name, tech stack preferences, auth requirements, deployment target
- **Output:** Orchestration log, all handoff documents, final summary

---

### `bff.analyzer`
- **Model:** claude-sonnet-4-5
- **Readonly:** false
- **Tools:** Web fetch (Figma URL), file read/write, structured output
- **Pattern Role:** Sequential stage 1
- **Role:** Analyzes Figma screens and user flows to extract structured requirements. Identifies user stories with acceptance criteria, data entities and their relationships, API endpoints needed per flow, authentication and authorization requirements, and edge cases/error states.
- **Input:** Figma URL or exported screen images/HTML, project name
- **Output:** `analysis/user-stories.md`, `analysis/data-entities.md`, `analysis/api-requirements.md`, `HANDOFF_ANALYSIS.md`
- **Handoff to:** bff.architect (via HANDOFF_ANALYSIS.md)

---

### `bff.architect`
- **Model:** claude-sonnet-4-5
- **Readonly:** false
- **Tools:** File read/write, Mermaid diagram generation
- **Pattern Role:** Sequential stage 2
- **Role:** Takes the analysis output and produces a complete architecture blueprint. Creates the ERD from identified entities, selects and justifies the tech stack, designs the authentication/authorization strategy, defines database schema, and plans service boundaries.
- **Input:** `HANDOFF_ANALYSIS.md`, `analysis/` folder contents, tech stack preferences
- **Output:** `architecture/erd.md`, `architecture/tech-stack.md`, `architecture/architecture.md`, `HANDOFF_ARCHITECTURE.md`
- **Handoff to:** bff.api-designer (via HANDOFF_ARCHITECTURE.md)

---

### `bff.api-designer`
- **Model:** claude-sonnet-4-5
- **Readonly:** false
- **Tools:** File read/write, YAML generation, JSON generation, shell (for mock server setup)
- **Pattern Role:** Sequential stage 3 + parallel gate enabler
- **Role:** Designs the complete API contract using the architecture blueprint. Produces a full OpenAPI 3.0 specification with all endpoints, request/response schemas, error codes, and security schemes. Sets up a mock server (JSON Server or MSW) so frontend development can proceed in parallel.
- **Input:** `HANDOFF_ARCHITECTURE.md`, `architecture/` folder contents
- **Output:** `api/openapi.yaml`, `api/mock-server/` (JSON Server + seed data), `api/postman-collection.json`, `HANDOFF_API.md`
- **Handoff to:** bff.implementer (via HANDOFF_API.md) + frontend team (via mock server)

---

### `bff.implementer`
- **Model:** claude-sonnet-4-5
- **Readonly:** false
- **Tools:** File read/write, shell execution (npm/pnpm commands), code generation
- **Pattern Role:** Sequential stage 4
- **Role:** Implements the complete backend based on the API contract and architecture. Sets up the project with TypeScript, installs dependencies, generates Prisma schema from ERD, creates routes/controllers/services, implements authentication middleware, adds validation (Zod), error handling, and logging.
- **Input:** `HANDOFF_API.md`, `api/openapi.yaml`, `architecture/erd.md`, `architecture/tech-stack.md`
- **Output:** Complete `src/` directory, `prisma/schema.prisma`, `package.json`, `tsconfig.json`, `.env.example`, `HANDOFF_IMPL.md`
- **Handoff to:** bff.integrator (via HANDOFF_IMPL.md)

---

### `bff.integrator`
- **Model:** claude-sonnet-4-5
- **Readonly:** false
- **Tools:** File read/write, shell execution (test runners, Docker), code generation
- **Pattern Role:** Sequential stage 5 (final)
- **Role:** Wires frontend to backend (CORS, auth token flows, environment config), writes integration and E2E tests, creates Docker and docker-compose configs, sets up CI/CD pipeline (GitHub Actions), and configures basic application monitoring (health checks, structured logging, error tracking).
- **Input:** `HANDOFF_IMPL.md`, `src/` structure, `api/openapi.yaml`, deployment target preference
- **Output:** `tests/` (integration + E2E), `deploy/Dockerfile`, `deploy/docker-compose.yml`, `.github/workflows/ci.yml`, monitoring setup, final delivery report
- **Handoff to:** End user (final summary)

---

## Handoff Document Schema

Each agent produces a `HANDOFF_*.md` file as a structured context bridge for the next agent. Format:

```markdown
# HANDOFF: [Phase Name]
Generated by: [agent-name]
For: [next-agent-name]
Timestamp: [ISO timestamp]

## Summary
[One-paragraph summary of what was produced]

## Key Decisions
- [Decision 1 with rationale]
- [Decision 2 with rationale]

## Files Produced
- [path]: [description]

## Context for Next Agent
[Specific instructions, flags, or caveats the next agent needs to know]

## Open Questions
[Any unresolved items that need user clarification or future iteration]
```

---

## Error Handling

| Phase | Failure | Recovery |
|-------|---------|----------|
| Analyzer | Cannot access Figma URL | Ask user for exported screen images or manual description |
| Analyzer | Prototype too sparse | Produce minimal analysis with explicit gaps marked; proceed |
| Architect | Conflicting tech preferences | Default to Node+Express+PostgreSQL+Prisma; note alternatives |
| API Designer | Ambiguous endpoint semantics | Use REST best practices as default; document assumptions |
| Implementer | Missing environment values | Use `.env.example` placeholders; document in README |
| Integrator | Tests fail | Report failures in summary; do not block delivery |
