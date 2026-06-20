"""Tests for marketdata helpers (bar-size + what-to-show resolution)."""

from __future__ import annotations

import pytest
from ibkrapi.errors import APIError
from ibkrapi.marketdata import _resolve_bar_size, _resolve_what_to_show


class TestResolveBarSize:
    def test_default(self):
        assert _resolve_bar_size(None) == "1 hour"
        assert _resolve_bar_size("") == "1 hour"

    @pytest.mark.parametrize(
        "short,full",
        [
            ("1m", "1 min"),
            ("5m", "5 mins"),
            ("1h", "1 hour"),
            ("4h", "4 hours"),
            ("1d", "1 day"),
            ("1w", "1 week"),
            ("1mo", "1 month"),
        ],
    )
    def test_short_aliases(self, short, full):
        assert _resolve_bar_size(short) == full

    def test_passthrough_full_form(self):
        assert _resolve_bar_size("1 hour") == "1 hour"
        assert _resolve_bar_size("5 mins") == "5 mins"

    def test_unknown_rejected(self):
        with pytest.raises(APIError) as exc:
            _resolve_bar_size("7m")
        assert exc.value.status_code == 400
        assert "accepted" in exc.value.details


class TestResolveWhatToShow:
    def test_default(self):
        assert _resolve_what_to_show(None) == "TRADES"

    def test_lowercase_alias(self):
        assert _resolve_what_to_show("midpoint") == "MIDPOINT"
        assert _resolve_what_to_show("bid_ask") == "BID_ASK"

    def test_passthrough_upper(self):
        assert _resolve_what_to_show("TRADES") == "TRADES"

    def test_unknown_rejected(self):
        with pytest.raises(APIError) as exc:
            _resolve_what_to_show("garbage")
        assert exc.value.status_code == 400
