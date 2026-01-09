"""API routers."""

from app.routers.health import router as health_router
from app.routers.todos import router as todos_router

__all__ = ["health_router", "todos_router"]
