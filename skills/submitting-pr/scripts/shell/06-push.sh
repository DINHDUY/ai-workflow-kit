#!/usr/bin/env bash
# Pushes the current branch to origin.
# Pass --force to use --force-with-lease (required after a squash).
# Refuses to push (or force-push) to main or master.
# Usage: 06-push.sh [--force]
set -euo pipefail

FORCE="${1:-}"

BRANCH=$(git branch --show-current)
if [[ "${BRANCH}" == "main" || "${BRANCH}" == "master" ]]; then
  echo "Error: refusing to push to '${BRANCH}'. Switch to a feature branch first." >&2
  exit 1
fi

if [[ "${FORCE}" == "--force" ]]; then
  git push --force-with-lease origin HEAD
else
  git push -u origin HEAD
fi
