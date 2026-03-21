#!/usr/bin/env bash
# Opens a pull request via the gh CLI.
# Usage: 07-create-pr.sh <base-branch> <title> <body>
set -euo pipefail

BASE_BRANCH="${1:-}"
TITLE="${2:-}"
BODY="${3:-}"

if [[ -z "${BASE_BRANCH}" || -z "${TITLE}" ]]; then
  echo "Usage: $0 <base-branch> <title> [body]" >&2
  exit 1
fi

BODY_FILE=$(mktemp)
trap 'rm -f "${BODY_FILE}"' EXIT
printf '%s' "${BODY}" > "${BODY_FILE}"

gh pr create \
  --base "${BASE_BRANCH}" \
  --title "${TITLE}" \
  --body-file "${BODY_FILE}"
