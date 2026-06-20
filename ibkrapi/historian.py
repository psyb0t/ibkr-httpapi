"""Live-response historian — piggyback on /tick + /chain to grow the goldmine.

Every call to a "live" endpoint that returns point-in-time data also
appends a snapshot row to disk. No extra IBKR hits — the same response
the caller gets is forked off to the historian.

Two file shapes:

  - Per-contract tick snapshots:
        data/history/snapshots/<class>/<symbol>.csv (or .../<UNDERLYING>/<OCC>.csv
        for options)
    Columns: time,bid,ask,last,bidSize,askSize,lastSize,volume,iv,delta,
             gamma,theta,vega,underlyingPrice
    Most columns are empty for non-options.

  - Per-chain snapshots (one row per strike per snapshot):
        data/history/chains/<UNDERLYING>/<EXPIRY>.csv
    Columns: time,exchange,tradingClass,multiplier,strike

The historian writes are best-effort — a failure NEVER blocks the
caller's response. Errors logged at WARN, the request still succeeds.
"""

from __future__ import annotations

import asyncio
import csv
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from ibkrapi.logger import log

_TICK_HEADER = [
    "time",
    "bid",
    "ask",
    "last",
    "bidSize",
    "askSize",
    "lastSize",
    "volume",
    "iv",
    "delta",
    "gamma",
    "theta",
    "vega",
    "underlyingPrice",
]

_CHAIN_HEADER = [
    "time",
    "exchange",
    "tradingClass",
    "multiplier",
    "strike",
]

_SYMBOL_SAFE = re.compile(r"[^A-Za-z0-9._\-]")


def _safe(s: str) -> str:
    return _SYMBOL_SAFE.sub("_", s or "")


@dataclass
class HistorianConfig:
    enabled: bool = True
    path: str = "/app/data/history"


_CFG = HistorianConfig()
_LOCKS: dict[str, asyncio.Lock] = {}


def configure(cfg: HistorianConfig) -> None:
    global _CFG
    _CFG = cfg
    if cfg.enabled:
        os.makedirs(os.path.join(cfg.path, "snapshots"), exist_ok=True)
        os.makedirs(os.path.join(cfg.path, "chains"), exist_ok=True)
        log.info("historian_configured", path=cfg.path)


def _lock(path: str) -> asyncio.Lock:
    lk = _LOCKS.get(path)
    if lk is None:
        lk = asyncio.Lock()
        _LOCKS[path] = lk
    return lk


def snapshot_path(
    asset_class: str,
    symbol: str,
    *,
    underlying: str | None = None,
) -> str:
    """File path for a per-contract tick-snapshot history."""
    cls = _safe(asset_class)
    sym = _safe(symbol)
    if asset_class.lower().startswith("opt") and underlying:
        return os.path.join(_CFG.path, "snapshots", cls, _safe(underlying), f"{sym}.csv")
    return os.path.join(_CFG.path, "snapshots", cls, f"{sym}.csv")


def chain_path(underlying: str, expiry: str) -> str:
    """File path for a per-chain snapshot history."""
    return os.path.join(_CFG.path, "chains", _safe(underlying), f"{_safe(expiry)}.csv")


def _now() -> int:
    return int(datetime.now(UTC).timestamp())


def _extract_tick_row(ticker: dict, now: int) -> list:
    """Pluck the values we want out of an ibkrapi.serialize.ticker_dict."""
    greeks = ticker.get("modelGreeks") or ticker.get("greeks") or {}
    return [
        now,
        ticker.get("bid"),
        ticker.get("ask"),
        ticker.get("last"),
        ticker.get("bidSize"),
        ticker.get("askSize"),
        ticker.get("lastSize"),
        ticker.get("volume"),
        greeks.get("impliedVol"),
        greeks.get("delta"),
        greeks.get("gamma"),
        greeks.get("theta"),
        greeks.get("vega"),
        greeks.get("undPrice") or ticker.get("underlyingPrice"),
    ]


def _append_row(path: str, header: list[str], row: list) -> None:
    """Synchronous append. Caller MUST hold the path's lock."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new_file = not os.path.isfile(path)
    with open(path, "a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        if new_file:
            writer.writerow(header)
        writer.writerow(row)


async def record_tick(
    asset_class: str,
    symbol: str,
    ticker: dict,
    *,
    underlying: str | None = None,
) -> None:
    """Best-effort: append a tick snapshot row. Never raises."""
    if not _CFG.enabled:
        return
    path = snapshot_path(asset_class, symbol, underlying=underlying)
    try:
        async with _lock(path):
            row = _extract_tick_row(ticker, _now())
            _append_row(path, _TICK_HEADER, row)
    except Exception as exc:
        log.warning(
            "historian_tick_failed",
            err=str(exc),
            asset_class=asset_class,
            symbol=symbol,
        )


async def record_chain(
    underlying: str,
    chain_entries: list[dict[str, Any]],
) -> None:
    """Best-effort: append one row per strike per (underlying, expiry) file.

    `chain_entries` is the list of OptionChainEntry-shaped dicts from
    /options/{symbol}/chain — one entry per (exchange, expirations[],
    strikes[], tradingClass, multiplier).
    """
    if not _CFG.enabled:
        return
    now = _now()
    # group rows by (expiry) since we file per-expiry
    by_expiry: dict[str, list[list]] = {}
    for entry in chain_entries:
        exchange = entry.get("exchange") or ""
        trading_class = entry.get("tradingClass") or ""
        multiplier = entry.get("multiplier") or ""
        for expiry in entry.get("expirations") or []:
            for strike in entry.get("strikes") or []:
                by_expiry.setdefault(expiry, []).append(
                    [now, exchange, trading_class, multiplier, strike]
                )
    for expiry, rows in by_expiry.items():
        path = chain_path(underlying, expiry)
        try:
            async with _lock(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                new_file = not os.path.isfile(path)
                with open(path, "a", encoding="utf-8", newline="") as fh:
                    writer = csv.writer(fh)
                    if new_file:
                        writer.writerow(_CHAIN_HEADER)
                    writer.writerows(rows)
        except Exception as exc:
            log.warning(
                "historian_chain_failed",
                err=str(exc),
                underlying=underlying,
                expiry=expiry,
            )
