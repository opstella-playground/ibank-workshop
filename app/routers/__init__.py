"""API routers."""

from app.routers.config import router as config_router
from app.routers.health import router as health_router
from app.routers.todos import router as todos_router

__all__ = ["health_router", "todos_router", "config_router"]
