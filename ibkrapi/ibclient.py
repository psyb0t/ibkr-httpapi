"""ib_async lifecycle: single shared IB instance, single-flight connect,
reconnect on disconnect (the IBKR Gateway gets restarted nightly).

Every router pulls the connected IB via `get_ib()`. The first caller waits
for the connect; subsequent callers reuse the connection. If the socket
drops mid-flight, the next `get_ib()` call reconnects with exponential
backoff.
"""

from __future__ import annotations

import asyncio
import logging

from ib_async import IB, util

from ibkrapi.config import (
    ACCOUNT,
    CLIENT_ID,
    CONNECT_TIMEOUT_SECONDS,
    GATEWAY_HOST,
    GATEWAY_PORT,
    MARKET_DATA_TYPE,
    RECONNECT_BACKOFF_SECONDS,
    RECONNECT_MAX_BACKOFF_SECONDS,
)
from ibkrapi.logger import log

_ib: IB | None = None
_lock = asyncio.Lock()


def _new_ib() -> IB:
    util.logToConsole(level=logging.WARNING)
    ib = IB()
    return ib


async def _connect_with_retry(ib: IB) -> None:
    backoff = RECONNECT_BACKOFF_SECONDS
    attempt = 0
    while True:
        attempt += 1
        try:
            log.info(
                "ib_async_connect_attempt",
                attempt=attempt,
                host=GATEWAY_HOST,
                port=GATEWAY_PORT,
                clientId=CLIENT_ID,
                account=ACCOUNT or "<default>",
            )
            await ib.connectAsync(
                GATEWAY_HOST,
                GATEWAY_PORT,
                clientId=CLIENT_ID,
                timeout=CONNECT_TIMEOUT_SECONDS,
                account=ACCOUNT or "",
                readonly=False,
            )
        except Exception as exc:  # log on the spot, never silent
            log.warning(
                "ib_async_connect_failed",
                attempt=attempt,
                err=str(exc),
                retry_in_seconds=round(backoff, 1),
            )
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, RECONNECT_MAX_BACKOFF_SECONDS)
            continue
        log.info(
            "ib_async_connected",
            host=GATEWAY_HOST,
            port=GATEWAY_PORT,
            clientId=CLIENT_ID,
            serverVersion=ib.client.serverVersion(),
        )
        if MARKET_DATA_TYPE != 1:
            ib.reqMarketDataType(MARKET_DATA_TYPE)
            log.info("market_data_type_set", market_data_type=MARKET_DATA_TYPE)
        return


async def get_ib() -> IB:
    """Return a connected IB instance. Reconnects on demand."""
    global _ib
    if _ib is not None and _ib.isConnected():
        return _ib
    async with _lock:
        if _ib is not None and _ib.isConnected():
            return _ib
        if _ib is None:
            _ib = _new_ib()
        else:
            # intentional: best-effort disconnect before reconnect; the
            # socket may already be half-dead and ib_async raises on a
            # second close. Logged at warning so it's not silent.
            try:
                _ib.disconnect()
            except Exception as exc:  # log on the spot, never silent
                log.warning("disconnect_before_reconnect_failed", err=str(exc))
        await _connect_with_retry(_ib)
        return _ib


async def shutdown() -> None:
    global _ib
    if _ib is None:
        return
    log.info("ib_async disconnecting")
    try:
        _ib.disconnect()
    except Exception as exc:  # log on the spot, never silent
        log.warning("ib_async disconnect error", err=str(exc))
    _ib = None
