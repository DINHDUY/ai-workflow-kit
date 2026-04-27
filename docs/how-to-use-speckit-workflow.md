# How to Use the SpecKit Workflow

This guide demonstrates using the SpecKit workflow for automated spec-driven development from initial concept to full implementation.

## Overview

The SpecKit workflow automates the entire [GitHub SpecKit](https://github.com/github/spec-kit) development process through intelligent agents that programmatically invoke SpecKit commands, validate outputs, and automatically progress through all phases without human intervention.

## Prerequisites

Before using the SpecKit workflow, ensure your project has:

1. **SpecKit initialized:**
   ```bash
   uvx --from git+https://github.com/github/spec-kit.git specify init --here
   ```

2. **Git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Build system** (optional but recommended):
   - Node.js: `package.json`
   - .NET: `*.csproj`
   - Java: `pom.xml` or `build.gradle`
   - Python: `requirements.txt`

## Installation

Install the workflow into your Cursor workspace:

**Cursor:**
```bash
uvx --from git+https://github.com/DINHDUY/ai-workflow-kit-py ^
    add-workflows speckit --output .cursor/agents
```

This installs the workflow agents into your `.cursor/agents/` directory.

## Usage

Invoke the orchestrator agent with your feature description:

```
/speckit-overlay.orchestrator Implement a user authentication system with email/password login, JWT tokens, and password reset functionality.
```

The orchestrator coordinates the full 7-phase workflow:
1. **Constitution** - Project principles and constraints
2. **Specification** - Detailed requirements with user stories
3. **Clarification** - Requirement refinement and gap filling
4. **Planning** - Technical implementation plan
5. **Task Breakdown** - Dependency-ordered tasks
6. **Analysis** - Cross-artifact consistency validation
7. **Implementation** - Full code generation with testing

## Example Invocations

**Basic feature request:**
```
@speckit-overlay.orchestrator Create a REST API for managing customer orders with CRUD operations.
```

**With technology preferences:**
```
@speckit-overlay.orchestrator Build a real-time chat application using WebSockets. Prefer .NET Aspire and SignalR.
```

**Skip optional phases:**
```
@speckit-overlay.orchestrator Add export to CSV functionality. Skip clarification phase.
```

## Output

All artifacts are saved to `.specify/specs/<feature-id>/`:

- **constitution.md** - Project governance principles
- **spec.md** - Complete specification with user stories and acceptance criteria
- **plan.md** - Technical architecture and implementation details
- **tasks.md** - Actionable task breakdown with dependencies
- **Source files** - Fully implemented codebase per specification
- **speckit-execution-log.md** - Complete execution log with all command outputs

## Specialized Agents

The workflow includes 8 specialized agents:

| Agent | Purpose |
|-------|---------|
| `speckit-overlay.orchestrator` | Coordinates the full workflow |
| `speckit-overlay.constitution` | Generates project principles |
| `speckit-overlay.specify` | Creates detailed specifications |
| `speckit-overlay.clarify` | Refines requirements |
| `speckit-overlay.plan` | Produces technical plan |
| `speckit-overlay.tasks` | Generates task breakdown |
| `speckit-overlay.analyze` | Validates consistency |
| `speckit-overlay.implement` | Executes implementation |

You can invoke individual agents directly for specific phases, though the orchestrator is recommended for full automation.

## Benefits

- **Zero-touch automation** - From concept to implementation without manual intervention
- **Consistent structure** - Standard SpecKit artifacts for all features
- **Validation gates** - Automatic consistency checking between phases
- **Resilient execution** - Built-in retry logic for command failures
- **Complete traceability** - Full execution logs for every phase
