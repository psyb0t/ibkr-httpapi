"""Entry point: uvicorn serving the FastAPI app."""

from __future__ import annotations

import sys

import uvicorn

from ibkrapi.config import (
    API_TOKEN,
    GATEWAY_HOST,
    GATEWAY_PORT,
    HOST,
    IDENTITY,
    MARKET_DATA_TYPE,
    PORT,
    WICKWORKS_URL,
)
from ibkrapi.logger import log

# uvicorn handles SIGINT/SIGTERM itself — graceful shutdown out of the box.
# No custom signal handler needed; the lifespan hook in server.py is where
# disconnect-from-gateway runs.


def main():
    # Startup config dump per `~/.claude/rules/06-logging.md` —
    # secrets redacted (API_TOKEN length only, not value).
    log.info(
        "starting",
        identity=IDENTITY,
        host=HOST,
        port=PORT,
        gateway_host=GATEWAY_HOST,
        gateway_port=GATEWAY_PORT,
        market_data_type=MARKET_DATA_TYPE,
        wickworks_configured=bool(WICKWORKS_URL),
        api_token_set=bool(API_TOKEN),
        api_token_length=len(API_TOKEN) if API_TOKEN else 0,
    )
    config = uvicorn.Config(
        "ibkrapi.server:app",
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=False,  # we log via middleware
        loop="asyncio",
    )
    server = uvicorn.Server(config)
    try:
        server.run()
    except KeyboardInterrupt:
        log.info("interrupted")
    except Exception:
        log.exception("server_crashed")
        sys.exit(1)
    finally:
        log.critical("api_process_exiting", identity=IDENTITY)
