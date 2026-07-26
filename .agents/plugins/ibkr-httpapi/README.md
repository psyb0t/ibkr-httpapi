# @psyb0t/ibkr-httpapi

An OpenClaw/MCP plugin that connects your agent to a self-hosted
[ibkr-httpapi](https://github.com/psyb0t/ibkr-httpapi) — an HTTP wrapper over
Interactive Brokers — over the
[Model Context Protocol](https://modelcontextprotocol.io).

ibkr-httpapi already serves a Streamable-HTTP MCP endpoint at `/mcp`. This
package is a thin stdio↔HTTP bridge (via
[`mcp-remote`](https://www.npmjs.com/package/mcp-remote)) for MCP clients that
speak local stdio servers — it forwards everything to your running
ibkr-httpapi instance and adds a bearer token when your endpoint requires one.

> ibkr-httpapi is **self-hosted** and fronts a **LIVE Interactive Brokers
> account**. This plugin does not ship the broker connection — it connects to
> an ibkr-httpapi server that **you** run. Order placement, cancellation, and
> option exercise are real, irreversible actions on that account. See the
> [ibkr-httpapi repo](https://github.com/psyb0t/ibkr-httpapi) to stand one up.

## Tools

The ibkr-httpapi MCP tools become available to your agent — **dedicated typed
tools** grouped by family, with the 6 asset classes collapsed behind an
`asset_class` enum: market data (`get_contract`, `get_quote`, `get_rates`,
`get_rates_ta`, `get_stock_ticks`), specials (`get_option_chain`,
`place_option_combo`, `exercise_option`, `get_future_continuous`,
`list_future_contracts`), orders (`list_orders`, `get_order`, `place_order`,
`cancel_order`, `cancel_all_orders`), and account/positions/history
(`get_account`, `get_account_values`, `list_accounts`, `list_positions`,
`get_executions`, `get_completed_orders`, `ping`). A generic `request` +
`endpoints` catalog cover anything without a dedicated tool. The order /
exercise tools are irreversible actions on a live brokerage account.

## Configuration

| Env var | Required | Description |
|---|---|---|
| `IBKR_HTTPAPI_URL` | yes | Base URL of your running ibkr-httpapi server, e.g. `http://localhost:8889`. The bridge appends `/mcp/`. This is the app root — **not** the `/v1` REST prefix. |
| `IBKR_HTTPAPI_TOKEN` | no | Bearer token — required whenever the server has `api_token`/`API_TOKEN` configured. This is the **same token** that guards the REST API; an empty server-side token means auth is disabled. |

## Install

Install it into your OpenClaw agent from ClawHub:

```bash
openclaw plugins install clawhub:@psyb0t/ibkr-httpapi
```

Then set `IBKR_HTTPAPI_URL` (and `IBKR_HTTPAPI_TOKEN` if your server has a
token configured) in the plugin's environment.

## Native remote MCP (no install)

If your MCP client already supports **remote** Streamable-HTTP servers, you
don't need this bridge — point the client straight at `$IBKR_HTTPAPI_URL/mcp`
(with an `Authorization: Bearer <token>` header if the server requires one).

## License

MIT. See [LICENSE](LICENSE).
