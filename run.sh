#!/bin/bash
set -eo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${DIR}/run.log"
exec > >(tee "${LOG_FILE}") 2>&1

mkdir -p "${DIR}/logs" "${DIR}/.data/ibgateway" "${DIR}/.data/nginx"

if [ ! -f "${DIR}/docker-compose.yml" ]; then
    if [ -f "${DIR}/docker-compose.yml.example" ]; then
        echo "docker-compose.yml not found — seeding from docker-compose.yml.example"
        cp "${DIR}/docker-compose.yml.example" "${DIR}/docker-compose.yml"
    else
        echo "ERROR: neither docker-compose.yml nor docker-compose.yml.example found." >&2
        exit 1
    fi
fi

if [ ! -f "${DIR}/config/config.yaml" ]; then
    echo "ERROR: config/config.yaml not found."
    echo "  Copy config/config.yaml.example to config/config.yaml and edit."
    exit 1
fi

if [ ! -f "${DIR}/.env.ibkr" ]; then
    echo "ERROR: .env.ibkr not found."
    echo "  Copy .env.ibkr.example to .env.ibkr, fill in your IBKR credentials."
    exit 1
fi

if [ ! -f "${DIR}/nginx/nginx.conf" ]; then
    cp "${DIR}/nginx/nginx.conf.example" "${DIR}/.data/nginx/nginx.conf"
    echo "nginx config seeded from nginx.conf.example"
else
    cp "${DIR}/nginx/nginx.conf" "${DIR}/.data/nginx/nginx.conf"
fi

: > "${DIR}/.env"

API_TOKEN=$(python3 -c "
import yaml,sys
with open('${DIR}/config/config.yaml') as f:
    cfg = yaml.safe_load(f) or {}
print((cfg.get('api_token') or ''))
")
if [ -n "${API_TOKEN}" ]; then
    echo "API_TOKEN=${API_TOKEN}" >> "${DIR}/.env"
    echo "API token loaded from config.yaml"
else
    echo "WARNING: api_token is empty in config.yaml — API will run without auth"
fi

GATEWAY_PORT=$(python3 -c "
import yaml
with open('${DIR}/config/config.yaml') as f:
    cfg = yaml.safe_load(f) or {}
gw = cfg.get('gateway') or {}
print(gw.get('port') or 4002)
")
echo "IBKR_GATEWAY_PORT=${GATEWAY_PORT}" >> "${DIR}/.env"
echo "API_HOST_PORT=${API_HOST_PORT:-8889}" >> "${DIR}/.env"

WICKWORKS_URL=$(python3 -c "
import yaml
with open('${DIR}/config/config.yaml') as f:
    cfg = yaml.safe_load(f) or {}
ww = cfg.get('wickworks') or {}
print(ww.get('url') or '')
")
if [ -n "${WICKWORKS_URL}" ]; then
    echo "WICKWORKS_URL=${WICKWORKS_URL}" >> "${DIR}/.env"
fi

if docker compose -f "${DIR}/docker-compose.yml" ps -q 2>/dev/null | grep -q .; then
    echo "Container is already running."
    read -p "Stop and restart? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    docker compose -f "${DIR}/docker-compose.yml" down
fi

echo "Starting IBKR HTTP API stack..."
docker compose -f "${DIR}/docker-compose.yml" up -d

echo ""
echo "  API entry: http://localhost:${API_HOST_PORT:-8889}"
echo "  Asset prefixes:"
echo "    /stocks/<symbol>"
echo "    /options/<symbol>?expiry=YYYYMMDD&strike=N&right=C|P"
echo "    /options/<symbol>/chain"
echo "    /futures/<symbol>?expiry=YYYYMM&exchange=CME"
echo "    /cfd/<symbol>"
echo "    /forex/<pair>"
echo "    /crypto/<symbol>"
echo "    /orders"
echo "    /positions /accounts /history/executions"
echo ""
echo "  Logs: docker compose -f ${DIR}/docker-compose.yml logs -f"
