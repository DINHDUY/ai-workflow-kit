# SpecKit Command Wrapper - Workflow Specification

## Overview

This workflow creates Cursor agents that wrap GitHub SpecKit's slash commands (`/speckit.*`) and invoke them programmatically to automate the entire spec-driven development process from initial project description to full implementation without human intervention.

## Key Difference from Base SpecKit Workflow

- **Base workflow (`workflows/speckit/`)**: Reimplements SpecKit logic in agents
- **This overlay (`workflows/speckit-overlay/`)**: Wraps and invokes actual SpecKit slash commands programmatically

## Purpose

Transform SpecKit's interactive command-based workflow into a fully automated agentic system where:
- Cursor agents invoke actual SpecKit slash commands via programmatic execution
- Steps flow automatically from one to the next without human review
- Context passes seamlessly between command invocations
- Errors trigger automatic retry logic (max 3 attempts per command)

## Prerequisites

- SpecKit must be initialized in the project (`specify init . --ai cursor`)
- `.specify/` directory structure must exist
- SpecKit slash commands (` /speckit.*`) must be available in the project

## User Input

**Required:**
- `projectDescription`: Natural language description of what to build (what and why, not how)

**Optional:**
- `techStack`: Technology stack preferences (e.g., ".NET Aspire, Postgres, Blazor")
- `principles`: Custom project governance principles (if omitted, agent generates defaults)
- `skipClarify`: Boolean to skip `/speckit.clarify` step (default: false)
- `skipAnalyze`: Boolean to skip `/speckit.analyze` step (default: false)

## Expected Output

**Final Deliverables:**
- `.specify/memory/constitution.md` - Project governance principles (via `/speckit.constitution`)
- `.specify/specs/{feature-id}/spec.md` - Complete specification with user stories (via `/speckit.specify`)
- `.specify/specs/{feature-id}/plan.md` - Technical implementation plan (via `/speckit.plan`)
- `.specify/specs/{feature-id}/tasks.md` - Actionable task breakdown (via `/speckit.tasks`)
- Fully implemented codebase per specification (via `/speckit.implement`)
- `speckit-execution-log.md` - Complete execution log with all command outputs and retry attempts

## Workflow Steps (7 SpecKit Commands)

### 1. Constitution Creation
**Agent:** `speckit-overlay.constitution`
**Command Invoked:** `/speckit.constitution`
**Input:** Project description, custom principles (optional)
**Action:** Programmatically execute `/speckit.constitution Create principles focused on...`
**Output:** `.specify/memory/constitution.md`
**Validation:** File exists, contains Core Principles, Technology Constraints, Quality Standards

### 2. Specification Creation
**Agent:** `speckit-overlay.specify`
**Command Invoked:** `/speckit.specify`
**Input:** Project description
**Action:** Programmatically execute `/speckit.specify {projectDescription}`
**Output:** `.specify/specs/{feature-id}/spec.md` with user stories and requirements
**Validation:** Spec file exists, contains User Stories, Functional Requirements, Acceptance Criteria

### 3. Clarification (Optional)
**Agent:** `speckit-overlay.clarify`
**Command Invoked:** `/speckit.clarify`
**Input:** Current spec
**Action:** Programmatically execute `/speckit.clarify`
**Output:** Updated spec with Clarifications section
**Validation:** Clarifications section added to spec.md
**Skip Condition:** If `skipClarify=true`

### 4. Technical Planning
**Agent:** `speckit-overlay.plan`
**Command Invoked:** `/speckit.plan`
**Input:** Tech stack preferences
**Action:** Programmatically execute `/speckit.plan {techStackDescription}`
**Output:** `.specify/specs/{feature-id}/plan.md` with architecture and implementation details
**Validation:** Plan file exists, contains Implementation Plan, Technical Stack, File Structure

### 5. Consistency Analysis (Optional)
**Agent:** `speckit-overlay.analyze`
**Command Invoked:** `/speckit.analyze`
**Input:** Spec, plan, tasks (after tasks created)
**Action:** Programmatically execute `/speckit.analyze`
**Output:** Analysis report with consistency checks
**Validation:** Analysis passes or issues documented
**Skip Condition:** If `skipAnalyze=true`
**Timing:** Runs AFTER task generation

### 6. Task Breakdown
**Agent:** `speckit-overlay.tasks`
**Command Invoked:** `/speckit.tasks`
**Input:** Plan
**Action:** Programmatically execute `/speckit.tasks`
**Output:** `.specify/specs/{feature-id}/tasks.md` with actionable, dependency-ordered tasks
**Validation:** Tasks file exists, contains task list with IDs and dependencies

### 7. Implementation
**Agent:** `speckit-overlay.implement`
**Command Invoked:** `/speckit.implement`
**Input:** Spec, plan, tasks
**Action:** Programmatically execute `/speckit.implement`
**Output:** Fully implemented codebase
**Validation:** Implementation completes, all tests pass (if tests exist)

## Command Execution Method

Each agent uses the `run_vscode_command` tool to invoke SpecKit commands:

```javascript
// Example: Invoking /speckit.constitution
run_vscode_command({
  command: "workbench.action.chat.submit",
  args: {
    prompt: "/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements"
  }
})
```

Alternatively, agents may use programmatic chat APIs if available in Cursor.

## Error Handling & Retry Logic

**Per-Step Retry Policy:**
- Each command execution has max 3 retry attempts
- Retry triggers:
  - Command fails to execute
  - Output validation fails (expected files not created)
  - SpecKit reports errors in command output
- Between retries: 5-second delay
- Retry strategy: Re-invoke same command with identical parameters

**Orchestrator Failure Handling:**
- If step fails after 3 retries: Log failure, halt workflow, report to user
- Log format:
  ```
  ❌ Step 4 (Planning) FAILED after 3 attempts
  
  Attempt 1: [error message]
  Attempt 2: [error message]
  Attempt 3: [error message]
  
  Workflow halted. Manual intervention required.
  ```

## Orchestration Flow

```
User Input
    ↓
speckit-overlay.orchestrator
    ↓
┌─────────────────────────────────────────┐
│ Phase 1: Constitution                    │
│ → speckit-overlay.constitution          │
│ → Invoke /speckit.constitution          │
│ → Validate output                       │
│ → Retry up to 3 times on failure        │
└─────────────────────────────────────────┘
    ↓ (success)
┌─────────────────────────────────────────┐
│ Phase 2: Specification                   │
│ → speckit-overlay.specify               │
│ → Invoke /speckit.specify               │
│ → Validate output                       │
│ → Retry up to 3 times on failure        │
└─────────────────────────────────────────┘
    ↓ (success)
┌─────────────────────────────────────────┐
│ Phase 3: Clarification (optional)        │
│ → speckit-overlay.clarify               │
│ → Invoke /speckit.clarify               │
│ → Validate output                       │
│ → Retry up to 3 times on failure        │
└─────────────────────────────────────────┘
    ↓ (success)
┌─────────────────────────────────────────┐
│ Phase 4: Planning                        │
│ → speckit-overlay.plan                  │
│ → Invoke /speckit.plan                  │
│ → Validate output                       │
│ → Retry up to 3 times on failure        │
└─────────────────────────────────────────┘
    ↓ (success)
┌─────────────────────────────────────────┐
│ Phase 5: Task Generation                 │
│ → speckit-overlay.tasks                 │
│ → Invoke /speckit.tasks                 │
│ → Validate output                       │
│ → Retry up to 3 times on failure        │
└─────────────────────────────────────────┘
    ↓ (success)
┌─────────────────────────────────────────┐
│ Phase 6: Analysis (optional)             │
│ → speckit-overlay.analyze               │
│ → Invoke /speckit.analyze               │
│ → Validate output                       │
│ → Retry up to 3 times on failure        │
└─────────────────────────────────────────┘
    ↓ (success)
┌─────────────────────────────────────────┐
│ Phase 7: Implementation                  │
│ → speckit-overlay.implement             │
│ → Invoke /speckit.implement             │
│ → Validate output                       │
│ → Retry up to 3 times on failure        │
└─────────────────────────────────────────┘
    ↓ (success)
Execution Report Generated
```

## Success Criteria

- All 7 SpecKit commands execute successfully (or 5 if optional steps skipped)
- Constitution file created with comprehensive principles
- Spec contains detailed user stories and acceptance criteria
- Plan includes complete technical architecture
- Tasks are actionable and properly sequenced
- Implementation passes all validations
- No build/runtime errors in final code
- Execution log documents entire workflow with timestamps and outputs

## Use Cases

1. **Fully Automated Greenfield**: Provide project description, get working app without any manual steps
2. **Brownfield Feature Addition**: Add features to existing SpecKit-managed codebases automatically
3. **Batch Feature Generation**: Queue multiple features, run orchestrator sequentially
4. **CI/CD Integration**: Trigger from PRs, run full spec-driven process in pipeline
5. **Training & Demonstrations**: Show complete SpecKit workflow in action
