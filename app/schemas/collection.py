"""Schema for the collection endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class CollectionCreate(BaseModel):
    """Request body for ``POST /collections``."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class CollectionUpdate(BaseModel):
    """Request body for ``PATCH /collections/{collection_id}``.
    All fields are optional to support partial updates.
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class CollectionRead(BaseResponse):

    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
