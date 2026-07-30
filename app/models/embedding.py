"""Embedding: a vector representation of a chunk, stored via pgvector."""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# Default dimensionality for the initial embedding provider. Revisit via a
# migration if a provider with a different dimensionality is introduced.
EMBEDDING_DIMENSIONS = 1536


class Embedding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A vector embedding of a single chunk's content."""

    __tablename__ = "embeddings"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    vector: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS), nullable=False)
