---
title: "Getting started"
description: "From a fresh clone to a working /v1/ping: gateway image, config.yaml, .env.ibkr, make up, the first 2FA login and the first market data calls."
nav_order: 2
---

# Getting started

This page takes you from nothing to a running stack that answers `GET /v1/ping` with `"connected": true`. Use a paper account for all of it. Every order endpoint acts on whatever account the gateway logs into.

## Before you start

- An IBKR Pro account (Lite accounts have no API access) and its paper trading login.
- IBKR Mobile paired with the account. The first login and then roughly one login a week ask for a 2FA push.
- Docker with the Compose plugin, Make, and `python3` with PyYAML on the host. [`run.sh`](https://github.com/psyb0t/ibkr-httpapi/blob/main/run.sh) reads `config/config.yaml` with Python before it starts the stack.

## 1. Clone

```bash
git clone https://github.com/psyb0t/ibkr-httpapi
cd ibkr-httpapi
```

## 2. Pick the gateway image

The `ibgateway` service runs whatever `IBKR_GATEWAY_IMAGE` names. Unset, it pulls `ghcr.io/gnzsnz/ib-gateway:stable`. IBKR's installer license forbids redistributing images that contain the gateway, so the intended route is to build one yourself from [gnzsnz/ib-gateway-docker](https://github.com/gnzsnz/ib-gateway-docker) (its build downloads the installer and checks its checksum) and point the variable at it:

```bash
export IBKR_GATEWAY_IMAGE=registry.example.com/ib-gateway@sha256:<digest>
```

`run.sh` rewrites `.env` on every start, so set this in your shell or edit the `image:` line in `docker-compose.yml` after the first run. Do not put it in `.env`.

## 3. Write config/config.yaml

```bash
cp config/config.yaml.example config/config.yaml
```

Change these three things:

- `api_token`: set it to a random value, for example the output of `openssl rand -hex 32`. Empty means no auth at all.
- `market_data_type`: the example ships with `1` (live), which needs paid market data subscriptions. Set `3` (delayed, free) if you have none.
- `gateway.port`: `4002` for paper, `4001` for live. See [troubleshooting](troubleshooting.md#the-api-never-connects-to-the-gateway) if the API cannot connect with the gnzsnz image.

Every other key is described on the [configuration page](configuration.md).

## 4. Write .env.ibkr

```bash
cp .env.ibkr.example .env.ibkr
```

```bash
TWS_USERID=your_ibkr_username
TWS_PASSWORD=your_ibkr_password
TRADING_MODE=paper
```

Compose loads this file into the gateway container only. The API never sees your IBKR password.

## 5. Start the stack

```bash
make up
```

`make up` runs `run.sh`, which:

1. creates `logs/`, `.data/ibgateway/` and `.data/nginx/`;
2. copies `docker-compose.yml.example` to `docker-compose.yml` if it does not exist yet;
3. stops with an error if `config/config.yaml` or `.env.ibkr` is missing;
4. copies `nginx/nginx.conf` (or the example) to `.data/nginx/nginx.conf`;
5. writes `.env` with `API_TOKEN`, `IBKR_GATEWAY_PORT`, `API_HOST_PORT` and `WICKWORKS_URL` taken from `config.yaml`;
6. asks before restarting if the stack is already up, then runs `docker compose up -d`.

The first start builds the `api` image and pulls nginx and wickworks. IBC then logs the gateway into IBKR. Watch it and approve the 2FA push on your phone when it arrives:

```bash
docker compose logs -f ibgateway api
```

The API logs `ib_async_connected` once the socket is up.

## 6. Check it

```bash
export API_TOKEN=<the api_token from config.yaml>

curl -s -H "Authorization: Bearer $API_TOKEN" http://localhost:8889/v1/ping
```

```json
{
  "status": "ok",
  "connected": true,
  "serverVersion": 178,
  "startTime": "2026-06-19T00:00:00+00:00",
  "uptimeSeconds": 12.5,
  "msgsSent": 20,
  "msgsRecv": 31
}
```

Every REST path lives under `/v1`. `http://localhost:8889/ping` without the prefix is a 404.

## 7. First real calls

```bash
# Contract details
curl -s -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:8889/v1/stocks/AAPL

# Snapshot quote
curl -s -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:8889/v1/stocks/AAPL/tick

# 30 days of daily bars
curl -s -H "Authorization: Bearer $API_TOKEN" \
  "http://localhost:8889/v1/stocks/AAPL/rates?duration=30+D&barSize=1d"

# Option chain, then one contract's quote with Greeks
curl -s -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:8889/v1/options/AAPL/chain
curl -s -H "Authorization: Bearer $API_TOKEN" \
  "http://localhost:8889/v1/options/AAPL/tick?expiry=20260619&strike=200&right=C"
```

Pick an expiry and strike that exist in the chain response. With delayed data (`market_data_type: 3`) the Greeks fields are often `null`.

## Next

- Every endpoint and its parameters: [REST API](api.md).
- Connect an agent: [MCP server](mcp.md) and [Agent integrations](agent-integrations.md).
- Before you open it to anything but localhost: [Security](security.md).
