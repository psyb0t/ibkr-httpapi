"""Tests for ibkrapi.historian — live-snapshot piggyback historian."""

from __future__ import annotations

import csv
import os

import pytest
from ibkrapi import historian


@pytest.fixture
def hist_dir(tmp_path):
    historian.configure(historian.HistorianConfig(enabled=True, path=str(tmp_path)))
    yield str(tmp_path)
    historian.configure(historian.HistorianConfig(enabled=False))


def _read_csv(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


async def test_record_tick_stocks_writes_row(hist_dir):
    ticker = {
        "bid": 150.0,
        "ask": 150.1,
        "last": 150.05,
        "bidSize": 100,
        "askSize": 200,
        "volume": 12345,
    }
    await historian.record_tick("stocks", "AAPL", ticker)
    path = historian.snapshot_path("stocks", "AAPL")
    assert os.path.isfile(path)
    rows = _read_csv(path)
    assert len(rows) == 1
    assert rows[0]["bid"] == "150.0"
    assert rows[0]["last"] == "150.05"


async def test_record_tick_options_includes_greeks(hist_dir):
    ticker = {
        "bid": 2.45,
        "ask": 2.50,
        "last": 2.48,
        "modelGreeks": {
            "impliedVol": 0.182,
            "delta": 0.523,
            "gamma": 0.041,
            "theta": -0.087,
            "vega": 0.215,
            "undPrice": 400.25,
        },
    }
    await historian.record_tick("options", "SPY_240615C00400000", ticker, underlying="SPY")
    path = historian.snapshot_path("options", "SPY_240615C00400000", underlying="SPY")
    assert os.path.isfile(path)
    # Grouped under SPY/
    assert "/SPY/" in path
    rows = _read_csv(path)
    assert rows[0]["iv"] == "0.182"
    assert rows[0]["delta"] == "0.523"
    assert rows[0]["underlyingPrice"] == "400.25"


async def test_record_tick_appends_not_clobbers(hist_dir):
    ticker = {"bid": 1.0, "ask": 1.1, "last": 1.05}
    await historian.record_tick("forex", "EURUSD", ticker)
    await historian.record_tick("forex", "EURUSD", ticker)
    await historian.record_tick("forex", "EURUSD", ticker)
    rows = _read_csv(historian.snapshot_path("forex", "EURUSD"))
    assert len(rows) == 3


async def test_record_chain_writes_per_expiry_files(hist_dir):
    entries = [
        {
            "exchange": "SMART",
            "tradingClass": "SPY",
            "multiplier": "100",
            "expirations": ["20260620", "20260919"],
            "strikes": [395.0, 400.0, 405.0],
        }
    ]
    await historian.record_chain("SPY", entries)
    p1 = historian.chain_path("SPY", "20260620")
    p2 = historian.chain_path("SPY", "20260919")
    assert os.path.isfile(p1)
    assert os.path.isfile(p2)
    rows = _read_csv(p1)
    assert len(rows) == 3
    assert {float(r["strike"]) for r in rows} == {395.0, 400.0, 405.0}


async def test_historian_disabled_writes_nothing(tmp_path):
    historian.configure(historian.HistorianConfig(enabled=False, path=str(tmp_path)))
    await historian.record_tick("stocks", "AAPL", {"bid": 1.0})
    assert not any(tmp_path.iterdir())


async def test_record_tick_swallows_errors(hist_dir, monkeypatch):
    """Historian must never raise — caller's response should never fail."""

    def boom(*_a, **_kw):
        raise OSError("disk full")

    monkeypatch.setattr(historian, "_append_row", boom)
    # Must not raise.
    await historian.record_tick("stocks", "AAPL", {"bid": 1.0})


async def test_safe_filenames(hist_dir):
    await historian.record_tick("forex", "EUR/USD", {"bid": 1.0})
    p = historian.snapshot_path("forex", "EUR/USD")
    assert os.path.basename(p) == "EUR_USD.csv"
