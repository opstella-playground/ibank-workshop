"""Logging configuration for FastAPI with OpenTelemetry OTLP support.

This module provides structured logging with best practices:
- JSON formatted logs for OTLP exporters
- Log correlation with OpenTelemetry traces
- Configurable log levels
- Request context enrichment
"""

import logging
import sys
from typing import Any

from app.config import get_settings

# Try to import OpenTelemetry for trace correlation
try:
    from opentelemetry import trace
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON-like logging.

    Produces logs in a format that's easy to parse and works well with
    log aggregation systems like Grafana Loki via OTLP.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with structured data."""
        # Add trace context if OpenTelemetry is available
        trace_id = ""
        span_id = ""

        if OTEL_AVAILABLE:
            span = trace.get_current_span()
            if span.is_recording():
                ctx = span.get_span_context()
                trace_id = format(ctx.trace_id, "032x")
                span_id = format(ctx.span_id, "016x")

        # Build the log message with structured context
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace context if available
        if trace_id:
            log_data["trace_id"] = trace_id
            log_data["span_id"] = span_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the record
        extra_keys = [
            "request_id",
            "user_id",
            "path",
            "method",
            "status_code",
            "duration_ms",
            "todo_id",
            "action",
        ]
        for key in extra_keys:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        # Format as structured log line
        extra_str = " ".join(
            f"{k}={v}" for k, v in log_data.items() if k not in ["message", "timestamp", "level", "logger"]
        )

        return f"{log_data['timestamp']} | {log_data['level']:8s} | {log_data['logger']} | {log_data['message']} | {extra_str}"


def setup_logging(log_level: str | None = None) -> logging.Logger:
    """Configure application logging with OTLP support.

    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured root logger for the application
    """
    settings = get_settings()

    # Determine log level (priority: parameter > settings > debug fallback)
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    elif settings.log_level:
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
    elif settings.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # Create the application logger
    logger = logging.getLogger("app")
    logger.setLevel(level)
    logger.handlers.clear()  # Clear any existing handlers

    # Console handler with structured formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(
        StructuredFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z")
    )
    logger.addHandler(console_handler)

    # Setup OpenTelemetry logging if available and configured
    if OTEL_AVAILABLE:
        try:
            # Create OTLP log exporter
            otlp_exporter = OTLPLogExporter()

            # Create logger provider with batch processor
            logger_provider = LoggerProvider()
            logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(otlp_exporter)
            )
            set_logger_provider(logger_provider)

            # Add OTLP handler to the logger
            otel_handler = LoggingHandler(
                level=level,
                logger_provider=logger_provider,
            )
            logger.addHandler(otel_handler)

            logger.info(
                "OpenTelemetry logging initialized",
                extra={"action": "otel_init", "status": "success"},
            )
        except Exception as e:
            logger.warning(
                f"Failed to initialize OTLP logging: {e}. Using console logging only.",
                extra={"action": "otel_init", "status": "failed", "error": str(e)},
            )

    # Configure uvicorn and third-party loggers
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "sqlalchemy"]:
        third_party_logger = logging.getLogger(logger_name)
        third_party_logger.handlers.clear()
        third_party_logger.addHandler(console_handler)
        third_party_logger.setLevel(logging.WARNING if not settings.debug else logging.INFO)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__ of the calling module)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"app.{name}")
    return logging.getLogger("app")


# Convenience functions for logging with extra context
class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context to all log messages."""

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Add extra context to log messages."""
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def get_request_logger(request_id: str, **extra: Any) -> LoggerAdapter:
    """Get a logger adapter with request context.

    Args:
        request_id: Unique request identifier
        **extra: Additional context to include in all logs

    Returns:
        Logger adapter with request context
    """
    logger = get_logger("request")
    context = {"request_id": request_id, **extra}
    return LoggerAdapter(logger, context)
