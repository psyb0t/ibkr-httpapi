"""Tests for ibkrapi.pacing — preemptive rate-limit gate."""

from __future__ import annotations

import asyncio

import pytest
from ibkrapi import pacing
from ibkrapi.errors import CODE_RATE_LIMIT_NEAR, APIError


@pytest.fixture(autouse=True)
def fresh_tiers():
    pacing.configure(
        {
            "historical": pacing.TierConfig(
                per_window=10,
                per_window_soft=7,
                per_window_hard=8,
                window_sec=60,
                per_contract_per_sec=2,
                concurrent=3,
            ),
            "market_data": pacing.TierConfig(
                per_window=60,
                per_window_soft=50,
                per_window_hard=55,
                window_sec=1,
                per_contract_per_sec=5,
                concurrent=4,
            ),
        }
    )
    yield
    pacing.configure({})


async def test_under_soft_passes_no_warning():
    async with pacing.guard("historical", "STK:AAPL"):
        pass


async def test_hard_cap_raises_429():
    # Push to the hard cap (8). Use UNIQUE contract keys so we hit the
    # global window cap, not the per-contract per-second cap.
    for i in range(8):
        async with pacing.guard("historical", f"STK:H{i}"):
            pass
    with pytest.raises(APIError) as exc:
        async with pacing.guard("historical", "STK:OVER"):
            pass
    assert exc.value.status_code == 429
    assert exc.value.code == CODE_RATE_LIMIT_NEAR
    assert exc.value.details["rule"].startswith("historical_")
    assert exc.value.details["used"] >= 8
    assert exc.value.details["limit"] == 10


async def test_per_contract_per_sec_raises():
    # 2/sec cap. Two pass, third fails.
    async with pacing.guard("historical", "STK:AAPL"):
        pass
    async with pacing.guard("historical", "STK:AAPL"):
        pass
    with pytest.raises(APIError) as exc:
        async with pacing.guard("historical", "STK:AAPL"):
            pass
    assert exc.value.details["rule"] == "historical_per_contract_per_sec"
    assert exc.value.details["contract"] == "STK:AAPL"


async def test_per_contract_independent_of_other_contracts():
    async with pacing.guard("historical", "STK:AAPL"):
        pass
    async with pacing.guard("historical", "STK:AAPL"):
        pass
    # Different contract — still allowed under per-contract cap.
    async with pacing.guard("historical", "STK:MSFT"):
        pass


async def test_concurrent_cap_serializes():
    """concurrent=3 means at most 3 in-flight at any time."""
    tier = pacing.get_tier("historical")
    held: list[int] = []
    enter_count = 0

    async def worker(i: int):
        nonlocal enter_count
        async with pacing.guard("historical", f"STK:S{i}"):
            enter_count += 1
            held.append(enter_count)
            await asyncio.sleep(0.05)
            enter_count -= 1

    # Burst 8 concurrent — but cap is 3.
    await asyncio.gather(*[worker(i) for i in range(8)])
    assert max(held) <= tier.cfg.concurrent


async def test_same_contract_serializes_via_lock():
    """Two concurrent calls for the SAME contract MUST run sequentially."""
    in_flight = 0
    max_in_flight = 0

    async def worker():
        nonlocal in_flight, max_in_flight
        async with pacing.guard("market_data", "STK:SAME"):
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
            await asyncio.sleep(0.02)
            in_flight -= 1

    await asyncio.gather(*[worker() for _ in range(5)])
    assert max_in_flight == 1


def test_unknown_tier_raises():
    with pytest.raises(KeyError):
        pacing.get_tier("nonexistent")


def test_invalid_tier_config_raises():
    with pytest.raises(ValueError):
        pacing.Tier(pacing.TierConfig(concurrent=0))
    with pytest.raises(ValueError):
        pacing.Tier(pacing.TierConfig(per_window=10, per_window_hard=20))


def test_contract_key_stable():
    class C:
        secType = "OPT"
        symbol = "SPY"
        exchange = "SMART"
        currency = "USD"
        lastTradeDateOrContractMonth = "20260620"
        strike = 400.0
        right = "C"

    k = pacing.contract_key(C())
    assert k == "OPT:SPY:SMART:USD:20260620:400.0:C"


def test_contract_key_stock_minimal():
    class C:
        secType = "STK"
        symbol = "AAPL"
        exchange = "SMART"
        currency = "USD"
        lastTradeDateOrContractMonth = ""
        strike = 0.0
        right = ""

    assert pacing.contract_key(C()) == "STK:AAPL:SMART:USD"
