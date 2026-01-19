"""FastAPI Todo Starter Application.

This application demonstrates logging best practices with OpenTelemetry OTLP support.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.database import create_db_and_tables
from app.logging_config import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.routers import config_router, health_router, todos_router

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor

    OTEL_INSTRUMENTATION_AVAILABLE = True
except ImportError:
    OTEL_INSTRUMENTATION_AVAILABLE = False

settings = get_settings()

# Initialize logging before anything else
logger = setup_logging()

# Initialize Logging Instrumentation (captures standard logs)
if OTEL_INSTRUMENTATION_AVAILABLE:
    # LoggingInstrumentor().instrument(set_logging_packages=True)
    pass


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # === DEMO: Different log levels for startup ===

    # INFO: Application lifecycle events
    logger.info(
        "🚀  Application starting up",
        extra={
            "action": "startup",
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "debug_mode": settings.debug,
        },
    )

    # DEBUG: Detailed technical information (only shown when DEBUG=true)
    logger.debug(
        "⚙️ Configuration loaded",
        extra={
            "action": "config_load",
            "database_url": settings.database_url,
            "api_prefix": settings.api_prefix,
        },
    )

    # Startup: Create database tables
    try:
        create_db_and_tables()
        logger.info(
            "✅ Database tables created successfully",
            extra={"action": "db_init", "status": "success"},
        )
    except Exception as e:
        # ERROR: Something went wrong but app might still work
        logger.error(
            f"❌ Failed to create database tables: {e}",
            extra={"action": "db_init", "status": "failed"},
            exc_info=True,
        )
        raise

    # INFO: Startup complete
    logger.info(
        "🔥 Application ready to receive requests",
        extra={"action": "startup_complete"},
    )

    yield

    # === DEMO: Shutdown logging ===
    logger.info(
        "💀 Application shutting down",
        extra={"action": "shutdown"},
    )
    # Shutdown: Cleanup if needed
    logger.debug(
        "🧹 Cleanup completed",
        extra={"action": "shutdown_complete"},
    )


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A FastAPI starter kit with Todo CRUD API and SQLite database",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

if OTEL_INSTRUMENTATION_AVAILABLE:
    FastAPIInstrumentor.instrument_app(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware (added after CORS so it runs first)
app.add_middleware(RequestLoggingMiddleware)


@app.get("/", tags=["root"], include_in_schema=False)
def root() -> RedirectResponse:
    """Root endpoint redirecting to API docs."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(todos_router, prefix=settings.api_prefix)
app.include_router(config_router, prefix=settings.api_prefix)
