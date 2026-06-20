#!/usr/bin/env bash
# Audit every docker-compose / compose file in the repo against the
# hardening rules from ~/.claude/rule-details/hardening-containers.md
# (compose orchestration section). Exits non-zero on any violation.
#
# Run before every release tag, alongside `make audit` / `make audit-go`.
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")/.."

FILES=$(ls docker-compose*.yml docker-compose*.yml.example compose*.yml compose*.yml.example \
        docker-compose*.yaml docker-compose*.yaml.example compose*.yaml compose*.yaml.example \
        2>/dev/null | sort -u || true)
if [[ -z "$FILES" ]]; then
    echo "no compose files found — nothing to audit"
    exit 0
fi

FAIL=0

# Banned-in-prod settings.
BANNED_PATTERN='privileged:\s*true|pid:\s*host|ipc:\s*host|network:\s*host|userns_mode:\s*host|/var/run/docker\.sock|cgroup:\s*host|cap_add:\s*\[[^]]*SYS_ADMIN'
if HITS=$(grep -nHE "$BANNED_PATTERN" $FILES 2>/dev/null); then
    echo "FAIL: banned settings detected"
    echo "$HITS"
    FAIL=1
fi

# Loopback bind enforcement — `ports:` entries without an explicit
# 127.0.0.1 / loopback variable / tailnet IP need a justification.
# Allow $VAR-substituted bind IPs since those are intentionally
# operator-configurable (default-loopback is enforced via the default).
PUBLIC_PORTS=$(grep -nHE '^\s+-\s+"[0-9]+:[0-9]+"' $FILES 2>/dev/null || true)
if [[ -n "$PUBLIC_PORTS" ]]; then
    echo "WARN: public-bound ports (no 127.0.0.1 prefix) — confirm intentional:"
    echo "$PUBLIC_PORTS"
fi

# Digest pinning — every `image:` line should reference @sha256: OR be
# a locally-built artifact (image: foo:local / image: foo-httpapi:local
# patterns mean `docker build` produced it in this tree). Anything else
# is a mutable tag.
UNPINNED=$(grep -nHE '^\s+image:\s+' $FILES \
    | grep -vE '@sha256:|:local|\$\{' \
    || true)
if [[ -n "$UNPINNED" ]]; then
    echo "WARN: unpinned image tag — pin via @sha256:<digest> for prod:"
    echo "$UNPINNED"
fi

# Every service should have read_only / cap_drop / security_opt /
# resource limits / healthcheck / logging caps. Cheap structural check:
# count `services:` children + count appearances of each hardening key.
# Doesn't enforce per-service (would need yq); a count mismatch is a
# loud "go look".
SERVICE_COUNT=$( { grep -cE '^[a-z_-]+:\s*$' $FILES || true; } | awk -F: '{s+=$NF} END{print s+0}')
for key in 'cap_drop:' 'security_opt:' 'pids_limit:|^\s+pids:' 'logging:' 'healthcheck:' 'init:\s*true'; do
    KEY_COUNT=$( { grep -hcE "$key" $FILES || true; } | awk '{s+=$1} END{print s+0}')
    if (( KEY_COUNT < SERVICE_COUNT - 1 )); then
        echo "WARN: '$key' appears $KEY_COUNT time(s) across $SERVICE_COUNT service(s) — confirm each service has the hardening it needs"
    fi
done

if (( FAIL > 0 )); then
    echo
    echo "audit-compose: FAILED"
    exit 1
fi

echo "audit-compose: OK"
