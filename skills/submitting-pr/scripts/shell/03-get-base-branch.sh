#!/usr/bin/env bash
# Resolves the upstream default branch (HEAD branch) from the remote.
# Prints the branch name to stdout; falls back to "main" if unresolvable.
set -euo pipefail

git fetch origin 2>/dev/null || true

BASE_BRANCH=$(git remote show origin 2>/dev/null \
  | grep "HEAD branch" \
  | awk '{print $NF}')

if [[ -z "${BASE_BRANCH}" ]]; then
  echo "Warning: could not resolve remote HEAD branch — falling back to 'main'." >&2
  BASE_BRANCH="main"
fi

echo "${BASE_BRANCH}"
