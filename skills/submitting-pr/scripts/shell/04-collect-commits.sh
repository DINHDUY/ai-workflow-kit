#!/usr/bin/env bash
# Prints the log of commits on HEAD that are not yet in origin/<base-branch>.
# Output is used as the PR body and to derive the squash commit message.
# Usage: 04-collect-commits.sh <base-branch>
set -euo pipefail

BASE_BRANCH="${1:-}"
if [[ -z "${BASE_BRANCH}" ]]; then
  echo "Usage: $0 <base-branch>" >&2
  exit 1
fi

git log "origin/${BASE_BRANCH}..HEAD" \
  --pretty=format:"%h %s%n%b" \
  --no-merges
