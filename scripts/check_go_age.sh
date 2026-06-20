#!/usr/bin/env bash
# Refuse to `go get` a module@version published within the last 7 days.
# Go has no native age-gate flag — wrap go get in this script per
# ~/.claude/rule-details/managing-dependencies.md.
#
# Usage: scripts/check_go_age.sh <module>@<version>
set -euo pipefail

PKG="${1:?usage: $0 <module>@<version>}"
MOD="${PKG%@*}"
VER="${PKG#*@}"

[[ "$MOD" == "$VER" ]] && { echo "must include @version (got $PKG)" >&2; exit 1; }

INFO="$(curl -fsS "https://proxy.golang.org/${MOD}/@v/${VER}.info")" \
    || { echo "proxy lookup failed for $PKG" >&2; exit 1; }

PUBLISH_TS="$(echo "$INFO" | jq -r .Time)"
[[ -z "$PUBLISH_TS" || "$PUBLISH_TS" == "null" ]] && {
    echo "ERROR: no .Time in proxy response for $PKG" >&2; exit 1; }

PUBLISH_EPOCH="$(date -d "$PUBLISH_TS" +%s)"
CUTOFF_EPOCH="$(date -u -d '7 days ago' +%s)"

if (( PUBLISH_EPOCH > CUTOFF_EPOCH )); then
    echo "REFUSED: $PKG published $PUBLISH_TS — within 7-day supply-chain attack window" >&2
    exit 1
fi

echo "OK: $PKG published $PUBLISH_TS (older than 7 days)"
