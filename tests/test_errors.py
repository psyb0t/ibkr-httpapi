"""Tests for the error envelope."""

from __future__ import annotations

import json

from ibkrapi.errors import (
    CODE_BAD_REQUEST,
    CODE_NOT_FOUND,
    CODE_UNAUTHORIZED,
    APIError,
    envelope,
    error_response,
)


class TestEnvelope:
    def test_minimal(self):
        e = envelope("BAD_REQUEST", "bad input")
        assert e == {"code": "BAD_REQUEST", "message": "bad input"}
        assert "details" not in e

    def test_with_details(self):
        e = envelope("BAD_REQUEST", "bad", details={"field": "foo"})
        assert e["details"] == {"field": "foo"}


class TestErrorResponse:
    def test_status_to_code_mapping(self):
        r = error_response(404, "missing")
        body = json.loads(r.body)
        assert r.status_code == 404
        assert body["code"] == CODE_NOT_FOUND
        assert body["message"] == "missing"

    def test_explicit_code_wins(self):
        r = error_response(400, "bad", code="CUSTOM_CODE")
        body = json.loads(r.body)
        assert body["code"] == "CUSTOM_CODE"

    def test_401_maps_to_unauthorized(self):
        r = error_response(401, "no token")
        body = json.loads(r.body)
        assert body["code"] == CODE_UNAUTHORIZED


class TestAPIError:
    def test_basic(self):
        exc = APIError(400, "bad input")
        assert exc.status_code == 400
        assert exc.code == CODE_BAD_REQUEST
        assert exc.message == "bad input"
        assert exc.details is None

    def test_to_envelope(self):
        exc = APIError(404, "missing", details={"id": 1})
        env = exc.to_envelope()
        assert env == {"code": CODE_NOT_FOUND, "message": "missing", "details": {"id": 1}}
