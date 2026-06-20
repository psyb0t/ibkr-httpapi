"""Structured JSON logger.

Every record is one JSON line with fields:
  time, level, file, line, func, msg, identity, + any extras passed via
  logging.LogRecord.__dict__.

Targets: stdout (captured by docker logs) AND logs/full.log
(mkdir-locked across processes so multiple api instances on a shared
log dir don't interleave).

Secrets / PII filtering: callers MUST never pass API_TOKEN /
TWS_PASSWORD / full request bodies as fields. Per `.claude/rules/
logging.md`.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import sys
import time

from ibkrapi.config import FULL_LOG, IDENTITY, LOG_DIR

# Built-in LogRecord attributes we DON'T want to dump as "extras".
_RESERVED_RECORD_ATTRS = frozenset(
    {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
        "message",
    }
)


class _JSONFormatter(logging.Formatter):
    def __init__(self, identity: str):
        super().__init__()
        self._identity = identity

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created))
            + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "file": record.filename,
            "line": record.lineno,
            "func": record.funcName,
            "identity": self._identity,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key in _RESERVED_RECORD_ATTRS:
                continue
            if key.startswith("_"):
                continue
            try:
                json.dumps(value)
            except (TypeError, ValueError):
                value = repr(value)
            payload[key] = value
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


class _LockedFileHandler(logging.FileHandler):
    """FileHandler that uses mkdir/rmdir as a cross-process mutex."""

    def __init__(self, filename: str, **kwargs):
        self._lock_dir = filename + ".lock"
        super().__init__(filename, **kwargs)

    def _acquire(self) -> bool:
        for _ in range(200):
            try:
                os.mkdir(self._lock_dir)
                return True
            except OSError:
                time.sleep(0.01)
        return False

    def _release(self) -> None:
        # intentional: best-effort release; another process may have
        # taken the lock between our acquire and release if we exceeded
        # the spin budget. Re-acquire would loop forever, so we suppress
        # the OSError silently.
        with contextlib.suppress(OSError):
            os.rmdir(self._lock_dir)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record) + self.terminator
            self._acquire()
            try:
                if self.stream is not None:
                    self.stream.write(msg)
                    self.stream.flush()
            finally:
                self._release()
        except Exception:
            self.handleError(record)


class _StructuredAdapter(logging.LoggerAdapter):
    """Lets callers pass structured fields directly as kwargs:

        log.info("started", port=8889, mode="paper")

    stdlib `Logger.info(msg, **kwargs)` raises on unknown kwargs; this
    adapter splits them out into `extra=` automatically so the JSON
    formatter can pick them up.
    """

    _LOG_KW = frozenset({"exc_info", "stack_info", "stacklevel", "extra"})

    def process(self, msg, kwargs):
        extra = kwargs.pop("extra", None) or {}
        for key in list(kwargs):
            if key in self._LOG_KW:
                continue
            extra[key] = kwargs.pop(key)
        if extra:
            kwargs["extra"] = extra
        return msg, kwargs


_base = logging.getLogger("ibkrapi")
_base.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
_base.propagate = False

if not _base.handlers:
    formatter = _JSONFormatter(IDENTITY)

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(formatter)
    _base.addHandler(stdout)

    os.makedirs(LOG_DIR, exist_ok=True)
    fileh = _LockedFileHandler(FULL_LOG, encoding="utf-8")
    fileh.setFormatter(formatter)
    _base.addHandler(fileh)


log = _StructuredAdapter(_base, {})
