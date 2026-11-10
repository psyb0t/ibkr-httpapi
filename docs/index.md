---
title: "Home"
description: "ibkr-httpapi puts Interactive Brokers behind curl and JSON: market data, positions and orders for six asset classes over REST and MCP, self-hosted."
nav_order: 1
permalink: /
seo:
  type: WebSite
---

# ibkr-httpapi

ibkr-httpapi is a self-hosted HTTP API over Interactive Brokers. A FastAPI app talks to a local IB Gateway container through [ib_async](https://github.com/ib-api-reloaded/ib_async), so you get contract details, quotes, historical bars, option chains with Greeks, account state, positions and order entry as plain JSON over curl. The same operations are also typed MCP tools at `/mcp` for agents.

It is the Interactive Brokers half of [mt5-httpapi](https://github.com/psyb0t/mt5-httpapi), with the same asset-class routing. MT5 needs a Windows VM. IB Gateway runs on Linux, so this whole stack is four Linux containers.

```bash
curl -s -H "Authorization: Bearer $API_TOKEN" \
  "http://localhost:8889/v1/stocks/AAPL/rates?duration=30+D&barSize=1d"
```

This drives a real brokerage account. `POST /v1/orders` places a real order. Start on a paper account (`TRADING_MODE=paper`) and keep the API on loopback until a token is set.

## What's in the box

| Part | What it does |
| --- | --- |
| REST API under `/v1` | 42 operations across `/stocks`, `/options`, `/futures`, `/cfd`, `/forex`, `/crypto`, plus `/orders`, `/positions`, `/account`, `/accounts`, `/history` and `/ping`. |
| MCP at `/mcp` | 24 typed tools over the same handlers, with the same bearer token. |
| IB Gateway container | IB Gateway and IBC from gnzsnz/ib-gateway-docker. IBC logs in unattended and restarts the gateway daily. |
| Pacing gate | Refuses a request with `429 RATE_LIMIT_NEAR` before IBKR's own pacing limits would trip. |
| Disk stores | Every bar, tick snapshot, option chain, execution and completed order you fetch is appended under `data/history/`. |
| TA sidecar (optional) | `POST .../rates/ta` sends bars to [wickworks](https://github.com/psyb0t/docker-wickworks) and returns them with indicator series. |
| Typed clients | A Go client and a Python client generated from the OpenAPI spec. |

## What you need

- An IBKR Pro account. IBKR Lite has the API turned off.
- IBKR Mobile paired with the account, for the weekly 2FA push.
- A Linux host with Docker and Docker Compose.
- An IB Gateway image you build yourself. IBKR's license forbids redistributing images that contain the gateway installer, so nobody can hand you one.
- For real-time option quotes and Greeks, an OPRA market data subscription. Free delayed data works for daily and hourly bars.

## Where to go next

| You want to | Read |
| --- | --- |
| Get from nothing to a working `/v1/ping` | [Getting started](getting-started.md) |
| Understand the containers, ports, networks and data on disk | [Deployment](deployment.md) |
| Look up a config key or environment variable | [Configuration](configuration.md) |
| Call an endpoint | [REST API](api.md) |
| Connect an MCP client | [MCP server](mcp.md) |
| Know what gets rate-limited and what gets saved to disk | [Pacing and history](pacing-and-history.md) |
| Use the Go or Python client | [Client libraries](clients.md) |
| Install the agent skill or plugin | [Agent integrations](agent-integrations.md) |
| Put it on a network | [Security](security.md) |
| Fix a request that hangs or a 429 | [Troubleshooting](troubleshooting.md) |
| Change the code or run the tests | [Development](development.md) |
