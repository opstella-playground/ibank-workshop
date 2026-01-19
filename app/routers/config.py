"""Configuration API router."""

import os
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/config", tags=["config"])

class ConfigResponse(BaseModel):
    """Configuration response model."""

    app_name: str
    app_version: str
    debug: bool
    log_level: str
    otlp_endpoint: str | None
    environment_variables: dict[str, str]


@router.get("/", response_model=ConfigResponse)
def read_config() -> Any:
    """Get current application configuration and environment variables.
    
    WARNING: be careful exposing this in production as it may show sensitive secrets.
    """
    settings = get_settings()

    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Configuration endpoint is only available in debug mode."
        )

    # Get relevant environment variables for debugging
    env_vars = {
        "OTEL_EXPORTER_OTLP_ENDPOINT": os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "Not Set"),
        "OTEL_EXPORTER_OTLP_PROTOCOL": os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "Not Set"),
        "OTEL_RESOURCE_ATTRIBUTES": os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "Not Set"),
    }

    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "otlp_endpoint": os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
        "environment_variables": env_vars,
    }
