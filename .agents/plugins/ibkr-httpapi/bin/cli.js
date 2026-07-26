#!/usr/bin/env node
// ibkr-httpapi MCP bridge. A thin stdio<->HTTP proxy: forwards MCP over stdio to a
// running ibkr-httpapi server's Streamable-HTTP endpoint (`$IBKR_HTTPAPI_URL/mcp/`),
// authenticating with `$IBKR_HTTPAPI_TOKEN` when the server requires it.
//
// stdout IS the MCP protocol channel, so diagnostics go to stderr only — the
// sole output here is a fatal pre-launch console.error (user-facing CLI
// output). The token is passed to the proxy as an argv header, never logged.
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);

const MCP_PATH = "/mcp/";

const base = process.env.IBKR_HTTPAPI_URL;

if (!base) {
  console.error(
    `[ibkr-httpapi-mcp] Missing IBKR_HTTPAPI_URL.

Point this bridge at your running ibkr-httpapi server, e.g.:
  export IBKR_HTTPAPI_URL=http://localhost:8889

ibkr-httpapi is self-hosted — see https://github.com/psyb0t/ibkr-httpapi`,
  );
  process.exit(1);
}

// /mcp is mounted at the app ROOT, not under the /v1 REST prefix. IBKR_HTTPAPI_URL
// conventionally carries the /v1 REST base, so strip a trailing /v1 — this way the
// MCP URL is correct whether the operator points the var at the root or at /v1.
const root = base.replace(/\/+$/, "").replace(/\/v1$/, "");
const url = `${root}${MCP_PATH}`;
const token = process.env.IBKR_HTTPAPI_TOKEN;
const proxyEntry = require.resolve("mcp-remote/dist/proxy.js");

const args = [proxyEntry, url, "--transport", "http-only"];
if (token) {
  args.push("--header", `Authorization: Bearer ${token}`);
}
args.push(...process.argv.slice(2));

const result = spawnSync(process.execPath, args, { stdio: "inherit" });
process.exit(result.status ?? 1);
