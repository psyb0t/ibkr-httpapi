---
title: "Troubleshooting"
description: "Real ibkr-httpapi failures with their exact messages: hanging requests, gateway connection errors, unhealthy containers, 429, 404, 500 TypeError and TA sidecar errors."
nav_order: 11
---

# Troubleshooting

Start with the logs. The API writes one JSON line per event to stdout and to `logs/full.log`:

```bash
docker compose logs -f api
docker compose logs -f ibgateway
docker compose ps
```

## make up stops before starting anything

`run.sh` checks its inputs first. The messages:

| Message | Fix |
| --- | --- |
| `ERROR: config/config.yaml not found.` | `cp config/config.yaml.example config/config.yaml` and edit it. |
| `ERROR: .env.ibkr not found.` | `cp .env.ibkr.example .env.ibkr` and fill in the login. |
| `ERROR: neither docker-compose.yml nor docker-compose.yml.example found.` | Restore `docker-compose.yml.example` from Git. |
| `ModuleNotFoundError: No module named 'yaml'` | The host's `python3` needs PyYAML (`python3-yaml` on Debian and Ubuntu). |

`WARNING: api_token is empty in config.yaml` is not fatal: the stack starts with no auth. Set a token.

## The API exits right after start

The config is checked at import time. Look for a `ValueError` in `docker compose logs api`:

- `config.market_data_type must be 1/2/3/4 (live/frozen/delayed/delayed-frozen), got ...`
- `pacing.<tier>.per_window_hard (...) must be <= per_window (...)` or `pacing.<tier>.concurrent must be >= 1`
- `Invalid duration: ...` or `Unknown duration unit: ...` for one of the duration keys.

Fix the key in `config/config.yaml` and run `make up` again.

## The API never connects to the gateway

The api log repeats `ib_async_connect_failed` with a growing `retry_in_seconds`. Check, in this order:

1. The gateway is up and logged in: `docker compose logs ibgateway`. A pending 2FA push on IBKR Mobile blocks the login.
2. `gateway.port` matches `TRADING_MODE`: 4002 for paper, 4001 for live.
3. The gnzsnz gateway image accepts API connections from other containers on relay ports 4004 (paper) and 4003 (live); 4001 and 4002 answer only inside its own container. If the connection is refused on 4002, set `gateway.port: 4004` (or `4003` for live) and run `make up`. `run.sh` passes the value on as `IBKR_GATEWAY_PORT`.
4. No other process uses the same `client_id` on this login. A second connection with the same ID drops the first.
5. The account is IBKR Pro. Lite accounts have no API access.

## Requests hang and then return 504

While the gateway socket is down (daily restart, 2FA timeout, gateway still booting), `ibclient.get_ib()` keeps reconnecting and every request waits for it, `/v1/ping` included. nginx gives up after 300 seconds and answers `504 Gateway Time-out`. Nothing is wrong with the API; check the gateway as in the section above. The api log shows `ib_async_connect_attempt` and `ib_async_connect_failed` lines while it waits.

## nginx never starts once api_token is set

`docker compose up` fails with `dependency failed to start: container ibkr-httpapi-api is unhealthy`. The `api` health check in `docker-compose.yml.example` calls `/v1/ping` without a token, gets `401`, and nginx waits for a healthy `api` forever. Send the token in the check. In your `docker-compose.yml`:

```yaml
healthcheck:
  test:
    - CMD
    - python
    - -c
    - >-
      import os, urllib.request;
      urllib.request.urlopen(urllib.request.Request(
      'http://127.0.0.1:8889/v1/ping',
      headers={'Authorization': 'Bearer ' + os.environ.get('API_TOKEN', '')}),
      timeout=2)
```

The `api` service already receives `API_TOKEN` from `.env`.

## nginx shows as unhealthy

The nginx health check fetches `/healthz`, which nginx proxies to the API, and the API has no such route. The container keeps serving; only its health status is wrong. Nothing depends on it unless you enable the `cloudflared` service. To fix it, add this to the `server` block of `nginx/nginx.conf` (copy the example first) and run `make up`:

```nginx
location = /healthz {
    return 200 "ok\n";
}
```

## 404 on every path

The REST API lives under `/v1`. `http://localhost:8889/ping` is a 404 with FastAPI's `{"detail": "Not Found"}`; `http://localhost:8889/v1/ping` is the right URL. MCP is the exception, at `/mcp`.

## 404 Contract not found or not qualifyable

IBKR could not match the contract. Common causes:

- futures without `exchange`, or with an expiry that is not listed (check `GET /v1/futures/{symbol}/contracts?exchange=...`);
- options with a strike or expiry that is not in the chain (check `GET /v1/options/{symbol}/chain`);
- a symbol that needs `primaryExchange` or a different `currency` to be unique.

## /rates returns 500 with Internal error: TypeError

The bars store under `data/history/` fails on every bar IBKR returns: the api log shows `request_crash` with `TypeError: can only concatenate str (not "int") to str`. This is a bug in the current code. Work around it by turning the store off in `config/config.yaml` and running `make up`:

```yaml
history_cache:
  enabled: false
```

`/rates/ta` goes through the same store and has the same problem. Snapshots, chains, the metadata cache and executions are unaffected.

## 429 RATE_LIMIT_NEAR

The pacing gate refused the call before IBKR would have. Wait `details.retry_after_sec` and retry. If it happens in normal use, you are close to IBKR's real limits (60 historical requests per 10 minutes is the tight one); spread the requests out rather than raising `pacing.historical.per_window_hard`. See [Pacing and history](pacing-and-history.md#pacing).

## 503 TA_SIDECAR_UNAVAILABLE and 502 Wickworks unreachable

- `Wickworks TA sidecar not configured`: `wickworks.url` and `WICKWORKS_URL` are both empty.
- `Wickworks URL must be http(s)`: the URL has another scheme.
- `502 Wickworks unreachable`: the URL is set but nothing answers. Check `docker compose ps wickworks` and that the URL uses the service name (`http://wickworks:8000/`).
- `502 Wickworks returned HTTP <n>`: wickworks rejected the request; `details.upstream_body` has its answer, usually an unknown indicator name or parameter.

## Option Greeks or quotes are null

With `market_data_type: 3` or `4` (delayed), IBKR often sends no Greeks and sometimes no bid or ask. Real-time option data needs an OPRA subscription on the account and `market_data_type: 1`.

## Forex bars come back empty or fail

`/v1/forex/{pair}/rates` defaults to `whatToShow=TRADES`, and IDEALPRO has no trade data. Pass `whatToShow=MIDPOINT` (or `BID`, `ASK`).

## 500 on an option request with a bad right

`right` must be `C`, `P`, `CALL` or `PUT`. Any other value raises inside the contract builder and comes back as `500 INTERNAL_SERVER_ERROR` with `Internal error: ValueError` instead of a 400.

## MCP futures tools return 422

`get_future_continuous` and `list_future_contracts` do not send their `exchange` argument, which the REST routes require. Call the `request` tool with `{"method": "GET", "path": "/v1/futures/ES/contracts", "query": {"exchange": "CME"}}` instead. `place_order` has no `exchange` parameter, so futures orders also need `request`. See [MCP server](mcp.md).
