"""Generic async repository providing standard CRUD for any ORM model."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import ColumnElement, Select, UnaryExpression, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


class BaseRepository[ModelType: Base]:
    """Generic repository - provides standard CRUD for any model.

    The session is injected once at construction time (per request / unit
    of work) rather than passed into every call. Inherit this and pass in
    your model class; only add methods that are specific to the child
    model (e.g. ``get_by_name``) - the CRUD verbs below cover everything
    a straightforward, persistence-only repository needs. Models are
    expected to carry an ``id`` column (per project convention, every
    model uses ``UUIDPrimaryKeyMixin``); ``created_at`` is used for
    default ordering when present but is not required.
    """

    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self.session = session
        self.model = model

    def _build_query(
        self,
        *criteria: ColumnElement[bool],
        order_by: UnaryExpression[Any] | ColumnElement[Any] | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Select[tuple[ModelType]]:
        statement = select(self.model)

        if criteria:
            statement = statement.where(*criteria)

        if order_by is not None:
            statement = statement.order_by(order_by)
        else:
            created_at = getattr(self.model, "created_at", None)
            if created_at is not None:
                statement = statement.order_by(created_at)

        if offset:
            statement = statement.offset(offset)

        if limit:
            statement = statement.limit(limit)

        return statement

    async def _first(
        self,
        *criteria: ColumnElement[bool],
        **kwargs: Any,
    ) -> ModelType | None:
        result = await self.session.execute(self._build_query(*criteria, **kwargs))
        return result.scalars().first()

    async def _all(
        self,
        *criteria: ColumnElement[bool],
        **kwargs: Any,
    ) -> Sequence[ModelType]:
        result = await self.session.execute(self._build_query(*criteria, **kwargs))
        return result.scalars().all()

    async def _count(self, *criteria: ColumnElement[bool]) -> int:
        statement = select(func.count()).select_from(self.model)

        if criteria:
            statement = statement.where(*criteria)

        result = await self.session.execute(statement)
        return int(result.scalar_one())

    @property
    def _id_column(self) -> Any:
        """The model's ``id`` column, typed as ``Any`` since it isn't part
        of the ``Base`` bound - every model has one by project convention
        (``UUIDPrimaryKeyMixin``), but that mixin isn't itself a subtype
        of ``Base``.
        """
        return cast(Any, self.model).id

    async def get_by_id(self, id: UUID) -> ModelType | None:
        return await self._first(self._id_column == id)

    async def get_many_by_ids(self, ids: Sequence[UUID]) -> Sequence[ModelType]:
        if not ids:
            return []
        return await self._all(self._id_column.in_(ids))

    async def get_all(self) -> Sequence[ModelType]:
        """Return every row for this model, unpaginated."""
        return await self._all()

    async def get_page(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Return a bounded page of rows, capped at 100 per page."""
        skip = max(0, skip)
        limit = min(max(0, limit), 100)
        return await self._all(offset=skip, limit=limit)

    async def create(self, obj: ModelType) -> ModelType:
        """Persist a new, already-constructed model instance."""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Persist changes on ``obj`` (attached or detached) and flush."""
        merged = await self.session.merge(obj)
        await self.session.flush()
        await self.session.refresh(merged)
        return merged

    async def delete(self, id: UUID) -> None:
        """Delete the row with the given id, if it exists."""
        obj = await self.get_by_id(id)
        if obj is None:
            return
        await self.session.delete(obj)
        await self.session.flush()
