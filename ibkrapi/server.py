"""FastAPI app: middleware + asset-class router registration."""

from __future__ import annotations

import hmac
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from ibkrapi import cache_bars, cache_meta, exec_history, historian, ibclient, pacing
from ibkrapi.api._generated.routers import (
    cfd,
    crypto,
    forex,
    futures,
    history,
    options,
    orders,
    stocks,
    system,
)
from ibkrapi.config import (
    API_TOKEN,
    EXEC_HISTORY_ENABLED,
    EXEC_HISTORY_PATH,
    HISTORIAN_ENABLED,
    HISTORIAN_PATH,
    HISTORY_CACHE_ENABLED,
    HISTORY_CACHE_PATH,
    HISTORY_CACHE_PERSIST_OPEN_BAR,
    HISTORY_CACHE_REFRESH_TAIL_BARS,
    META_CACHE_ENABLED,
    META_CACHE_PATH,
    META_CACHE_TTL_SEC,
    PACING_TIERS,
)
from ibkrapi.errors import (
    CODE_INTERNAL,
    CODE_UNAUTHORIZED,
    CODE_VALIDATION_FAILED,
    APIError,
    error_response,
)
from ibkrapi.logger import log

_AUTH_HEADER_PREFIX = "Bearer "


def _configure_pacing_and_caches() -> None:
    """Wire pacing + cache modules from config. Runs once at import time
    so the modules are ready before the first request lands."""
    pacing.configure({name: pacing.TierConfig(**cfg) for name, cfg in PACING_TIERS.items()})
    cache_bars.configure(
        cache_bars.CacheConfig(
            enabled=HISTORY_CACHE_ENABLED,
            path=HISTORY_CACHE_PATH,
            refresh_tail_bars=HISTORY_CACHE_REFRESH_TAIL_BARS,
            persist_open_bar=HISTORY_CACHE_PERSIST_OPEN_BAR,
        )
    )
    historian.configure(
        historian.HistorianConfig(
            enabled=HISTORIAN_ENABLED,
            path=HISTORIAN_PATH,
        )
    )
    cache_meta.configure(
        cache_meta.MetaCacheConfig(
            enabled=META_CACHE_ENABLED,
            path=META_CACHE_PATH,
            ttl_sec=META_CACHE_TTL_SEC or None,
        )
    )
    exec_history.configure(
        exec_history.ExecHistoryConfig(
            enabled=EXEC_HISTORY_ENABLED,
            path=EXEC_HISTORY_PATH,
        )
    )


_configure_pacing_and_caches()


@asynccontextmanager
async def _lifespan(app: FastAPI):
    log.info("startup", event="startup", action="connect_gateway")
    try:
        await ibclient.get_ib()
    except Exception as exc:
        log.warning(
            "startup connect failed (will retry on first request)",
            event="startup",
            err=str(exc),
        )
    try:
        yield
    finally:
        log.info("shutdown", event="shutdown", action="disconnect_gateway")
        await ibclient.shutdown()


app = FastAPI(
    title="ibkr-httpapi",
    version="0.3.0",
    description="HTTP wrapper over IBKR via ib_async. Asset-class routed.",
    lifespan=_lifespan,
)


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "-"


def _check_auth(header_value: str) -> bool:
    """Constant-time bearer compare. NEVER use `==` here.

    Length-leak alone is enough to bisect a token over a few thousand
    requests, hence `hmac.compare_digest`.
    """
    if not header_value.startswith(_AUTH_HEADER_PREFIX):
        return False
    presented = header_value[len(_AUTH_HEADER_PREFIX) :]
    return hmac.compare_digest(presented.encode("utf-8"), API_TOKEN.encode("utf-8"))


@app.middleware("http")
async def _log_and_auth(request: Request, call_next):
    req_id = os.urandom(4).hex()
    start = time.monotonic()
    path = request.url.path
    method = request.method
    log.info(
        "request_in",
        req_id=req_id,
        method=method,
        path=path,
        ip=_client_ip(request),
        ua=request.headers.get("user-agent", "-"),
    )

    if API_TOKEN:
        auth_header = request.headers.get("authorization", "")
        if not _check_auth(auth_header):
            elapsed_ms = (time.monotonic() - start) * 1000
            log.info(
                "request_out",
                req_id=req_id,
                method=method,
                path=path,
                status=401,
                dur_ms=round(elapsed_ms, 1),
            )
            return error_response(401, "Missing or invalid bearer token", code=CODE_UNAUTHORIZED)

    try:
        response = await call_next(request)
    except APIError:
        raise
    except Exception as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        log.exception(
            "request_crash",
            req_id=req_id,
            method=method,
            path=path,
            err=repr(exc),
            dur_ms=round(elapsed_ms, 1),
        )
        return error_response(500, f"Internal error: {exc.__class__.__name__}", code=CODE_INTERNAL)

    elapsed_ms = (time.monotonic() - start) * 1000
    log.info(
        "request_out",
        req_id=req_id,
        method=method,
        path=path,
        status=response.status_code,
        dur_ms=round(elapsed_ms, 1),
    )
    return response


@app.exception_handler(APIError)
async def _api_error(request: Request, exc: APIError):
    return error_response(
        exc.status_code,
        exc.message,
        code=exc.code,
        details=exc.details,
    )


@app.exception_handler(RequestValidationError)
async def _validation_error(request: Request, exc: RequestValidationError):
    return error_response(
        422,
        "Request validation failed",
        code=CODE_VALIDATION_FAILED,
        details={"errors": exc.errors()},
    )


# All API routers are spec-generated and mounted under `/v1` per the
# `servers.url` in `api/v1.yaml` (Option B versioning — paths in the spec
# are unversioned; the runtime prefix lives here). Per
# `~/.claude/rules/45-api-design.md`: health endpoints (`/ping`, etc.)
# CAN stay unversioned; we put `/ping` under `/v1` deliberately since it
# reports IBKR-gateway state (an API behavior, not pure infra liveness).
_API_V1_PREFIX = "/v1"
for router in (
    system,
    stocks,
    options,
    futures,
    cfd,
    forex,
    crypto,
    orders,
    history,
):
    app.include_router(router.router, prefix=_API_V1_PREFIX)
