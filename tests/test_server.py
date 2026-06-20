"""End-to-end-ish HTTP tests via FastAPI's TestClient.

ib_async is mocked via the `mock_ib` fixture in conftest.py — these
tests exercise routing + auth + error envelope without touching a real
gateway.
"""

from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


def _make_client_with_token(monkeypatch, token: str) -> TestClient:
    """Reload `ibkrapi.config` + `ibkrapi.server` so the API_TOKEN
    module-level constant reflects per-test monkeypatching of the env,
    then return a fresh TestClient.

    Extracted from inline boilerplate because forgetting the
    `reload(server)` step silently exercises stale auth middleware and
    a test would pass for the wrong reason.
    """
    monkeypatch.setenv("API_TOKEN", token)
    import ibkrapi.config

    importlib.reload(ibkrapi.config)
    import ibkrapi.server

    importlib.reload(ibkrapi.server)
    return TestClient(ibkrapi.server.app)


@pytest.fixture
def client(monkeypatch, mock_ib):
    """Default open-auth client (empty API_TOKEN)."""
    return _make_client_with_token(monkeypatch, "")


@pytest.fixture
def auth_client(monkeypatch, mock_ib):
    """Client wired to require Bearer `sekret` for every request."""
    return _make_client_with_token(monkeypatch, "sekret")


def test_ping_open(client, mock_ib):
    r = client.get("/v1/ping")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["connected"] is True


def test_accounts(client, mock_ib):
    r = client.get("/v1/accounts")
    assert r.status_code == 200
    assert r.json() == {"accounts": ["DU1234567"]}


def test_unknown_route_404(client):
    r = client.get("/v1/no-such-thing")
    assert r.status_code == 404


def test_error_envelope_shape(client, mock_ib):
    # qualifyContractsAsync returning [] → 404 with envelope shape
    mock_ib.qualifyContractsAsync.return_value = []
    r = client.get("/v1/stocks/NONEXISTENT/tick")
    assert r.status_code == 404
    body = r.json()
    assert body["code"] == "NOT_FOUND"
    assert "message" in body


def test_bad_bar_size_400_envelope(client, mock_ib):
    # Path: build a contract -> qualify returns one -> historical bars
    # branch hits _resolve_bar_size("999q") -> APIError(400, ..., details={accepted: [...]})
    from ib_async import Stock

    mock_ib.qualifyContractsAsync.return_value = [Stock("AAPL", "SMART", "USD")]
    r = client.get("/v1/stocks/AAPL/rates?duration=1+D&barSize=999q")
    assert r.status_code == 400
    body = r.json()
    assert body["code"] == "BAD_REQUEST"
    assert "accepted" in body["details"]


def test_auth_missing_token(auth_client):
    r = auth_client.get("/v1/ping")
    assert r.status_code == 401
    assert r.json()["code"] == "UNAUTHORIZED"


def test_auth_bad_token(auth_client):
    r = auth_client.get("/v1/ping", headers={"Authorization": "Bearer wrong"})
    assert r.status_code == 401


def test_auth_good_token(auth_client):
    r = auth_client.get("/v1/ping", headers={"Authorization": "Bearer sekret"})
    assert r.status_code == 200


def test_auth_non_bearer_rejected(auth_client):
    r = auth_client.get("/v1/ping", headers={"Authorization": "Token sekret"})
    assert r.status_code == 401


def test_validation_error_envelope(client, mock_ib):
    # /orders POST with missing required field
    r = client.post("/v1/orders", json={"symbol": "AAPL"})
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "VALIDATION_FAILED"
    assert "errors" in body["details"]
