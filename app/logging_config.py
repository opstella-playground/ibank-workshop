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

# Suppress noisy gRPC and OpenTelemetry exporter warnings
# These are especially noisy when OTLP endpoint is unavailable (e.g., local dev)
for noisy_logger in [
    "opentelemetry.sdk._logs._internal.export",
    "opentelemetry.sdk._logs.export",
    "opentelemetry.exporter.otlp.proto.grpc.exporter",
    "grpc._channel",
]:
    logging.getLogger(noisy_logger).setLevel(logging.ERROR)

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


class ColoredConsoleFormatter(logging.Formatter):
    """Custom formatter for colorful, human-readable console output."""

    # ANSI color codes
    GREY = "\x1b[38;5;240m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[31m"
    BOLD_RED = "\x1b[31;1m"
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    RESET = "\x1b[0m"

    LEVEL_COLORS = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors and proper alignment."""
        # 1. Timestamp (Grey)
        timestamp = self.formatTime(record, "%H:%M:%S")
        ts_str = f"{self.GREY}{timestamp}{self.RESET}"

        # 2. Level (Colored)
        color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        level_str = f"{color}{record.levelname:<8}{self.RESET}"

        # 3. Logger Name (Blue)
        logger_name = f"{self.BLUE}{record.name:<15}{self.RESET}"

        # 4. Message (White/Default)
        message = record.getMessage()

        # 5. Extract extra fields for context
        extra_context = []
        
        # Add Trace ID if present and valid (subtle grey)
        if OTEL_AVAILABLE:
            span = trace.get_current_span()
            if span.is_recording():
                ctx = span.get_span_context()
                trace_id = format(ctx.trace_id, "032x")
                # specific short trace id for console
                extra_context.append(f"{self.GREY}trace_id={trace_id[:7]}...{self.RESET}")

        # Add specific relevant fields
        std_attrs = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        extra_keys = {k: v for k, v in record.__dict__.items() if k not in std_attrs and k != "message" and not k.startswith("_")}
        
        # Filter unwanted OTLP/internal keys if any
        ignored_keys = {"action", "otelSpanID", "otelTraceID", "otelServiceName"}
        
        for k, v in extra_keys.items():
            if k not in ignored_keys:
                extra_context.append(f"{self.CYAN}{k}={v}{self.RESET}")

        extra_str = " ".join(extra_context)
        if extra_str:
            return f"{ts_str} | {level_str} | {logger_name} | {message} | {extra_str}"
        return f"{ts_str} | {level_str} | {logger_name} | {message}"


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
    console_handler.setFormatter(ColoredConsoleFormatter())
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
                "✅ OpenTelemetry logging initialized",
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
