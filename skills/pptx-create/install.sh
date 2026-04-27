#!/usr/bin/env bash
# Per-skill wrapper. Delegates to repo-root installer with --skill <this-dir-name>.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"
SKILL_NAME="$(basename "$SKILL_DIR")"

exec "$REPO_ROOT/install.sh" --skill "$SKILL_NAME" "$@"
