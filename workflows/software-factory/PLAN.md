# AI-Powered Software Factory - Multi-Agent Plan

Source research: `workflows/software-factory/software-factory-research.md`

---

## Architecture Overview

The Software Factory decomposes into **11 specialized agents**:
- **1 orchestrator** — Factory Manager that coordinates the full idea-to-deployment pipeline
- **2 discovery agents** — Idea Validator and Product Manager
- **2 design agents** — System Architect and UX Designer
- **2 coding agents** — Backend Coder and Frontend Coder
- **1 quality agent** — QA Tester
- **1 documentation agent** — Documenter
- **1 deployment agent** — Deployer
- **1 monitoring agent** — Monitor (post-launch, async)

**Orchestration Pattern:** Sequential Pipeline with parallel fan-out at the Design phase and the Coding phase.

```
User → sf.orchestrator → Discovery → Design (parallel) → Coding (parallel) → Quality → Docs → Deploy → Monitor
```

---

## Design Principles

1. **Modular & Observable**: Each agent produces versioned output files; all actions are logged with reasoning to `.sf/logs/`.
2. **Human-in-the-Loop Gates**: HITL checkpoints after idea validation and before production release.
3. **Git-First**: Every project begins with an auto-created Git repo; all agent outputs are committed.
4. **Cost & Quality Tracking**: Token/API spend tracked per project; quality gates (test coverage, security) enforced before deploy.
5. **Resilient Execution**: 3-retry policy on agent failures; orchestrator escalates to human when confidence < threshold.
6. **Feedback Loop**: Monitor agent creates improvement tickets back to the idea queue post-launch.

---

## Workflow-to-Agent Mapping

| Workflow Phase | Agent | Pattern Role |
|---|---|---|
| Phase 0 — Factory Initialization | `sf.orchestrator` | Pipeline orchestrator |
| Phase 1 — Idea Validation | `sf.idea-validator` | Sequential stage 1 |
| Phase 2 — Product Requirements | `sf.product-manager` | Sequential stage 2 |
| Phase 3a — System Architecture | `sf.system-architect` | Parallel worker A |
| Phase 3b — UI/UX Design | `sf.ux-designer` | Parallel worker B |
| Phase 4a — Backend Implementation | `sf.backend-coder` | Parallel worker C |
| Phase 4b — Frontend Implementation | `sf.frontend-coder` | Parallel worker D |
| Phase 5 — QA & Testing | `sf.qa-tester` | Sequential stage 5 (iterative loop) |
| Phase 6 — Documentation | `sf.documenter` | Sequential stage 6 |
| Phase 7 — Deployment & CI/CD | `sf.deployer` | Sequential stage 7 |
| Phase 8 — Post-Launch Monitoring | `sf.monitor` | Continuous async stage |

---

## Agent Inventory

| Agent Name | Model | Readonly | Purpose |
|------------|-------|----------|---------|
| `sf.orchestrator` | sonnet | false | Factory Manager: coordinates full pipeline, enforces HITL gates, tracks costs |
| `sf.idea-validator` | sonnet | false | Deduplication, market/competitor research, feasibility report, MVP scope |
| `sf.product-manager` | sonnet | false | PRD, user stories, acceptance criteria, personas, tech stack recommendation |
| `sf.system-architect` | sonnet | false | Architecture diagram (Mermaid), data model, API contracts (OpenAPI), ADRs |
| `sf.ux-designer` | fast | false | UI component scaffolding, page layout descriptions, Tailwind/shadcn stubs |
| `sf.backend-coder` | sonnet | false | Backend services (FastAPI/Node/Django), Git commits per feature |
| `sf.frontend-coder` | sonnet | false | Frontend app (Next.js/React), page-by-page commits |
| `sf.qa-tester` | sonnet | false | Unit/integration/E2E tests, OWASP security scan, bug-fix loop (max 3 rounds) |
| `sf.documenter` | fast | false | README, API docs, user guide, architecture decision records |
| `sf.deployer` | sonnet | false | GitHub Actions CI/CD, cloud deployment, Sentry setup, Git release tag |
| `sf.monitor` | fast | true | Post-launch log/metric analysis, improvement ticket creation |

---

## Pipeline

```
User Idea Input
       ↓
sf.orchestrator  ──  creates project folder + Git repo + .sf/ workspace
       ↓
[Phase 1]  sf.idea-validator
       ↓   feasibility report + duplicate check + competitor analysis
       ↓   ── HITL GATE 1: Human approves / rejects / refines ──
       ↓
[Phase 2]  sf.product-manager
       ↓   PRD + user stories + acceptance criteria + tech stack
       ↓
[Phase 3]  ┌── sf.system-architect  (architecture.md + api-contracts.yaml + ADR)
           └── sf.ux-designer       (ux-design.md + component stubs)
       ↓   (artifacts merged into .sf/)
[Phase 4]  ┌── sf.backend-coder    (backend implementation + smoke tests)
           └── sf.frontend-coder   (frontend implementation + visual smoke test)
       ↓   (codebase merged, PRs opened)
[Phase 5]  sf.qa-tester  ◄──── iterative loop: Code → Test → Fix (max 3 rounds)
       ↓   green build + ≥70% coverage + OWASP pass
       ↓   ── HITL GATE 2: Human reviews QA report + live preview ──
       ↓
[Phase 6]  sf.documenter
       ↓   README + API docs + user guide + ADRs finalized
[Phase 7]  sf.deployer
       ↓   GitHub Actions + cloud deploy + Git release tag + live URL
[Phase 8]  sf.monitor  (async, ongoing)
           watches metrics → creates improvement tickets → feeds back to queue
```

---

## Parallelization Strategy

**Phase 3 Fan-Out**: `sf.system-architect` and `sf.ux-designer` run concurrently — system design and UI scaffolding are independent concerns that both consume the PRD.

**Phase 4 Fan-Out**: `sf.backend-coder` and `sf.frontend-coder` run concurrently, sharing context through the architecture spec and API contracts produced in Phase 3. Frontend uses the API contract as the interface boundary; no blocking dependency on backend completion.

**Phase 8 Async**: `sf.monitor` runs asynchronously after deployment, continuously in the background without blocking the pipeline completion signal.

---

## Output Artifacts Per Project

```
/projects/{project-slug}/
├── .sf/
│   ├── idea.json              # Idea metadata + priority score
│   ├── prd.md                 # Product Requirements Document
│   ├── architecture.md        # System design + Mermaid diagrams
│   ├── api-contracts.yaml     # OpenAPI specification
│   ├── ux-design.md           # UI/UX component descriptions
│   ├── adr/                   # Architecture Decision Records
│   ├── reports/
│   │   ├── feasibility-report.md
│   │   ├── tech-stack.md
│   │   ├── qa-report.md
│   │   └── monitor-report.md
│   └── logs/                  # Agent execution logs with reasoning
├── README.md
├── docs/
│   ├── api.md
│   ├── user-guide.md
│   └── adr/
├── src/  (or app/)
├── tests/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
└── deployment.md
```

---

## HITL Gate Specification

### Gate 1 — Post-Idea-Validation
- **Trigger**: `sf.idea-validator` completes and writes feasibility report
- **Decision options**:
  - ✅ **Approve** → continue to Phase 2
  - ❌ **Reject** → archive idea with reason
  - 🔄 **Refine** → re-run `sf.idea-validator` with amended scope or constraints
- **Timeout**: 24 hours — orchestrator sends reminder; after 48h auto-escalates

### Gate 2 — Pre-Production-Release
- **Trigger**: `sf.qa-tester` completes with green build
- **Required review**: `.sf/reports/qa-report.md` + live preview URL
- **Decision options**:
  - ✅ **Approve** → continue to Phase 6 (docs) and Phase 7 (deploy)
  - 🔄 **Request changes** → re-enter Phase 5 with specific instructions
  - ❌ **Abandon** → archive project with reason

---

## Cost & Quality Controls

| Control | Mechanism |
|---------|-----------|
| Budget per project | Orchestrator tracks token/API spend; auto-pauses at 80% of budget and notifies human |
| Test coverage gate | `sf.qa-tester` enforces ≥70% line coverage; blocks Phase 6 if not met |
| Security gate | `sf.qa-tester` runs OWASP Top-10 checklist; blocks deploy on Critical or High findings |
| Code quality gate | `sf.qa-tester` runs linter with zero-error policy before signaling completion |
| Audit log | Every agent action stored in `.sf/logs/{phase}-{agent}.log` with ISO timestamp + reasoning |
| Git release tags | `sf.deployer` tags releases (`v1.0.0`); rollback via `git revert` or checkout |
| Rollback procedure | Documented in `deployment.md`; deployer provides one-command revert |

---

## Agent Specifications

### `sf.orchestrator`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash, Git, subagent Task delegation
- **Pattern Role:** Pipeline orchestrator
- **Role:** Pulls the next idea from the queue (or accepts direct input), creates the project workspace and Git repo, spawns the correct agent team based on project type, maintains full pipeline state in `.sf/logs/`, enforces HITL gates, tracks costs, and escalates to human when confidence < threshold.
- **Input:** Idea title + description (or queue item ID), project type override (optional)
- **Output:** Final project report with live URL, repo link, cost summary

### `sf.idea-validator`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Web Search, Semantic Search
- **Pattern Role:** Sequential stage 1
- **Role:** Checks for duplicate ideas in project history via semantic search. Performs market and competitor research using web search. Assesses technical feasibility and estimated effort. Produces a structured feasibility report with a go/no-go/refine recommendation and a suggested MVP scope.
- **Input:** Idea title, description, problem statement, target users
- **Output:** `.sf/reports/feasibility-report.md` (duplicate check + competitor analysis + risk assessment + MVP scope)

### `sf.product-manager`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write
- **Pattern Role:** Sequential stage 2
- **Role:** Transforms the validated idea and feasibility report into a complete PRD. Generates 2-3 user personas, user stories in Gherkin format with acceptance criteria, success metrics (KPIs), and a tech stack recommendation based on project type.
- **Input:** Feasibility report, idea metadata
- **Output:** `.sf/prd.md`, `.sf/reports/tech-stack.md`

### `sf.system-architect`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Web Search
- **Pattern Role:** Parallel stage 3a
- **Role:** Designs the complete system architecture: components, APIs, database schema, security model, scaling strategy. Produces a Mermaid architecture diagram, OpenAPI spec skeleton, ERD in Mermaid, and an ADR for key technology choices.
- **Input:** PRD, tech stack preferences
- **Output:** `.sf/architecture.md`, `.sf/api-contracts.yaml`, `.sf/adr/001-system-design.md`

### `sf.ux-designer`
- **Model:** fast
- **Readonly:** false
- **Tools:** File Read/Write
- **Pattern Role:** Parallel stage 3b
- **Role:** Translates PRD and user stories into page layout descriptions, UI component trees, and Tailwind/shadcn component stubs. Does not generate images; produces structured component hierarchy and layout descriptions sufficient for `sf.frontend-coder` to implement.
- **Input:** PRD, user stories, target platform (web/mobile)
- **Output:** `.sf/ux-design.md`, scaffolded component stubs in `src/components/`

### `sf.backend-coder`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash (sandbox), Git
- **Pattern Role:** Parallel stage 4a
- **Role:** Implements backend services from the architecture spec and API contracts, feature by feature. Uses secure coding practices (input validation, parameterized queries, auth middleware, rate limiting). Commits to Git after each feature. Runs the service in sandbox to confirm it starts and passes smoke tests.
- **Input:** Architecture spec, API contracts, PRD feature list
- **Output:** Implemented backend in `src/` or `backend/`, Git commits per feature, passing smoke tests

### `sf.frontend-coder`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash (sandbox), Git
- **Pattern Role:** Parallel stage 4b
- **Role:** Implements the frontend application using the UX design spec and API contracts as boundaries. Builds from the component stubs scaffolded by `sf.ux-designer`. Connects to backend APIs. Commits after each page/feature. Verifies the app builds and renders without console errors.
- **Input:** UX design spec, API contracts, component stubs
- **Output:** Implemented frontend in `src/` or `frontend/`, Git commits per page

### `sf.qa-tester`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash, Git
- **Pattern Role:** Sequential stage 5 (iterative loop, max 3 rounds)
- **Role:** Writes and runs unit tests (pytest/vitest), integration tests, and E2E tests (Playwright). Runs OWASP Top-10 checklist against the codebase. Measures test coverage and enforces the ≥70% gate. When tests fail, creates a structured bug report and triggers a fix round by delegating back to the relevant coder agent.
- **Input:** Implemented codebase, PRD acceptance criteria
- **Output:** `.sf/reports/qa-report.md`, test files in `tests/`, green build

### `sf.documenter`
- **Model:** fast
- **Readonly:** false
- **Tools:** File Read/Write
- **Pattern Role:** Sequential stage 6
- **Role:** Generates a comprehensive README with project overview, prerequisites, setup, and usage. Produces API documentation from the OpenAPI spec. Writes a user guide covering key workflows. Finalizes ADRs for all major architectural decisions made during the pipeline run.
- **Input:** PRD, architecture spec, API contracts, codebase structure
- **Output:** `README.md`, `docs/api.md`, `docs/user-guide.md`, `docs/adr/`

### `sf.deployer`
- **Model:** sonnet
- **Readonly:** false
- **Tools:** File Read/Write, Bash, Git, cloud provider APIs
- **Pattern Role:** Sequential stage 7
- **Role:** Creates GitHub Actions CI/CD workflows (lint → type-check → test → build → deploy). Deploys to the configured cloud provider (Vercel, Railway, Fly.io, or AWS). Sets up Sentry for error monitoring. Tags the Git release and writes `deployment.md` with rollback instructions.
- **Input:** Codebase, deployment platform preference, environment secrets
- **Output:** `.github/workflows/`, `deployment.md`, live URL, Git release tag

### `sf.monitor`
- **Model:** fast
- **Readonly:** true
- **Tools:** File Read, Web API calls (Sentry/monitoring), Bash (read-only)
- **Pattern Role:** Continuous async stage 8
- **Role:** Polls deployment logs, Sentry events, and performance metrics after launch. Detects error spikes, performance regressions, and anomalous patterns. Creates structured improvement tickets and appends them to the project's idea queue for future factory runs.
- **Input:** Deployment URL, monitoring credentials, project ID
- **Output:** `.sf/reports/monitor-report.md`, improvement tickets in queue
