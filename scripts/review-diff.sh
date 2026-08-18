#!/usr/bin/env bash
# Print a review-friendly diff against the pristine Init commit (3f52abe).
set -euo pipefail

BASE="${BASE_COMMIT:-3f52abe}"
MODE="${1:-}"

case "${MODE}" in
  --full)
    git diff "${BASE}"..HEAD
    ;;
  --log)
    git log --oneline "${BASE}"..HEAD
    ;;
  ""|--stat)
    echo "RBAC diff vs Init commit (${BASE}):"
    git diff --stat "${BASE}"..HEAD
    echo ""
    echo "Commits:"
    git log --oneline "${BASE}"..HEAD
    ;;
  -h|--help)
    cat <<EOF
Usage: $0 [--stat|--full|--log]

  (default)  Short stat + commit list vs Init commit
  --full     Full patch
  --log      Commit list only

Override base: BASE_COMMIT=<sha> $0
EOF
    ;;
  *)
    echo "Unknown option: ${MODE}" >&2
    exit 1
    ;;
esac
