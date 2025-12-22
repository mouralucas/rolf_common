import datetime
import uuid
from typing import (
    Any,
    Dict,
    List,
)

from sqlalchemy import MetaData, Table, TIMESTAMP, String, text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from rolf_common.util.datetime import get_timestamp_aware


class SQLModel(DeclarativeBase):
    """Base class used for model definitions.

    Provides convenience methods that can be used to convert model
    to the corresponding schema.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column("id", primary_key=True, default=uuid.uuid4)
    active: Mapped[bool] = mapped_column("active", default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        "created_at", type_=TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
    edited_at: Mapped[datetime.datetime] = mapped_column(
        "edited_at", type_=TIMESTAMP(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime.datetime] = mapped_column(
        "deleted_at", type_=TIMESTAMP(timezone=True), nullable=True
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        "created_by", nullable=True, default=None
    )
    edited_by: Mapped[uuid.UUID] = mapped_column(
        "edited_by", nullable=True, default=None
    )
    deleted_by: Mapped[uuid.UUID] = mapped_column(
        "deleted_by", nullable=True, default=None
    )

    @classmethod
    def schema(cls) -> str:
        """Return name of database schema the model refers to."""

        _schema = cls.__mapper__.selectable.schema
        if _schema is None:
            raise ValueError("Cannot identify model schema")
        return _schema

    @classmethod
    def table_name(cls) -> str:
        """Return name of the table the model refers to."""

        return cls.__tablename__

    @classmethod
    def fields(cls) -> List[str]:
        """Return list of model field names."""

        return cls.__mapper__.selectable.c.keys()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to a dictionary."""

        _dict: Dict[str, Any] = dict()
        for key in self.__mapper__.c.keys():
            _dict[key] = getattr(self, key)
        return _dict

    @classmethod
    def gather_metadata(cls, engine=None) -> MetaData:
        """Gather metadata from all subclasses."""
        metadata = MetaData()
        if engine is not None and hasattr(engine, "sync_engine"):
            engine = engine.sync_engine

        for subclass in cls.__subclasses__():
            if engine is None:
                raise ValueError("Engine must be provided for autoload")
            Table(subclass.__tablename__, metadata, autoload_with=engine)
        return metadata

    @classmethod
    async def async_gather_metadata(cls, async_engine) -> MetaData:
        """Async-safe version of gather_metadata."""
        metadata = MetaData()

        async with async_engine.connect() as conn:

            def sync_fn(sync_conn):
                for subclass in cls.__subclasses__():
                    Table(subclass.__tablename__, metadata, autoload_with=sync_conn)
                return metadata

            return await conn.run_sync(sync_fn)
