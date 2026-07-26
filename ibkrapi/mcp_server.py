"""MCP server for ibkr-httpapi — mounted at ``/mcp`` on the FastAPI app.

Exposes the HTTP REST surface as dedicated, typed MCP tools grouped by
family — market data (contracts / quotes / historical bars+ticks / TA),
orders (list / place / cancel), positions, account, and history/health —
plus a generic ``request`` escape hatch and an ``endpoints`` catalog for
anything not covered by a dedicated tool. Every tool is a THIN wrapper: it
maps friendly, typed parameters to (method, path, query, body) and calls
the SAME in-process helper below — no handler logic is reimplemented, and
auth / request logging are never bypassed.

This is a LIVE TRADING API. Order placement, cancellation, and option
exercise are real, irreversible actions on a live brokerage account —
those tools only fire on an explicit user request.

Tools proxy IN-PROCESS to the same FastAPI app via httpx's ASGI transport
— one code path, always in sync with the REST API, same routers /
validation / auth. Mounted stateless with ``streamable_http_path = "/"``
so ``/mcp`` maps 1:1 (the ``server.py`` ``Mount("/mcp", ...)`` doesn't
double-prefix).
"""

from __future__ import annotations

import json
from typing import Any

# httpx is used ONLY for its in-process ASGI transport (ASGITransport) to dial
# this same app with no network hop. It is a hard dependency of `mcp`, not a new
# one — the stack's "use urllib, not httpx" rule targets OUTBOUND HTTP (e.g. the
# wickworks call), for which there is a stdlib path; in-process ASGI has none.
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from ibkrapi.config import API_TOKEN
from ibkrapi.logger import log

# ASGITransport routes by path, not host, so the base URL is arbitrary — it only
# has to be a well-formed absolute URL for httpx to build request targets from.
_INTERNAL_BASE = "http://ibkr.local"
_REQUEST_TIMEOUT_SECONDS = 120.0

# asset_class -> URL prefix under /v1. Forex is the odd one out: its path
# param is {pair}, every other asset class uses {symbol}.
_ASSET_CLASS_PREFIXES = {
    "stock": "stocks",
    "option": "options",
    "future": "futures",
    "cfd": "cfd",
    "forex": "forex",
    "crypto": "crypto",
}


def _prefix_for(asset_class: str) -> str:
    prefix = _ASSET_CLASS_PREFIXES.get(asset_class)
    if prefix is None:
        raise ValueError(
            f"Unknown asset_class {asset_class!r}; "
            f"expected one of {sorted(_ASSET_CLASS_PREFIXES)}"
        )
    return prefix


def _drop_empty(query: dict[str, Any]) -> dict[str, Any]:
    """Drop params that are unset (empty string / None) so we don't send
    accidental overrides of server-side defaults for optional query params."""
    return {k: v for k, v in query.items() if v not in (None, "")}


def build_mcp_server() -> FastMCP:
    """Construct the FastMCP server mounted under ``/mcp``."""
    mcp = FastMCP(
        name="ibkr-httpapi",
        instructions=(
            "HTTP interface to Interactive Brokers (via IB Gateway), exposed over "
            "MCP. Tool families: market data (contracts, quotes, historical "
            "bars/ticks, TA-enriched bars, option chains, future continuous/"
            "contracts) across stocks / options / futures / forex / crypto / CFD; "
            "orders (list, place, cancel); positions; account (summary, values, "
            "list accounts); and history/health (executions, completed orders, "
            "ping). Use `endpoints` to see the full raw REST catalog and `request` "
            "as a generic fallback for anything not covered by a dedicated tool. "
            "This is a LIVE brokerage account — placing orders, cancelling orders "
            "and exercising options are real and irreversible; only call those "
            "tools on the user's explicit request."
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

    async def _call(
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Shared in-process call helper every typed tool routes through — same
        code path as the generic ``request`` tool: same auth, same handlers."""
        log.info("mcp tool request", http_method=method, path=path)
        async with _client() as client:
            resp = await client.request(method, path, params=query, json=body)
            return {"status": resp.status_code, "body": _decode(resp)}

    # --- market data ----------------------------------------------------------

    @mcp.tool()
    async def get_contract(
        asset_class: str,
        symbol: str,
        exchange: str = "",
        currency: str = "",
        expiry: str = "",
        strike: float = 0,
        right: str = "",
    ) -> dict[str, Any]:
        """Look up contract details for a symbol on a given asset class
        (``stock`` / ``option`` / ``future`` / ``cfd`` / ``forex`` / ``crypto``).
        For ``forex``, ``symbol`` is the currency pair (e.g. ``EURUSD``).
        ``expiry`` is required for ``option`` and ``future``; ``strike`` and
        ``right`` (``C``/``P``) are also required for ``option``."""
        prefix = _prefix_for(asset_class)
        query = _drop_empty(
            {
                "exchange": exchange,
                "currency": currency,
                "expiry": expiry,
                "strike": strike or None,
                "right": right,
            }
        )
        return await _call("GET", f"/v1/{prefix}/{symbol}", query=query)

    @mcp.tool()
    async def get_quote(
        asset_class: str,
        symbol: str,
        exchange: str = "",
        currency: str = "",
        expiry: str = "",
        strike: float = 0,
        right: str = "",
    ) -> dict[str, Any]:
        """Snapshot bid/ask/last quote for a symbol (plus Greeks when
        ``asset_class`` is ``option``). Same required params as ``get_contract``:
        ``expiry``/``strike``/``right`` for options, ``expiry`` for futures."""
        prefix = _prefix_for(asset_class)
        query = _drop_empty(
            {
                "exchange": exchange,
                "currency": currency,
                "expiry": expiry,
                "strike": strike or None,
                "right": right,
            }
        )
        return await _call("GET", f"/v1/{prefix}/{symbol}/tick", query=query)

    @mcp.tool()
    async def get_rates(
        asset_class: str,
        symbol: str,
        duration: str,
        bar_size: str = "",
        end_date_time: str = "",
        what_to_show: str = "",
        use_rth: bool = True,
        exchange: str = "",
        currency: str = "",
        expiry: str = "",
        strike: float = 0,
        right: str = "",
    ) -> dict[str, Any]:
        """Historical OHLC bars. ``duration`` is an IBKR duration string (e.g.
        ``"30 D"``, ``"1 Y"``). ``bar_size`` an IBKR bar-size string (e.g.
        ``"1 hour"``, ``"1 day"``); server default is used if omitted.
        ``expiry``/``strike``/``right`` required for options, ``expiry``
        required for futures."""
        prefix = _prefix_for(asset_class)
        query = _drop_empty(
            {
                "duration": duration,
                "barSize": bar_size,
                "endDateTime": end_date_time,
                "whatToShow": what_to_show,
                "useRTH": use_rth,
                "exchange": exchange,
                "currency": currency,
                "expiry": expiry,
                "strike": strike or None,
                "right": right,
            }
        )
        return await _call("GET", f"/v1/{prefix}/{symbol}/rates", query=query)

    @mcp.tool()
    async def get_rates_ta(
        asset_class: str,
        symbol: str,
        duration: str,
        indicators: dict[str, Any],
        bar_size: str = "",
        end_date_time: str = "",
        what_to_show: str = "",
        use_rth: bool = True,
        recent_bars: int = 0,
        exchange: str = "",
        currency: str = "",
        expiry: str = "",
        strike: float = 0,
        right: str = "",
    ) -> dict[str, Any]:
        """Historical bars enriched with technical-analysis indicators (computed
        server-side by the wickworks sidecar). ``indicators`` is a dict of
        indicator name -> params, e.g. ``{"rsi": {"period": 14}}``. Same
        required identifying params as ``get_rates`` for the URL/query; the rest
        of ``duration``/``bar_size``/etc. go in the JSON body."""
        prefix = _prefix_for(asset_class)
        query = _drop_empty(
            {
                "exchange": exchange,
                "currency": currency,
                "expiry": expiry,
                "strike": strike or None,
                "right": right,
            }
        )
        body = _drop_empty(
            {
                "duration": duration,
                "barSize": bar_size,
                "endDateTime": end_date_time,
                "whatToShow": what_to_show,
                "useRTH": use_rth,
                "indicators": indicators,
                "recentBars": recent_bars or None,
            }
        )
        return await _call("POST", f"/v1/{prefix}/{symbol}/rates/ta", query=query, body=body)

    @mcp.tool()
    async def get_stock_ticks(
        symbol: str,
        start_date_time: str = "",
        end_date_time: str = "",
        number_of_ticks: int = 1000,
        what_to_show: str = "",
        use_rth: bool = True,
        exchange: str = "",
        currency: str = "",
        primary_exchange: str = "",
    ) -> dict[str, Any]:
        """Historical raw tick-by-tick data for a stock (stocks only —
        no equivalent endpoint for other asset classes)."""
        query = _drop_empty(
            {
                "startDateTime": start_date_time,
                "endDateTime": end_date_time,
                "numberOfTicks": number_of_ticks,
                "whatToShow": what_to_show,
                "useRTH": use_rth,
                "exchange": exchange,
                "currency": currency,
                "primaryExchange": primary_exchange,
            }
        )
        return await _call("GET", f"/v1/stocks/{symbol}/ticks", query=query)

    # --- options / futures specials --------------------------------------------

    @mcp.tool()
    async def get_option_chain(
        symbol: str,
        underlying_sec_type: str = "STK",
        fut_fop_exchange: str = "",
        underlying_con_id: int = 0,
    ) -> dict[str, Any]:
        """Full option chain (expirations + strikes per exchange/trading class)
        for the underlying ``symbol``. ``underlying_sec_type`` defaults to
        ``STK``; set ``fut_fop_exchange`` when the underlying is a future."""
        query = _drop_empty(
            {
                "underlyingSecType": underlying_sec_type,
                "futFopExchange": fut_fop_exchange,
                "underlyingConId": underlying_con_id or None,
            }
        )
        return await _call("GET", f"/v1/options/{symbol}/chain", query=query)

    @mcp.tool()
    async def place_option_combo(body: dict[str, Any]) -> dict[str, Any]:
        """Place a multi-leg option combo (BAG) order. ``body`` is a
        ComboOrderRequest: ``symbol``, ``legs`` (list of
        ``{conid, ratio, action, exchange}``), ``action``, ``quantity``,
        plus optional ``orderType``, ``lmtPrice``, ``tif``, ``exchange``,
        ``currency``, ``account``.

        This places a real, irreversible multi-leg order on a live brokerage
        account — only call this when the user has explicitly asked for it."""
        return await _call("POST", "/v1/options/combo", body=body)

    @mcp.tool()
    async def exercise_option(body: dict[str, Any]) -> dict[str, Any]:
        """Exercise or lapse an option position. ``body`` is an ExerciseRequest:
        ``conid``, ``action`` (``EXERCISE`` or ``LAPSE``), ``quantity``,
        ``account``, optional ``override``.

        This is a real, irreversible action on a live brokerage account —
        only call this when the user has explicitly asked for it."""
        return await _call("POST", "/v1/options/exercise", body=body)

    @mcp.tool()
    async def get_future_continuous(
        symbol: str,
        exchange: str,
        currency: str = "",
    ) -> dict[str, Any]:
        """Contract details for the continuous (front-month, non-expiring)
        future for ``symbol`` on ``exchange``."""
        query = _drop_empty({"currency": currency})
        return await _call("GET", f"/v1/futures/{symbol}/continuous", query=query)

    @mcp.tool()
    async def list_future_contracts(
        symbol: str,
        exchange: str,
        currency: str = "",
        include_expired: bool = False,
    ) -> dict[str, Any]:
        """List all future contracts (every expiry) for ``symbol`` on
        ``exchange``. Set ``include_expired`` to include expired contracts."""
        query = _drop_empty({"currency": currency, "includeExpired": include_expired})
        return await _call("GET", f"/v1/futures/{symbol}/contracts", query=query)

    # --- orders -----------------------------------------------------------------

    @mcp.tool()
    async def list_orders() -> dict[str, Any]:
        """List all currently open/working orders (trades) on the account."""
        return await _call("GET", "/v1/orders")

    @mcp.tool()
    async def get_order(order_id: int) -> dict[str, Any]:
        """Get the full trade (contract, order, status, fills) for one order ID."""
        return await _call("GET", f"/v1/orders/{order_id}")

    @mcp.tool()
    async def place_order(
        asset_class: str,
        symbol: str,
        action: str,
        quantity: float,
        order_type: str = "MKT",
        lmt_price: float = 0,
        aux_price: float = 0,
        tif: str = "DAY",
        expiry: str = "",
        strike: float = 0,
        right: str = "",
        outside_rth: bool = False,
        account: str = "",
    ) -> dict[str, Any]:
        """Place an order. ``asset_class``: stock/option/future/cfd/forex/crypto.
        ``action``: BUY or SELL. ``order_type``: MKT/LMT/STP/STP_LMT; ``lmt_price``
        required for LMT/STP_LMT, ``aux_price`` (stop price) required for
        STP/STP_LMT. ``expiry``/``strike``/``right`` required for options,
        ``expiry`` required for futures.

        This places a real, irreversible order on a live brokerage account —
        only call this when the user has explicitly asked for it, and confirm
        the parameters first."""
        body = _drop_empty(
            {
                "assetClass": asset_class,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "orderType": order_type,
                "lmtPrice": lmt_price or None,
                "auxPrice": aux_price or None,
                "tif": tif,
                "expiry": expiry,
                "strike": strike or None,
                "right": right,
                "outsideRth": outside_rth,
                "account": account,
            }
        )
        return await _call("POST", "/v1/orders", body=body)

    @mcp.tool()
    async def cancel_order(order_id: int) -> dict[str, Any]:
        """Cancel one open order by ID.

        This cancels a real order on a live brokerage account and cannot be
        undone — only call this when the user has explicitly asked for it."""
        return await _call("DELETE", f"/v1/orders/{order_id}")

    @mcp.tool()
    async def cancel_all_orders() -> dict[str, Any]:
        """Cancel every open order on the account (IBKR global cancel).

        This cancels EVERY open order on a live brokerage account and cannot
        be undone — only call this when the user has explicitly asked for it."""
        return await _call("DELETE", "/v1/orders")

    # --- account / positions -----------------------------------------------------

    @mcp.tool()
    async def get_account(account: str = "") -> dict[str, Any]:
        """Account summary (equity, buying power, margin, etc.) for the default
        account, or ``account`` if given."""
        query = _drop_empty({"account": account})
        return await _call("GET", "/v1/account", query=query)

    @mcp.tool()
    async def get_account_values(account: str = "") -> dict[str, Any]:
        """Raw account values keyed by tag (same shape as ``get_account`` but
        the unfiltered underlying value set)."""
        query = _drop_empty({"account": account})
        return await _call("GET", "/v1/account/values", query=query)

    @mcp.tool()
    async def list_accounts() -> dict[str, Any]:
        """List every account ID visible to this IBKR login."""
        return await _call("GET", "/v1/accounts")

    @mcp.tool()
    async def list_positions(account: str = "") -> dict[str, Any]:
        """List all open positions (contract, size, average cost) for the
        default account, or ``account`` if given."""
        query = _drop_empty({"account": account})
        return await _call("GET", "/v1/positions", query=query)

    # --- history / health ---------------------------------------------------------

    @mcp.tool()
    async def get_executions(
        account: str = "",
        client_id: int = 0,
        sec_type: str = "",
        symbol: str = "",
        exchange: str = "",
        side: str = "",
        time_after: str = "",
    ) -> dict[str, Any]:
        """List trade executions (fills), optionally filtered by account,
        client_id, sec_type, symbol, exchange, side, or time_after
        (ISO-ish timestamp — only executions after this time)."""
        query = _drop_empty(
            {
                "account": account,
                "clientId": client_id or None,
                "secType": sec_type,
                "symbol": symbol,
                "exchange": exchange,
                "side": side,
                "timeAfter": time_after,
            }
        )
        return await _call("GET", "/v1/history/executions", query=query)

    @mcp.tool()
    async def get_completed_orders(api_only: bool = False) -> dict[str, Any]:
        """List completed (filled/cancelled) orders. Set ``api_only`` to
        restrict to orders placed via this API (excludes TWS-placed orders)."""
        query = {"apiOnly": api_only}
        return await _call("GET", "/v1/history/completed_orders", query=query)

    @mcp.tool()
    async def ping() -> dict[str, Any]:
        """Liveness plus IB-gateway connection state (``GET /v1/ping``)."""
        return await _call("GET", "/v1/ping")

    # --- escape hatch + discovery -------------------------------------------------

    @mcp.tool()
    async def endpoints() -> dict[str, Any]:
        """List every REST endpoint (method, path, summary) from the live OpenAPI
        schema — the full catalog, including routes with no dedicated tool.
        Use this to discover routes before falling back to ``request``."""
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
        """Generic fallback: call any ibkr-httpapi REST endpoint directly and
        return its JSON response. Prefer the dedicated typed tools above; use
        this only for routes without one (see ``endpoints``).

        ``method``: GET / POST / DELETE / etc. ``path``: a full route from
        ``endpoints``, e.g. ``/v1/positions`` or ``/v1/stocks/AAPL/rates``.
        ``query``: URL query params. ``body``: JSON body for POST / PUT. The call
        runs the exact same handler, validation and auth as a real HTTP request
        (in-process), so the response envelope matches REST byte-for-byte.

        POST / DELETE routes can place or cancel real orders and exercise
        options on a LIVE account and cannot be undone — only call them when
        the user asked for that exact action, and confirm the parameters
        first."""
        verb = method.upper().strip()
        target = path if path.startswith("/") else "/" + path
        return await _call(verb, target, query=query, body=body)

    return mcp


def _decode(resp: httpx.Response) -> Any:
    """Return the response as parsed JSON, falling back to raw text for the rare
    non-JSON body so a tool call never fails on decoding alone."""
    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError):
        return {"raw": resp.text}
