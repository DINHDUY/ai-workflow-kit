# SpecKit Command Wrapper - Multi-Agent Plan

## Architecture Overview

The SpecKit overlay workflow decomposes into **8 specialized agents**:
- **1 orchestrator** - coordinates the full 7-step SpecKit command workflow
- **7 command-wrapper agents** - each wraps one SpecKit slash command

**Orchestration Pattern:** Sequential pipeline with command execution, output validation, and retry logic between phases.

```
User → speckit-overlay.orchestrator → Command Wrapper Agents (1-7) → Implementation Complete
```

## Design Principles

1. **Thin Wrappers**: Agents invoke actual SpecKit commands, not reimplementations
2. **Observable Execution**: Every command invocation is logged with input/output
3. **Resilient by Default**: 3-retry policy on all command failures
4. **Validation Gates**: Each phase validates expected outputs before proceeding
5. **Context Preservation**: Orchestrator maintains full workflow context across phases

## Agent Inventory

| Agent Name | Model | Readonly | SpecKit Command | Purpose |
|------------|-------|----------|-----------------|---------|
| speckit-overlay.orchestrator | sonnet | false | N/A | Coordinates full 7-step workflow |
| speckit-overlay.constitution | fast | false | `/speckit.constitution` | Wraps constitution creation command |
| speckit-overlay.specify | sonnet | false | `/speckit.specify` | Wraps specification creation command |
| speckit-overlay.clarify | sonnet | false | `/speckit.clarify` | Wraps clarification command |
| speckit-overlay.plan | sonnet | false | `/speckit.plan` | Wraps planning command |
| speckit-overlay.tasks | fast | false | `/speckit.tasks` | Wraps task generation command |
| speckit-overlay.analyze | fast | true | `/speckit.analyze` | Wraps analysis command |
| speckit-overlay.implement | sonnet | false | `/speckit.implement` | Wraps implementation command |

## Command Execution Strategy

### Tool Selection

Cursor agents have two options for invoking SpecKit commands:

**Option 1: Direct Command Invocation (Preferred)**
- Use `run_vscode_command` tool to trigger SpecKit commands
- Advantage: Direct, synchronous execution
- Challenge: Requires knowledge of VS Code command IDs for SpecKit

**Option 2: Chat Submission Simulation**
- Use programmatic chat API to submit `/speckit.*` commands
- Advantage: Identical to user typing command
- Challenge: Async nature, need to poll for completion

**Recommended Approach:** Each wrapper agent will attempt Option 1, fallback to Option 2 if unavailable.

### Output Capture

After command execution, agents will:
1. Wait for command completion (polling if async)
2. Read resulting files from `.specify/` directory
3. Validate file contents against expected schema
4. Extract key information for orchestrator logging

## Phase-by-Phase Agent Specifications

---

### Agent 1: speckit-overlay.orchestrator

**Model:** sonnet (complex coordination, state management, decision-making)
**Readonly:** false
**Tools Required:** File read/write, subagent invocation, logging

**Input:**
```typescript
{
  projectDescription: string,      // Required: what to build
  techStack?: string,              // Optional: tech preferences
  principles?: string,             // Optional: custom principles
  skipClarify?: boolean,           // Optional: default false
  skipAnalyze?: boolean,           // Optional: default false
  resumeFromPhase?: number         // Optional: 1-7, for retry scenarios
}
```

**Output:**
```typescript
{
  status: "success" | "failed",
  completedPhases: number[],       // E.g., [1, 2, 3, 4, 5, 6, 7]
  failedPhase?: number,
  featureId: string,               // E.g., "001-user-auth"
  artifactPaths: {
    constitution: string,
    spec: string,
    plan: string,
    tasks: string,
    implementation: string[]
  },
  executionLog: string             // Path to speckit-execution-log.md
}
```

**Behavior:**

#### 1. Parse Input & Initialize

- Validate `projectDescription` is non-empty
- Generate feature short-name from description (2-4 words, kebab-case)
- Scan `.specify/specs/` to determine next feature number (001, 002, etc.)
- Create feature ID: `{number}-{short-name}` (e.g., `001-user-auth`)
- Initialize execution log file: `speckit-execution-log.md`

#### 2. Pre-Flight Checks

- Verify `.specify/` directory exists
- Verify SpecKit commands available (check for SpecKit templates)
- Verify project is Git-initialized (SpecKit requirement)
- If checks fail: Report error, halt workflow

#### 3. Phase Execution Loop

For each phase (1-7):

**a. Check Skip Conditions**
- Phase 3 (Clarify): Skip if `skipClarify === true`
- Phase 6 (Analyze): Skip if `skipAnalyze === true`

**b. Invoke Phase Agent**
```javascript
const result = await invokeSubagent({
  agent: `speckit-overlay.{phase-name}`,
  context: {
    featureId: featureId,
    projectDescription: projectDescription,
    techStack: techStack,           // Phase 4 only
    principles: principles,         // Phase 1 only
    previousOutputs: {...}          // Context from prior phases
  }
})
```

**c. Retry Logic**
```javascript
let attempts = 0;
const maxAttempts = 3;
let success = false;

while (attempts < maxAttempts && !success) {
  attempts++;
  try {
    result = await invokePhaseAgent();
    success = validateOutput(result);
  } catch (error) {
    logError(phase, attempts, error);
    if (attempts < maxAttempts) {
      await sleep(5000); // 5 second delay
    }
  }
}

if (!success) {
  logFailure(phase, attempts);
  haltWorkflow();
}
```

**d. Log Phase Completion**
```markdown
✅ Phase {N}: {PhaseName} - COMPLETE
   
   Command: /speckit.{command}
   Duration: {seconds}s
   Attempts: {attempts}/3
   Output: {file_path}
   
   Key Details:
   - {detail_1}
   - {detail_2}
```

**e. Pass Context to Next Phase**
- Accumulate outputs in `previousOutputs` object
- Pass to next phase agent

#### 4. Generate Final Report

After all phases complete:

```markdown
# SpecKit Overlay Execution Report

**Feature:** {projectDescription}
**Feature ID:** {featureId}
**Timestamp:** {ISO_timestamp}
**Status:** {SUCCESS | FAILED}

## Phases Completed

- ✅ Phase 1: Constitution
- ✅ Phase 2: Specification
- ✅ Phase 3: Clarification  (skipped)
- ✅ Phase 4: Planning
- ✅ Phase 5: Task Generation
- ✅ Phase 6: Analysis
- ✅ Phase 7: Implementation

## Artifacts Generated

- Constitution: `.specify/memory/constitution.md`
- Specification: `.specify/specs/{featureId}/spec.md`
- Plan: `.specify/specs/{featureId}/plan.md`
- Tasks: `.specify/specs/{featureId}/tasks.md`
- Implementation: [list of files created]

## Execution Timeline

| Phase | Duration | Attempts | Status |
|-------|----------|----------|--------|
| 1 | 12s | 1 | ✅ |
| 2 | 45s | 1 | ✅ |
| ... | ... | ... | ... |

## Total Duration

{total_seconds}s ({minutes}m {seconds}s)

## Notes

{any_warnings_or_important_observations}
```

Write report to `speckit-execution-log.md` in project root.

#### 5. Error Handling

**Phase Failure After Max Retries:**
- Log detailed failure info (phase, attempts, errors)
- Report to user: "❌ Phase {N} failed after 3 attempts. See speckit-execution-log.md"
- Do NOT proceed to next phase
- Exit with failure status

**Invalid Input:**
- Report specific validation error
- Do NOT start workflow
- Provide example of correct input format

---

### Agent 2: speckit-overlay.constitution

**Model:** fast (simple command wrapper, minimal reasoning)
**Readonly:** false
**Tools Required:** Command execution, file validation

**SpecKit Command:** `/speckit.constitution`

**Input:**
```typescript
{
  featureId: string,
  projectDescription: string,
  principles?: string              // Optional custom principles
}
```

**Output:**
```typescript
{
  success: boolean,
  constitutionPath: string,        // .specify/memory/constitution.md
  sections: string[],              // List of section titles found
  errorMessage?: string
}
```

**Behavior:**

1. **Build Command Prompt**
   
   If `principles` provided:
   ```
   /speckit.constitution Create principles focused on: {principles}
   ```
   
   If `principles` NOT provided (generate defaults):
   ```
   /speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements. Include governance for how these principles should guide technical decisions and implementation choices.
   ```

2. **Execute SpecKit Command**
   
   ```javascript
   // Attempt 1: Direct command invocation
   try {
     await run_vscode_command({
       command: "workbench.action.chat.submit",
       args: { prompt: commandPrompt }
     });
   } catch (error) {
     // Fallback: Simulate chat submission
     // (implementation depends on Cursor API availability)
   }
   ```

3. **Wait for Completion**
   
   - Poll for `.specify/memory/constitution.md` file creation
   - Max wait time: 60 seconds
   - Poll interval: 2 seconds

4. **Validate Output**
   
   Read `.specify/memory/constitution.md` and verify:
   - File is non-empty (> 100 characters)
   - Contains required sections:
     - "Core Principles" or "Principles"
     - "Technology Constraints" or "Tech Stack"
     - "Quality Standards" or "Quality"
   - Sections have actual content (not just headings)

5. **Return Result**
   
   If validation passes:
   ```typescript
   {
     success: true,
     constitutionPath: ".specify/memory/constitution.md",
     sections: ["Core Principles", "Technology Constraints", "Quality Standards", ...]
   }
   ```
   
   If validation fails or timeout:
   ```typescript
   {
     success: false,
     constitutionPath: "",
     sections: [],
     errorMessage: "Constitution file not created after 60 seconds"
   }
   ```

**Error Handling:**
- Command execution fails: Return `success: false` with error details
- File not created: Return `success: false` with "timeout" error
- Invalid content: Return `success: false` with "validation failed" error
- Orchestrator handles retries based on `success` flag

---

### Agent 3: speckit-overlay.specify

**Model:** sonnet (needs to understand and validate complex specifications)
**Readonly:** false
**Tools Required:** Command execution, file validation, semantic analysis

**SpecKit Command:** `/speckit.specify`

**Input:**
```typescript
{
  featureId: string,
  projectDescription: string,
  constitutionPath: string         // From Phase 1
}
```

**Output:**
```typescript
{
  success: boolean,
  specPath: string,                // .specify/specs/{featureId}/spec.md
  userStoryCount: number,
  sectionsFound: string[],
  errorMessage?: string
}
```

**Behavior:**

1. **Build Command Prompt**
   
   ```
   /speckit.specify {projectDescription}
   ```

2. **Execute SpecKit Command**
   
   (Same method as constitution agent: direct command or chat simulation)

3. **Wait for Completion**
   
   - Poll for `.specify/specs/{featureId}/spec.md` file creation
   - Max wait time: 120 seconds (specs take longer)
   - Poll interval: 3 seconds

4. **Validate Output**
   
   Read `.specify/specs/{featureId}/spec.md` and verify:
   - File is non-empty (> 500 characters)
   - Contains required sections:
     - "User Stories" or "Stories"
     - "Functional Requirements" or "Requirements"
     - "Acceptance Criteria" or "Acceptance"
   - Has at least 1 user story (starts with "As a" or similar pattern)
   - User stories have acceptance criteria

5. **Extract Metrics**
   
   - Count user stories (look for "As a", "US1:", "Story 1:", etc.)
   - List all section headings
   - Note any warnings or quality issues

6. **Return Result**
   
   Success:
   ```typescript
   {
     success: true,
     specPath: ".specify/specs/001-user-auth/spec.md",
     userStoryCount: 5,
     sectionsFound: ["User Stories", "Functional Requirements", "Non-Functional Requirements", "Acceptance Criteria"]
   }
   ```

**Error Handling:**
- Same pattern as constitution agent
- Validation failure includes specific missing elements

---

### Agent 4: speckit-overlay.clarify

**Model:** sonnet (needs to understand clarification context and validate improvements)
**Readonly:** false
**Tools Required:** Command execution, file comparison

**SpecKit Command:** `/speckit.clarify`

**Input:**
```typescript
{
  featureId: string,
  specPath: string,                // From Phase 2
  constitutionPath: string
}
```

**Output:**
```typescript
{
  success: boolean,
  clarificationsAdded: boolean,
  clarificationCount: number,
  errorMessage?: string
}
```

**Behavior:**

1. **Build Command Prompt**
   
   ```
   /speckit.clarify
   ```
   
   (No arguments - operates on current spec in context)

2. **Capture Baseline**
   
   - Read current contents of `specPath` before command execution
   - Store for comparison

3. **Execute SpecKit Command**
   
   (Same execution method as prior agents)

4. **Wait for Completion**
   
   - Poll for changes to spec file (modification time change)
   - Max wait time: 90 seconds
   - Poll interval: 3 seconds

5. **Validate Output**
   
   - Read updated spec file
   - Check for new section: "Clarifications" or "Clarified Requirements"
   - Count clarification items (typically bullet points or numbered lists)
   - Verify existing sections still intact

6. **Return Result**
   
   Success (clarifications added):
   ```typescript
   {
     success: true,
     clarificationsAdded: true,
     clarificationCount: 7
   }
   ```
   
   Success (no clarifications needed):
   ```typescript
   {
     success: true,
     clarificationsAdded: false,
     clarificationCount: 0
   }
   ```

**Error Handling:**
- If spec file unchanged after command: Still return success (means spec was clear)
- If spec file corrupted: Return failure

---

### Agent 5: speckit-overlay.plan

**Model:** sonnet (needs to understand technical architecture)
**Readonly:** false
**Tools Required:** Command execution, file validation

**SpecKit Command:** `/speckit.plan`

**Input:**
```typescript
{
  featureId: string,
  specPath: string,
  techStack?: string,
  constitutionPath: string
}
```

**Output:**
```typescript
{
  success: boolean,
  planPath: string,                // .specify/specs/{featureId}/plan.md
  sectionsFound: string[],
  fileStructureDefined: boolean,
  errorMessage?: string
}
```

**Behavior:**

1. **Build Command Prompt**
   
   If `techStack` provided:
   ```
   /speckit.plan {techStack}
   ```
   
   Example:
   ```
   /speckit.plan The application uses .NET Aspire with PostgreSQL database. Frontend uses Blazor Server with real-time SignalR updates. REST API with minimal dependencies.
   ```
   
   If `techStack` NOT provided:
   ```
   /speckit.plan Use modern, maintainable technologies appropriate for this feature. Prefer simplicity and standard patterns.
   ```

2. **Execute SpecKit Command**
   
   (Same method as prior agents)

3. **Wait for Completion**
   
   - Poll for `.specify/specs/{featureId}/plan.md` creation
   - Max wait time: 180 seconds (planning takes longest)
   - Poll interval: 5 seconds

4. **Validate Output**
   
   Read plan file and verify:
   - File is non-empty (> 1000 characters)
   - Contains required sections:
     - "Implementation Plan" or "Plan"
     - "Technical Stack" or "Technology"
     - "File Structure" or "Architecture"
   - Has file/directory structure defined
   - Has component list or module breakdown
   - Has dependencies or libraries listed

5. **Extract Metrics**
   
   - List all sections
   - Check for file structure (code blocks or lists of files)
   - Note technology choices

6. **Return Result**
   
   Success:
   ```typescript
   {
     success: true,
     planPath: ".specify/specs/001-user-auth/plan.md",
     sectionsFound: ["Implementation Plan", "Technical Stack", "File Structure", "Dependencies"],
     fileStructureDefined: true
   }
   ```

**Error Handling:**
- Timeout: Return failure
- Missing critical sections: Return failure with specific gaps

---

### Agent 6: speckit-overlay.tasks

**Model:** fast (straightforward command wrapper)
**Readonly:** false
**Tools Required:** Command execution, file validation

**SpecKit Command:** `/speckit.tasks`

**Input:**
```typescript
{
  featureId: string,
  planPath: string                 // From Phase 4
}
```

**Output:**
```typescript
{
  success: boolean,
  tasksPath: string,               // .specify/specs/{featureId}/tasks.md
  taskCount: number,
  hasDependencies: boolean,
  errorMessage?: string
}
```

**Behavior:**

1. **Build Command Prompt**
   
   ```
   /speckit.tasks
   ```
   
   (No arguments - operates on current plan in context)

2. **Execute SpecKit Command**
   
   (Same method as prior agents)

3. **Wait for Completion**
   
   - Poll for `.specify/specs/{featureId}/tasks.md` creation
   - Max wait time: 90 seconds
   - Poll interval: 3 seconds

4. **Validate Output**
   
   Read tasks file and verify:
   - File is non-empty (> 300 characters)
   - Contains task list (numbered or checkboxes)
   - Each task has:
     - Task ID or number
     - Task description
     - File path or location
   - Optional: Dependency indicators (e.g., "Depends on Task 3")

5. **Extract Metrics**
   
   - Count tasks (lines starting with number, checkbox, or bullet)
   - Check for dependency markers
   - Check for parallel execution markers `[P]` if SpecKit uses them

6. **Return Result**
   
   Success:
   ```typescript
   {
     success: true,
     tasksPath: ".specify/specs/001-user-auth/tasks.md",
     taskCount: 23,
     hasDependencies: true
   }
   ```

**Error Handling:**
- Empty task list: Return failure (invalid output)
- Format errors: Return failure with description

---

### Agent 7: speckit-overlay.analyze

**Model:** fast (read-only analysis)
**Readonly:** true
**Tools Required:** Command execution, output interpretation

**SpecKit Command:** `/speckit.analyze`

**Input:**
```typescript
{
  featureId: string,
  specPath: string,
  planPath: string,
  tasksPath: string
}
```

**Output:**
```typescript
{
  success: boolean,
  analysisPass: boolean,           // Did analysis find issues?
  issuesFound: string[],           // List of consistency issues
  errorMessage?: string
}
```

**Behavior:**

1. **Build Command Prompt**
   
   ```
   /speckit.analyze
   ```
   
   (No arguments - analyzes current spec/plan/tasks in context)

2. **Execute SpecKit Command**
   
   (Same method as prior agents)

3. **Wait for Completion**
   
   - Wait for command output (may not create file, just report)
   - Max wait time: 60 seconds
   - Capture output text from SpecKit response

4. **Parse Analysis Output**
   
   SpecKit's `/speckit.analyze` typically outputs:
   - ✅ Consistency checks passed
   - ❌ Issues found: [list]
   
   Parse output for:
   - Pass/fail status
   - List of issues (gaps, inconsistencies, scope creep)

5. **Validate Output**
   
   - Check if analysis completed (got output)
   - Determine pass/fail from output

6. **Return Result**
   
   Success (analysis pass):
   ```typescript
   {
     success: true,
     analysisPass: true,
     issuesFound: []
   }
   ```
   
   Success (issues found but analysis completed):
   ```typescript
   {
     success: true,
     analysisPass: false,
     issuesFound: [
       "Spec mentions 'user profile' but tasks don't implement it",
       "Plan specifies Redis but tasks don't configure it"
     ]
   }
   ```

**Error Handling:**
- Command fails: Return `success: false`
- Orchestrator decision: Even if `analysisPass: false`, may proceed (soft gate)
- Critical issues: Orchestrator may halt workflow

---

### Agent 8: speckit-overlay.implement

**Model:** sonnet (needs to monitor complex implementation process)
**Readonly:** false
**Tools Required:** Command execution, test validation, file change tracking

**SpecKit Command:** `/speckit.implement`

**Input:**
```typescript
{
  featureId: string,
  specPath: string,
  planPath: string,
  tasksPath: string
}
```

**Output:**
```typescript
{
  success: boolean,
  filesCreated: string[],
  filesModified: string[],
  testsPass: boolean,
  implementationDuration: number,  // seconds
  errorMessage?: string
}
```

**Behavior:**

1. **Capture Baseline**
   
   - List all files in workspace (snapshot)
   - Note Git status (dirty files)
   - Prepare for change tracking

2. **Build Command Prompt**
   
   ```
   /speckit.implement
   ```
   
   (No arguments - implements current tasks)

3. **Execute SpecKit Command**
   
   (Same method as prior agents)

4. **Monitor Implementation**
   
   - Implementation can take minutes to hours
   - No fixed timeout (use progress indicators)
   - Monitor for SpecKit completion signals:
     - "Implementation complete" message
     - Command exits
     - No file changes for 30 seconds

5. **Detect Completion**
   
   SpecKit may signal completion via:
   - Chat message: "✅ Implementation complete"
   - Command finishes executing
   - Writes completion marker file
   
   Once detected:
   - Compare workspace files to baseline
   - Track created files
   - Track modified files

6. **Validate Output**
   
   **a. File Changes**
   - Verify files were created/modified
   - Verify file paths match tasks.md expectations
   
   **b. Build Validation (if applicable)**
   - Run build command (`npm run build`, `dotnet build`, etc.)
   - Check exit code
   
   **c. Test Validation (if tests exist)**
   - Run test command (`npm test`, `dotnet test`, etc.)
   - Check exit code
   - Parse test output for pass/fail count
   
   **d. Quality Checks**
   - No uncommitted `.env` files with secrets
   - No obvious syntax errors in created files

7. **Return Result**
   
   Success:
   ```typescript
   {
     success: true,
     filesCreated: ["src/auth/AuthService.cs", "src/auth/IAuthService.cs", ...],
     filesModified: ["src/Program.cs", "src/appsettings.json", ...],
     testsPass: true,
     implementationDuration: 342
   }
   ```

**Error Handling:**
- Build fails: Return `success: false` with build errors
- Tests fail: Return `success: false` with test failures
- No files changed: Return `success: false` (implementation didn't work)
- Timeout (> 1 hour): Return `success: false` with timeout error

---

## Context Passing Strategy

### Orchestrator State Object

The orchestrator maintains a cumulative state object passed to each phase:

```typescript
interface WorkflowState {
  featureId: string;
  projectDescription: string;
  techStack?: string;
  principles?: string;
  
  phase1?: {
    constitutionPath: string;
    sections: string[];
  };
  
  phase2?: {
    specPath: string;
    userStoryCount: number;
  };
  
  phase3?: {
    clarificationsAdded: boolean;
    clarificationCount: number;
  };
  
  phase4?: {
    planPath: string;
    fileStructureDefined: boolean;
  };
  
  phase5?: {
    tasksPath: string;
    taskCount: number;
  };
  
  phase6?: {
    analysisPass: boolean;
    issuesFound: string[];
  };
  
  phase7?: {
    filesCreated: string[];
    testsPass: boolean;
  };
}
```

Each phase agent receives relevant subset of state and returns its results to update state.

## Validation Schema

### Constitution Validation
- File exists: `.specify/memory/constitution.md`
- Min size: 100 characters
- Required sections: Core Principles, Technology Constraints, Quality Standards

### Spec Validation
- File exists: `.specify/specs/{featureId}/spec.md`
- Min size: 500 characters
- Required sections: User Stories, Functional Requirements, Acceptance Criteria
- Min user stories: 1

### Plan Validation
- File exists: `.specify/specs/{featureId}/plan.md`
- Min size: 1000 characters
- Required sections: Implementation Plan, Technical Stack, File Structure
- Has file structure defined: Yes

### Tasks Validation
- File exists: `.specify/specs/{featureId}/tasks.md`
- Min size: 300 characters
- Min tasks: 3

### Implementation Validation
- Files created: > 0
- Build passes: Yes (if applicable)
- Tests pass: Yes (if tests exist)

## Execution Log Format

The `speckit-execution-log.md` file contains:

```markdown
# SpecKit Overlay Execution Log

Generated: {ISO_timestamp}
Feature: {projectDescription}
Feature ID: {featureId}

---

## Phase 1: Constitution

**Command:** `/speckit.constitution Create principles...`
**Started:** {timestamp}
**Duration:** 12s
**Attempts:** 1
**Status:** ✅ SUCCESS

**Output:**
- File: `.specify/memory/constitution.md`
- Sections: Core Principles, Technology Constraints, Quality Standards, Testing Standards

**Validation:**
✅ File created
✅ Min size met (482 characters)
✅ All required sections present

---

## Phase 2: Specification

**Command:** `/speckit.specify {description}`
**Started:** {timestamp}
**Duration:** 45s
**Attempts:** 1
**Status:** ✅ SUCCESS

**Output:**
- File: `.specify/specs/001-user-auth/spec.md`
- User Stories: 5
- Sections: User Stories, Functional Requirements, Non-Functional Requirements, Acceptance Criteria

**Validation:**
✅ File created
✅ Min size met (1842 characters)
✅ All required sections present
✅ User stories found (5)

---

[... continue for all phases ...]

---

## Summary

**Total Duration:** 8m 23s
**Phases Completed:** 7/7
**Files Created:** 23
**Files Modified:** 5
**Tests Pass:** ✅ Yes
**Overall Status:** ✅ SUCCESS
```

## Error Recovery Strategies

### Phase Fails After Retry 1
- Log error details
- Wait 5 seconds
- Retry with identical parameters

### Phase Fails After Retry 2
- Log error details
- Wait 5 seconds
- Retry with identical parameters

### Phase Fails After Retry 3
- Log failure
- Write execution log with failure details
- Report to user: "Workflow failed at Phase {N}. See speckit-execution-log.md"
- Exit with error code

### Orchestrator Crash
- Execution log written to disk after each phase
- User can resume from last successful phase using `resumeFromPhase` parameter
- Orchestrator reads log, skips completed phases

## Testing Strategy

### Unit Testing Each Agent
- Mock SpecKit command execution
- Test input validation
- Test output validation
- Test timeout handling
- Test retry logic

### Integration Testing Orchestrator
- Use test project with SpecKit installed
- Run full workflow end-to-end
- Verify all files created
- Verify execution log accuracy
- Test failure scenarios (induce command failures)

### Manual Testing
- Run on real projects
- Verify actual SpecKit commands execute
- Verify output quality matches manual SpecKit usage
- Compare overlay results vs manual SpecKit workflow

## Deployment

### Agent Files Location
All agents stored in `.cursor/agents/` directory:
- `speckit-overlay.orchestrator.md`
- `speckit-overlay.constitution.md`
- `speckit-overlay.specify.md`
- `speckit-overlay.clarify.md`
- `speckit-overlay.plan.md`
- `speckit-overlay.tasks.md`
- `speckit-overlay.analyze.md`
- `speckit-overlay.implement.md`

### Usage

**Trigger orchestrator:**
```
@speckit-overlay.orchestrator Build a user authentication system with email/password login, password reset, and session management.
```

**With tech stack:**
```
@speckit-overlay.orchestrator Build a todo app with categories and priorities.

Tech stack: React, Node.js, PostgreSQL, Tailwind CSS
```

**Skip optional steps:**
```
@speckit-overlay.orchestrator Build a blog CMS.

Tech stack: Python Flask, SQLite
Skip: clarify, analyze
```

## Success Metrics

### Workflow Success Rate
- Target: > 90% of workflows complete all 7 phases
- Measure: Completed phases / Total phases across all runs

### Retry Rate
- Target: < 10% of phases require retries
- Measure: Retry attempts / Total phase executions

### Time to Implementation
- Target: < 10 minutes for simple features
- Measure: Execution log total duration

### Output Quality
- Target: 100% of implementations pass tests (if tests defined)
- Measure: Test pass rate from phase 7 results
