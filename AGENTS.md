# ibkr-httpapi

Instructions for AI coding agents (Codex, Claude Code and others) working in this repository. Human contributors can read it too; the user documentation is the site under `docs/`.

## Agent setup

`AGENTS.md` is the source of these instructions. `CLAUDE.md` is a committed symlink to `AGENTS.md`, and `.claude` is a committed symlink to `.agents`, so Claude Code reads the same instructions, rules and skills as Codex. Claude's Edit and Write tools refuse to write through a symlink, so edit `AGENTS.md` and `.agents/rules/*.md` directly.

## What it is

An HTTP and MCP wrapper over Interactive Brokers. A FastAPI app talks to a local IB Gateway container through `ib_async` over the TWS API socket and exposes market data, account state and order entry for stocks, options, futures, CFDs, forex and crypto as JSON under `/v1`, plus the same operations as typed MCP tools at `/mcp`. It is the IBKR counterpart of [mt5-httpapi](https://github.com/psyb0t/mt5-httpapi) with the same asset-class routing, and needs no Windows VM because IB Gateway runs on Linux. It ships as a Docker Compose stack, not a published image: IBKR's license forbids redistributing images that contain the gateway installer.

It drives a real brokerage account. `POST /orders`, `POST /options/combo`, `POST /options/exercise` and both `DELETE /orders` routes move real money.

## Architecture

- `ibgateway` service (compose): an IB Gateway image built from gnzsnz/ib-gateway-docker. IBC logs in with the credentials from `.env.ibkr` and opens the TWS API socket on 4002 (paper) or 4001 (live) on the `backend` network.
- `api` service: `Dockerfile.api`, `python -m ibkrapi`. `ibkrapi/main.py` starts uvicorn on `ibkrapi.server:app`, port 8889.
  - `ibkrapi/server.py`: builds the app, configures pacing and the disk caches at import time, adds the logging and bearer-auth middleware, mounts the generated routers under `/v1` and the MCP app at `/mcp`. The lifespan connects to the gateway on startup (a failure is logged and retried on the first request) and disconnects on shutdown.
  - `ibkrapi/api/_generated/`: routers and Pydantic models generated from `api/v1.yaml`. Each handler is one line that calls the function with the same snake-cased `operationId` in `ibkrapi/api/impl.py`.
  - `ibkrapi/api/impl.py`: all endpoint logic. Builds contracts (`contracts.py`), wraps every IBKR call in `pacing.guard`, and routes data through the caches.
  - `ibkrapi/ibclient.py`: one shared `IB()` instance, single-flight connect, reconnect with exponential backoff that never gives up.
  - `ibkrapi/marketdata.py`: qualify, contract details, snapshot ticks, historical bars and ticks, and the wickworks POST for `/rates/ta`.
  - `ibkrapi/pacing.py`, `cache_bars.py`, `cache_meta.py`, `historian.py`, `exec_history.py`: rate-limit gate and the four on-disk stores under `data/history/`.
  - `ibkrapi/mcp_server.py`: FastMCP server with 24 tools. Each tool calls the same app in process through `httpx.ASGITransport`, so auth, validation and handlers are shared with REST.
- `nginx` service: publishes the API on `127.0.0.1:8889` by default and proxies everything to `api:8889`.
- `wickworks` service (optional): TA sidecar on an `internal` network with no egress; `api` POSTs bars to it.

Data flow: client -> nginx -> api (FastAPI middleware -> generated router -> `impl` -> `pacing.guard` -> `ib_async`) -> ibgateway (TWS socket) -> IBKR. `/rates/ta` adds api -> wickworks.

## Stack

- Python 3.12 (`python:3.12-slim-bookworm` by digest), FastAPI 0.136, Starlette 1.3, uvicorn 0.49, Pydantic 2.13, `ib_async` 2.1.0, `mcp` 1.27, PyYAML. Pins in `requirements.in`, hash-locked in `requirements.txt`.
- Codegen: fastapi-code-generator, oapi-codegen (Go client), openapi-python-client (Python client). Lint: ruff, pyright, bandit. Tests: pytest with pytest-asyncio. All in the dev image from `Dockerfile.dev`.
- IB Gateway with IBC from gnzsnz/ib-gateway-docker, nginx 1.27-alpine by digest, optional psyb0t/docker-wickworks.

## Layout

| Path | Contents |
| --- | --- |
| `api/v1.yaml` | OpenAPI 3.1.0 spec, the source of truth for all generators. |
| `api/_templates/` | Jinja templates that make fastapi-code-generator emit `async def` handlers delegating to `impl`. |
| `api/oapi-codegen-go.yaml` | Go client generator config. |
| `ibkrapi/` | The Python package (the `api` service). |
| `ibkrapi/api/_generated/` | Generated routers and models. Never hand-edit. |
| `ibkrapi/api/impl.py` | Hand-written endpoint logic. |
| `ibkrapi/routers/_constants.py` | Shared string constants (sec types, order types, asset aliases). |
| `pkg/clients/go/`, `pkg/clients/python/` | Generated typed clients, each installable from this repository. |
| `tests/` | pytest suite with a mocked `IB` (`conftest.py`). |
| `config/config.yaml.example` | Every config key with comments. The real `config/config.yaml` is gitignored. |
| `.env.ibkr.example` | Gateway login template. The real `.env.ibkr` is gitignored. |
| `docker-compose.yml.example`, `nginx/nginx.conf.example` | Stack and proxy templates. `run.sh` copies them into place. |
| `Dockerfile.api`, `Dockerfile.dev`, `Dockerfile.novnc` | Production image, dev and lint image, optional noVNC proxy (not wired into compose). |
| `scripts/` | Age-gate bump, Go module age check, compose audit, the one-time v0.3.0 spec patch. |
| `docs/` | The documentation site (Jekyll, just-the-docs), published from `main` at https://psyb0t.github.io/ibkr-httpapi/. |
| `.agents/skills/ibkr-httpapi/` | Client skill for agents talking to a running server. |
| `.agents/plugins/ibkr-httpapi/` | OpenClaw stdio-to-HTTP MCP bridge (`mcp-remote`). |
| `.agents/.claude-plugin/`, `.agents/.codex-plugin/` | Plugin manifests for the psyb0t/agents marketplace. |
| `.agents/rules/` | Rules for every change. |
| `.github/workflows/pipeline.yml` | CI: lint and tests, badges, release, ClawHub publish. |

## Commands

Docker and Make are enough; lint, tests and codegen run in the dev container.

```bash
make help                 # every target
make lint                 # ruff + pyright + bandit (what CI runs)
make test                 # pytest (what CI runs)
make format               # ruff format
make generate             # regenerate routers, models and both clients from api/v1.yaml
make generate-api-check   # fail if ibkrapi/api/_generated drifts from the spec
make audit                # pip-audit on requirements.txt
make audit-compose        # hardening check on the compose files
make docs                 # build the documentation site with GitHub's Pages image
make up                   # ./run.sh: check config, seed compose and nginx files, compose up
make down                 # docker compose down
make logs                 # follow compose logs
```

## Project-specific landmines

- Generated handlers call `impl` with positional arguments in spec order, `refresh` before `body`. A reordered impl signature silently swaps values; the `/rates/ta` routes once received `body=False` and returned 500. Read `.agents/rules/codegen.md` before touching an impl signature.
- `ibkrapi/config.py` reads `config/config.yaml`, CLI flags and the environment once at import time into module constants. Tests that change a setting must reload `ibkrapi.config` and every module that imported the constant.
- `ibclient.get_ib()` retries forever with backoff up to `reconnect_max_backoff`. While the gateway is down, every request (including `/v1/ping`) waits instead of failing, and nginx gives up after its 300 s `proxy_read_timeout`.
- The bars cache is an archive, not a read cache: `/rates` always fetches from IBKR. Only the meta cache (contract details, futures lists, chain strike lists) serves hits from disk.
- Open bug: `cache_bars.get_or_fetch` receives bars whose `time` is an ISO string from `serialize.bar_dict`, and `_drop_open_bar` adds an int to it, so with `history_cache.enabled: true` any `/rates` or `/rates/ta` call that returns bars fails with `TypeError`. The tests do not catch it because `conftest.py` turns the cache off.
- One TWS API connection per `clientId` per gateway login. A second process with the same `client_id` disconnects the first.
- `config.yaml` keys `ibkr_login` and `tailscale` are not read by any code. Gateway credentials come only from `.env.ibkr`.
- The MCP `get_rates`, `get_rates_ta` and `get_stock_ticks` tools default `use_rth` to `true`; the REST `useRTH` default is `false`.
- Option exercise works because this project uses the TWS socket API; the Client Portal REST API has no exercise call.
- IBKR Lite accounts have the API disabled. Real-time option quotes and Greeks need an OPRA subscription and `market_data_type: 1`.

## Rules

Rules for every change: `.agents/rules/`. Read the ones that match what you are touching before editing.
