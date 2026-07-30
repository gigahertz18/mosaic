"""Health check route.

Reports process liveness only in Milestone 1. Dependency checks (database,
object storage) can be added as the corresponding providers are introduced,
without changing this route's public shape.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return basic liveness information about the running application."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment.value,
    )
