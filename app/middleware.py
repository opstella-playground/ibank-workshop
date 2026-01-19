"""FastAPI middleware for logging and monitoring.

This module provides middleware for:
- Request/Response logging with timing
- Request ID generation and propagation
- Error logging with context
"""

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import get_logger

logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses.

    Best Practices Demonstrated:
    - INFO level for successful requests
    - WARNING level for client errors (4xx)
    - ERROR level for server errors (5xx)
    - DEBUG level for detailed request/response info
    - Structured logging with consistent fields
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request and log relevant information."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Extract request details
        path = request.url.path
        method = request.method
        client_host = request.client.host if request.client else "unknown"

        # Log request start (DEBUG level for high-volume endpoints)
        if path in ["/health", "/api/v1/health"]:
            logger.debug(
                f"Request started: {method} {path}",
                extra={
                    "request_id": request_id,
                    "path": path,
                    "method": method,
                    "client_ip": client_host,
                    "action": "request_start",
                },
            )
        else:
            logger.info(
                f"Request started: {method} {path}",
                extra={
                    "request_id": request_id,
                    "path": path,
                    "method": method,
                    "client_ip": client_host,
                    "action": "request_start",
                },
            )

        # Process request and measure duration
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as e:
            # Log unhandled exceptions at ERROR level
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Request failed with exception: {method} {path}",
                extra={
                    "request_id": request_id,
                    "path": path,
                    "method": method,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                    "action": "request_error",
                },
                exc_info=True,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code

        # Add request ID to response headers for tracing
        response.headers["X-Request-ID"] = request_id

        # Log based on status code (Best Practice: different levels for different outcomes)
        log_extra = {
            "request_id": request_id,
            "path": path,
            "method": method,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "action": "request_complete",
        }

        if status_code >= 500:
            # Server errors: ERROR level
            logger.error(
                f"Request completed with server error: {method} {path} -> {status_code}",
                extra=log_extra,
            )
        elif status_code >= 400:
            # Client errors: WARNING level
            logger.warning(
                f"Request completed with client error: {method} {path} -> {status_code}",
                extra=log_extra,
            )
        elif path in ["/health", "/api/v1/health"]:
            # Health checks: DEBUG level to reduce noise
            logger.debug(
                f"Request completed: {method} {path} -> {status_code} ({duration_ms:.2f}ms)",
                extra=log_extra,
            )
        else:
            # Successful requests: INFO level
            logger.info(
                f"Request completed: {method} {path} -> {status_code} ({duration_ms:.2f}ms)",
                extra=log_extra,
            )

        return response
