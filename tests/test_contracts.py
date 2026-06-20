"""Pure-logic tests for the asset-class contract factories."""

from __future__ import annotations

import pytest
from ibkrapi import contracts


class TestStock:
    def test_defaults(self):
        s = contracts.stock("AAPL")
        assert s.symbol == "AAPL"
        assert s.secType == "STK"
        assert s.exchange == "SMART"
        assert s.currency == "USD"

    def test_explicit_overrides(self):
        s = contracts.stock("ASML", exchange="AEB", currency="EUR", primary_exchange="AEB")
        assert s.exchange == "AEB"
        assert s.currency == "EUR"
        assert s.primaryExchange == "AEB"


class TestOption:
    def test_basic(self):
        o = contracts.option("AAPL", expiry="20260619", strike=200, right="C")
        assert o.secType == "OPT"
        assert o.symbol == "AAPL"
        assert o.lastTradeDateOrContractMonth == "20260619"
        assert o.strike == 200.0
        assert o.right == "C"
        assert o.multiplier == "100"

    def test_long_right_form(self):
        assert contracts.option("X", expiry="202609", strike=50, right="CALL").right == "C"
        assert contracts.option("X", expiry="202609", strike=50, right="PUT").right == "P"

    def test_lowercase_right(self):
        assert contracts.option("X", expiry="202609", strike=50, right="c").right == "C"

    @pytest.mark.parametrize("bad_right", ["", "X", "BUY", "1"])
    def test_invalid_right_rejected(self, bad_right):
        with pytest.raises(ValueError, match="option right"):
            contracts.option("X", expiry="202609", strike=50, right=bad_right)

    def test_custom_multiplier(self):
        o = contracts.option("ESM", expiry="202609", strike=4500, right="C", multiplier="50")
        assert o.multiplier == "50"


class TestFuture:
    def test_requires_exchange(self):
        f = contracts.future("ES", expiry="202609", exchange="CME")
        assert f.exchange == "CME"
        assert f.symbol == "ES"
        assert f.lastTradeDateOrContractMonth == "202609"

    def test_include_expired(self):
        f = contracts.future("ES", expiry="202403", exchange="CME", include_expired=True)
        assert f.includeExpired is True


class TestCFD:
    def test_defaults(self):
        c = contracts.cfd("IBDE40")
        assert c.secType == "CFD"
        assert c.exchange == "SMART"


class TestForex:
    def test_defaults(self):
        f = contracts.forex("EURUSD")
        assert f.secType == "CASH"
        assert f.symbol == "EUR"
        assert f.currency == "USD"
        assert f.exchange == "IDEALPRO"


class TestCrypto:
    def test_defaults(self):
        c = contracts.crypto("BTC")
        assert c.secType == "CRYPTO"
        assert c.exchange == "PAXOS"
        assert c.currency == "USD"


class TestCombo:
    def test_two_leg_vertical(self):
        bag = contracts.combo(
            "AAPL",
            legs=[
                {"conid": 1, "ratio": 1, "action": "BUY"},
                {"conid": 2, "ratio": 1, "action": "SELL"},
            ],
        )
        assert bag.secType == "BAG"
        assert len(bag.comboLegs) == 2
        assert bag.comboLegs[0].action == "BUY"
        assert bag.comboLegs[1].action == "SELL"

    def test_default_leg_ratio_is_one(self):
        bag = contracts.combo("AAPL", legs=[{"conid": 1, "action": "BUY"}])
        assert bag.comboLegs[0].ratio == 1

    def test_action_uppercased(self):
        bag = contracts.combo("AAPL", legs=[{"conid": 1, "action": "buy"}])
        assert bag.comboLegs[0].action == "BUY"


class TestByConid:
    def test_bare_conid(self):
        c = contracts.by_conid(265598)
        assert c.conId == 265598
