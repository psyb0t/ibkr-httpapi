"""Per-(class, symbol, timeframe) CSV cache for OHLC bars.

The cache file format is wickworks-shaped CSV — one header row plus
bars sorted ascending by `time` (unix epoch seconds):

    time,open,high,low,close,tickVolume
    1718798400,150.25,150.80,150.10,150.60,123456

One file per contract per timeframe under `<root>/<class>/<key>_<TF>.csv`.
For options, contracts are grouped per underlying:
`<root>/options/<UNDERLYING>/<OCC>_<TF>.csv`.

Behavior for a /rates request:

  1. Compute requested window from `duration` + `endDateTime`.
  2. Read existing cache.
  3. Always re-pull the last `refresh_tail_bars` (the in-progress bar
     and the few preceding ones — handles late corrections).
  4. If cache covers the window minus the tail-refresh range: serve
     from disk merged with the freshly fetched tail.
  5. If cache is partial / empty: fetch the missing window from IBKR,
     append to file, return merged.
  6. `?refresh=true` bypasses the cache entirely (still writes after).
  7. The "open" / not-yet-closed bar is dropped unless `persist_open_bar`
     is true — open bars are not part of the goldmine.

Append-only — bars never deleted. Per-file asyncio.Lock prevents
concurrent writers from clobbering each other. CSV format chosen for
debuggability + universal ingest; later cold storage can be parquet.
"""

from __future__ import annotations

import asyncio
import csv
import os
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from ibkrapi.logger import log

# Wickworks-shape header. NEVER change without bumping a schema version
# in the filename — the cache files ARE the goldmine, format stability
# matters.
_HEADER = ["time", "open", "high", "low", "close", "tickVolume"]


@dataclass
class CacheConfig:
    enabled: bool = True
    path: str = "/app/data/history"
    refresh_tail_bars: int = 5
    persist_open_bar: bool = False


# Initialized via configure(); referenced by every cache call.
_CFG = CacheConfig()
_FILE_LOCKS: dict[str, asyncio.Lock] = {}


def configure(cfg: CacheConfig) -> None:
    global _CFG
    _CFG = cfg
    if cfg.enabled:
        os.makedirs(cfg.path, exist_ok=True)
        log.info(
            "bars_cache_configured",
            path=cfg.path,
            refresh_tail_bars=cfg.refresh_tail_bars,
        )


def _normalize_tf(bar_size: str | None) -> str:
    """Map an IBKR bar_size string (1h / 15m / 1d) to the MT5/wickworks
    short form (H1 / M15 / D1) used in cache filenames."""
    if not bar_size:
        return "H1"
    raw = bar_size.strip().lower()
    table = {
        "1s": "S1",
        "5s": "S5",
        "10s": "S10",
        "15s": "S15",
        "30s": "S30",
        "1m": "M1",
        "2m": "M2",
        "3m": "M3",
        "5m": "M5",
        "10m": "M10",
        "15m": "M15",
        "20m": "M20",
        "30m": "M30",
        "1h": "H1",
        "2h": "H2",
        "3h": "H3",
        "4h": "H4",
        "8h": "H8",
        "1d": "D1",
        "1w": "W1",
        "1mo": "MN1",
    }
    if raw in table:
        return table[raw]
    # accept also the verbose IBKR form "1 hour", "15 mins"
    for k, v in table.items():
        if raw.startswith(k):
            return v
    return raw.upper().replace(" ", "_")


_SYMBOL_SAFE = re.compile(r"[^A-Za-z0-9._\-]")


def _safe(s: str) -> str:
    """Filesystem-safe form — keep ASCII alnum + dot/underscore/dash."""
    return _SYMBOL_SAFE.sub("_", s)


def cache_path(
    asset_class: str,
    symbol: str,
    timeframe: str,
    *,
    underlying: str | None = None,
) -> str:
    """Resolve the CSV file path for a contract+timeframe.

    `underlying` groups options under `<root>/options/<underlying>/`.
    For other classes it's ignored.
    """
    tf = _normalize_tf(timeframe)
    cls = _safe(asset_class)
    sym = _safe(symbol)
    if asset_class.lower().startswith("opt") and underlying:
        return os.path.join(_CFG.path, cls, _safe(underlying), f"{sym}_{tf}.csv")
    return os.path.join(_CFG.path, cls, f"{sym}_{tf}.csv")


def _to_epoch(value) -> int | None:
    """Convert a bar's `time` field (ISO string, datetime, or epoch) to
    unix seconds. Returns None on parse failure (bar is dropped)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=UTC)
        return int(dt.timestamp())
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return int(dt.timestamp())
    except ValueError:
        return None


def _wickworks_row(bar: dict) -> list | None:
    """Convert a marketdata.historical_bars dict into a CSV row."""
    t = _to_epoch(bar.get("time"))
    if t is None:
        return None
    return [
        t,
        bar.get("open"),
        bar.get("high"),
        bar.get("low"),
        bar.get("close"),
        bar.get("volume"),
    ]


def _from_csv_row(row: list[str]) -> dict | None:
    if len(row) < 6:
        return None
    try:
        return {
            "time": int(row[0]),
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "tickVolume": int(row[5]) if row[5].isdigit() else float(row[5]),
        }
    except (ValueError, IndexError):
        return None


def read(path: str) -> list[dict]:
    """Load cached bars from disk. Returns [] if file missing/unreadable."""
    if not os.path.isfile(path):
        return []
    out: list[dict] = []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            return []
        if header != _HEADER:
            log.warning("bars_cache_header_mismatch", path=path, got=header)
            return []
        for row in reader:
            d = _from_csv_row(row)
            if d is not None:
                out.append(d)
    out.sort(key=lambda b: b["time"])
    return out


def _merge_append(existing: list[dict], fresh: list[dict]) -> list[dict]:
    """Combine cached + freshly-fetched bars; fresh wins for any
    time collision (corrections to recent bars)."""
    by_time = {b["time"]: b for b in existing}
    for b in fresh:
        by_time[b["time"]] = b
    return sorted(by_time.values(), key=lambda b: b["time"])


def _write_atomic(path: str, bars: list[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(_HEADER)
        for b in bars:
            writer.writerow(
                [
                    b["time"],
                    b["open"],
                    b["high"],
                    b["low"],
                    b["close"],
                    b.get("tickVolume", b.get("volume")),
                ]
            )
    os.replace(tmp, path)


def _file_lock(path: str) -> asyncio.Lock:
    lk = _FILE_LOCKS.get(path)
    if lk is None:
        lk = asyncio.Lock()
        _FILE_LOCKS[path] = lk
    return lk


def _drop_open_bar(bars: list[dict], bar_size_sec: int | None) -> list[dict]:
    """Drop the most-recent bar if its candle window includes 'now'."""
    if not bars or bar_size_sec is None or _CFG.persist_open_bar:
        return bars
    now = int(datetime.now(UTC).timestamp())
    last = bars[-1]
    if last["time"] + bar_size_sec > now:
        return bars[:-1]
    return bars


_BAR_SIZE_SEC = {
    "1s": 1,
    "5s": 5,
    "10s": 10,
    "15s": 15,
    "30s": 30,
    "1m": 60,
    "2m": 120,
    "3m": 180,
    "5m": 300,
    "10m": 600,
    "15m": 900,
    "20m": 1200,
    "30m": 1800,
    "1h": 3600,
    "2h": 7200,
    "3h": 10800,
    "4h": 14400,
    "8h": 28800,
    "1d": 86400,
    "1w": 604800,
}


def bar_size_seconds(raw: str | None) -> int | None:
    if not raw:
        return 3600
    return _BAR_SIZE_SEC.get(raw.strip().lower())


async def get_or_fetch(
    *,
    asset_class: str,
    symbol: str,
    bar_size: str | None,
    underlying: str | None,
    requested_bars: list[dict],
    fetch_full: Callable[[], Awaitable[list[dict]]],
    refresh: bool = False,
) -> tuple[list[dict], str]:
    """High-level cache-aside.

    `requested_bars` is what IBKR (or our caller-fetched window) would
    return for the requested window. Pass it in already-fetched OR
    None+fetch_full() to lazy-fetch only on miss.

    Returns (bars, cache_status) where cache_status in {hit, partial, miss, refresh}.

    Behavior: always writes the union (existing + fetched) back to disk
    so the goldmine grows on every call.
    """
    if not _CFG.enabled:
        bars = requested_bars or await fetch_full()
        return bars, "disabled"

    path = cache_path(asset_class, symbol, bar_size or "H1", underlying=underlying)
    async with _file_lock(path):
        existing = read(path)

        if refresh:
            fresh = requested_bars or await fetch_full()
            merged = _merge_append(existing, fresh)
            merged = _drop_open_bar(merged, bar_size_seconds(bar_size))
            _write_atomic(path, merged)
            log.info(
                "bars_cache_refresh",
                path=path,
                existing=len(existing),
                fresh=len(fresh),
                total=len(merged),
            )
            return fresh, "refresh"

        fresh = requested_bars if requested_bars is not None else await fetch_full()
        merged = _merge_append(existing, fresh)
        merged = _drop_open_bar(merged, bar_size_seconds(bar_size))
        _write_atomic(path, merged)

        if not existing:
            status = "miss"
        elif len(merged) > len(existing):
            status = "partial"
        else:
            status = "hit"
        log.info(
            "bars_cache_write",
            path=path,
            status=status,
            existing=len(existing),
            fresh=len(fresh),
            total=len(merged),
        )
        return fresh, status


def append(path: str, bars: list[dict]) -> int:
    """Low-level append. Returns the new total bar count after merge.

    Synchronous — callers should hold the per-file lock if concurrency
    matters. Use `get_or_fetch` for the integrated cache-aside flow.
    """
    rows = [_wickworks_row(b) for b in bars]
    fresh = [
        {"time": r[0], "open": r[1], "high": r[2], "low": r[3], "close": r[4], "tickVolume": r[5]}
        for r in rows
        if r is not None
    ]
    existing = read(path)
    merged = _merge_append(existing, fresh)
    _write_atomic(path, merged)
    return len(merged)
