# SpecKit Overlay Workflow

An agentic workflow system that automates the entire [GitHub SpecKit](https://github.com/github/spec-kit) spec-driven development process from initial concept to full implementation.

## Overview

SpecKit Overlay wraps the 7-step SpecKit workflow with intelligent Cursor agents that programmatically invoke SpecKit commands, validate outputs, handle errors, and automatically progress through all phases without human review.

**SpecKit Steps Automated:**
1. `/speckit.constitution` → Project principles and constraints
2. `/speckit.specify` → Detailed specification with user stories
3. `/speckit.clarify` → Requirement refinement and gap filling
4. `/speckit.plan` → Technical implementation plan
5. `/speckit.tasks` → Dependency-ordered task breakdown
6. `/speckit.analyze` → Cross-artifact consistency validation
7. `/speckit.implement` → Full code implementation with testing

## Quick Start

### Prerequisites

1. **SpecKit Initialized:**
   ```bash
   # Initialize SpecKit in your project
   npx @github/spec-kit init
   ```

2. **Git Repository:**
   ```bash
   # Ensure project is a git repository
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Build System (Optional):**
   - Node.js: `package.json` present
   - .NET: `*.csproj` present
   - Java: `pom.xml` or `build.gradle` present
   - Python: `requirements.txt` present

### Usage

Invoke the orchestrator agent from Cursor with your feature description:

```
@speckit-overlay.orchestrator Please implement a user authentication system with email/password login, JWT tokens, and password reset functionality.
```

The orchestrator will:
- ✅ Generate project constitution
- ✅ Create detailed specification
- ✅ Clarify ambiguities
- ✅ Build implementation plan
- ✅ Break down into tasks
- ✅ Validate consistency
- ✅ Execute full implementation
- ✅ Run tests and verify build

All outputs saved to `.specify/specs/<feature-id>/`

## Architecture

### Agent System

The workflow consists of 8 specialized agents:

| Agent | Role | Model |
|-------|------|-------|
| `speckit-overlay.orchestrator` | Coordinates full 7-phase workflow | Sonnet |
| `speckit-overlay.constitution` | Wraps `/speckit.constitution` | Fast |
| `speckit-overlay.specify` | Wraps `/speckit.specify` | Fast |
| `speckit-overlay.clarify` | Wraps `/speckit.clarify` | Fast |
| `speckit-overlay.plan` | Wraps `/speckit.plan` | Fast |
| `speckit-overlay.tasks` | Wraps `/speckit.tasks` | Fast |
| `speckit-overlay.analyze` | Wraps `/speckit.analyze` | Fast |
| `speckit-overlay.implement` | Wraps `/speckit.implement` | Sonnet |

### Execution Flow

```
User Input
    ↓
Orchestrator
    ↓
Phase 1: Constitution → constitution.md
    ↓
Phase 2: Specify → spec.md
    ↓
Phase 3: Clarify → spec.md (updated)
    ↓
Phase 4: Plan → plan.md
    ↓
Phase 5: Tasks → tasks.md
    ↓
Phase 6: Analyze → validation report
    ↓
Phase 7: Implement → source files + tests
    ↓
Execution Report → speckit-execution-log.md
```

### Retry Logic

Each phase includes automatic retry on failure:
- Max 3 attempts per phase
- 5-second delay between retries
- Failures halt workflow and report error
- Tracks attempt count in execution log

### Validation

Every phase validates its output:

| Phase | Validation Criteria |
|-------|---------------------|
| Constitution | File exists, >100 chars, 3/4 required sections |
| Specify | File exists, >500 chars, user story count ≥ 3 |
| Clarify | Modifications detected OR spec unchanged (both valid) |
| Plan | File exists, >1000 chars, file structure present, tech stack mentioned |
| Tasks | File exists, >300 chars, task count ≥ 3 |
| Analyze | Command output captured, issues parsed |
| Implement | Files created/modified, build passes, tests pass |

## File Structure

After successful execution:

```
.specify/
  specs/
    <feature-id>/          # e.g., 001-user-auth
      constitution.md      # Project principles
      spec.md              # Requirements specification
      plan.md              # Implementation plan
      tasks.md             # Task breakdown
      analysis-report.md   # Consistency analysis (optional)
speckit-execution-log.md   # Full execution log
```

## Examples

### Example 1: REST API Feature

```
@speckit-overlay.orchestrator Build a REST API for managing blog posts with CRUD operations, pagination, and search by tags.
```

**Output:**
- Constitution with RESTful principles
- Spec with 8 user stories (create post, update post, delete post, etc.)
- Plan with Express.js + MongoDB tech stack
- 23 tasks including controllers, models, routes, tests
- Implementation with all files created
- Tests passing (15/15)
- Duration: ~6 minutes

### Example 2: With Custom Constitution

```
@speckit-overlay.orchestrator Implement real-time chat with websockets. Use custom constitution from ./docs/principles.md
```

**Output:**
- Uses provided constitution instead of generating one
- Spec with websocket connection, message broadcast, user presence
- Plan with Socket.IO architecture
- Implementation with real-time event handling
- Duration: ~8 minutes

### Example 3: With Tech Stack Specified

```
@speckit-overlay.orchestrator Create a file upload service with virus scanning. Use Python FastAPI and ClamAV.
```

**Output:**
- Constitution with security-first principles
- Spec with upload, scan, quarantine user stories
- Plan explicitly using FastAPI + ClamAV
- Tasks including async upload, virus scan integration, storage
- Implementation with Python code and pytest tests
- Duration: ~10 minutes

## Execution Log

The workflow generates a detailed execution log at `speckit-execution-log.md`:

```markdown
# SpecKit Execution Log - 001-user-auth

**Status:** ✅ SUCCESS
**Total Duration:** 342 seconds

## Phase Summary
- Phase 1 (Constitution): ✅ SUCCESS (12s)
- Phase 2 (Specify): ✅ SUCCESS (18s)
- Phase 3 (Clarify): ⏭️ SKIPPED
- Phase 4 (Plan): ✅ SUCCESS (25s)
- Phase 5 (Tasks): ✅ SUCCESS (15s)
- Phase 6 (Analyze): ✅ SUCCESS (8s)
- Phase 7 (Implement): ✅ SUCCESS (264s)

## Detailed Logs
[Phase-by-phase execution details...]
```

## Troubleshooting

### SpecKit Not Initialized

**Error:** `SpecKit not initialized in this workspace`

**Solution:**
```bash
npx @github/spec-kit init
```

### Git Not Initialized

**Error:** `Git repository not initialized`

**Solution:**
```bash
git init
git add .
git commit -m "Initial commit"
```

### Build Failures

If implementation phase fails with build errors:

1. Check build tool is installed (`npm`, `dotnet`, etc.)
2. Verify dependencies are installed
3. Review generated code in `.specify/specs/<feature-id>/`
4. Check execution log for specific build errors

**Manual Fix:**
```bash
# Fix issues in generated code
# Then re-run just the implementation phase:
@speckit-overlay.implement
```

### Test Failures

If tests fail after implementation:

1. Review test output in execution log
2. Check generated test files
3. Verify test framework is configured

**Options:**
- Fix tests manually and commit
- Re-run implementation with clarified requirements
- Skip test validation (not recommended)

### Timeout Issues

If implementation times out (>2 hours):

**Causes:**
- Very large feature scope
- Complex implementation
- Resource constraints

**Solutions:**
- Break feature into smaller sub-features
- Increase timeout in `speckit-overlay.implement.md`
- Monitor implementation progress manually

### Clarification Phase Skipped

This is **normal** if spec is already clear. The orchestrator skips clarification when:
- Spec has sufficient detail
- All user stories are well-defined
- No ambiguities detected

### Analysis Finds Issues

If Phase 6 (Analyze) finds inconsistencies:

**Behavior:** Orchestrator logs warnings but proceeds to implementation

**Issues Found Examples:**
- "Spec mentions user profile editing but tasks don't implement it"
- "Plan specifies Redis caching but spec has no caching requirements"

**Options:**
- Let implementation proceed (issues may be non-critical)
- Halt and fix manually (edit spec/plan/tasks)
- Re-run from earlier phase with corrections

## Advanced Configuration

### Custom Constitution

Provide your own project principles:

```
@speckit-overlay.orchestrator Implement feature X. Use constitution from ./docs/constitution.md
```

### Tech Stack Specification

Force specific technologies:

```
@speckit-overlay.orchestrator Build feature Y. Tech stack: React, Node.js, PostgreSQL, Redis.
```

### Skipping Phases

To skip clarification (if spec is already detailed):

1. Edit `speckit-overlay.orchestrator.md`
2. Set `shouldClarify: false` in Phase 3 logic
3. Comment out Phase 3 invocation

### Adjusting Timeouts

If commands need more time:

1. Edit individual agent files (e.g., `speckit-overlay.implement.md`)
2. Increase `maxWaitTime` in polling strategy
3. Increase timeout in command execution

## Best Practices

### Feature Sizing

**Optimal:** Single feature with 5-15 user stories
- Example: User authentication system
- Duration: 5-15 minutes

**Too Small:** 1-2 user stories
- Example: Add a button
- Overhead not justified

**Too Large:** >30 user stories
- Example: Complete e-commerce platform
- Risk of timeout, break into sub-features

### Input Quality

Provide clear, detailed feature descriptions:

✅ **Good:**
```
Implement a user authentication system with email/password login, JWT token 
generation, password hashing with bcrypt, refresh tokens, and password reset 
via email with expiring tokens.
```

❌ **Poor:**
```
Add login
```

### Tech Stack Alignment

Specify tech stack for consistency:

✅ **Good:**
```
Build REST API with Node.js, Express, MongoDB. Use JWT for auth.
```

❌ **Poor:**
```
Build REST API
```
(Orchestrator/SpecKit will choose tech stack, may not match existing project)

### Dependency Management

Ensure dependencies are installed before implementation:

```bash
# Node.js
npm install

# .NET
dotnet restore

# Python
pip install -r requirements.txt
```

### Version Control

Commit before running workflow:

```bash
git add .
git commit -m "Pre-feature: user auth"

# Run workflow

git add .
git commit -m "Feature: user authentication implemented via SpecKit"
```

## Limitations

1. **SpecKit Dependency:** Requires SpecKit to be installed and initialized
2. **Command Invocation:** Relies on VS Code command API (fallback to manual instructions)
3. **Single Feature:** Processes one feature at a time (no batch processing)
4. **Language Support:** Build/test validation supports common languages (Node.js, .NET, Java, Python, Rust)
5. **Manual Review:** No human review checkpoints (fully automated)

## Roadmap

Future enhancements:

- [ ] Multi-feature batch processing
- [ ] Parallel task execution (for independent tasks)
- [ ] Incremental implementation (checkpoint/resume)
- [ ] Integration with CI/CD pipelines
- [ ] Visual progress dashboard
- [ ] Interactive clarification mode (human-in-the-loop)
- [ ] Rollback capability (revert to checkpoint)
- [ ] Cost estimation (token usage, duration prediction)

## Contributing

To extend or customize this workflow:

1. **Add Validation Rules:** Edit agent files to add custom validation logic
2. **Support New Build Tools:** Update `detectBuildTool()` in `speckit-overlay.implement.md`
3. **Custom Phases:** Add new agent files and wire into orchestrator
4. **Alternative Execution Strategies:** Modify command invocation logic in agents

## Resources

- [GitHub SpecKit](https://github.com/github/spec-kit) - Original SpecKit framework
- [SPEC.md](./SPEC.md) - Detailed workflow specification
- [PLAN.md](./PLAN.md) - Multi-agent architecture plan

## License

This workflow system is licensed under the MIT License. See root LICENSE file for details.

---

**Built with:** Cursor Agents + GitHub SpecKit

**Last Updated:** 2025-01-13
