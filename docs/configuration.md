---
title: "Configuration"
description: "Every config.yaml key, environment variable and command line flag ibkr-httpapi reads, with defaults, precedence, valid values and the keys it ignores."
nav_order: 4
---

# Configuration

The API reads one file, `config/config.yaml`, once at startup. [`config/config.yaml.example`](https://github.com/psyb0t/ibkr-httpapi/blob/main/config/config.yaml.example) has every key with comments; copy it and edit. Changes take effect when the `api` container restarts. Use `make up`: it rewrites `.env` and recreates the containers. A plain `docker compose restart api` keeps the `API_TOKEN`, `IBKR_GATEWAY_PORT` and `WICKWORKS_URL` values compose passed in when it created the container, and those environment variables override `config.yaml`.

A missing file is not an error: every key falls back to the default in [`ibkrapi/config.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/config.py).

## Precedence

For keys that have an override, the first one set wins:

1. command line flag (`python -m ibkrapi --port 9000`);
2. environment variable;
3. `config.yaml`;
4. built-in default.

The compose file sets `IBKR_GATEWAY_HOST=ibgateway` and `IBKR_CLIENT_ID=1` in the `api` environment, so under compose `gateway.host` and `gateway.client_id` in `config.yaml` have no effect. Change them in `docker-compose.yml` instead.

## Durations

`connect_timeout`, `reconnect_backoff`, `reconnect_max_backoff` and `wickworks.timeout` take a number of seconds or a string of number-unit pairs with units `s`, `m`, `h`, `d`: `"20s"`, `"5m"`, `"1h30m"`. Any other unit stops the API at startup with `ValueError`.

## Keys

### API server

| Key | Flag | Env | Default | Meaning |
| --- | --- | --- | --- | --- |
| `api_token` | `--token` | `API_TOKEN` | `""` | Bearer token required on every request, `/v1/*` and `/mcp` alike. Empty turns auth off. |
| (none) | `--host` | `API_HOST` | `0.0.0.0` | Bind address inside the container. |
| (none) | `--port` | `API_PORT` | `8889` | Listen port inside the container. |

### Gateway connection

| Key | Flag | Env | Default | Meaning |
| --- | --- | --- | --- | --- |
| `gateway.host` | `--gateway-host` | `IBKR_GATEWAY_HOST` | `ibgateway` | Where the TWS API socket listens. |
| `gateway.port` | `--gateway-port` | `IBKR_GATEWAY_PORT` | `4002` | IB Gateway uses 4002 for paper and 4001 for live; TWS uses 7497 and 7496. |
| `gateway.client_id` | `--client-id` | `IBKR_CLIENT_ID` | `1` | TWS API client ID. A second connection with the same ID on the same login disconnects the first. |
| `gateway.account` | `--account` | `IBKR_ACCOUNT` | `""` | Account passed to `connectAsync`. Empty uses the gateway's default; set it when the login has several linked accounts. |
| `gateway.connect_timeout` | | | `20s` | Timeout for one connect attempt. |
| `gateway.reconnect_backoff` | | | `5s` | First wait after a failed connect. Doubles on each failure. |
| `gateway.reconnect_max_backoff` | | | `60s` | Ceiling for that wait. The API never stops retrying. |

### Market data

| Key | Default | Valid values |
| --- | --- | --- |
| `market_data_type` | `3` when the key is missing | `1` live (needs subscriptions), `2` frozen, `3` delayed (free, 15 to 20 minutes), `4` delayed frozen. Anything else stops the API at startup. The example file sets `1`. |

The API calls `reqMarketDataType` after each connect when the value is not `1`.

### Wickworks TA sidecar

| Key | Env | Default | Meaning |
| --- | --- | --- | --- |
| `wickworks.url` | `WICKWORKS_URL` | `""` | URL the API POSTs bars to for `/rates/ta`. Empty, or anything not starting with `http://` or `https://`, makes `/rates/ta` return `503 TA_SIDECAR_UNAVAILABLE`. The example sets `http://wickworks:8000/`. |
| `wickworks.timeout` | `WICKWORKS_TIMEOUT` | `30s` | Request timeout. `0` means 30 seconds. |

### Contract defaults

`contract_defaults.<class>` fills in fields a request leaves out. A query parameter or body field always wins.

| Class key | Fields read | Built-in fallback |
| --- | --- | --- |
| `stocks` | `exchange`, `currency` | `SMART`, `USD` |
| `options` | `exchange`, `currency`, `multiplier` | `SMART`, `USD`, `100` |
| `futures` | `exchange`, `currency` | none, `USD` |
| `cfd` | `exchange`, `currency` | `SMART`, `USD` |
| `forex` | `exchange` | `IDEALPRO` |
| `crypto` | `exchange`, `currency` | `PAXOS`, `USD` |
| `index` | `exchange`, `currency` | `CBOE`, `USD` (no endpoint uses it yet) |

Every futures endpoint and every futures order requires `exchange` in the request, so `contract_defaults.futures.exchange` is never used.

### Pacing

`pacing.<tier>.<key>` for the tiers `historical`, `market_data` and `orders`. Each key you set replaces that one default; the rest stay. See [Pacing and history](pacing-and-history.md#pacing) for what each tier covers.

| Key | `historical` | `market_data` | `orders` | Meaning |
| --- | --- | --- | --- | --- |
| `per_window` | 60 | 2400 | 300 | The real limit, used in messages. |
| `per_window_soft` | 50 | 2000 | 250 | Calls in the window that log a `pacing_soft_cap` warning. |
| `per_window_hard` | 55 | 2200 | 275 | Calls in the window that make new requests fail with 429. Must not exceed `per_window`. |
| `window_sec` | 600 | 60 | 60 | Sliding window length in seconds. |
| `per_contract_per_sec` | 2 | 5 | 2 | Calls per contract key per second before 429. `0` turns the check off. |
| `concurrent` | 3 | 10 | 3 | Calls in flight at once for the tier. Must be at least 1. |

A `per_window_hard` above `per_window` or a `concurrent` below 1 stops the API at startup with `ValueError`.

### History stores

| Key | Env | Default | Meaning |
| --- | --- | --- | --- |
| `history_cache.enabled` | | `true` | Write fetched bars to CSV. |
| `history_cache.path` | `HISTORY_CACHE_PATH` | `<project>/data/history` (`/app/data/history` in the container) | Root for all four stores. |
| `history_cache.refresh_tail_bars` | | `5` | Read and logged; has no effect on fetching today. |
| `history_cache.persist_open_bar` | | `false` | Keep the newest bar in the file even if its period has not closed. |
| `historian.enabled` | | `true` | Append a row per `/tick` call and per strike per `/chain` call. |
| `meta_cache.enabled` | | `true` | Cache contract details, futures lists and chain strike lists as JSON. |
| `meta_cache.ttl_sec.contract_details` | | `604800` (7 days) | TTL for `/<class>/{symbol}` contract details and `/futures/{symbol}/continuous`. |
| `meta_cache.ttl_sec.futures_expiries` | | `86400` (1 day) | TTL for `/futures/{symbol}/contracts`. |
| `meta_cache.ttl_sec.chain_strike_list` | | `86400` (1 day) | TTL for `/options/{symbol}/chain`. |
| `exec_history.enabled` | | `true` | Append executions and completed orders to daily JSONL files. |

### Keys the API ignores

`ibkr_login.*` and `tailscale.*` appear in the example file but no code reads them. Gateway credentials come only from `.env.ibkr`. The tailscale sidecar in the compose file reads `TS_AUTHKEY` and `TS_EXTRA_ARGS` from the environment.

## Other environment variables

| Variable | Read by | Default | Meaning |
| --- | --- | --- | --- |
| `LOG_LEVEL` | api | `INFO` | Python log level for the `ibkrapi` logger. |
| `API_HOST_BIND` | compose | `127.0.0.1` | Host address nginx publishes on. |
| `API_HOST_PORT` | compose, `run.sh` | `8889` | Host port nginx publishes on. |
| `IBKR_GATEWAY_IMAGE` | compose | `ghcr.io/gnzsnz/ib-gateway:stable` | Gateway image. Set it in your shell, not in `.env`. |

`run.sh` rewrites `.env` on every start with `API_TOKEN`, `IBKR_GATEWAY_PORT` and `WICKWORKS_URL` from `config.yaml`, plus `API_HOST_PORT`. Anything else you put in `.env` is lost.

## .env.ibkr

Loaded into the `ibgateway` container only. The variables belong to the gateway image:

| Variable | Meaning |
| --- | --- |
| `TWS_USERID` | IBKR username. |
| `TWS_PASSWORD` | IBKR password. |
| `TRADING_MODE` | `paper` or `live`. Match `gateway.port`. |
| `READ_ONLY_API` | `yes` blocks order placement in the gateway itself. Commented out in the example. |
