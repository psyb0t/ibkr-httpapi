"""Long-TTL JSON cache for quasi-static metadata.

For things that change rarely (contract metadata, futures expiry lists,
options chain strike lists) we cache the raw response as a JSON file
with an embedded `cached_at` timestamp + per-scope TTL. Reads return
the cached value if not expired, else None (caller refetches).

File layout: data/history/meta/<scope>/<key>.json
Each file: {"cached_at": <epoch>, "ttl_sec": <int>, "value": <payload>}

Scopes have sensible default TTLs (overridable via config):
  - contract_details:  7 days  (conId/tickSize/multiplier rarely change)
  - futures_expiries:  1 day   (new expiry strips added daily)
  - chain_strike_list: 1 day   (new strikes added intraday but slow)

Refresh modes:
  - get(scope, key) returns cached value if fresh, None if expired/missing
  - put(scope, key, value, ttl_sec) writes
  - get_or_fetch(scope, key, fetcher, ttl_sec) cache-aside helper with
    per-key asyncio.Lock single-flight

Per the caching rule (~/.claude/rule-details/adding-caching.md):
  - Every cached value has a TTL (no perma-cache)
  - Single-flight on miss prevents concurrent re-fetch stampede
  - Keys are sanitized (no user-controlled chars hit the filename)
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from ibkrapi.logger import log

DEFAULT_TTL_SEC = {
    "contract_details": 7 * 24 * 3600,
    "futures_expiries": 24 * 3600,
    "chain_strike_list": 24 * 3600,
}

_SAFE = re.compile(r"[^A-Za-z0-9._\-]")


def _safe(s: str) -> str:
    return _SAFE.sub("_", s or "")


@dataclass
class MetaCacheConfig:
    enabled: bool = True
    path: str = "/app/data/history/meta"
    ttl_sec: dict[str, int] | None = None


_CFG = MetaCacheConfig()
_KEY_LOCKS: dict[str, asyncio.Lock] = {}


def configure(cfg: MetaCacheConfig) -> None:
    global _CFG
    _CFG = cfg
    if cfg.enabled:
        os.makedirs(cfg.path, exist_ok=True)
        log.info("meta_cache_configured", path=cfg.path)


def _lock(file_key: str) -> asyncio.Lock:
    lk = _KEY_LOCKS.get(file_key)
    if lk is None:
        lk = asyncio.Lock()
        _KEY_LOCKS[file_key] = lk
    return lk


def _file_path(scope: str, key: str) -> str:
    return os.path.join(_CFG.path, _safe(scope), f"{_safe(key)}.json")


def _ttl_for(scope: str) -> int:
    if _CFG.ttl_sec and scope in _CFG.ttl_sec:
        return int(_CFG.ttl_sec[scope])
    return DEFAULT_TTL_SEC.get(scope, 3600)


def _now() -> int:
    return int(datetime.now(UTC).timestamp())


def get(scope: str, key: str) -> Any | None:
    """Return cached value if fresh, else None."""
    if not _CFG.enabled:
        return None
    path = _file_path(scope, key)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            envelope = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("meta_cache_read_failed", path=path, err=str(exc))
        return None
    cached_at = int(envelope.get("cached_at") or 0)
    ttl = int(envelope.get("ttl_sec") or 0)
    if cached_at + ttl <= _now():
        return None
    return envelope.get("value")


def put(scope: str, key: str, value: Any, ttl_sec: int | None = None) -> None:
    """Persist value with TTL. Atomic write via tmp+rename."""
    if not _CFG.enabled:
        return
    path = _file_path(scope, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    envelope = {
        "cached_at": _now(),
        "ttl_sec": int(ttl_sec or _ttl_for(scope)),
        "value": value,
    }
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(envelope, fh, default=str)
    os.replace(tmp, path)


async def get_or_fetch(
    scope: str,
    key: str,
    fetcher: Callable[[], Awaitable[Any]],
    *,
    ttl_sec: int | None = None,
    refresh: bool = False,
) -> tuple[Any, str]:
    """Cache-aside with per-key single-flight.

    Returns (value, status) where status in {hit, miss, refresh, disabled}.
    """
    if not _CFG.enabled:
        return await fetcher(), "disabled"

    if not refresh:
        cached = get(scope, key)
        if cached is not None:
            return cached, "hit"

    async with _lock(_file_path(scope, key)):
        # Re-check after acquiring the lock — another caller may have
        # populated while we waited (classic single-flight pattern).
        if not refresh:
            cached = get(scope, key)
            if cached is not None:
                return cached, "hit"
        fresh = await fetcher()
        put(scope, key, fresh, ttl_sec=ttl_sec)
        log.info(
            "meta_cache_write",
            scope=scope,
            key=key,
            status="refresh" if refresh else "miss",
        )
        return fresh, ("refresh" if refresh else "miss")


def invalidate(scope: str, key: str) -> None:
    if not _CFG.enabled:
        return
    path = _file_path(scope, key)
    try:
        os.remove(path)
    except FileNotFoundError:
        return
    except OSError as exc:
        log.warning("meta_cache_invalidate_failed", path=path, err=str(exc))
