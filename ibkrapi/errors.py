"""Standard error envelope. Used by every router.

Shape: {"code": "UPPER_SNAKE_CASE", "message": "...", "details": {...}}

`code` is a stable machine-readable identifier clients SWITCH on.
`message` is human-readable, safe for UI.
`details` is an optional structured payload.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Stable error codes.
CODE_BAD_REQUEST = "BAD_REQUEST"
CODE_UNAUTHORIZED = "UNAUTHORIZED"
CODE_NOT_FOUND = "NOT_FOUND"
CODE_VALIDATION_FAILED = "VALIDATION_FAILED"
CODE_RATE_LIMITED = "RATE_LIMITED"
CODE_UPSTREAM_FAILED = "UPSTREAM_FAILED"
CODE_GATEWAY_UNAVAILABLE = "GATEWAY_UNAVAILABLE"
CODE_TA_SIDECAR_UNAVAILABLE = "TA_SIDECAR_UNAVAILABLE"
CODE_INTERNAL = "INTERNAL_SERVER_ERROR"


_STATUS_TO_CODE = {
    400: CODE_BAD_REQUEST,
    401: CODE_UNAUTHORIZED,
    404: CODE_NOT_FOUND,
    422: CODE_VALIDATION_FAILED,
    429: CODE_RATE_LIMITED,
    502: CODE_UPSTREAM_FAILED,
    503: CODE_GATEWAY_UNAVAILABLE,
    500: CODE_INTERNAL,
}


def envelope(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        out["details"] = details
    return out


def error_response(
    status: int,
    message: str,
    *,
    code: str | None = None,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        envelope(code or _STATUS_TO_CODE.get(status, CODE_INTERNAL), message, details),
        status_code=status,
    )


class APIError(HTTPException):
    """HTTPException carrying a stable error code + optional details."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code or _STATUS_TO_CODE.get(status_code, CODE_INTERNAL)
        self.message = message
        self.details = details

    def to_envelope(self) -> dict[str, Any]:
        return envelope(self.code, self.message, self.details)
