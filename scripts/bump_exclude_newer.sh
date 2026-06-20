#!/usr/bin/env bash
# Rewrite [tool.uv] exclude-newer in pyproject.toml to (today_utc - 7 days).
# Called by Makefile's pkg-add / pkg-update / pkg-upgrade / pkg-remove
# BEFORE any dep mutation, so the lock under the new resolution is gated
# against a 7-day-old timestamp at the moment of mutation (supply-chain
# attack window floor).
#
# NEVER bump to "today" — defeats the floor. Per
# ~/.claude/rule-details/managing-dependencies.md.
set -euo pipefail

PYPROJECT="${1:-pyproject.toml}"
test -f "$PYPROJECT" || { echo "ERROR: $PYPROJECT not found" >&2; exit 1; }

CUTOFF="$(date -u -d '7 days ago' +%Y-%m-%dT00:00:00Z)"

# Only rewrite the [tool.uv] one — leave any other 'exclude-newer' alone.
# Match the line; replace its value preserving the key + quotes.
sed -i -E "s|^(exclude-newer\s*=\s*)\"[^\"]*\"|\1\"${CUTOFF}\"|" "$PYPROJECT"

# Verify the rewrite landed.
grep -qE "^exclude-newer\s*=\s*\"${CUTOFF}\"" "$PYPROJECT" || {
    echo "ERROR: failed to rewrite exclude-newer in $PYPROJECT" >&2
    exit 1
}

echo "bumped exclude-newer → ${CUTOFF}"
