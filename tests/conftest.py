"""Shared pytest fixtures.

ib_async is heavy — tests mock it at the ibclient boundary so handlers
exercise pure logic without spinning up a real Gateway. Integration
tests against a live demo gateway live in tests/integration/ (skipped
unless IBKR_INTEGRATION=1).
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_ib(monkeypatch):
    """Replace ibkrapi.ibclient.get_ib with a MagicMock that returns
    an AsyncMock IB instance. Tests call setattr() on the returned mock
    to wire per-test behaviour for qualifyContractsAsync, reqTickersAsync,
    placeOrder, etc.
    """
    ib = MagicMock(name="IB")
    ib.isConnected = MagicMock(return_value=True)
    ib.qualifyContractsAsync = AsyncMock(return_value=[])
    ib.reqContractDetailsAsync = AsyncMock(return_value=[])
    ib.reqTickersAsync = AsyncMock(return_value=[])
    ib.reqHistoricalDataAsync = AsyncMock(return_value=[])
    ib.reqHistoricalTicksAsync = AsyncMock(return_value=[])
    ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[])
    ib.accountSummaryAsync = AsyncMock(return_value=[])
    ib.reqExecutionsAsync = AsyncMock(return_value=[])
    ib.reqCompletedOrdersAsync = AsyncMock(return_value=[])
    ib.placeOrder = MagicMock()
    ib.cancelOrder = MagicMock()
    ib.reqGlobalCancel = MagicMock()
    ib.exerciseOptions = MagicMock()
    ib.positions = MagicMock(return_value=[])
    ib.openTrades = MagicMock(return_value=[])
    ib.accountValues = MagicMock(return_value=[])
    ib.managedAccounts = MagicMock(return_value=["DU1234567"])
    ib.client = MagicMock()
    ib.client.serverVersion = MagicMock(return_value=178)
    ib.client.twsConnectionTime = MagicMock(return_value="20260619 00:00:00")

    async def _fake_get_ib():
        return ib

    monkeypatch.setattr("ibkrapi.ibclient.get_ib", _fake_get_ib)
    monkeypatch.setattr("ibkrapi.marketdata.get_ib", _fake_get_ib)
    return ib


@pytest.fixture
def integration_required():
    """Skip the test unless IBKR_INTEGRATION=1.

    Integration tests connect to a real (paper) IB Gateway via the
    address in IBKR_GATEWAY_HOST / IBKR_GATEWAY_PORT. Never point at a
    live account from CI.
    """
    if os.environ.get("IBKR_INTEGRATION") != "1":
        pytest.skip("Set IBKR_INTEGRATION=1 to run integration tests")
