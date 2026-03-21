#!/usr/bin/env bash
# Soft-resets to origin/<base-branch> and re-commits with a single squash message.
# No-ops when only one commit exists ahead of the base (squash not needed).
# Message must follow Commitizen format: <type>[optional scope]: <description>
# Usage: 05-squash.sh <base-branch> <squash-message>
set -euo pipefail

BASE_BRANCH="${1:-}"
MESSAGE="${2:-}"
if [[ -z "${BASE_BRANCH}" || -z "${MESSAGE}" ]]; then
  echo "Usage: $0 <base-branch> <squash-message>" >&2
  exit 1
fi

COMMIT_COUNT=$(git rev-list --count "origin/${BASE_BRANCH}..HEAD")

if [[ "${COMMIT_COUNT}" -le 1 ]]; then
  echo "Only ${COMMIT_COUNT} commit(s) ahead of origin/${BASE_BRANCH} — squash not needed."
  exit 0
fi

COMMITIZEN_PATTERN='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+'
if ! echo "${MESSAGE}" | grep -qE "${COMMITIZEN_PATTERN}"; then
  echo "Error: squash message does not follow Commitizen format." >&2
  echo "  Expected: <type>[optional scope]: <description>" >&2
  echo "  Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert" >&2
  echo "  Example: feat: add dark mode toggle" >&2
  exit 1
fi

git reset --soft "origin/${BASE_BRANCH}"
git commit -m "${MESSAGE}" || {
  echo "Error: commit failed after reset. To complete manually, run:" >&2
  echo "  git commit -m '${MESSAGE}'" >&2
  exit 1
}
echo "Squashed ${COMMIT_COUNT} commit(s) into one."
