"""Tests for ibkrapi.serialize — dataclass → dict converters + NaN scrub.

The NaN scrub is a regression test for the Phase 1 bug-fix: `ib_async`
signals "no quote yet" with NaN / ±Inf floats; FastAPI's default JSON
encoder raises `ValueError: Out of range float values are not JSON
compliant`. The serializer replaces non-finite floats with None.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from ibkrapi.serialize import (
    _coerce,
    _scrub,
    bar_dict,
    contract_dict,
    position_dict,
    tick_dict,
    ticker_dict,
)


class TestScrub:
    def test_finite_float_passes(self):
        assert _scrub(1.5) == 1.5
        assert _scrub(0.0) == 0.0
        assert _scrub(-3.14) == -3.14

    def test_nan_to_none(self):
        assert _scrub(float("nan")) is None

    def test_inf_to_none(self):
        assert _scrub(float("inf")) is None
        assert _scrub(float("-inf")) is None

    def test_int_passes(self):
        assert _scrub(42) == 42

    def test_string_passes(self):
        assert _scrub("hello") == "hello"

    def test_none_passes(self):
        assert _scrub(None) is None


class TestCoerce:
    def test_datetime_to_iso(self):
        dt = datetime(2026, 6, 20, 12, 30, 45, tzinfo=UTC)
        assert _coerce(dt) == "2026-06-20T12:30:45+00:00"

    def test_nan_float_to_none(self):
        assert _coerce(math.nan) is None
        assert _coerce(math.inf) is None

    def test_dataclass_to_dict(self):
        @dataclass
        class Foo:
            a: int
            b: float

        assert _coerce(Foo(1, 2.5)) == {"a": 1, "b": 2.5}

    def test_nested_dict(self):
        assert _coerce({"x": [1, 2.5, math.nan]}) == {"x": [1, 2.5, None]}

    def test_list_of_dataclasses(self):
        @dataclass
        class P:
            n: int

        assert _coerce([P(1), P(2)]) == [{"n": 1}, {"n": 2}]


def _fake_contract(**overrides):
    base = {
        "conId": 12345,
        "symbol": "AAPL",
        "secType": "STK",
        "exchange": "SMART",
        "primaryExchange": "NASDAQ",
        "currency": "USD",
        "lastTradeDateOrContractMonth": "",
        "strike": 0.0,
        "right": "",
        "multiplier": "",
        "tradingClass": "NMS",
        "localSymbol": "AAPL",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class TestContractDict:
    def test_stock(self):
        c = _fake_contract()
        d = contract_dict(c)
        assert d["conid"] == 12345
        assert d["symbol"] == "AAPL"
        assert d["secType"] == "STK"

    def test_option_fields(self):
        c = _fake_contract(
            secType="OPT",
            lastTradeDateOrContractMonth="20260619",
            strike=600.0,
            right="C",
            multiplier="100",
        )
        d = contract_dict(c)
        assert d["strike"] == 600.0
        assert d["right"] == "C"
        assert d["multiplier"] == "100"

    def test_missing_optional_attrs_default(self):
        c = SimpleNamespace(
            conId=1,
            symbol="X",
            secType="STK",
            exchange="SMART",
            currency="USD",
        )  # no strike/right/etc.
        d = contract_dict(c)
        assert d["strike"] == 0.0
        assert d["right"] == ""


class TestTickerDict:
    def test_nan_fields_scrubbed(self):
        ticker = SimpleNamespace(
            contract=_fake_contract(),
            time=None,
            bid=float("nan"),
            bidSize=float("nan"),
            ask=float("nan"),
            askSize=float("nan"),
            last=742.5,
            lastSize=10,
            close=740.0,
            open=float("nan"),
            high=745.0,
            low=738.0,
            volume=1_000_000,
            vwap=float("nan"),
            halted=False,
        )
        d = ticker_dict(ticker)
        assert d["bid"] is None
        assert d["bidSize"] is None
        assert d["ask"] is None
        assert d["open"] is None
        assert d["vwap"] is None
        # Finite values pass through
        assert d["last"] == 742.5
        assert d["close"] == 740.0
        assert d["volume"] == 1_000_000

    def test_time_iso_formatted(self):
        ticker = SimpleNamespace(
            contract=_fake_contract(),
            time=datetime(2026, 6, 20, 14, 0, tzinfo=UTC),
            bid=None,
            bidSize=None,
            ask=None,
            askSize=None,
            last=None,
            lastSize=None,
            close=None,
            open=None,
            high=None,
            low=None,
            volume=None,
            vwap=None,
            halted=None,
        )
        d = ticker_dict(ticker)
        assert d["time"] == "2026-06-20T14:00:00+00:00"

    def test_model_greeks_coerced_when_present(self):
        @dataclass
        class Greeks:
            delta: float
            gamma: float
            theta: float
            vega: float
            impliedVol: float

        ticker = SimpleNamespace(
            contract=_fake_contract(secType="OPT"),
            time=None,
            bid=1.5,
            bidSize=10,
            ask=1.6,
            askSize=10,
            last=1.55,
            lastSize=5,
            close=1.5,
            open=1.5,
            high=1.6,
            low=1.4,
            volume=100,
            vwap=1.5,
            halted=False,
            modelGreeks=Greeks(0.5, 0.01, -0.02, 0.3, 0.25),
        )
        d = ticker_dict(ticker)
        assert d["modelGreeks"] == {
            "delta": 0.5,
            "gamma": 0.01,
            "theta": -0.02,
            "vega": 0.3,
            "impliedVol": 0.25,
        }


class TestBarDict:
    def test_basic(self):
        bar = SimpleNamespace(
            date=datetime(2026, 6, 20, 9, 30, tzinfo=UTC),
            open=100.0,
            high=101.5,
            low=99.5,
            close=101.0,
            volume=10_000,
            average=100.5,
            barCount=42,
        )
        d = bar_dict(bar)
        assert d["time"] == "2026-06-20T09:30:00+00:00"
        assert d["open"] == 100.0
        assert d["volume"] == 10_000
        assert d["average"] == 100.5

    def test_string_date_fallback(self):
        # ib_async sometimes returns date as a string for unusual cases
        bar = SimpleNamespace(
            date="2026-06-20",
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=1,
        )
        d = bar_dict(bar)
        assert d["time"] == "2026-06-20"


class TestTickDict:
    def test_with_price(self):
        tick = SimpleNamespace(
            time=datetime(2026, 6, 20, 14, 0, tzinfo=UTC),
            price=100.5,
            size=10,
            priceBid=None,
            priceAsk=None,
            sizeBid=None,
            sizeAsk=None,
        )
        d = tick_dict(tick)
        assert d["time"] == "2026-06-20T14:00:00+00:00"
        assert d["price"] == 100.5
        assert d["size"] == 10


class TestPositionDict:
    def test_basic(self):
        pos = SimpleNamespace(
            account="DU1234567",
            contract=_fake_contract(),
            position=100.0,
            avgCost=149.50,
        )
        d = position_dict(pos)
        assert d["account"] == "DU1234567"
        assert d["position"] == 100.0
        assert d["avgCost"] == 149.50
        assert d["contract"]["symbol"] == "AAPL"


class TestJSONSafety:
    """End-to-end: a scrubbed ticker dict can be JSON-encoded."""

    def test_ticker_dict_json_encodable(self):
        import json

        ticker = SimpleNamespace(
            contract=_fake_contract(),
            time=None,
            bid=float("nan"),
            bidSize=float("inf"),
            ask=None,
            askSize=None,
            last=100.0,
            lastSize=10,
            close=99.5,
            open=99.5,
            high=100.5,
            low=99.0,
            volume=1000,
            vwap=99.75,
            halted=False,
        )
        d = ticker_dict(ticker)
        # Must NOT raise
        encoded = json.dumps(d)
        assert '"bid": null' in encoded
        assert '"bidSize": null' in encoded
        assert '"last": 100.0' in encoded


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_scrub_non_finite(bad):
    """Parametrize the 3 IEEE non-finite floats to be sure."""
    assert _scrub(bad) is None
