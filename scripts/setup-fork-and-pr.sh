#!/usr/bin/env bash
# Fork upstream template and push RBAC branch for GitHub PR workflow.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM="fastapi/full-stack-fastapi-template"
FORK_OWNER="${FORK_OWNER:-yanhub}"
FORK_REPO="${FORK_REPO:-full-stack-fastapi-template}"
BASE_COMMIT="${BASE_COMMIT:-3f52abe}"

cd "${ROOT_DIR}"

get_github_token() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    echo "${GITHUB_TOKEN}"
    return
  fi
  if [[ -n "${GH_TOKEN:-}" ]]; then
    echo "${GH_TOKEN}"
    return
  fi
  printf 'protocol=https\nhost=github.com\n\n' | git credential fill 2>/dev/null \
    | awk -F= '/^password=/{print $2; exit}'
}

TOKEN="$(get_github_token || true)"
if [[ -z "${TOKEN}" ]]; then
  echo "No GitHub token. Set GITHUB_TOKEN or run: gh auth login" >&2
  echo "Manual fork: https://github.com/${UPSTREAM}/fork" >&2
  exit 1
fi

echo "Creating fork ${FORK_OWNER}/${FORK_REPO}..."
FORK_JSON="$(curl -sS -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${UPSTREAM}/forks" \
  -d "{\"name\":\"${FORK_REPO}\",\"default_branch_only\":true}")"

FORK_NAME="$(echo "${FORK_JSON}" | jq -r '.full_name // empty')"
FORK_MSG="$(echo "${FORK_JSON}" | jq -r '.message // empty')"

if [[ -z "${FORK_NAME}" ]]; then
  if [[ "${FORK_MSG}" == *"already exists"* ]] || curl -sS -H "Authorization: Bearer ${TOKEN}" \
    "https://api.github.com/repos/${FORK_OWNER}/${FORK_REPO}" | jq -e .id >/dev/null 2>&1; then
    FORK_NAME="${FORK_OWNER}/${FORK_REPO}"
    echo "Fork already exists: ${FORK_NAME}"
  else
    echo "Fork failed: ${FORK_MSG}" >&2
    exit 1
  fi
else
  echo "Fork created: ${FORK_NAME}"
fi

if git remote get-url upstream >/dev/null 2>&1; then
  git remote set-url upstream "git@github.com:${UPSTREAM}.git"
else
  git remote add upstream "git@github.com:${UPSTREAM}.git"
fi

if git remote get-url origin | grep -q "${FORK_REPO}"; then
  :
else
  git remote set-url origin "git@github.com:${FORK_NAME}.git"
fi

echo "Pushing main to fork..."
git push -u origin main --force-with-lease

COMPARE_URL="https://github.com/${UPSTREAM}/compare/master...${FORK_OWNER}:${FORK_REPO}:main"
PR_URL=""

PR_JSON="$(curl -sS -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${UPSTREAM}/pulls" \
  -d "$(jq -n \
    --arg title "feat: RBAC for Fullstack Dev Test Task" \
    --arg head "${FORK_OWNER}:main" \
    --arg base "master" \
    --arg body "Role-based access control (admin/manager/member) for users, metrics, and settings. See README permission matrix and tests in \`test_authorization.py\`. Diff vs template baseline commit ${BASE_COMMIT}." \
    '{title: $title, head: $head, base: $base, body: $body}')")"

PR_URL="$(echo "${PR_JSON}" | jq -r '.html_url // empty')"
PR_ERR="$(echo "${PR_JSON}" | jq -r '.message // empty')"

cat <<EOF

Done.

Fork:     https://github.com/${FORK_NAME}
Compare:  ${COMPARE_URL}
EOF

if [[ -n "${PR_URL}" ]]; then
  echo "PR:       ${PR_URL}"
else
  echo "PR:       open manually from Compare URL (${PR_ERR})"
fi

EOF
