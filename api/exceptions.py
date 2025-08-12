from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.core.landing_page.plausible import (
    PlausibleAPIError,
    PlausibleAuthError,
    PlausibleRateLimitError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(PlausibleAuthError)
    async def handle_auth_error(_: Request, exc: PlausibleAuthError):
        return JSONResponse(
            status_code=exc.status_code or 401,
            content={
                "error": "plausible_auth_error",
                "message": str(exc),
            },
        )

    @app.exception_handler(PlausibleRateLimitError)
    async def handle_rl_error(_: Request, exc: PlausibleRateLimitError):
        return JSONResponse(
            status_code=429,
            content={
                "error": "plausible_rate_limited",
                "message": str(exc),
            },
        )

    @app.exception_handler(PlausibleAPIError)
    async def handle_api_error(_: Request, exc: PlausibleAPIError):
        return JSONResponse(
            status_code=exc.status_code or 500,
            content={
                "error": "plausible_api_error",
                "message": str(exc),
                "details": exc.payload if hasattr(exc, "payload") else None,
            },
        )
