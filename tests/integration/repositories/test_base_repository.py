"""Integration tests for BaseRepository's generic CRUD against a live schema.

CollectionRepository exercises the common path (create/get_by_id/get_all/
update/delete) end to end, but doesn't touch every generic method on
BaseRepository directly (``get_many_by_ids``, ``get_page``, ``_count``,
explicit ``order_by``). These tests instantiate BaseRepository directly,
parameterized on Collection, to cover the rest of the generic surface.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.repositories.base import BaseRepository


def _make_collection(**overrides: object) -> Collection:
    defaults: dict[str, object] = {
        "name": f"collection-{uuid.uuid4()}",
        "description": "a test collection",
    }
    defaults.update(overrides)
    return Collection(**defaults)


@pytest.fixture
def repository(db_session: AsyncSession) -> BaseRepository[Collection]:
    return BaseRepository(db_session, Collection)


async def test_get_many_by_ids_returns_only_matching_rows(repository: BaseRepository[Collection]) -> None:
    first = await repository.create(_make_collection())
    second = await repository.create(_make_collection())
    await repository.create(_make_collection())  # a third row that should be excluded

    found = await repository.get_many_by_ids([first.id, second.id])

    assert {c.id for c in found} == {first.id, second.id}


async def test_get_many_by_ids_returns_empty_for_empty_input(repository: BaseRepository[Collection]) -> None:
    found = await repository.get_many_by_ids([])

    assert found == []


async def test_get_many_by_ids_ignores_unknown_ids(repository: BaseRepository[Collection]) -> None:
    created = await repository.create(_make_collection())

    found = await repository.get_many_by_ids([created.id, uuid.uuid4()])

    assert [c.id for c in found] == [created.id]


async def test_get_page_defaults_to_first_hundred_rows(repository: BaseRepository[Collection]) -> None:
    created = await repository.create(_make_collection())

    page = await repository.get_page()

    assert created.id in {c.id for c in page}


async def test_get_page_respects_limit(repository: BaseRepository[Collection]) -> None:
    for _ in range(3):
        await repository.create(_make_collection())

    page = await repository.get_page(limit=2)

    assert len(page) == 2


async def test_get_page_clamps_limit_above_hundred(repository: BaseRepository[Collection]) -> None:
    created = await repository.create(_make_collection())

    # A limit above the 100-row cap should not raise and should still
    # return results - it's silently clamped down to 100.
    page = await repository.get_page(limit=1000)

    assert created.id in {c.id for c in page}


async def test_get_page_clamps_negative_skip_to_zero(repository: BaseRepository[Collection]) -> None:
    created = await repository.create(_make_collection())

    page = await repository.get_page(skip=-5)

    assert created.id in {c.id for c in page}


async def test_get_page_skip_moves_past_earlier_rows(repository: BaseRepository[Collection]) -> None:
    first = await repository.create(_make_collection())
    second = await repository.create(_make_collection())

    first_page = await repository.get_page(skip=0, limit=1)
    second_page = await repository.get_page(skip=1, limit=1)

    assert [c.id for c in first_page] == [first.id]
    assert [c.id for c in second_page] == [second.id]


async def test_build_query_honors_explicit_order_by(repository: BaseRepository[Collection]) -> None:
    await repository.create(_make_collection(name="b-collection"))
    await repository.create(_make_collection(name="a-collection"))

    ordered = await repository._all(order_by=Collection.name)

    names = [c.name for c in ordered]
    assert names == sorted(names)


async def test_count_reflects_row_count(repository: BaseRepository[Collection]) -> None:
    assert await repository._count() == 0

    await repository.create(_make_collection())
    await repository.create(_make_collection())

    assert await repository._count() == 2


async def test_count_applies_criteria(repository: BaseRepository[Collection]) -> None:
    target = await repository.create(_make_collection(name="findable"))
    await repository.create(_make_collection(name="not-findable"))

    matching = await repository._count(Collection.name == target.name)

    assert matching == 1
