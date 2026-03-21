#!/usr/bin/env bash
# Prints the current branch name and working-tree status.
# Exits non-zero if on a protected branch (main or master).
# Outputs machine-parseable keys so callers can branch on results.
set -euo pipefail

BRANCH=$(git branch --show-current)
echo "current-branch: ${BRANCH}"

if [[ -z "${BRANCH}" ]]; then
  echo "Error: not on a branch (detached HEAD). Check out a feature branch before submitting a PR." >&2
  exit 1
fi

if [[ "${BRANCH}" == "main" || "${BRANCH}" == "master" ]]; then
  echo "Error: current branch is '${BRANCH}'. Switch to a feature branch before submitting a PR." >&2
  exit 1
fi

STATUS=$(git status --short)
if [[ -z "${STATUS}" ]]; then
  echo "working-tree: clean"
else
  echo "working-tree: dirty"
  echo "${STATUS}"
fi
