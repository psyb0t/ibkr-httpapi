# ibkr-httpapi

HTTP wrapper over Interactive Brokers via [ib_async](https://github.com/ib-api-reloaded/ib_async) and a local IB Gateway container. Same shape as [mt5-httpapi](https://github.com/psyb0t/mt5-httpapi) — talk to your brokerage with curl + JSON, get OHLC/ticks/account/positions/orders back, server-side TA via the wickworks sidecar.

Unlike MT5 (Windows-only Python wheel → needs a Windows VM), IBKR's IB Gateway runs Linux-native, so the whole stack is just Linux containers. No KVM, no Windows ISO.

## Contents

- [Asset class routes](#asset-class-routes)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Endpoint catalog](#endpoint-catalog)
- [Stack](#stack)
- [Layout](#layout)
- [Licensing notes](#licensing-notes)

## Asset class routes

Every market type lives under its own URL prefix:

| Prefix | Asset class | Notes |
|--------|-------------|-------|
| `/stocks/<symbol>` | Equities (STK) | Default exchange SMART |
| `/options/<symbol>` | Options (OPT) | `?expiry=YYYYMMDD&strike=N&right=C\|P` |
| `/options/<symbol>/chain` | Option chain | All strikes × expirations |
| `/options/exercise` | Exercise / lapse | POST |
| `/options/combo` | Multi-leg spread (BAG) | POST — vertical, condor, butterfly, calendar |
| `/futures/<symbol>` | Futures (FUT) | `?expiry=YYYYMM&exchange=CME` mandatory |
| `/futures/<symbol>/continuous` | Continuous future | No expiry |
| `/cfd/<symbol>` | CFDs | SMART/USD defaults |
| `/forex/<pair>` | Currencies (CASH) | IDEALPRO by default |
| `/crypto/<symbol>` | Crypto (CRYPTO) | PAXOS by default |
| `/orders` | Cross-asset order entry | POST/GET/DELETE |
| `/positions` | Position list | `?account=` to filter |
| `/account` `/accounts` | Account summary | |
| `/history/executions` | Today's fills | |
| `/ping` | Health | Confirms gateway connection |

Per-symbol endpoints (where they make sense for that asset class):

- `GET /<class>/<symbol>` — contract details
- `GET /<class>/<symbol>/tick` — snapshot bid/ask/last (+ Greeks on options)
- `GET /<class>/<symbol>/rates` — historical OHLC bars
- `GET /<class>/<symbol>/ticks` — historical raw ticks
- `POST /<class>/<symbol>/rates/ta` — bars + wickworks TA enrichment

## Quick start

```bash
git clone <this-repo>
cd ibkr-httpapi
cp config/config.yaml.example config/config.yaml   # set api_token, gateway port, market_data_type
cp .env.ibkr.example .env.ibkr                     # IBKR_USERID + password for the gateway auto-login
make up
```

First boot pulls images, starts the gateway container, IBC logs into IBKR (paper or live per `TRADING_MODE`), the API process connects via the TWS API socket on port 4002 (paper) / 4001 (live).

Verify:

```bash
curl -H "Authorization: Bearer $API_TOKEN" http://localhost:8889/ping
# {"status":"ok","connected":true,...}

curl -H "Authorization: Bearer $API_TOKEN" \
    "http://localhost:8889/stocks/AAPL/rates?duration=30+D&barSize=1d"

curl -H "Authorization: Bearer $API_TOKEN" \
    "http://localhost:8889/options/AAPL/chain"

curl -H "Authorization: Bearer $API_TOKEN" \
    "http://localhost:8889/options/AAPL/tick?expiry=20260619&strike=200&right=C"
```

## Configuration

Single file: `config/config.yaml`. See `config/config.yaml.example` for the schema. Key fields:

- `api_token` — bearer token clients send in `Authorization: Bearer ...`. Empty = no auth.
- `gateway.host` / `gateway.port` — IB Gateway TWS API endpoint. `ibgateway`:4002 by default (paper).
- `gateway.client_id` — unique integer per concurrent socket. Default 1.
- `gateway.account` — IBKR account number to scope to. Empty = use default.
- `market_data_type` — 1=live (needs OPRA sub), 3=delayed-free, 4=delayed-frozen-free.
- `wickworks.url` — optional TA sidecar. Empty = `/<class>/<symbol>/rates/ta` returns 503.
- `contract_defaults.<class>` — per-asset-class default exchange/currency/multiplier so callers don't repeat them per request.

IBKR login credentials live in **`.env.ibkr`** (gitignored, loaded into the gateway container only). Never put them in `config.yaml`.

## Endpoint catalog

### Market data

```bash
# Stocks
curl ".../stocks/AAPL"
curl ".../stocks/AAPL/tick"
curl ".../stocks/AAPL/rates?duration=1+Y&barSize=1d&whatToShow=ADJUSTED_LAST"

# Options
curl ".../options/AAPL/chain"
curl ".../options/AAPL/tick?expiry=20260619&strike=200&right=C"
curl ".../options/AAPL/rates?expiry=20260619&strike=200&right=C&duration=10+D&barSize=1h"

# Futures
curl ".../futures/ES/continuous?exchange=CME"
curl ".../futures/ES/contracts?exchange=CME"           # all expiries
curl ".../futures/ES/rates?expiry=202609&exchange=CME&duration=30+D&barSize=1d"

# Forex / CFD / Crypto
curl ".../forex/EURUSD/rates?duration=30+D&barSize=1h&whatToShow=MIDPOINT"
curl ".../cfd/IBDE40/tick"
curl ".../crypto/BTC/tick?currency=USD"
```

### TA enrichment

```bash
curl -X POST -H "Content-Type: application/json" \
    ".../stocks/AAPL/rates/ta" \
    -d '{
      "duration": "200 D",
      "barSize": "1d",
      "whatToShow": "ADJUSTED_LAST",
      "indicators": {
        "rsi": true,
        "macd": true,
        "bbands": {"length": 20, "std": 2}
      }
    }'
```

Indicator catalog matches `mt5-httpapi` — same wickworks sidecar.

### Orders

```bash
# Stock market order
curl -X POST -H "Content-Type: application/json" .../orders -d '{
  "assetClass": "stock", "symbol": "AAPL",
  "action": "BUY", "quantity": 10, "orderType": "MKT"
}'

# Future limit order
curl -X POST -H "Content-Type: application/json" .../orders -d '{
  "assetClass": "future", "symbol": "ES", "expiry": "202609", "exchange": "CME",
  "action": "BUY", "quantity": 1, "orderType": "LMT", "lmtPrice": 5500.00
}'

# Vertical call spread (multi-leg)
curl -X POST -H "Content-Type: application/json" .../options/combo -d '{
  "symbol": "AAPL",
  "legs": [
    {"conid": 681000001, "ratio": 1, "action": "BUY"},
    {"conid": 681000002, "ratio": 1, "action": "SELL"}
  ],
  "action": "BUY", "quantity": 1, "orderType": "LMT", "lmtPrice": 1.20
}'

# List + cancel
curl .../orders
curl -X DELETE .../orders/12345
```

### Exercise

```bash
curl -X POST -H "Content-Type: application/json" .../options/exercise -d '{
  "conid": 681000001, "action": "EXERCISE", "quantity": 1, "account": "DU1234567"
}'
```

## Stack

- **Python 3.12**, **FastAPI** + **uvicorn**, **ib_async** for the TWS-API socket.
- **IB Gateway** in Docker via [gnzsnz/ib-gateway-docker](https://github.com/gnzsnz/ib-gateway-docker) (built locally — IBKR forbids redistributing pre-built images with their installer).
- **IBC** (IB Controller) inside the gateway image handles auto-login + daily reconnect.
- **nginx** in front for loopback-bound routing + future tailnet exposure.
- **Wickworks** TA sidecar (optional, same image as mt5-httpapi).

## Layout

```
ibkr-httpapi/
├── api/                    OpenAPI 3.1.0 source of truth
│   ├── v1.yaml             42 operations, 34 schemas — drives all generators
│   ├── _templates/         Custom Jinja for fastapi-codegen (async def + delegate)
│   └── oapi-codegen-go.yaml Go client generator config
├── ibkrapi/                FastAPI package
│   ├── config.py           YAML + env config
│   ├── ibclient.py         ib_async lifecycle + reconnect
│   ├── contracts.py        Asset class → Contract factories
│   ├── marketdata.py       Shared bars/ticks/TA helpers
│   ├── serialize.py        Dataclass → dict converters
│   ├── server.py           FastAPI app + middleware + /v1 prefix wiring
│   ├── main.py             uvicorn entry
│   └── api/
│       ├── impl.py         Hand-written impl module (business logic)
│       └── _generated/     fastapi-codegen output — NEVER hand-edit
│           ├── models.py   Pydantic v2 schemas from v1.yaml
│           └── routers/    Per-asset router stubs (async def → impl.*)
├── pkg/clients/
│   ├── go/                 Generated Go client (oapi-codegen)
│   └── python/             Generated Python client (openapi-python-client)
├── tests/                  pytest — 93 tests, mocked ib_async via conftest.py
├── scripts/                Supply-chain helpers (age-gate bump + audits)
├── config/                 config.yaml.example (real config.yaml gitignored)
├── nginx/                  nginx.conf.example (real nginx.conf gitignored)
├── Dockerfile.api          Multi-stage prod image (non-root, --require-hashes)
├── Dockerfile.dev          Dev container (lint + tests + codegen tooling)
├── Dockerfile.novnc        Optional noVNC sidecar
├── docker-compose.yml.example  Stack template (loopback default, isolated networks)
├── .env.ibkr.example       Gateway credentials env template
├── pyproject.toml          Project meta + [tool.uv] exclude-newer age-gate
├── requirements.in         Direct deps (hand-edited)
├── requirements.txt        Hash-locked lock (generated, committed)
├── requirements-dev.txt    Dev-only tooling (not hash-locked)
├── CHANGELOG.md            Per-release notes
├── run.sh                  Bootstrap + compose up
└── Makefile                up/down/logs/build, lint/test, pkg-*, audit*, generate*
```

## Supply chain

- `make audit` — `pip-audit` against `requirements.txt` (OSV/GHSA scan).
- `make audit-go` — `govulncheck` against `pkg/clients/go/go.sum`.
- `make audit-compose` — greps `docker-compose.yml*` for banned settings (`privileged`, `pid:host`, `docker.sock`, `SYS_ADMIN`), unpinned image tags, public-bound ports.
- Age-gate (`[tool.uv] exclude-newer` in `pyproject.toml`) bumps automatically on every `make pkg-{add,update,upgrade,remove}` via `scripts/bump_exclude_newer.sh` — 7-day floor at the moment of mutation.
- All base images SHA-digest pinned. `requirements.txt` hash-locked via `uv pip compile --generate-hashes`.

## Pacing + history caches (v0.2.0)

Every IBKR-bound endpoint is preemptively rate-limited AND every endpoint
that returns historical / quasi-static / piggyback-snapshottable data is
transparently cached to disk under `data/history/`. Goal: protect API
access (IBKR revokes for repeat pacing violations) AND grow a long-term
goldmine of market data on every call.

- **Pacing** — 3 tiers (`historical` / `market_data` / `orders`) with
  sliding-window counters + per-contract `asyncio.Lock` + global
  semaphore. Defaults sit BELOW IBKR's published caps. Hard cap →
  `429 RATE_LIMIT_NEAR`. Tune via `config.yaml:pacing.<tier>.<key>`.
- **Bars cache** — `/rates` + `/ticks` persist to wickworks-shaped CSV
  per (asset class, symbol, timeframe). Append-only.
- **Live snapshot historian** — every `/tick` and `/chain` call appends
  to disk (bid/ask/last + Greeks/IV for options, per-strike rows for
  chains). Best-effort; never blocks the caller.
- **Meta cache** — long-TTL JSON for contract details (7d), futures
  expiry lists (1d), option chain strike lists (1d).
- **Exec ledger** — `/history/executions` + `/history/completed_orders`
  append-only JSONL by day, dedup'd by execId / (permId, orderId).

Mount `./data:/app/data` (compose does this by default). Back up that
directory — it IS the goldmine. Configure or disable per-feature via
`config/config.yaml`.

**Licensing caveat:** IBKR's market data terms restrict redistribution.
Internal backtesting / model training / forensics on the cache is fine
(and explicitly allowed). Selling raw OHLC from the cache likely
violates OPRA / NYSE / Nasdaq redistributor licenses + IBKR's API
license — sell derived analysis (signals, backtests, aggregated stats)
instead.

## Code generation

`api/v1.yaml` is the source of truth. `make generate` (umbrella) runs:

- `make generate-api` — fastapi-codegen + custom Jinja → `ibkrapi/api/_generated/`
- `make generate-client-go` — oapi-codegen → `pkg/clients/go/client.gen.go`
- `make generate-client-python` — openapi-python-client → `pkg/clients/python/ibkr-httpapi-client/`

NEVER hand-edit anything under `_generated/` or `pkg/clients/*/`. Edit the spec, rerun the make target.

## Licensing notes

- **You must build the IB Gateway image locally.** IBKR's installer license forbids redistributing pre-built images containing their binary. `gnzsnz/ib-gateway-docker` builds with a checksum-verified download at build time — clone it, build it, push to your own private registry if you need to share across hosts.
- **OPRA market data subscription** is needed for real-time options data. Free delayed (15-20 min) works for swing timeframes — set `market_data_type: 3` in config. For real-time, subscribe to the US Securities Snapshot and Futures Value Bundle + OPRA in your IBKR account (~$5-15/mo non-pro).
- **API requires IBKR Pro.** IBKR Lite accounts have the API disabled.
- **Daily restart**: IBKR forces a logout once a day. IB Gateway 974+ + IBC 3.15+ handles this without human intervention; the API process reconnects automatically.
- **Weekly 2FA**: IBKR may push a 2FA prompt once per week (mobile app push). Pair IBKR Mobile to your account for one-tap accept.

This project is licensed under WTFPL — see `LICENSE`.
