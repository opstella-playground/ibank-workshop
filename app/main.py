"""FastAPI Todo Starter Application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_db_and_tables
from app.routers import todos_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Cleanup if needed


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A FastAPI starter kit with Todo CRUD API and SQLite database",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    """Root endpoint returning API info."""
    return {
        "message": "Welcome to FastAPI Todo Starter",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(todos_router, prefix=settings.api_prefix)
