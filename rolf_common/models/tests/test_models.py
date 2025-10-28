import pytest
from rolf_common.models.base import DummyModel, SQLModel

@pytest.mark.asyncio
async def test_table_name():
    assert DummyModel.table_name() == "dummy"


@pytest.mark.asyncio
async def test_fields():
    fields = DummyModel.fields()
    assert "id" in fields
    assert "name" in fields
    assert "created_at" in fields


@pytest.mark.asyncio
async def test_to_dict(session):
    obj = DummyModel(name="John Doe")
    session.add(obj)
    await session.commit()
    d = obj.to_dict()

    assert isinstance(d, dict)
    assert d["name"] == "John Doe"
    assert "created_at" in d


@pytest.mark.asyncio
async def test_gather_metadata(async_engine):
    metadata = await SQLModel.async_gather_metadata(async_engine)
    tables = [t.name for t in metadata.tables.values()]
    assert "dummy" in tables