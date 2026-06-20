"""Tests for ibkrapi.config duration parser."""

from __future__ import annotations

import pytest
from ibkrapi.config import parse_duration_to_seconds


class TestParseDuration:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            (None, 0.0),
            ("", 0.0),
            (0, 0.0),
            (5, 5.0),
            (5.5, 5.5),
            ("5", 5.0),
            ("5s", 5.0),
            ("30m", 1800.0),
            ("2h", 7200.0),
            ("1d", 86400.0),
            ("1h30m", 5400.0),
            ("2h45m30s", 2 * 3600 + 45 * 60 + 30),
            ("90m", 5400.0),
        ],
    )
    def test_known_forms(self, raw, expected):
        assert parse_duration_to_seconds(raw) == expected

    def test_uppercase_units(self):
        assert parse_duration_to_seconds("5M") == 300.0
        assert parse_duration_to_seconds("2H") == 7200.0

    @pytest.mark.parametrize("bad", ["5x", "abc", "5 banana", "1y"])
    def test_unknown_unit_rejected(self, bad):
        with pytest.raises(ValueError):
            parse_duration_to_seconds(bad)
