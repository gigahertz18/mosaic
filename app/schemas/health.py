"""Schemas for the health endpoint."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for ``GET /health``."""

    status: str
    app_name: str
    environment: str
