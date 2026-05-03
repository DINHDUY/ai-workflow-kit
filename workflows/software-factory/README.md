# AI-Powered Software Factory

An autonomous multi-agent system that transforms raw ideas into deployed, production-ready software. Ideas enter a prioritized queue, flow through a structured 8-phase pipeline, and emerge as live applications with full test coverage, documentation, CI/CD pipelines, and post-launch monitoring.

The factory enforces two Human-in-the-Loop (HITL) gates — after idea validation and before production release — to keep humans in control while maximizing automated output.

## What It Does

1. **Validates ideas** against existing projects, performs market and competitor research, assesses technical feasibility, and defines an MVP scope — then gates on human approval before committing resources
2. **Writes a complete PRD** with user personas, Gherkin user stories, acceptance criteria, success metrics, and a concrete tech stack recommendation
3. **Designs the full system architecture** with Mermaid component diagrams, OpenAPI 3.1 contracts, database ERDs, security model, and Architecture Decision Records — in parallel with UI component scaffolding
4. **Implements backend and frontend in parallel** — backend services (FastAPI/Node) commit feature by feature; frontend pages (Next.js/React) build against the API contract with loading/error/empty states for every data-fetching component
5. **Runs an iterative QA loop** (max 3 rounds) with unit, integration, and Playwright E2E tests; enforces ≥70% coverage gate and OWASP Top-10 security checklist; gates on human approval before release
6. **Generates comprehensive documentation** — README, API reference from the OpenAPI spec, user guide with step-by-step workflows, and consolidated ADRs
7. **Deploys with full CI/CD** — GitHub Actions workflows (lint → type-check → test → build → deploy), cloud deployment (Vercel + Railway/Fly.io/AWS), Sentry monitoring, and a tagged Git release with rollback instructions
8. **Monitors post-launch** continuously — watches error rates, performance metrics, and anomalies; creates structured improvement tickets fed back into the idea queue

## Agents

| Agent | Role |
|-------|------|
| `sf.orchestrator` | Factory Manager: coordinates all 8 phases, enforces HITL gates, tracks costs, manages retries and escalation |
| `sf.idea-validator` | Validates ideas: duplicate detection, market/competitor research, feasibility assessment, MVP scope definition |
| `sf.product-manager` | Generates PRD: user personas, Gherkin user stories, acceptance criteria, success metrics, tech stack recommendation |
| `sf.system-architect` | Designs system: Mermaid architecture diagram, OpenAPI spec, database ERD, security model, ADRs |
| `sf.ux-designer` | UI/UX design: page layout specs, component hierarchy, Tailwind/shadcn component stubs (runs parallel with sf.system-architect) |
| `sf.backend-coder` | Implements backend: FastAPI/Node services, DB models and migrations, auth middleware, Git commit per feature |
| `sf.frontend-coder` | Implements frontend: Next.js/React pages, API service layer, React Query hooks, Git commit per page |
| `sf.qa-tester` | Quality assurance: unit/integration/E2E tests, OWASP scan, coverage gate, iterative bug-fix loop |
| `sf.documenter` | Documentation: README, API reference, user guide, consolidated ADRs |
| `sf.deployer` | Deployment: GitHub Actions CI/CD, Vercel/Railway/Fly.io/AWS deployment, Sentry, Git release tag |
| `sf.monitor` | Post-launch: availability checks, Sentry analysis, performance metrics, improvement ticket creation |

## Pipeline

```
Idea Input
    ↓
sf.orchestrator  (workspace + Git init)
    ↓
Phase 1: sf.idea-validator
    ↓ ── HITL GATE 1: Approve / Reject / Refine ──
Phase 2: sf.product-manager
    ↓
Phase 3: sf.system-architect ┬ (parallel)
         sf.ux-designer      ┘
    ↓
Phase 4: sf.backend-coder  ┬ (parallel)
         sf.frontend-coder ┘
    ↓
Phase 5: sf.qa-tester  ◄── iterative loop (max 3 rounds)
    ↓ ── HITL GATE 2: Approve / Request Changes / Abandon ──
Phase 6: sf.documenter
Phase 7: sf.deployer
    ↓
Phase 8: sf.monitor  (async, ongoing)
```

## How to Use

### Full Pipeline

Invoke `sf.orchestrator` with an idea description:

```
@sf.orchestrator Build a SaaS app that lets small teams track feature flags with role-based access and a visual dashboard.

Type: web
Stack: Next.js, FastAPI, PostgreSQL
Deploy to: vercel
Budget: $10
```

The orchestrator will run all 8 phases with HITL gates and deliver:
- Live URL
- Git repository with full codebase
- `README.md` + `docs/`
- `.github/workflows/` CI/CD pipelines
- `deployment.md` with rollback instructions
- `.sf/` factory artifacts (PRD, architecture, QA report)

### Individual Agents

**Validate an idea only:**
```
@sf.idea-validator
Project root: /path/to/project
Idea: A CLI tool for developers to sync dotfiles across multiple machines
Target users: software engineers
Project type: cli
```

**Generate PRD from a validated idea:**
```
@sf.product-manager
Project root: /path/to/project
Feasibility report: .sf/reports/feasibility-report.md
Idea metadata: .sf/idea.json
```

**Design system architecture:**
```
@sf.system-architect
Project root: /path/to/project
PRD: .sf/prd.md
Tech stack: .sf/reports/tech-stack.md
```

**Run QA on an existing codebase:**
```
@sf.qa-tester
Project root: /path/to/project
PRD acceptance criteria: .sf/prd.md
Architecture spec: .sf/architecture.md
Max fix iterations: 3
Iteration number: 1
```

**Deploy an existing project:**
```
@sf.deployer
Project root: /path/to/project
Deploy target: railway
Tech stack: .sf/reports/tech-stack.md
Release version: v1.0.0
```

**Check post-launch health:**
```
@sf.monitor
Project root: /path/to/project
Live URL: https://my-app.vercel.app
Project slug: my-app
Monitoring platform: sentry
```

## Output Structure

Every factory run produces:

```
projects/{project-slug}/
├── .sf/
│   ├── idea.json               # Idea metadata + factory state
│   ├── prd.md                  # Product Requirements Document
│   ├── architecture.md         # System design + diagrams
│   ├── api-contracts.yaml      # OpenAPI 3.1 specification
│   ├── ux-design.md            # UI/UX page specifications
│   ├── adr/                    # Architecture Decision Records
│   ├── reports/
│   │   ├── feasibility-report.md
│   │   ├── tech-stack.md
│   │   ├── qa-report.md
│   │   ├── monitor-report.md
│   │   └── improvement-queue.md
│   └── logs/                   # Agent execution logs
├── README.md
├── docs/
│   ├── api.md
│   ├── user-guide.md
│   └── adr/
├── backend/
├── frontend/
├── tests/
├── e2e/
├── .github/workflows/
└── deployment.md
```

## Quality Gates

| Gate | Threshold | Blocks |
|------|-----------|--------|
| HITL Gate 1 | Human approval | Phase 2 onwards |
| Test coverage | ≥70% line coverage | Phase 6 (docs) |
| OWASP security | No Critical or High findings | Phase 7 (deploy) |
| Build | Zero TypeScript errors, zero lint warnings | Phase 6 |
| HITL Gate 2 | Human approval | Phase 7 (deploy) |

## Supported Tech Stacks

| Project Type | Default Stack |
|-------------|--------------|
| Web app | Next.js 15 + FastAPI + PostgreSQL + Vercel/Railway |
| API service | FastAPI or Hono + PostgreSQL + Railway/Fly.io |
| CLI tool | Python + Click or TypeScript + Commander.js |
| Mobile app | React Native (Expo) + FastAPI + EAS |

## Governance

- **Cost control**: Orchestrator tracks token/API spend per project; auto-pauses at 80% of budget
- **Audit log**: Every agent action logged with timestamp and reasoning in `.sf/logs/`
- **Rollback**: All releases are Git-tagged; one-command rollback documented in `deployment.md`
- **HITL override**: Human can pause, modify prompts, or take over at any gate
- **Feedback loop**: Monitor agent feeds improvement tickets back into the queue for future runs

## Setup

No special installation required — agents run directly in your AI editor (Cursor, VS Code with Copilot, etc.).

**Prerequisites for the deployed applications:**
- Node.js 22+
- Python 3.12+
- Docker (for local database)
- GitHub account (for CI/CD)
- Accounts on your chosen cloud provider (Vercel, Railway, Fly.io, or AWS)

**Optional monitoring:**
- Sentry account (free tier sufficient for MVP)
