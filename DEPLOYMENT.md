# Deployment Guide

This document covers how to set up, release, and publish `@dtranllc/ai-workflow-kit` to [npmjs.com](https://www.npmjs.com).

---

## Overview

Releases are **fully automated** via [semantic-release](https://semantic-release.gitbook.io/semantic-release/) triggered by GitHub Actions. There is no manual `npm publish` step in normal operations.

```
Merge PR to master
      │
      ▼
GitHub Actions: release.yml
      │
      ├─ typecheck + build + test
      │
      ▼
semantic-release analyzes commits
      │
      ├─ No releasable commits → exits silently (no release)
      │
      └─ Releasable commits found:
           ├─ Bumps version in package.json
           ├─ Updates CHANGELOG.md
           ├─ Publishes to npmjs.com (with provenance)
           ├─ Creates GitHub Release with notes
           └─ Commits package.json + CHANGELOG.md back to master
```

---

## Prerequisites

### 1. npm Account and Package Scope

1. Create or log in to an account at [npmjs.com](https://www.npmjs.com)
2. The package is published under the `@dtranllc` scope — ensure you own or have access to this scope
3. Create an npm **Automation Token** (recommended over Classic for CI):
   - Go to npmjs.com → Account Settings → Access Tokens → Generate New Token → **Automation**
   - Copy the token — you will only see it once

### 2. GitHub Repository Secret: `NPM_TOKEN`

Store the npm token as a GitHub Actions secret:

1. Go to the GitHub repository → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `NPM_TOKEN`
4. Value: the npm Automation Token from step above
5. Click **Add secret**

> The `GITHUB_TOKEN` is automatically provided by GitHub Actions — no setup needed.

### 3. GitHub Actions Permissions

Ensure the repository allows Actions to write back to the repo (required for semantic-release's git commit):

1. Go to **Settings → Actions → General → Workflow permissions**
2. Select **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**

---

## First-Time Publish

If the package has never been published to npm (or you need to manually publish the initial version):

```bash
# 1. Ensure you're logged in to npm
npm whoami

# If not logged in:
npm login

# 2. Build the package
npm run build

# 3. Dry run — preview exactly what will be published
npm pack --dry-run

# 4. Publish (scoped public package requires --access public on first publish)
npm publish --access public

# 5. Verify it's live
npm view @dtranllc/ai-workflow-kit
```

After the initial publish, all subsequent releases are handled automatically by the GitHub Actions release workflow.

---

## How Releases Work

### Semver Bump Rules

semantic-release analyzes commit messages since the last release tag and determines the version bump:

| Commit type | Example | Version bump |
|-------------|---------|-------------|
| `feat:` | `feat: add --recursive flag` | **minor** (1.1.0 → 1.2.0) |
| `fix:` | `fix: handle missing output dir` | **patch** (1.1.0 → 1.1.1) |
| `perf:` | `perf: stream large files` | **patch** |
| `feat!:` / `BREAKING CHANGE:` | `feat!: rename binary` | **major** (1.1.0 → 2.0.0) |
| `docs:`, `chore:`, `ci:`, `test:`, `refactor:` | any | **no release** |

### Triggering a Release

Simply **merge a PR to `master`** that contains at least one releasable commit (`feat:`, `fix:`, `perf:`, or a breaking change). The release workflow fires automatically.

To preview what version would be released without publishing:

```bash
NPM_TOKEN=<your-token> npx semantic-release --dry-run
```

### What Gets Published to npm

The `"files"` field in `package.json` controls the published contents:

```
dist/         ← Compiled JS, declaration files, source maps
skills/       ← Bundled skill templates
commands/     ← Bundled command templates
workflows/    ← Bundled workflow templates
README.md
CHANGELOG.md
LICENSE
```

Verify before a release:

```bash
npm pack --dry-run
```

---

## CI/CD Workflows

### `.github/workflows/ci.yml` — Quality Gate

Runs on **every push and pull request**:

| Step | Command |
|------|---------|
| Type check | `npm run typecheck` |
| Build | `npm run build` |
| Lint | `npm run lint` |
| Format check | `npm run format:check` |
| Tests | `npm test` |
| Security audit | `npm audit --omit=dev` |

PRs must pass all checks before merging.

### `.github/workflows/release.yml` — Automated Release

Runs on **push to `master` only** (excludes `[skip ci]` commits from semantic-release itself):

| Step | Description |
|------|-------------|
| Checkout (fetch-depth: 0) | Full history required for semantic-release to calculate versions |
| Build + Test | Final quality check before publishing |
| semantic-release | Analyze commits → bump version → publish to npm → create GitHub Release → commit back |

npm provenance is enabled via `NPM_CONFIG_PROVENANCE=true` and `id-token: write` permission, linking the published package to its source commit on GitHub.

---

## Emergency / Manual Release

Use only if the automated workflow fails and a release is urgently needed:

```bash
# 1. Ensure you're on master and up to date
git checkout master && git pull

# 2. Install and build
npm ci && npm run build

# 3. Run semantic-release manually with your tokens
GITHUB_TOKEN=<gh-token> NPM_TOKEN=<npm-token> npx semantic-release

# Alternatively, bump version manually and publish:
npm version patch   # or minor / major
npm publish
git push --follow-tags
```

---

## Troubleshooting

### Release workflow ran but no release was created

No releasable commits (`feat:`, `fix:`, `perf:`, breaking) were found since the last tag. Inspect recent commits with:

```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

### `npm publish` fails with 403

- Confirm the `NPM_TOKEN` secret is set and is an **Automation** token (not Publish or Legacy)
- Confirm the token has write access to the `@dtranllc` scope
- Verify `publishConfig.access: "public"` is in `package.json`

### semantic-release fails to push back to master

- Verify **Settings → Actions → General → Workflow permissions** is set to **Read and write**
- The `persist-credentials: false` in the checkout step, combined with `GITHUB_TOKEN`, allows the push

### Build errors on CI but not locally

- Ensure you're using Node >=22 locally (`node --version`)
- CI uses `npm ci` (locked versions) — run `npm ci` locally to reproduce
