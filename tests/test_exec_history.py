"""Tests for ibkrapi.exec_history — append-only fills/orders ledger."""

from __future__ import annotations

import pytest
from ibkrapi import exec_history


@pytest.fixture
def exec_dir(tmp_path):
    exec_history.configure(exec_history.ExecHistoryConfig(enabled=True, path=str(tmp_path)))
    yield str(tmp_path)
    exec_history.configure(exec_history.ExecHistoryConfig(enabled=False))


async def test_record_executions_writes_jsonl(exec_dir):
    fills = [
        {"execution": {"execId": "e1"}, "contract": {"symbol": "AAPL"}},
        {"execution": {"execId": "e2"}, "contract": {"symbol": "MSFT"}},
    ]
    n = await exec_history.record_executions(fills)
    assert n == 2
    replayed = exec_history.replay("executions")
    assert len(replayed) == 2
    assert {r["execution"]["execId"] for r in replayed} == {"e1", "e2"}


async def test_record_executions_dedupes_existing(exec_dir):
    fills = [
        {"execution": {"execId": "x1"}, "contract": {"symbol": "AAPL"}},
    ]
    await exec_history.record_executions(fills)
    n = await exec_history.record_executions(fills)  # same execId
    assert n == 0
    assert len(exec_history.replay("executions")) == 1


async def test_record_executions_adds_only_new(exec_dir):
    old = [{"execution": {"execId": "a"}}]
    await exec_history.record_executions(old)
    mix = [
        {"execution": {"execId": "a"}},  # dedupe
        {"execution": {"execId": "b"}},  # new
        {"execution": {"execId": "c"}},  # new
    ]
    n = await exec_history.record_executions(mix)
    assert n == 2


async def test_record_completed_orders_dedupes(exec_dir):
    trades = [
        {"order": {"permId": 100, "orderId": 1}, "contract": {}},
        {"order": {"permId": 101, "orderId": 2}, "contract": {}},
    ]
    n = await exec_history.record_completed_orders(trades)
    assert n == 2
    # repeat → 0 new
    assert await exec_history.record_completed_orders(trades) == 0


async def test_disabled_no_writes(tmp_path):
    exec_history.configure(exec_history.ExecHistoryConfig(enabled=False, path=str(tmp_path)))
    n = await exec_history.record_executions([{"execution": {"execId": "z"}}])
    assert n == 0
    assert exec_history.replay("executions") == []


async def test_empty_fills_no_file_created(exec_dir, tmp_path):
    n = await exec_history.record_executions([])
    assert n == 0
    # No file should exist.
    assert exec_history.replay("executions") == []


async def test_missing_exec_id_skipped(exec_dir):
    fills = [
        {"execution": {}},  # no execId — skipped
        {"execution": {"execId": "valid"}},
    ]
    n = await exec_history.record_executions(fills)
    assert n == 1
