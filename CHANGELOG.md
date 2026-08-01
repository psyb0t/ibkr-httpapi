# Changelog

All notable changes per release. Versions follow [semver](https://semver.org)
pre-1.0 conventions: minor bumps may include breaking REST changes (called
out explicitly), patch bumps are docs / build / fixes only.

## v0.5.5 — 2026-08-01

Infrastructure only. No code in this repo changed — every commit since v0.5.4
touches `.github/workflows/`.

- The pipeline was split: building and publishing stay in `pipeline.yml`, and
  everything that leaves the host now lives beside it in `mirror-and-archive.yml`.
- The repo is mirrored to Codeberg as well as GitLab.
- It is archived to the Wayback Machine, Software Heritage and archive.org.
- Issues opened on either mirror are copied back to GitHub every six hours, and
  closed here when the original closes.
- Pull requests are switched off on the mirrors: they are force-pushed from
  GitHub, so anything merged there would be destroyed by the next sync. Issues
  and forking stay enabled.

## v0.5.4 — 2026-07-27

- Fixed the **Agent integrations** README section: the Codex subsection was missing its
  install command. It now reads `codex plugin add ibkr-httpapi@psyb0t` right after the
  marketplace-add line, matching the Claude Code subsection above it.
- Clarified that the skill's invocation form differs by install path: via the marketplace
  it invokes as `$ibkr-httpapi:ibkr-httpapi`; picked up automatically from this repo's own
  `.agents/skills/` (no install needed) it invokes as plain `$ibkr-httpapi`.

## v0.5.3 — 2026-07-27

- Added `.agents/.claude-plugin/plugin.json` and `.agents/.codex-plugin/plugin.json` so the
  existing `ibkr-httpapi` skill and OpenClaw MCP-bridge plugin install natively in Claude Code
  and Codex from the central `psyb0t/agents` marketplace.
- Added a top-level **Agent integrations** README section (with matching Table of Contents
  entry) documenting the Claude Code, Codex, and OpenClaw install commands, including the
  `@psyb0t/ibkr-httpapi` MCP-bridge plugin.

## v0.5.2 — 2026-07-27

- Added a GitHub Actions CI status badge to the README.

## v0.5.1 — 2026-07-27

- Added self-hosted version and license badges; wired a badges job into pipeline.yml.

## v0.5.0 — 2026-07-26

MCP interface reworked from a generic passthrough to dedicated, typed tools.

- **`/mcp` now exposes ~24 dedicated typed tools** grouped by family, with the 6 asset classes collapsed behind an `asset_class` enum: `get_contract` / `get_quote` / `get_rates` / `get_rates_ta` replace 24 near-duplicate per-class routes, plus option/future specials (`get_option_chain`, `place_option_combo`, `exercise_option`, `get_future_continuous`, `list_future_contracts`), orders (`list_orders`, `get_order`, `place_order`, `cancel_order`, `cancel_all_orders`), account/positions (`get_account`, `get_account_values`, `list_accounts`, `list_positions`), and history/health. Each tool has typed params + a description the agent reads — the schema IS the documentation. Order/exercise tools carry an irreversible-live-account note. A generic `request` + `endpoints` catalog remain as a fallback. Every tool runs the same routers/validation/auth in-process. README + skill + plugin docs updated.
- `mcp_server.py` now logs via the project's `ibkrapi.logger.log` (structured), matching the rest of the package.

## v0.4.0 — 2026-07-26

New MCP interface — ibkr-httpapi is now also driveable over the Model Context Protocol.

- **MCP server mounted at `/mcp`** (streamable-HTTP), in the same FastAPI app as the REST API. Three tools mirror the whole REST surface: `ping` (gateway liveness), `endpoints` (the live OpenAPI route catalog), and `request(method, path, query, body)` — call any `/v1` endpoint, running the same handler + auth in-process. Same bearer auth as REST (empty `API_TOKEN` = off). See `ibkrapi/mcp_server.py`. New deps `mcp` + `httpx`, re-locked into `requirements.txt`.
- **`@psyb0t/ibkr-httpapi` ClawHub plugin** (`.agents/plugins/ibkr-httpapi/`) — a stdio↔HTTP `mcp-remote` bridge. Set `IBKR_HTTPAPI_URL` (the server root — a trailing `/v1` is stripped) plus `IBKR_HTTPAPI_TOKEN` if auth is on. **Note:** `/mcp` lives at the app root, not under `/v1`. CI publishes it to ClawHub alongside the skill.
- README and the `ibkr-httpapi` skill gain an **MCP interface** section. No REST endpoint change (additive).

## v0.3.4 — 2026-07-26

Security-documentation hardening for the `ibkr-httpapi` skill: no behavior
change, only warnings and agent guardrails. Adds a `## Security & safety`
section covering the destructive/irreversible nature of order placement,
cancellation, and exercise; the unauthenticated-when-`API_TOKEN`-unset
posture; and the outbound data flow to `IBKR_HTTPAPI_URL`. Strengthens the
existing order-placement confirmation rule to require echoing back
symbol/side/quantity/price before every order and to explicitly forbid
auto-retrying a rejected order.

## v0.3.3 — 2026-07-25

CI: publish the skill via `clawhub-publish.yml` directly — the
`clawhub-skills-publish-workflow.yml` shim was removed upstream. No code or API change.

## v0.3.0 — 2026-06-20

Closes the three deferred items from v0.2.0: `?refresh=true` query
param, `429 RATE_LIMIT_NEAR` documented in the OpenAPI spec, and
`/rates/ta` endpoints now hit the bars cache.

### Spec — v1.yaml additions (24 ops gain refresh, 36 gain 429)

- **New parameter** `RefreshQuery` (boolean, default false) — added to
  every cacheable endpoint. Setting `?refresh=true` bypasses the disk
  cache on read; the freshly-fetched value is still written back so
  subsequent requests benefit.
- **New response** `RateLimitNear` (429) — documented on every
  IBKR-bound endpoint (24 cacheable + 6 `/tick` + 6 order/exercise/
  cancel ops). Body uses the standard `ErrorEnvelope` with code
  `RATE_LIMIT_NEAR` + details `{rule, used, limit, window_sec,
  retry_after_sec, tier}`.
- `scripts/patch_spec_v030.py` — idempotent script that applies these
  refs across the spec by `operationId`. Run once; `make generate`
  picks up the rest.

### Impl — refresh plumbed through every cacheable path

- `_cached_bars`, `_cached_details`, `_paced_rates_ta` helpers accept
  `refresh: bool = False` kwarg and pass to the underlying cache call.
- 22 cacheable impl functions updated to accept the generated `refresh`
  arg and thread it through. `/stocks/ticks`, `/history/executions`,
  `/history/completed_orders` accept the arg too (no-op for now since
  those endpoints don't read a cache — the param is reserved for
  future ticks/exec cache reads).
- Generated FastAPI routers, Go client, Python client all regenerated.

### `/rates/ta` now hits the bars cache (deferred from v0.2.0)

- `marketdata.rates_with_ta` refactored into two phases:
  - `rates_with_ta` (legacy combined call — kept for back-compat) still
    does fetch + enrich in one step.
  - **`marketdata.ta_enrich(contract, bars, *, indicators, recent_bars)`**
    — new pure-enrichment helper that takes pre-fetched bars.
- `impl._paced_rates_ta` now composes `_cached_bars` + `ta_enrich`, so
  every `/rates/ta` request:
  - hits the same per-(class, symbol, timeframe) CSV cache `/rates`
    does (growing the goldmine on TA requests too);
  - applies pacing once per call (historical tier), accounting for
    both phases under one budget;
  - returns the same wickworks-enriched payload.

### Tests / quality gates

- **142 tests pass**, ruff + bandit + `make audit` + `make audit-compose` all clean.
- No new test files needed — the new behavior composes existing
  primitives (cache_bars + cache_meta + ta_enrich) each of which is
  unit-tested.

### Files

- `api/v1.yaml` — RefreshQuery + RateLimitNear components, refs on 24 + 36 ops
- `ibkrapi/api/_generated/{models,routers}/*` — regenerated
- `pkg/clients/{go,python}/*` — regenerated
- `ibkrapi/api/impl.py` — refresh plumbing, ta_enrich composition
- `ibkrapi/marketdata.py` — split out `ta_enrich`
- `pyproject.toml` + `ibkrapi/server.py` — version 0.3.0
- `scripts/patch_spec_v030.py` — one-shot spec patch helper

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
