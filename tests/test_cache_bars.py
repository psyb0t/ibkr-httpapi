"""Tests for ibkrapi.cache_bars — per-contract CSV cache."""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest
from ibkrapi import cache_bars


@pytest.fixture
def cache_dir(tmp_path):
    cache_bars.configure(
        cache_bars.CacheConfig(
            enabled=True,
            path=str(tmp_path),
            refresh_tail_bars=5,
            persist_open_bar=False,
        )
    )
    yield str(tmp_path)
    cache_bars.configure(cache_bars.CacheConfig(enabled=False))


def _bar(t: int, c: float = 100.0) -> dict:
    return {"time": t, "open": c, "high": c + 1, "low": c - 1, "close": c, "volume": 1000}


def test_normalize_tf():
    assert cache_bars._normalize_tf("1h") == "H1"
    assert cache_bars._normalize_tf("15m") == "M15"
    assert cache_bars._normalize_tf("1d") == "D1"
    assert cache_bars._normalize_tf("1w") == "W1"
    assert cache_bars._normalize_tf(None) == "H1"  # default


def test_cache_path_stocks(cache_dir):
    p = cache_bars.cache_path("stocks", "AAPL", "1h")
    assert p == os.path.join(cache_dir, "stocks", "AAPL_H1.csv")


def test_cache_path_options_grouped_by_underlying(cache_dir):
    p = cache_bars.cache_path("options", "SPY 240615C00400000", "15m", underlying="SPY")
    # Spaces in OCC sanitize to _; grouped under SPY/
    assert p == os.path.join(cache_dir, "options", "SPY", "SPY_240615C00400000_M15.csv")


def test_cache_path_safe_chars(cache_dir):
    p = cache_bars.cache_path("forex", "EUR/USD", "1m")
    assert "/" not in os.path.basename(p)
    assert os.path.basename(p) == "EUR_USD_M1.csv"


def test_to_epoch_variants():
    assert cache_bars._to_epoch(1718798400) == 1718798400
    assert cache_bars._to_epoch("1718798400") == 1718798400
    assert cache_bars._to_epoch("2024-06-19T12:00:00Z") == int(
        datetime(2024, 6, 19, 12, 0, 0, tzinfo=UTC).timestamp()
    )
    assert cache_bars._to_epoch("2024-06-19T12:00:00+00:00") == int(
        datetime(2024, 6, 19, 12, 0, 0, tzinfo=UTC).timestamp()
    )
    assert cache_bars._to_epoch(None) is None
    assert cache_bars._to_epoch("garbage") is None
    assert cache_bars._to_epoch("") is None


async def test_get_or_fetch_miss_writes_full(cache_dir):
    path = cache_bars.cache_path("stocks", "AAPL", "1h")
    bars_in = [_bar(1000), _bar(1000 + 3600), _bar(1000 + 7200)]

    async def fetcher():
        return bars_in

    out, status = await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="AAPL",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher,
    )
    assert status == "miss"
    assert out == bars_in
    on_disk = cache_bars.read(path)
    assert len(on_disk) == 3


async def test_get_or_fetch_hit_no_growth(cache_dir):
    """Second call with same data → no new bars added → status 'hit'."""
    bars_in = [_bar(1000), _bar(4600)]

    async def fetcher():
        return bars_in

    await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="AAPL",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher,
    )
    _, status = await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="AAPL",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher,
    )
    assert status == "hit"


async def test_get_or_fetch_partial_grows_file(cache_dir):
    """New bars beyond what's cached → status 'partial', file grows."""
    initial = [_bar(1000), _bar(4600)]
    extra = [*initial, _bar(8200), _bar(11800)]

    async def fetcher_1():
        return initial

    async def fetcher_2():
        return extra

    await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="AAPL",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher_1,
    )
    _, status = await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="AAPL",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher_2,
    )
    assert status == "partial"
    on_disk = cache_bars.read(cache_bars.cache_path("stocks", "AAPL", "1h"))
    assert len(on_disk) == 4


async def test_get_or_fetch_refresh_bypasses_but_writes(cache_dir):
    """refresh=true returns fresh, but the file still gets merged + written."""
    initial = [_bar(1000), _bar(4600)]
    fresh = [_bar(4600, c=101.5)]  # correction on time=4600

    async def fetcher_1():
        return initial

    async def fetcher_2():
        return fresh

    await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="AAPL",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher_1,
    )
    out, status = await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="AAPL",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher_2,
        refresh=True,
    )
    assert status == "refresh"
    assert out == fresh
    on_disk = cache_bars.read(cache_bars.cache_path("stocks", "AAPL", "1h"))
    # Original bar at t=1000 still present.
    assert any(b["time"] == 1000 for b in on_disk)
    # t=4600 was overwritten with the correction.
    [t46] = [b for b in on_disk if b["time"] == 4600]
    assert t46["close"] == 101.5


async def test_open_bar_dropped_by_default(cache_dir):
    """Last bar whose window includes 'now' is filtered before write."""
    now = int(datetime.now(UTC).timestamp())
    closed = _bar(now - 4 * 3600)  # closed 4h ago
    open_bar = _bar(now - 100, c=999.0)  # bar started 100s ago, 1h window → still open

    async def fetcher():
        return [closed, open_bar]

    await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="X",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher,
    )
    on_disk = cache_bars.read(cache_bars.cache_path("stocks", "X", "1h"))
    assert len(on_disk) == 1
    assert on_disk[0]["time"] == closed["time"]


async def test_disabled_cache_passes_through(tmp_path):
    cache_bars.configure(cache_bars.CacheConfig(enabled=False, path=str(tmp_path)))
    bars = [_bar(1000)]

    async def fetcher():
        return bars

    out, status = await cache_bars.get_or_fetch(
        asset_class="stocks",
        symbol="AAPL",
        bar_size="1h",
        underlying=None,
        requested_bars=None,
        fetch_full=fetcher,
    )
    assert status == "disabled"
    assert out == bars
    # No file should have been written.
    assert not (tmp_path / "stocks").exists()


def test_csv_round_trip(cache_dir):
    path = cache_bars.cache_path("stocks", "RT", "1h")
    bars = [
        {"time": 1000, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 100},
        {"time": 4600, "open": 1.5, "high": 2.5, "low": 1.0, "close": 2.0, "volume": 200},
    ]
    cache_bars._write_atomic(
        path,
        [
            {
                "time": b["time"],
                "open": b["open"],
                "high": b["high"],
                "low": b["low"],
                "close": b["close"],
                "tickVolume": b["volume"],
            }
            for b in bars
        ],
    )
    loaded = cache_bars.read(path)
    assert len(loaded) == 2
    assert loaded[0]["time"] == 1000
    assert loaded[1]["close"] == 2.0


def test_corrupt_header_returns_empty(cache_dir, tmp_path):
    path = tmp_path / "stocks" / "CORRUPT_H1.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("garbage,header,here\n100,1,2,3,4,5\n", encoding="utf-8")
    assert cache_bars.read(str(path)) == []
