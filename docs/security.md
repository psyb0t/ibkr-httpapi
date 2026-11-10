---
title: "Security"
description: "What an ibkr-httpapi deployment can reach, what it stores, how the bearer token works, and what to set before it leaves localhost."
nav_order: 10
---

# Security

Anyone who can send requests to this API can trade the brokerage account the gateway is logged into. Treat the API token like the account password.

## What the stack can do

- Read balances, positions, orders and executions for every account on the IBKR login.
- Place, cancel and exercise for real through `POST /v1/orders`, `POST /v1/options/combo`, `POST /v1/options/exercise`, `DELETE /v1/orders/{orderId}` and `DELETE /v1/orders`. The last one cancels every open order on the account, including orders placed in other tools.
- Do all of the above through MCP at `/mcp` with the same token.

The only built-in brake is IBKR's own: `READ_ONLY_API=yes` in `.env.ibkr` makes the gateway refuse orders. A paper login (`TRADING_MODE=paper`) keeps real money out of reach.

## Authentication

- One shared bearer token, `api_token` in `config.yaml` or `API_TOKEN` in the environment. The middleware in [`ibkrapi/server.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/server.py) checks it on every path: `/v1/*`, `/mcp`, `/docs` and `/openapi.json`. It compares with `hmac.compare_digest`.
- An empty token turns auth off for everything, with one warning line from `run.sh` at startup.
- There are no users, scopes or read-only tokens. Whoever has the token has full access.
- Generate a long random token and keep `config/config.yaml` out of Git (it is gitignored):

```bash
openssl rand -hex 32
```

## Network exposure

- nginx publishes the API on `127.0.0.1:8889` by default (`API_HOST_BIND`, `API_HOST_PORT`). nginx itself speaks plain HTTP; there is no TLS in the stack.
- The `api` container has no published port. The gateway's TWS socket is only on the internal `backend` network. VNC (`5900`) and port `8001` are published on `127.0.0.1` only.
- wickworks sits on an `internal: true` network with no route out.
- The MCP endpoint does not check the `Host` header (the SDK's DNS rebinding protection is turned off), so a browser page could reach a loopback API without a token if you run it without one. Always set a token, even on localhost.

Before you bind to anything but loopback:

1. Set a strong `api_token`.
2. Put TLS in front: the commented `cloudflared` service tunnels to `http://nginx:80` without a host port, and the `tailscale` service puts it on a tailnet. Add an access layer of your own (Cloudflare Access, tailnet ACLs) in front of the token.
3. Test the whole chain against a paper account from another network before you switch to live.
4. Rotate the token after testing.

## What is stored where

| Data | Location | Notes |
| --- | --- | --- |
| IBKR username and password | `.env.ibkr`, passed only to the `ibgateway` container | Gitignored. The API process never sees them. |
| API token | `config/config.yaml`, and `.env` (written by `run.sh`) | Both gitignored. The startup log records only whether a token is set and its length. |
| Gateway settings | `.data/ibgateway/` | |
| Request logs | `logs/full.log` and container stdout | Method, path, status, duration, client IP and user agent. No bodies, no tokens. |
| Market data and trading history | `data/history/` | Executions and completed orders include account numbers, prices and quantities. Protect backups accordingly. |

## Container hardening

`api`, `nginx` and `wickworks` run read-only with all capabilities dropped and `no-new-privileges`; the `api` image runs as a non-root user with hash-checked dependencies. The gateway container cannot be locked down the same way. Details on the [deployment page](deployment.md#container-hardening).

## Supply chain

Python dependencies are hash-locked and pass a 7-day age gate before they can enter the lock, base images are pinned by digest, and `make audit`, `make audit-go` and `make audit-compose` scan the Python deps, the Go client and the compose files. See [Development](development.md#dependencies).
