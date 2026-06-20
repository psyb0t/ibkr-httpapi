"""Preemptive rate-limiting gate that protects us from IBKR's pacing rules.

IBKR enforces strict pacing on the TWS API. Hitting their limits returns
error 162 and persistent abuse can revoke API access. We gate every
IBKR-bound request BEFORE forwarding to ib_async via three primitives:

  1. Sliding-window counter — refuses new requests when we're at the
     configured soft / hard thresholds (set BELOW IBKR's real cap for
     headroom).
  2. Per-contract per-second cap — IBKR rejects > 2/sec per contract
     for historical data; we mirror with a per-key sliding window.
  3. Per-contract asyncio.Lock — serializes concurrent requests for
     the SAME contract so they don't race against IBKR's per-contract
     pacing.
  4. Global asyncio.Semaphore — caps cross-contract concurrency under
     the TWS socket message ceiling (~50 msg/sec).

Three tiers — `historical`, `market_data`, `orders` — each with its
own threshold set. Defaults live in ibkrapi.config.PACING_TIERS.

Usage from impl.py:

    async with pacing.guard("historical", pacing.contract_key(c)):
        bars = await marketdata.historical_bars(c, ...)

On preempt, raises APIError(429, code=CODE_RATE_LIMIT_NEAR) with
details {rule, used, limit, window_sec, retry_after_sec, tier}.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
from collections import deque
from dataclasses import dataclass

from ibkrapi.errors import CODE_RATE_LIMIT_NEAR, APIError
from ibkrapi.logger import log


@dataclass
class TierConfig:
    per_window: int = 60
    per_window_soft: int = 50
    per_window_hard: int = 55
    window_sec: int = 600
    per_contract_per_sec: int = 2
    concurrent: int = 3
    name: str = "default"


class _SlidingWindow:
    def __init__(self, window_sec: float):
        self._window_sec = window_sec
        self._times: deque[float] = deque()

    def record(self, now: float) -> None:
        self._times.append(now)

    def prune(self, now: float) -> None:
        cutoff = now - self._window_sec
        while self._times and self._times[0] < cutoff:
            self._times.popleft()

    def count(self, now: float) -> int:
        self.prune(now)
        return len(self._times)

    def oldest(self, now: float) -> float | None:
        self.prune(now)
        return self._times[0] if self._times else None


class _PerKeyWindows:
    def __init__(self, window_sec: float):
        self._window_sec = window_sec
        self._by_key: dict[str, deque[float]] = {}

    def record(self, key: str, now: float) -> None:
        dq = self._by_key.setdefault(key, deque())
        dq.append(now)

    def count(self, key: str, now: float) -> int:
        dq = self._by_key.get(key)
        if dq is None:
            return 0
        cutoff = now - self._window_sec
        while dq and dq[0] < cutoff:
            dq.popleft()
        return len(dq)


class Tier:
    """Runtime state + acquire/release primitives for one pacing tier."""

    def __init__(self, cfg: TierConfig):
        if cfg.concurrent < 1:
            raise ValueError(f"pacing.{cfg.name}.concurrent must be >= 1")
        if cfg.per_window_hard > cfg.per_window:
            raise ValueError(
                f"pacing.{cfg.name}.per_window_hard ({cfg.per_window_hard}) "
                f"must be <= per_window ({cfg.per_window})"
            )
        self.cfg = cfg
        self._global = _SlidingWindow(cfg.window_sec)
        self._per_contract = _PerKeyWindows(window_sec=1.0)
        self._semaphore = asyncio.Semaphore(cfg.concurrent)
        self._contract_locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, key: str) -> asyncio.Lock:
        lk = self._contract_locks.get(key)
        if lk is None:
            lk = asyncio.Lock()
            self._contract_locks[key] = lk
        return lk

    def _preempt(self, contract_key: str | None) -> None:
        """Raise 429 if we'd cross hard caps. Pure-sync check, no locks held."""
        now = time.monotonic()
        used = self._global.count(now)
        if used >= self.cfg.per_window_hard:
            retry = self._retry_global(now)
            log.warning(
                "pacing_hard_cap",
                tier=self.cfg.name,
                used=used,
                hard=self.cfg.per_window_hard,
                retry_sec=retry,
            )
            raise APIError(
                429,
                (
                    f"Approaching IBKR {self.cfg.name} pacing "
                    f"({used}/{self.cfg.per_window} per {self.cfg.window_sec}s). "
                    "Backing off to protect API access."
                ),
                code=CODE_RATE_LIMIT_NEAR,
                details={
                    "rule": (f"{self.cfg.name}_{self.cfg.per_window}_per_{self.cfg.window_sec}s"),
                    "used": used,
                    "limit": self.cfg.per_window,
                    "window_sec": self.cfg.window_sec,
                    "retry_after_sec": retry,
                    "tier": self.cfg.name,
                },
            )
        if used >= self.cfg.per_window_soft:
            log.warning(
                "pacing_soft_cap",
                tier=self.cfg.name,
                used=used,
                soft=self.cfg.per_window_soft,
                hard=self.cfg.per_window_hard,
            )
        if contract_key is not None and self.cfg.per_contract_per_sec > 0:
            per_c = self._per_contract.count(contract_key, now)
            if per_c >= self.cfg.per_contract_per_sec:
                log.warning(
                    "pacing_per_contract_cap",
                    tier=self.cfg.name,
                    contract=contract_key,
                    used=per_c,
                    limit=self.cfg.per_contract_per_sec,
                )
                raise APIError(
                    429,
                    (
                        f"Per-contract pacing for {contract_key}: "
                        f"{per_c}/{self.cfg.per_contract_per_sec} in 1s"
                    ),
                    code=CODE_RATE_LIMIT_NEAR,
                    details={
                        "rule": f"{self.cfg.name}_per_contract_per_sec",
                        "contract": contract_key,
                        "used": per_c,
                        "limit": self.cfg.per_contract_per_sec,
                        "retry_after_sec": 1,
                        "tier": self.cfg.name,
                    },
                )

    def _retry_global(self, now: float) -> int:
        oldest = self._global.oldest(now)
        if oldest is None:
            return 1
        return max(1, int(self.cfg.window_sec - (now - oldest)) + 1)

    async def acquire(self, contract_key: str | None) -> None:
        """Block until allowed in. Raises 429 if preemptive limit hit."""
        self._preempt(contract_key)
        if contract_key is not None:
            await self._lock_for(contract_key).acquire()
        await self._semaphore.acquire()
        now = time.monotonic()
        self._global.record(now)
        if contract_key is not None:
            self._per_contract.record(contract_key, now)

    def release(self, contract_key: str | None) -> None:
        with contextlib.suppress(ValueError):
            self._semaphore.release()
        if contract_key is not None:
            lk = self._contract_locks.get(contract_key)
            if lk is not None and lk.locked():
                lk.release()


_TIERS: dict[str, Tier] = {}


def configure(tiers: dict[str, TierConfig]) -> None:
    """Reset state. Called at app startup with the resolved config dict."""
    _TIERS.clear()
    for name, cfg in tiers.items():
        cfg.name = name
        _TIERS[name] = Tier(cfg)
    log.info(
        "pacing_configured",
        tiers={
            n: {"per_window": t.cfg.per_window, "concurrent": t.cfg.concurrent}
            for n, t in _TIERS.items()
        },
    )


def get_tier(name: str) -> Tier:
    t = _TIERS.get(name)
    if t is None:
        raise KeyError(f"pacing tier {name!r} not configured")
    return t


class _Guard:
    def __init__(self, tier_name: str, contract_key: str | None):
        self._tier_name = tier_name
        self._contract_key = contract_key
        self._tier: Tier | None = None

    async def __aenter__(self) -> _Guard:
        self._tier = get_tier(self._tier_name)
        await self._tier.acquire(self._contract_key)
        return self

    async def __aexit__(self, _exc_type, _exc, _tb) -> bool:
        if self._tier is not None:
            self._tier.release(self._contract_key)
        return False


def guard(tier: str, contract_key: str | None = None) -> _Guard:
    """Async context manager: `async with pacing.guard('historical', key): ...`"""
    return _Guard(tier, contract_key)


def contract_key(contract) -> str:
    """Stable key string for an ib_async Contract."""
    parts = [
        getattr(contract, "secType", "?") or "?",
        getattr(contract, "symbol", "") or "",
        getattr(contract, "exchange", "") or "",
        getattr(contract, "currency", "") or "",
    ]
    for opt in ("lastTradeDateOrContractMonth", "strike", "right"):
        v = getattr(contract, opt, None)
        if v:
            parts.append(str(v))
    return ":".join(parts)
