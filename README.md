# ibkr-httpapi

[![CI](https://github.com/psyb0t/ibkr-httpapi/actions/workflows/pipeline.yml/badge.svg?branch=main)](https://github.com/psyb0t/ibkr-httpapi/actions/workflows/pipeline.yml)
[![version](https://raw.githubusercontent.com/psyb0t/ibkr-httpapi/badges/version.svg)](https://github.com/psyb0t/ibkr-httpapi/releases)
[![license](https://raw.githubusercontent.com/psyb0t/ibkr-httpapi/badges/license.svg)](https://github.com/psyb0t/ibkr-httpapi/blob/main/LICENSE)

Interactive Brokers over curl and JSON. A FastAPI app drives a local IB Gateway container through [ib_async](https://github.com/ib-api-reloaded/ib_async) and gives you contracts, quotes, historical bars, option chains with Greeks, positions, account data and order entry for stocks, options, futures, CFDs, forex and crypto. The same operations are typed MCP tools at `/mcp`, and server-side TA comes from the [wickworks](https://github.com/psyb0t/docker-wickworks) sidecar.

It is the IBKR half of [mt5-httpapi](https://github.com/psyb0t/mt5-httpapi), same shape. MT5 needs a Windows VM; IB Gateway runs on Linux, so this is just Linux containers.

This talks to a real brokerage account. `POST /v1/orders` places real orders. Start on a paper login and keep it on loopback until `api_token` is set.

## Contents

- [Quick start](#quick-start)
- [Routes](#routes)
- [MCP and agents](#mcp-and-agents)
- [Documentation](#documentation)
- [Development](#development)
- [Sponsor](#sponsor)
- [License](#license)

## Quick start

You need an IBKR Pro account (Lite has no API), IBKR Mobile for 2FA, Docker with Compose, Make, and `python3` with PyYAML on the host.

```bash
git clone https://github.com/psyb0t/ibkr-httpapi
cd ibkr-httpapi
cp config/config.yaml.example config/config.yaml   # set api_token and market_data_type
cp .env.ibkr.example .env.ibkr                     # TWS_USERID, TWS_PASSWORD, TRADING_MODE=paper
make up
```

Approve the 2FA push on your phone when the gateway logs in, then:

```bash
curl -s -H "Authorization: Bearer $API_TOKEN" http://localhost:8889/v1/ping

curl -s -H "Authorization: Bearer $API_TOKEN" \
  "http://localhost:8889/v1/stocks/AAPL/rates?duration=30+D&barSize=1d"
```

IBKR's license forbids redistributing images that contain IB Gateway, so build one from [gnzsnz/ib-gateway-docker](https://github.com/gnzsnz/ib-gateway-docker) and set `IBKR_GATEWAY_IMAGE`. The full walkthrough, including the gateway image and the config keys that matter, is in [Getting started](https://psyb0t.github.io/ibkr-httpapi/getting-started/).

## Routes

Everything lives under `/v1`. The asset class is the URL prefix:

| Prefix | Asset class |
| --- | --- |
| `/stocks/{symbol}` | Equities |
| `/options/{symbol}` | Options, plus `/chain`, `/options/combo` and `/options/exercise` |
| `/futures/{symbol}` | Futures, plus `/continuous` and `/contracts` |
| `/cfd/{symbol}` | CFDs |
| `/forex/{pair}` | Currency pairs |
| `/crypto/{symbol}` | Crypto |

Each class has `GET /{symbol}` (contract details), `/tick` (snapshot quote), `/rates` (OHLC bars) and `POST /rates/ta` (bars plus indicators); stocks also have `/ticks`. Cross-asset routes are `/orders`, `/positions`, `/account`, `/account/values`, `/accounts`, `/history/executions`, `/history/completed_orders` and `/ping`. Every parameter and response is in the [REST API reference](https://psyb0t.github.io/ibkr-httpapi/api/).

A pacing gate answers `429 RATE_LIMIT_NEAR` before IBKR's own limits would trip, and bars, quote snapshots, option chains and executions you fetch are appended under `data/history/`. See [Pacing and history](https://psyb0t.github.io/ibkr-httpapi/pacing-and-history/).

## MCP and agents

`http://localhost:8889/mcp` serves 24 typed MCP tools over the same handlers and the same bearer token. The client skill installs in Claude Code and Codex from the psyb0t/agents marketplace and in OpenClaw from ClawHub, and an OpenClaw plugin bridges `/mcp` to stdio-only clients:

```bash
claude plugin marketplace add psyb0t/agents
claude plugin install ibkr-httpapi@psyb0t
```

Details: [MCP server](https://psyb0t.github.io/ibkr-httpapi/mcp/) and [Agent integrations](https://psyb0t.github.io/ibkr-httpapi/agent-integrations/).

## Documentation

The full documentation is at **https://psyb0t.github.io/ibkr-httpapi/**.

| Page | What's there |
| --- | --- |
| [Getting started](https://psyb0t.github.io/ibkr-httpapi/getting-started/) | Clone to a working `/v1/ping`, step by step. |
| [Deployment](https://psyb0t.github.io/ibkr-httpapi/deployment/) | Services, networks, ports, state on disk, upgrades, the daily restart. |
| [Configuration](https://psyb0t.github.io/ibkr-httpapi/configuration/) | Every `config.yaml` key, environment variable and flag. |
| [REST API](https://psyb0t.github.io/ibkr-httpapi/api/) | All 42 operations, errors and rate limits. |
| [MCP server](https://psyb0t.github.io/ibkr-httpapi/mcp/) | The `/mcp` endpoint and its tools. |
| [Pacing and history](https://psyb0t.github.io/ibkr-httpapi/pacing-and-history/) | Rate limiting and what gets written to `data/history/`. |
| [Client libraries](https://psyb0t.github.io/ibkr-httpapi/clients/) | Generated Go and Python clients. |
| [Agent integrations](https://psyb0t.github.io/ibkr-httpapi/agent-integrations/) | Claude Code, Codex and OpenClaw. |
| [Security](https://psyb0t.github.io/ibkr-httpapi/security/) | What the token protects and what to do before exposing it. |
| [Troubleshooting](https://psyb0t.github.io/ibkr-httpapi/troubleshooting/) | Hanging requests, connection failures, known bugs. |
| [Development](https://psyb0t.github.io/ibkr-httpapi/development/) | Layout, tests, code generation, CI, releases. |

## Development

Lint, tests and code generation run in a dev container, so Docker and Make are enough:

```bash
make lint      # ruff, pyright, bandit
make test      # pytest with a mocked IB connection
make generate  # routers, models and clients from api/v1.yaml
make help      # everything else
```

[`api/v1.yaml`](https://github.com/psyb0t/ibkr-httpapi/blob/main/api/v1.yaml) is the source of truth; never edit generated code. Agent and contributor rules are in [`AGENTS.md`](https://github.com/psyb0t/ibkr-httpapi/blob/main/AGENTS.md). Release notes: [`CHANGELOG.md`](https://github.com/psyb0t/ibkr-httpapi/blob/main/CHANGELOG.md).

## Sponsor

<a href="https://www.buymeacoffee.com/psyb0t"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me a Coffee" height="60" width="217"></a>

## License

[WTFPL](https://github.com/psyb0t/ibkr-httpapi/blob/main/LICENSE).
