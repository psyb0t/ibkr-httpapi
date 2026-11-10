---
title: "MCP server"
description: "The /mcp endpoint: 24 typed Model Context Protocol tools over the same handlers and bearer token as REST, with every tool's parameters and limits."
nav_order: 6
---

# MCP server

The API also speaks the [Model Context Protocol](https://modelcontextprotocol.io) at `/mcp`, in the same process and on the same port as REST. It uses the streamable HTTP transport in stateless mode with JSON responses, so any MCP client that supports remote HTTP servers can connect without a bridge. For clients that only run local stdio servers, the [OpenClaw plugin](agent-integrations.md#openclaw-plugin) is a stdio-to-HTTP bridge.

The MCP server lives in [`ibkrapi/mcp_server.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/mcp_server.py).

## Connecting

- URL: `http://localhost:8889/mcp`. That is the app root, not the `/v1` REST prefix. A bare `/mcp` works; the app rewrites it to `/mcp/` so clients that do not follow redirects on POST still connect.
- Auth: the same bearer token as REST, enforced by the same middleware. An empty `api_token` leaves `/mcp` open as well.
- Host checks: the SDK's DNS rebinding protection is off, so the endpoint answers on any `Host`. Network access control belongs to your proxy or firewall.

```bash
curl -s http://localhost:8889/mcp \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "ping",
      "arguments": {}
    }
  }'
```

## How tools work

Each tool builds a REST request and sends it to the same FastAPI app in process through `httpx.ASGITransport`, adding the server's own `API_TOKEN`. Validation, pacing, caching and error envelopes are exactly those of the [REST API](api.md). Every tool returns:

```json
{
  "status": 200,
  "body": {
    "status": "ok",
    "connected": true
  }
}
```

`status` is the HTTP status the REST handler produced and `body` is its JSON (or `{"raw": "<text>"}` for a non-JSON body). An error shows up as a 4xx or 5xx `status` with the usual `{"code", "message", "details"}` body, not as an MCP protocol error. The in-process call times out after 120 seconds.

Empty strings, `0` for `strike`, `lmt_price`, `aux_price`, `recent_bars`, `client_id` and `underlying_con_id`, and `None` are dropped before the request is built, so the server-side defaults apply.

## Tools

`asset_class` is one of `stock`, `option`, `future`, `cfd`, `forex`, `crypto`. For `forex`, `symbol` is the pair, such as `EURUSD`.

### Market data

| Tool | Parameters | REST call |
| --- | --- | --- |
| `get_contract` | `asset_class`, `symbol`, `exchange`, `currency`, `expiry`, `strike`, `right` | `GET /v1/<class>/{symbol}` |
| `get_quote` | same as `get_contract` | `GET /v1/<class>/{symbol}/tick` |
| `get_rates` | `asset_class`, `symbol`, `duration`, `bar_size`, `end_date_time`, `what_to_show`, `use_rth` (default `true`), `exchange`, `currency`, `expiry`, `strike`, `right` | `GET /v1/<class>/{symbol}/rates` |
| `get_rates_ta` | `get_rates` parameters plus `indicators` (required object) and `recent_bars` | `POST /v1/<class>/{symbol}/rates/ta` |
| `get_stock_ticks` | `symbol`, `start_date_time`, `end_date_time`, `number_of_ticks` (default 1000), `what_to_show`, `use_rth` (default `true`), `exchange`, `currency`, `primary_exchange` | `GET /v1/stocks/{symbol}/ticks` |

Options need `expiry`, `strike` and `right`; futures need `expiry` and `exchange`. Note that `use_rth` defaults to `true` here while the REST `useRTH` defaults to `false`.

### Options and futures

| Tool | Parameters | REST call |
| --- | --- | --- |
| `get_option_chain` | `symbol`, `underlying_sec_type` (default `STK`), `fut_fop_exchange`, `underlying_con_id` | `GET /v1/options/{symbol}/chain` |
| `place_option_combo` | `body`: a combo order object as in [POST /options/combo](api.md#post-optionscombo) | `POST /v1/options/combo` |
| `exercise_option` | `body`: `conid`, `action`, `quantity`, `account`, `override` | `POST /v1/options/exercise` |
| `get_future_continuous` | `symbol`, `exchange`, `currency` | `GET /v1/futures/{symbol}/continuous` |
| `list_future_contracts` | `symbol`, `exchange`, `currency`, `include_expired` | `GET /v1/futures/{symbol}/contracts` |

`get_future_continuous` and `list_future_contracts` take `exchange` as a parameter but do not send it, and both REST routes require it, so they come back with `422`. Use `request` with an `exchange` query parameter instead.

### Orders

| Tool | Parameters | REST call |
| --- | --- | --- |
| `list_orders` | none | `GET /v1/orders` |
| `get_order` | `order_id` | `GET /v1/orders/{orderId}` |
| `place_order` | `asset_class`, `symbol`, `action`, `quantity`, `order_type` (default `MKT`), `lmt_price`, `aux_price`, `tif` (default `DAY`), `expiry`, `strike`, `right`, `outside_rth`, `account` | `POST /v1/orders` |
| `cancel_order` | `order_id` | `DELETE /v1/orders/{orderId}` |
| `cancel_all_orders` | none | `DELETE /v1/orders` |

`place_order` has no `exchange`, `currency` or `conid` parameter, so it cannot place a futures order (the REST handler requires `exchange`) or pick a non-default exchange. Use `request` with a full [order body](api.md#post-orders) for those.

### Account, positions and history

| Tool | Parameters | REST call |
| --- | --- | --- |
| `get_account` | `account` | `GET /v1/account` |
| `get_account_values` | `account` | `GET /v1/account/values` |
| `list_accounts` | none | `GET /v1/accounts` |
| `list_positions` | `account` | `GET /v1/positions` |
| `get_executions` | `account`, `client_id`, `sec_type`, `symbol`, `exchange`, `side`, `time_after` | `GET /v1/history/executions` |
| `get_completed_orders` | `api_only` | `GET /v1/history/completed_orders` |
| `ping` | none | `GET /v1/ping` |

### Discovery and fallback

| Tool | Parameters | What it does |
| --- | --- | --- |
| `endpoints` | none | Lists every route (method, path, summary) from the app's live OpenAPI schema. |
| `request` | `method`, `path`, `query`, `body` | Calls any route, such as `GET /v1/stocks/AAPL/rates`. Use it for anything the typed tools do not cover. |

## Live account warning

`place_order`, `place_option_combo`, `exercise_option`, `cancel_order`, `cancel_all_orders`, and `request` with `POST` or `DELETE`, act on the real account the gateway is logged into. Their descriptions tell the agent to act only on an explicit user request, and the server-level instructions repeat it. That is text an agent reads, not a technical control: for a hard stop, set `READ_ONLY_API=yes` in `.env.ibkr` or give the agent a paper login.
