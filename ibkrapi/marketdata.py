"""Shared market-data helpers for every asset router.

Wraps the ib_async historical / snapshot / chain / TA calls into one
place so the per-asset routers stay tiny.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from urllib import error as urllib_error
from urllib import request as urllib_request

from ib_async import Contract

from ibkrapi.config import WICKWORKS_TIMEOUT_SECONDS, WICKWORKS_URL
from ibkrapi.errors import (
    CODE_BAD_REQUEST,
    CODE_NOT_FOUND,
    CODE_TA_SIDECAR_UNAVAILABLE,
    CODE_UPSTREAM_FAILED,
    APIError,
)
from ibkrapi.ibclient import get_ib
from ibkrapi.logger import log
from ibkrapi.serialize import bar_dict, contract_details_dict, tick_dict, ticker_dict

# Valid ib_async bar sizes — exact strings the SDK expects.
BAR_SIZES = {
    "1s": "1 secs",
    "5s": "5 secs",
    "10s": "10 secs",
    "15s": "15 secs",
    "30s": "30 secs",
    "1m": "1 min",
    "2m": "2 mins",
    "3m": "3 mins",
    "5m": "5 mins",
    "10m": "10 mins",
    "15m": "15 mins",
    "20m": "20 mins",
    "30m": "30 mins",
    "1h": "1 hour",
    "2h": "2 hours",
    "3h": "3 hours",
    "4h": "4 hours",
    "8h": "8 hours",
    "1d": "1 day",
    "1w": "1 week",
    "1mo": "1 month",
}

WHAT_TO_SHOW = {
    "trades": "TRADES",
    "midpoint": "MIDPOINT",
    "bid": "BID",
    "ask": "ASK",
    "bid_ask": "BID_ASK",
    "adjusted_last": "ADJUSTED_LAST",
    "historical_volatility": "HISTORICAL_VOLATILITY",
    "option_implied_volatility": "OPTION_IMPLIED_VOLATILITY",
}


def _resolve_bar_size(raw: str | None) -> str:
    if not raw:
        return "1 hour"
    if raw in BAR_SIZES:
        return BAR_SIZES[raw]
    if raw in BAR_SIZES.values():
        return raw
    raise APIError(
        400,
        f"Unsupported bar size: {raw!r}",
        code=CODE_BAD_REQUEST,
        details={"accepted": sorted(BAR_SIZES)},
    )


def _resolve_what_to_show(raw: str | None) -> str:
    if not raw:
        return "TRADES"
    key = raw.lower()
    if key in WHAT_TO_SHOW:
        return WHAT_TO_SHOW[key]
    upper = raw.upper()
    if upper in WHAT_TO_SHOW.values():
        return upper
    raise APIError(
        400,
        f"Unsupported what_to_show: {raw!r}",
        code=CODE_BAD_REQUEST,
        details={"accepted": sorted(WHAT_TO_SHOW)},
    )


async def qualify(contract: Contract) -> Contract:
    ib = await get_ib()
    log.debug("qualify_contract", secType=contract.secType, symbol=contract.symbol)
    qualified = await ib.qualifyContractsAsync(contract)
    # ib_async returns [None] (not []) when a contract can't be qualified.
    # `not [None]` is False, so check element-wise. The element union also
    # includes list[Contract|None] for the returnAll=True path; we never
    # pass that flag so element is always Contract | None, but narrow via
    # isinstance to satisfy both the type checker and a defensive guard.
    first = qualified[0] if qualified else None
    if not isinstance(first, Contract):
        raise APIError(
            404,
            "Contract not found or not qualifyable",
            code=CODE_NOT_FOUND,
            details={"secType": contract.secType, "symbol": contract.symbol},
        )
    return first


async def contract_details(contract) -> list[dict]:
    ib = await get_ib()
    log.debug("contract_details", secType=contract.secType, symbol=contract.symbol)
    details = await ib.reqContractDetailsAsync(contract)
    if not details:
        raise APIError(
            404,
            "No contract details returned",
            code=CODE_NOT_FOUND,
            details={"secType": contract.secType, "symbol": contract.symbol},
        )
    return [contract_details_dict(d) for d in details]


async def snapshot_tick(contract) -> dict:
    ib = await get_ib()
    qualified = await qualify(contract)
    log.debug("snapshot_tick", conid=qualified.conId, symbol=qualified.symbol)
    tickers = await ib.reqTickersAsync(qualified)
    if not tickers:
        raise APIError(
            502,
            "No tick returned from IBKR",
            code=CODE_UPSTREAM_FAILED,
            details={"conid": qualified.conId},
        )
    return ticker_dict(tickers[0])


async def historical_bars(
    contract,
    *,
    duration: str,
    bar_size: str | None = None,
    end_datetime: str | None = None,
    what_to_show: str | None = None,
    use_rth: bool = False,
) -> list[dict]:
    """duration: '1 D', '30 D', '13 W', '6 M', '1 Y', '60 S', etc. (IBKR format).

    end_datetime: '' for now, or 'YYYYMMDD HH:MM:SS' UTC.
    """
    ib = await get_ib()
    qualified = await qualify(contract)
    log.debug(
        "historical_bars",
        conid=qualified.conId,
        symbol=qualified.symbol,
        duration=duration,
        bar_size=bar_size,
    )
    bars = await ib.reqHistoricalDataAsync(
        qualified,
        endDateTime=end_datetime or "",
        durationStr=duration,
        barSizeSetting=_resolve_bar_size(bar_size),
        whatToShow=_resolve_what_to_show(what_to_show),
        useRTH=use_rth,
        formatDate=2,  # epoch seconds
    )
    if bars is None:
        return []
    return [bar_dict(b) for b in bars]


async def historical_ticks(
    contract,
    *,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    number_of_ticks: int = 1000,
    what_to_show: str | None = None,
    use_rth: bool = False,
) -> list[dict]:
    ib = await get_ib()
    qualified = await qualify(contract)
    log.debug(
        "historical_ticks",
        conid=qualified.conId,
        symbol=qualified.symbol,
        n=number_of_ticks,
    )
    ticks = await ib.reqHistoricalTicksAsync(
        qualified,
        startDateTime=start_datetime or "",
        endDateTime=end_datetime or "",
        numberOfTicks=int(number_of_ticks),
        whatToShow=_resolve_what_to_show(what_to_show or "TRADES"),
        useRth=use_rth,
        ignoreSize=False,
    )
    return [tick_dict(t) for t in (ticks or [])]


def _wickworks_post(payload: dict) -> dict:
    if not WICKWORKS_URL:
        raise APIError(
            503,
            "Wickworks TA sidecar not configured",
            code=CODE_TA_SIDECAR_UNAVAILABLE,
            details={"hint": "set wickworks.url in config.yaml"},
        )
    # Reject anything other than http/https — defends against an
    # operator-misconfigured wickworks.url with `file:///` or other schemes
    # that urllib happily handles.
    if not WICKWORKS_URL.startswith(("http://", "https://")):
        raise APIError(
            503,
            "Wickworks URL must be http(s)",
            code=CODE_TA_SIDECAR_UNAVAILABLE,
            details={"got": WICKWORKS_URL.split(":", 1)[0]},
        )
    body = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(  # noqa: S310 — scheme allowlist enforced above
        WICKWORKS_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    log.debug("wickworks_call", url=WICKWORKS_URL, bytes=len(body))
    try:
        with urllib_request.urlopen(req, timeout=WICKWORKS_TIMEOUT_SECONDS) as resp:  # noqa: S310  # nosec B310 — scheme allowlist enforced above
            return json.loads(resp.read().decode("utf-8"))
    except urllib_error.HTTPError as exc:
        try:
            err_body = exc.read().decode("utf-8")
        except Exception as read_exc:  # body might already be consumed or non-UTF8
            log.debug("wickworks_http_error_body_unavailable", reason=str(read_exc))
            err_body = str(exc)
        log.warning("wickworks_http_error", status=exc.code, body=err_body[:500])
        raise APIError(
            502,
            f"Wickworks returned HTTP {exc.code}",
            code=CODE_UPSTREAM_FAILED,
            details={"upstream_status": exc.code, "upstream_body": err_body[:500]},
        ) from exc
    except urllib_error.URLError as exc:
        log.warning("wickworks_unreachable", err=str(exc.reason))
        raise APIError(
            502,
            "Wickworks unreachable",
            code=CODE_UPSTREAM_FAILED,
            details={"reason": str(exc.reason)},
        ) from exc


def ta_enrich(
    contract,
    bars: list[dict],
    *,
    indicators: dict,
    recent_bars: int | None = None,
) -> dict:
    """Wickworks TA enrichment phase. Caller supplies bars (typically
    from `cache_bars.get_or_fetch`); we just POST them to wickworks
    and shape the response.

    Split out from the (now deprecated) `rates_with_ta` so impl.py can
    cache the bars phase transparently. v0.3.0+ pattern."""
    payload = {
        "bars": bars,
        "indicators": indicators or {},
    }
    if recent_bars is not None:
        payload["recentBars"] = int(recent_bars)
    ta = _wickworks_post(payload)
    return {
        "symbol": contract.symbol,
        "secType": contract.secType,
        "bars": bars,
        "ta": ta.get("ta") if isinstance(ta, dict) else ta,
        "asOf": datetime.now(UTC).isoformat(),
    }


async def rates_with_ta(
    contract,
    *,
    duration: str,
    bar_size: str | None,
    end_datetime: str | None,
    what_to_show: str | None,
    use_rth: bool,
    indicators: dict,
    recent_bars: int | None = None,
) -> dict:
    """Legacy combined API — fetches bars then enriches. v0.3.0 impl.py
    no longer calls this; it composes `cache_bars.get_or_fetch` + the
    standalone `ta_enrich` instead so /rates/ta hits the bars cache.
    Kept for back-compat with any direct callers."""
    bars = await historical_bars(
        contract,
        duration=duration,
        bar_size=bar_size,
        end_datetime=end_datetime,
        what_to_show=what_to_show,
        use_rth=use_rth,
    )
    return ta_enrich(contract, bars, indicators=indicators, recent_bars=recent_bars)
