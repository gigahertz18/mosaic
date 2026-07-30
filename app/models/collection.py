"""Collection: a named, domain-agnostic grouping of documents."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Collection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A collection groups documents that share retrieval context.

    Mosaic never assumes anything about what a collection represents for
    the calling application (a project, a tenant, a topic, etc.).
    """

    __tablename__ = "collections"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
