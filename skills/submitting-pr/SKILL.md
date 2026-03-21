---
name: submitting-pr
description: Create and submit a Pull Request from the current branch. Supports GitHub (gh CLI), Azure DevOps Services (az repos), and Azure DevOps Server on-premises (REST API). Handles uncommitted changes, squashes all branch commits into one, then opens a PR with full commit details. Use when the user asks to "submit a PR", "create a PR", "open a pull request", "submit a pull request", or "create a pull request".
---

# Submit PR

## Workflow

**Detect script directory** — determine once, use throughout all steps:

| Shell environment | Script directory | Extension |
|---|---|---|
| Linux / macOS / Git Bash / WSL | `scripts/shell/` | `.sh` |
| Windows cmd or PowerShell (native) | `scripts/bat/` | `.bat` |

Progress checklist:

- [ ] Step 1 — Safety checks
- [ ] Step 2 — Commit uncommitted work *(skip if working tree is clean)*
- [ ] Step 3 — Identify base branch
- [ ] Step 4 — Collect commit details
- [ ] Step 5 — Squash commits *(skip if only one commit)*
- [ ] Step 6 — Push branch
- [ ] Step 7 — Create PR

For every script invocation below, prepend the detected script directory and extension — e.g. `scripts/shell/02-commit.sh` or `scripts/bat/02-commit.bat`.

Follow these steps in order:

### Step 1 — Safety checks

Run `01-safety-checks` from the detected script directory.

- If the script exits with an error (protected branch): relay the error to the user and stop.
- If `working-tree` is `dirty`: go to **Step 2**.
- If `working-tree` is `clean`: skip to **Step 3**.

### Step 2 — Commit uncommitted work

Ask the user for a commit message in Commitizen format (see [references/commitizen-types.md](references/commitizen-types.md)):

- Present the type list and prompt: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- Format: `<type>[optional scope]: <description>` — e.g. `feat(auth): add OAuth2 login`

> **Note:** `git add -A` stages all untracked files. If the project may contain sensitive files (`.env`, secrets, build artifacts) not covered by `.gitignore`, warn the user before proceeding.

Then run:

```
02-commit "<type>[scope]: <description>"
```

The script will reject messages that do not match the format. If rejected, re-prompt the user to correct the message and retry.

### Step 3 — Identify the base branch

Run `03-get-base-branch` from the detected script directory.

Store the printed value as `BASE_BRANCH` (defaults to `main` if the remote is unreachable).

### Step 4 — Collect all commit details

```
04-collect-commits <BASE_BRANCH>
```

Save the full output — it becomes the PR body.

### Step 5 — Squash all branch commits into one

Based on the commits collected in Step 4, infer the Commitizen type using the priority rule in [references/commitizen-types.md](references/commitizen-types.md) and suggest a squash message. Prompt the user to confirm or modify, then run:

```
05-squash <BASE_BRANCH> "<type>[scope]: <summary>"
```

The script is a no-op when only one commit exists ahead of the base. It will reject messages that do not match the Commitizen format. If rejected, re-prompt the user to correct the message and retry.

### Step 6 — Push the branch

```
06-push
```

If the push is rejected due to diverged history (force needed after squash):

```
06-push --force
```

### Step 7 — Create the PR

Use the final commit subject as the PR title — from the squash message confirmed in Step 5, or from the single commit in Step 4 if squash was skipped. Use the full commit log collected in Step 4 as the PR body:

```
07-create-pr <BASE_BRANCH> "<final commit subject>" "<PR body>"
```

Return the PR URL to the user when done.

## Rules

- Never commit with `--no-verify` unless the user explicitly asks.
- Never force-push to `main` or `master`.
- Always use `--force-with-lease` (not `--force`) when a force push is needed.
<<<<<<< HEAD
- The `07-create-pr` script auto-detects the hosting platform from the remote URL — no manual configuration needed.
- If a PR already exists for the branch, the script will print the existing PR list URL. Show it to the user.
- If there are no uncommitted changes, skip Step 2. The script in Step 5 handles the single-commit no-op automatically.

## Platform detection (handled by `07-create-pr`)

| Remote URL pattern | Tool used |
|---|---|
| `github.com` | `gh pr create` (install: `winget install GitHub.cli`) |
| `dev.azure.com` / `*.visualstudio.com` | `az repos pr create` (azure-devops extension) |
| Any other host (on-premises ADO Server) | REST API via PowerShell `Invoke-RestMethod -UseDefaultCredentials` |
=======
- If `gh` CLI is not installed, tell the user to install it (`winget install GitHub.cli` on Windows, `brew install gh` on macOS).
- If `gh pr create` fails because a PR already exists for the branch, show the user the existing PR with `gh pr view --web`.
- If there are no uncommitted changes, skip Step 2. The script in Step 5 handles the single-commit no-op automatically.
>>>>>>> master
