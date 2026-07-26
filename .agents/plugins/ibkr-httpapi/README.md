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

The ibkr-httpapi MCP tools become available to your agent. Rather than
mirroring every asset-class endpoint one-by-one, the server exposes its whole
REST surface through three generic tools:

- **`ping`** — gateway liveness (mirrors `GET /v1/ping`).
- **`endpoints`** — the live OpenAPI catalog (method + path + summary) for
  every REST route, so the agent can discover routes instead of guessing.
- **`request`** — call any REST endpoint by `method`, `path`, `query`, `body`;
  the single generic IO interface over the full API (market data, account,
  positions, orders, across stocks/options/futures/forex/crypto/CFD).

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
