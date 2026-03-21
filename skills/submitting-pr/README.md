# submitting-pr

An AI agent skill that automates the full GitHub Pull Request submission workflow — from safety checks through squash, push, and PR creation — in a single conversational step.

## What It Does

1. Checks that you are on a feature branch and detects uncommitted changes
2. Commits any uncommitted work using a [Commitizen](https://www.conventionalcommits.org/)-formatted message
3. Resolves the upstream base branch automatically
4. Collects the full commit log to use as the PR body
5. Squashes all branch commits into one clean Commitizen-formatted commit
6. Pushes the branch (with `--force-with-lease` when needed after a squash)
7. Opens a PR via the `gh` CLI and returns the PR URL

## When to Use

Invoke this skill when you want to submit work on a feature branch as a GitHub Pull Request. It handles the entire flow regardless of whether your working tree is clean or has pending changes.

## How to Invoke

Say any of the following to your AI agent:

- "Submit a PR"
- "Create a pull request"
- "Open a PR for this branch"
- "Submit a pull request"

The agent will guide you through each step interactively, prompting only when input is needed (commit message, squash message confirmation).

## Examples

**Clean branch, ready to submit:**
```
You:   Create a PR
Agent: Your branch has 3 commits ahead of main.
       Suggested squash message: "feat: add user profile page"
       Confirm or modify? [confirm]
       → PR created: https://github.com/org/repo/pull/42
```

**Uncommitted changes:**
```
You:   Submit a PR
Agent: You have uncommitted changes. Choose a commit type:
       feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
       Description? add input validation to login form
       → Committing as: fix: add input validation to login form
       → Squashing, pushing, and opening PR...
       → PR created: https://github.com/org/repo/pull/17
```

**On main by mistake:**
```
You:   Open a pull request
Agent: You are on the main branch. Please switch to a feature branch first.
```

## Requirements

| Dependency | Install |
|---|---|
| `git` | [git-scm.com](https://git-scm.com) |
| `gh` CLI | `winget install GitHub.cli` (Windows) · `brew install gh` (macOS) |

## Commit Message Convention

All commit and squash messages must follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

feat(auth): add OAuth2 login
fix: handle null response from payment API
docs: update README with setup instructions
```

Valid types: `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` `revert`

See [`references/commitizen-types.md`](references/commitizen-types.md) for the full reference.

## Cross-Platform Support

Scripts are available for both POSIX and Windows environments:

| Environment | Scripts |
|---|---|
| Linux / macOS / Git Bash / WSL | `scripts/shell/*.sh` |
| Windows cmd or PowerShell (native) | `scripts/bat/*.bat` |


## How-to Get This Skill 

For **Cursor**:

```bash
uvx --from git+https://itadoprd01.panagora.com/Research/training/_git/ai-agent-skills add-skills submitting-pr --output .cursor/skills
```

For **Claude**:

```bash
uvx --from git+https://itadoprd01.panagora.com/Research/training/_git/ai-agent-skills add-skills submitting-pr --output .claude/skills
```