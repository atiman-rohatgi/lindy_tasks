"""Return every error as {"error": true, "message": "..."}, the shape the frontend displays."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def error_response(status_code: int, message: str, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": True, "message": message}, headers=headers)


def _validation_message(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "Invalid request"
    first = errors[0]
    # loc looks like ("body", "email"); skip "body" and list indexes.
    field = next((p for p in reversed(first.get("loc", ())) if isinstance(p, str) and p != "body"), None)
    message = first.get("msg", "Invalid value").removeprefix("Value error, ")
    return f"{field}: {message}" if field else message


def register_error_handlers(app: FastAPI) -> None:
    """Call this before adding CORSMiddleware, so CORS headers wrap error responses too."""

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException):
        return error_response(exc.status_code, str(exc.detail), getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        return error_response(422, _validation_message(exc))

    # Unexpected crashes are caught in a middleware rather than an
    # exception_handler(Exception): Starlette runs that handler outside every
    # middleware, so the 500 would lack CORS headers and the browser would
    # hide it from the frontend ("Failed to fetch").
    @app.middleware("http")
    async def catch_unhandled_errors(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            logger.exception("Unhandled error on %s %s", request.method, request.url.path)
            return error_response(500, "Something went wrong. Please try again.")
