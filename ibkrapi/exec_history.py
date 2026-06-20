"""Append-only ledger for executions + completed orders.

Every call to /history/executions or /history/completed_orders writes
the fetched records into a per-day JSONL file. Records are deduplicated
on (execId) for fills and (permId, orderId) for completed orders.

File layout:
  data/history/exec/executions/YYYY-MM-DD.jsonl
  data/history/exec/completed_orders/YYYY-MM-DD.jsonl

JSONL chosen over CSV: fills + orders are deeply nested (commission
report, multi-leg, etc.) — JSONL preserves structure with zero schema
fuss and is line-streamable.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from ibkrapi.logger import log

_SAFE = re.compile(r"[^A-Za-z0-9._\-]")


def _safe(s: str) -> str:
    return _SAFE.sub("_", s or "")


@dataclass
class ExecHistoryConfig:
    enabled: bool = True
    path: str = "/app/data/history/exec"


_CFG = ExecHistoryConfig()
_LOCKS: dict[str, asyncio.Lock] = {}


def configure(cfg: ExecHistoryConfig) -> None:
    global _CFG
    _CFG = cfg
    if cfg.enabled:
        os.makedirs(os.path.join(cfg.path, "executions"), exist_ok=True)
        os.makedirs(os.path.join(cfg.path, "completed_orders"), exist_ok=True)
        log.info("exec_history_configured", path=cfg.path)


def _lock(path: str) -> asyncio.Lock:
    lk = _LOCKS.get(path)
    if lk is None:
        lk = asyncio.Lock()
        _LOCKS[path] = lk
    return lk


def _today() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _file_for(kind: str, day: str | None = None) -> str:
    return os.path.join(_CFG.path, _safe(kind), f"{_safe(day or _today())}.jsonl")


def _read_jsonl(path: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    out: list[dict] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _exec_id(fill: dict) -> str | None:
    exe = fill.get("execution") or {}
    return exe.get("execId") if isinstance(exe, dict) else None


def _completed_key(trade: dict) -> tuple:
    order = trade.get("order") or {}
    if not isinstance(order, dict):
        return ()
    return (order.get("permId"), order.get("orderId"))


async def record_executions(fills: list[dict[str, Any]]) -> int:
    """Append new fills (by execId) to today's executions JSONL.

    Returns the number of NEW fills appended (existing ones dedupe).
    """
    if not _CFG.enabled or not fills:
        return 0
    path = _file_for("executions")
    try:
        async with _lock(path):
            existing = _read_jsonl(path)
            seen = {_exec_id(f) for f in existing if _exec_id(f)}
            new = [f for f in fills if _exec_id(f) and _exec_id(f) not in seen]
            if not new:
                return 0
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a", encoding="utf-8") as fh:
                for f in new:
                    fh.write(json.dumps(f, default=str) + "\n")
            log.info("exec_history_append", kind="executions", new=len(new))
            return len(new)
    except Exception as exc:
        log.warning("exec_history_executions_failed", err=str(exc))
        return 0


async def record_completed_orders(trades: list[dict[str, Any]]) -> int:
    if not _CFG.enabled or not trades:
        return 0
    path = _file_for("completed_orders")
    try:
        async with _lock(path):
            existing = _read_jsonl(path)
            seen = {_completed_key(t) for t in existing}
            new = [t for t in trades if _completed_key(t) not in seen]
            if not new:
                return 0
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a", encoding="utf-8") as fh:
                for t in new:
                    fh.write(json.dumps(t, default=str) + "\n")
            log.info("exec_history_append", kind="completed_orders", new=len(new))
            return len(new)
    except Exception as exc:
        log.warning("exec_history_completed_failed", err=str(exc))
        return 0


def replay(kind: str, day: str | None = None) -> list[dict]:
    """Read back a day's records (for debugging / merging into responses)."""
    if not _CFG.enabled:
        return []
    return _read_jsonl(_file_for(kind, day=day))
