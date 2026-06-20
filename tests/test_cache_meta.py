"""Tests for ibkrapi.cache_meta — long-TTL JSON cache."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime

import pytest
from ibkrapi import cache_meta


@pytest.fixture
def meta_dir(tmp_path):
    cache_meta.configure(cache_meta.MetaCacheConfig(enabled=True, path=str(tmp_path)))
    yield str(tmp_path)
    cache_meta.configure(cache_meta.MetaCacheConfig(enabled=False))


def test_put_then_get_returns_value(meta_dir):
    cache_meta.put("contract_details", "STK:AAPL", {"conId": 265598})
    out = cache_meta.get("contract_details", "STK:AAPL")
    assert out == {"conId": 265598}


def test_get_missing_returns_none(meta_dir):
    assert cache_meta.get("contract_details", "STK:DOESNOTEXIST") is None


def test_expired_entry_returns_none(meta_dir):
    cache_meta.put("contract_details", "STK:X", {"conId": 1}, ttl_sec=1)
    # Manually backdate the cached_at field so the entry is "expired".
    path = cache_meta._file_path("contract_details", "STK:X")
    with open(path, encoding="utf-8") as fh:
        env = json.load(fh)
    env["cached_at"] = int(datetime.now(UTC).timestamp()) - 100
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(env, fh)
    assert cache_meta.get("contract_details", "STK:X") is None


async def test_get_or_fetch_miss_calls_fetcher(meta_dir):
    calls = 0

    async def fetcher():
        nonlocal calls
        calls += 1
        return {"hello": "world"}

    out, status = await cache_meta.get_or_fetch("contract_details", "STK:Y", fetcher)
    assert out == {"hello": "world"}
    assert status == "miss"
    assert calls == 1


async def test_get_or_fetch_hit_does_not_call_fetcher(meta_dir):
    cache_meta.put("contract_details", "STK:Z", {"v": 1})

    async def fetcher():
        raise RuntimeError("must not be called")

    out, status = await cache_meta.get_or_fetch("contract_details", "STK:Z", fetcher)
    assert out == {"v": 1}
    assert status == "hit"


async def test_get_or_fetch_refresh_bypasses_cache(meta_dir):
    cache_meta.put("contract_details", "STK:R", {"v": "old"})

    async def fetcher():
        return {"v": "new"}

    out, status = await cache_meta.get_or_fetch("contract_details", "STK:R", fetcher, refresh=True)
    assert out == {"v": "new"}
    assert status == "refresh"
    assert cache_meta.get("contract_details", "STK:R") == {"v": "new"}


async def test_get_or_fetch_single_flight(meta_dir):
    """N concurrent misses for the same key → fetcher called once."""
    calls = 0

    async def slow_fetcher():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.05)
        return {"v": "single"}

    results = await asyncio.gather(
        *[cache_meta.get_or_fetch("contract_details", "STK:SF", slow_fetcher) for _ in range(5)]
    )
    assert calls == 1
    assert all(r[0] == {"v": "single"} for r in results)


def test_invalidate_removes_file(meta_dir):
    cache_meta.put("contract_details", "STK:I", {"v": 1})
    cache_meta.invalidate("contract_details", "STK:I")
    assert cache_meta.get("contract_details", "STK:I") is None


def test_disabled_cache(tmp_path):
    cache_meta.configure(cache_meta.MetaCacheConfig(enabled=False, path=str(tmp_path)))
    cache_meta.put("contract_details", "STK:D", {"v": 1})
    assert cache_meta.get("contract_details", "STK:D") is None


def test_safe_filenames(meta_dir):
    cache_meta.put("contract_details", "OPT:SPY/240615C00400000", {"x": 1})
    # Must not have raw slash in filename
    import os

    files = []
    for root, _, fns in os.walk(meta_dir):
        for fn in fns:
            files.append(os.path.join(root, fn))
    assert any("/" not in f.rsplit("/", 1)[1] for f in files)


def test_ttl_defaults_per_scope():
    assert cache_meta.DEFAULT_TTL_SEC["contract_details"] == 7 * 24 * 3600
    assert cache_meta.DEFAULT_TTL_SEC["futures_expiries"] == 24 * 3600
    assert cache_meta.DEFAULT_TTL_SEC["chain_strike_list"] == 24 * 3600


def test_corrupt_file_returns_none(meta_dir, tmp_path):
    path = tmp_path / "contract_details" / "STK_C.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not json", encoding="utf-8")
    assert cache_meta.get("contract_details", "STK:C") is None
