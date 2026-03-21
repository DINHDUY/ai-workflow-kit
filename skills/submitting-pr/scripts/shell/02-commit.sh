#!/usr/bin/env bash
# Stages all changes and creates a commit with the provided message.
# Message must follow Commitizen format: <type>[optional scope]: <description>
# Usage: 02-commit.sh <commit-message>
set -euo pipefail

MESSAGE="${1:-}"
if [[ -z "${MESSAGE}" ]]; then
  echo "Usage: $0 <commit-message>" >&2
  exit 1
fi

COMMITIZEN_PATTERN='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+'
if ! echo "${MESSAGE}" | grep -qE "${COMMITIZEN_PATTERN}"; then
  echo "Error: commit message does not follow Commitizen format." >&2
  echo "  Expected: <type>[optional scope]: <description>" >&2
  echo "  Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert" >&2
  echo "  Example: feat(auth): add OAuth2 login" >&2
  exit 1
fi

git add -A
git commit -m "${MESSAGE}"
