#!/usr/bin/env bash
# Wrapper for install.py. Locates Python and forwards args.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "error: python3 not found." >&2
    echo "install python 3.8+ from https://www.python.org/downloads/ and re-run." >&2
    exit 1
fi

exec "$PY" "$SCRIPT_DIR/install.py" "$@"
