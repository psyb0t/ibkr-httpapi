"""MCP server for ibkr-httpapi — mounted at ``/mcp`` on the FastAPI app.

Exposes the whole HTTP REST surface as MCP tools so an agent can drive IBKR
over JSON-RPC / streamable-HTTP. Rather than hand-mirror every asset-class
endpoint (they'd drift from the REST spec), the tools proxy IN-PROCESS to the
same FastAPI app via httpx's ASGI transport — one code path, always in sync
with the REST API, same routers / validation / auth:

  - ``ping``      — gateway liveness (``GET /v1/ping``)
  - ``endpoints`` — the live OpenAPI catalog (method + path + summary) so an
                    agent can discover every route instead of guessing paths
  - ``request``   — call ANY REST endpoint (method, path, query, body); the
                    single generic IO interface over the full API

Mounted stateless with ``streamable_http_path = "/"`` so ``/mcp`` maps 1:1 (the
``server.py`` ``Mount("/mcp", ...)`` doesn't double-prefix).
"""

from __future__ import annotations

import json
import logging
from typing import Any

# httpx is used ONLY for its in-process ASGI transport (ASGITransport) to dial
# this same app with no network hop. It is a hard dependency of `mcp`, not a new
# one — the stack's "use urllib, not httpx" rule targets OUTBOUND HTTP (e.g. the
# wickworks call), for which there is a stdlib path; in-process ASGI has none.
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from ibkrapi.config import API_TOKEN

logger = logging.getLogger(__name__)

# ASGITransport routes by path, not host, so the base URL is arbitrary — it only
# has to be a well-formed absolute URL for httpx to build request targets from.
_INTERNAL_BASE = "http://ibkr.local"
_REQUEST_TIMEOUT_SECONDS = 120.0


def build_mcp_server() -> FastMCP:
    """Construct the FastMCP server mounted under ``/mcp``."""
    mcp = FastMCP(
        name="ibkr-httpapi",
        instructions=(
            "HTTP interface to Interactive Brokers (via IB Gateway), exposed over "
            "MCP. Call `endpoints` to discover every REST route (live quotes, "
            "historical bars, contract lookups, account, positions and orders "
            "across stocks / options / futures / forex / crypto / CFD), then "
            "`request` to call any of them. Order placement, cancellation and "
            "option exercise are real, irreversible actions on a live brokerage "
            "account — only call those routes when the user explicitly asked for "
            "that specific action, and confirm the parameters first."
        ),
        stateless_http=True,
        json_response=True,
        # ibkr-httpapi is a headless self-hosted service that the operator fronts
        # with their own reverse proxy / auth and reaches at an arbitrary Host.
        # The SDK's DNS-rebinding Host allowlist is a browser-localhost mitigation
        # that would 421 every real-hostname deployment; disable it and let the
        # operator's proxy own network-level access control.
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        ),
    )
    mcp.settings.streamable_http_path = "/"

    def _client() -> httpx.AsyncClient:
        # Late import: server.py imports THIS module at load time, so importing
        # the app at module scope here would be circular. ASGITransport dials the
        # same app in-process, reusing its routers / validation / auth verbatim.
        from ibkrapi.server import app

        headers: dict[str, str] = {}
        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url=_INTERNAL_BASE,
            headers=headers,
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )

    @mcp.tool()
    async def ping() -> dict[str, Any]:
        """Liveness plus IB-gateway connection state (``GET /v1/ping``)."""
        async with _client() as client:
            resp = await client.get("/v1/ping")
            return {"status": resp.status_code, "body": _decode(resp)}

    @mcp.tool()
    async def endpoints() -> dict[str, Any]:
        """List every REST endpoint (method, path, summary) from the live OpenAPI
        schema — the catalog of routes ``request`` can call. Discover routes here
        rather than guessing paths."""
        from ibkrapi.server import app

        found: list[dict[str, str]] = []
        for path, operations in app.openapi().get("paths", {}).items():
            for method, operation in operations.items():
                found.append(
                    {
                        "method": method.upper(),
                        "path": path,
                        "summary": operation.get("summary")
                        or operation.get("operationId", ""),
                    }
                )
        found.sort(key=lambda entry: (entry["path"], entry["method"]))
        return {"endpoints": found}

    @mcp.tool()
    async def request(
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call any ibkr-httpapi REST endpoint and return its JSON response.

        ``method``: GET / POST / DELETE / etc. ``path``: a full route from
        ``endpoints``, e.g. ``/v1/system/positions`` or ``/v1/stocks/AAPL/rates``.
        ``query``: URL query params. ``body``: JSON body for POST / PUT. The call
        runs the exact same handler, validation and auth as a real HTTP request
        (in-process), so the response envelope matches REST byte-for-byte.

        POST / DELETE routes place or cancel real orders and exercise options on a
        LIVE account and cannot be undone — only call them when the user asked for
        that exact action, and confirm the parameters first.
        """
        verb = method.upper().strip()
        target = path if path.startswith("/") else "/" + path
        # Log the route only — never the body/query, which can carry order
        # parameters (per the logging redaction rules).
        logger.info("mcp proxy request", extra={"http_method": verb, "path": target})
        async with _client() as client:
            resp = await client.request(verb, target, params=query, json=body)
            return {"status": resp.status_code, "body": _decode(resp)}

    return mcp


def _decode(resp: httpx.Response) -> Any:
    """Return the response as parsed JSON, falling back to raw text for the rare
    non-JSON body so a tool call never fails on decoding alone."""
    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError):
        return {"raw": resp.text}
