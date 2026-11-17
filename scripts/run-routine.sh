#!/usr/bin/env bash
# Crontab target. Publishing becomes an approval request, never an automatic push.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_NAME="${1:-}"
if [[ ! "$SKILL_NAME" =~ ^[a-z0-9-]+$ ]]; then
    echo 'Usage: run-routine.sh <registered-skill-name>' >&2
    exit 2
fi
cd "$WORKSPACE_ROOT"
PYTHON_BIN="${AGENTIC_OS_PYTHON:-python3}"
if [[ -x .venv/bin/python ]]; then PYTHON_BIN="$WORKSPACE_ROOT/.venv/bin/python"; fi
if [[ -n "$(git status --porcelain)" ]]; then
    echo 'Refusing routine in a dirty checkout; review and commit local changes first.' >&2
    exit 1
fi
git pull --ff-only
"$PYTHON_BIN" "$WORKSPACE_ROOT/apps/runner/server.py" trigger "$SKILL_NAME"
# Output/private vault are ignored. A human chooses reviewed files to commit/push.
"$PYTHON_BIN" - "$SKILL_NAME" <<'PY'
import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
queue = Path('output/approval_queue.jsonl')
queue.parent.mkdir(parents=True, exist_ok=True)
with queue.open('a', encoding='utf-8') as stream:
    stream.write(json.dumps({
        'id': 'publish-' + secrets.token_hex(8),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'pending', 'action': 'publish', 'skill': sys.argv[1],
        'payload': {'instruction': 'Review generated artifacts and memory pointers; select safe files, commit, and push manually.'}
    }) + '\n')
PY
