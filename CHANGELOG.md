# Changelog

All notable changes per release. Versions follow [semver](https://semver.org)
pre-1.0 conventions: minor bumps may include breaking REST changes (called
out explicitly), patch bumps are docs / build / fixes only.

## v0.2.0 — 2026-06-20

Preemptive IBKR pacing + transparent disk caching for every endpoint
that returns historical / quasi-static / piggyback-snapshottable data.
Goal: protect API access (IBKR revokes for repeat pacing violations)
AND grow a long-term goldmine of market data on every call.

### Pacing — preemptive rate-limit gate

- **Three tiers** with separate sliding-window counters, per-contract
  `asyncio.Lock` serialization, and global `asyncio.Semaphore`
  concurrency caps:
  - `historical` — gated against IBKR's 60-requests-per-10-min hard cap
    (default soft 50 / hard 55, leaves 5-request headroom).
  - `market_data` — gated under the ~50-msg/sec TWS socket ceiling
    (default 40/sec, 10 concurrent).
  - `orders` — deliberately tight (5/sec, 3 concurrent — order floods
    signal a bug).
- **Soft cap → `WARN` log** so operators see they're approaching the
  limit. **Hard cap → `429 RATE_LIMIT_NEAR`** error envelope with
  `{rule, used, limit, window_sec, retry_after_sec, tier}` details.
- Per-contract per-second cap mirrors IBKR's "2 hist requests / sec /
  contract" rule.
- All three tiers configurable via `config.yaml:pacing.<tier>.<key>`.

### History caches — every history endpoint cached transparently

- **`ibkrapi/cache_bars.py`** — per-(class, symbol, timeframe) CSV cache
  for `/rates` and `/ticks`. Wickworks-shaped (`time,open,high,low,
  close,tickVolume` with epoch seconds). Per-file `asyncio.Lock`. Bars
  merged + persisted on every call so the cache file grows append-only
  forever. Latest tail bars always re-pulled (`refresh_tail_bars: 5`).
  Open bars dropped by default (`persist_open_bar: false`). Atomic
  write via tmp+rename. Options grouped under per-underlying subdir
  (`data/history/options/SPY/<OCC>_<TF>.csv`).
- **`ibkrapi/cache_meta.py`** — long-TTL JSON cache for quasi-static
  metadata: contract details (7-day TTL), futures expiry lists (1 day),
  option chain strike lists (1 day). Per-key single-flight via
  `asyncio.Lock` prevents stampede on miss.
- **`ibkrapi/historian.py`** — live-snapshot piggyback. Every `/tick`
  appends a row to `data/history/snapshots/<class>/<symbol>.csv` with
  bid/ask/last + Greeks/IV for options. Every `/chain` appends rows
  per strike per expiry to
  `data/history/chains/<UNDERLYING>/<EXPIRY>.csv`. Writes are
  best-effort — a historian failure NEVER blocks the caller's
  response.
- **`ibkrapi/exec_history.py`** — append-only JSONL ledger of fills
  + completed orders at `data/history/exec/{executions,completed_orders}/
  YYYY-MM-DD.jsonl`. Dedup by execId for fills, (permId, orderId) for
  completed orders.
- **All caches OFF by default in tests** (`tests/conftest.py` autouse
  fixture); ON by default in prod via `history_cache.enabled: true` +
  friends in `config.yaml`.

### Compose / persistence

- New volume: `./data:/app/data` mounted into the `api` service so the
  cache + historian + meta + exec ledger persist across container
  recreates. Back this directory up — it IS the goldmine.
- `data/` added to `.gitignore` (the cache contents must NEVER enter
  git; data growth is unbounded over time).

### IBKR data redistribution — internal-use only

IBKR market data terms restrict redistribution. Selling raw OHLC
sourced via IBKR API access can violate OPRA / NYSE / Nasdaq
redistributor licenses + IBKR's API license. What IS fine: using the
cache for your own backtesting / strategy training / forensics
(IBKR explicitly allows this), and selling **derived analysis**
(signals, indicators, backtest results, aggregated statistics) that
aren't reconstructible into the original prints. Design the cache as
internal infrastructure; sell what you compute from it.

### Tests

- 49 new tests across `test_{pacing,cache_bars,historian,cache_meta,
  exec_history}.py`. **142 tests total, all green.**
- Conftest autouse fixture disables all persistence + seeds pacing
  with permissive limits so existing test_server.py tests are
  unaffected by the new wiring.

### Known v0.2.0 gaps (planned for v0.3.0)

- `?refresh=true` query param to bypass cache — needs `api/v1.yaml`
  update + regen + impl signature changes across 40+ ops; deferred.
- `429 RATE_LIMIT_NEAR` response not yet documented in `api/v1.yaml`
  (works at runtime; spec doc deferred to v0.3.0).
- `/rates/ta` endpoints are pacing-gated but bars NOT yet cached —
  needs splitting `marketdata.rates_with_ta` into separate cache +
  TA-enrichment phases; deferred.

## v0.1.0 — 2026-06-20

Initial public release. HTTP wrapper over Interactive Brokers via `ib_async`
and a Linux-native IB Gateway container, mirroring the operational shape of
sister project `mt5-httpapi` but without the Windows VM.

### Highlights

- **Spec-first API** — `api/v1.yaml` (OpenAPI 3.1.0, 42 operations, 34 schemas) is the source of truth. Every endpoint is reachable under `/v1/...` per Option B versioning (`servers: [{url: /v1}]`).
- **Generated FastAPI server** — `make generate-api` produces `ibkrapi/api/_generated/{models.py, routers/*.py}` via `fastapi-codegen` + custom Jinja templates that emit `async def` handlers delegating to hand-written `ibkrapi/api/impl.py`.
- **Generated Go client** — `make generate-client-go` emits `pkg/clients/go/client.gen.go` (full typed client + types) via `oapi-codegen v2.7.1`. Importable as `github.com/psyb0t/ibkr-httpapi/pkg/clients/go`.
- **Generated Python client** — `make generate-client-python` emits `pkg/clients/python/ibkr-httpapi-client/` (standalone Poetry package) via `openapi-python-client 0.29.0`. Installable via `pip install "git+https://github.com/psyb0t/ibkr-httpapi.git#subdirectory=pkg/clients/python/ibkr-httpapi-client"`.

### Asset surface

- `/v1/stocks/{symbol}` + `/tick` + `/rates` + `/ticks` + `/rates/ta`
- `/v1/options/{symbol}` + `/chain` + `/tick` + `/rates` + `/rates/ta`, plus `/v1/options/combo` (multi-leg BAG) + `/v1/options/exercise`
- `/v1/futures/{symbol}` + `/continuous` + `/contracts` + `/tick` + `/rates` + `/rates/ta`
- `/v1/cfd/{symbol}` + `/tick` + `/rates` + `/rates/ta`
- `/v1/forex/{pair}` + `/tick` + `/rates` + `/rates/ta`
- `/v1/crypto/{symbol}` + `/tick` + `/rates` + `/rates/ta`
- `/v1/orders` POST/GET/DELETE + `/v1/orders/{orderId}` GET/DELETE
- `/v1/history/executions` + `/v1/history/completed_orders`
- `/v1/ping` + `/v1/accounts` + `/v1/account` + `/v1/account/values` + `/v1/positions`

### Stack

- **Python 3.12** + FastAPI 0.136.3 + uvicorn 0.49.0 + Pydantic 2.13.4 + `ib_async` 2.1.0. Asyncio everywhere.
- **Docker stack:** `api` (FastAPI) + `ibgateway` (gnzsnz/ib-gateway-docker with IBC auto-login + daily relogin) + `nginx` front (loopback-only) + `novnc` websockify proxy (browser-accessible IB Gateway desktop on `:8006`).
- Base images SHA-pinned. `requirements.txt` hash-locked via `uv pip compile --generate-hashes` with 7-day age-gate.
- Multi-stage `Dockerfile.api` with non-root user, `read_only: true`, `cap_drop: ALL`, `no-new-privileges:true`, memory/cpu/pids limits.

### Security

- Bearer-token auth via `Authorization: Bearer <token>` — token loaded from `config.yaml.api_token` OR `API_TOKEN` env. Constant-time compare via `hmac.compare_digest`. Empty token = no auth (open localhost-only).
- aichteeteapee error envelope on every error response (`{code, message, details}`).
- SSRF defense on the wickworks outbound HTTP — explicit `http://`/`https://` scheme allowlist before `urllib.request.urlopen`.
- Bandit + ruff (E/F/W/I/UP/B/S/C4/SIM/RUF) clean.

### Supply chain

- **Age-gate** lives in `pyproject.toml` `[tool.uv] exclude-newer` as a fixed timestamp — bumped to `today_utc - 7 days` by `scripts/bump_exclude_newer.sh` on every Python dep mutation (`make pkg-add` / `pkg-update` / `pkg-upgrade` / `pkg-remove`). `make pkg-lock` reads the value; never bumps.
- **Hash-locked** `requirements.txt` via `uv pip compile --generate-hashes`. Docker installs with `pip install --require-hashes`.
- **CVE scan**: `make audit` runs `pip-audit` against `requirements.txt`. Clean at release time (`starlette` pinned directly to `1.3.1` to dodge [GHSA-82w8-qh3p-5jfq](https://github.com/advisories/GHSA-82w8-qh3p-5jfq) — DoS via `request.form()` ignoring `max_fields`/`max_part_size` on `application/x-www-form-urlencoded`).
- **Go client** (`pkg/clients/go/`): `scripts/check_go_age.sh` hits `proxy.golang.org/<mod>/@v/<ver>.info` and refuses any module published within 7 days. Wired into `make pkg-add-go` / `pkg-upgrade-go`. `make audit-go` runs `govulncheck`.
- **Base images** SHA-digest pinned (`python@sha256:76d4b7...`) across all 3 Dockerfiles. No mutable tags anywhere.
- **Compose hardening** — `docker-compose.yml.example` audited end-to-end per the container-hardening rule: loopback-default port publishing (nginx publishes via `${API_HOST_BIND:-127.0.0.1}:${API_HOST_PORT:-8889}:80` — override `API_HOST_BIND=0.0.0.0` only with a TLS terminator in front or tailnet exposure), isolated networks (`front` for nginx+api, `backend` for api+ibgateway, `internal: true` for api+wickworks — wickworks has zero egress), `cap_drop:[ALL]` + `no-new-privileges` + `read_only:true` + `tmpfs(noexec,nosuid,size=)` on every app service, `init: true` for proper signal/zombie handling, per-service resource caps (`memory`/`cpus`/`pids`), per-service healthchecks + `depends_on: condition: service_healthy`, log driver caps (`max-size: 10m`, `max-file: 5`). `make audit-compose` runs `scripts/audit_compose.sh` which greps for banned settings (`privileged`, `pid:host`, `ipc:host`, `network:host`, `docker.sock` mounts, `SYS_ADMIN`), unpinned image tags, and public-bound ports.

### Tests

- 93 tests across `tests/test_{config,contracts,errors,marketdata,serialize,server}.py` — pure logic, mocked `ib_async` via `conftest.py`.
- Test coverage includes NaN-scrub regression, auth (missing/bad/good/non-bearer token), error envelope shape, route validation envelopes.
- `tests/integration/` reserved for live-gateway tests (opt-in via `IBKR_INTEGRATION=1`).
