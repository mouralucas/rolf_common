from datetime import datetime
from pyexpat import model
from typing import Any, List, Sequence, Type

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select, RowMapping
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Executable

from rolf_common.models.base import SQLModel
from sqlalchemy.dialects.postgresql import insert as pg_insert


class BaseDataManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    """Base data manager class responsible for operations over database."""

    async def add_one(self, sql_model: SQLModel) -> SQLModel:
        """
        Created by: Lucas Penha de Moura - 18/06/2024

            Method to batch insert a list of models.

        :param sql_model: The model that will be inserted
        :return: The refreshed object of the inserted model
        """
        self.session.add(sql_model)
        await self.session.flush()
        await self.session.refresh(sql_model)

        return sql_model

    async def add_all(self, sql_models: list[SQLModel], refresh_response: bool = True) -> list[SQLModel]:
        """
        Created by: Lucas Penha de Moura - 18/06/2024

            Method to batch insert a list of models.

        :param sql_models: The list of models that will be inserted
        :param refresh_response: Whether to refresh the objects after adding new models, default True
        :return: the list of models that were inserted
        """
        self.session.add_all(sql_models)
        await self.session.flush()

        if refresh_response:
            [await self.session.refresh(i) for i in sql_models]

        return sql_models

    async def add_or_ignore_all(self, sql_model: Type[SQLModel], list_fields: list[dict[str, Any]]) -> list[SQLModel]:
        """
        Created by: Lucas Penha de Moura - 31/08/2024

            Method to add batch to a sql model ignoring if an entry with the same id already exists.
            This should be used with caution, it uses a dialect specific implementation and may be slow for some cases (not tested)

            This was created for populate in-memory test databases and development database, and should not be used in actual code.
                It uses commit directly, and this disrupts the "transaction mode" used in all endpoints

        :param sql_model: The model that data will be added to
        :param list_fields: A list o dict. The dict must contain all fields that will be added to the model.
        :return: The list o added models
        """
        for idx, i in enumerate(list_fields):
            new_row = pg_insert(sql_model).values(i).on_conflict_do_nothing(index_elements=['id'])
            await self.session.execute(new_row)

        await self.session.commit()
        added_rows = await self.get_all(select(sql_model))

        return added_rows

    async def update_one(self, sql_statement: Executable, sql_model: SQLModel) -> SQLModel:
        """
        Created by: Lucas Penha de Moura - 28/04/2024
            Update a register

        :param sql_statement: An update Executable SQLAlchemy statement
        :param sql_model: The model object with the changes to be updated
        :return: The updated and refreshed model object
        """
        if not sql_statement.is_update:
            raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED)

        try:
            sql_model.edited_at = datetime.utcnow()
            await self.session.execute(sql_statement)
            await self.session.flush()
            await self.session.refresh(sql_model)
        except Exception as e:
            raise e

        return sql_model

    async def get_first(self, sql_statement: Executable,
                        raise_exception: bool = False) -> BaseModel | None:
        """
        Created by: Lucas Penha de Moura - 19/02/2024
            Similar to get_only_one, but if none is found can return None or raise an exception, if more than one is found return first element

        :param sql_statement: A select Executable SQLAlchemy statement
        :param raise_exception: Whether raise exception if some error occurs
        :return: The first model object fetched
        """
        result = await self.session.execute(sql_statement)
        result = result.scalar()

        if raise_exception and result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No data found')

        return result

    async def get_only_one(self, select_statement: Executable) -> SQLModel | None:
        """
        Created by: Lucas Penha de Moura - 09/02/2024
            Get one register, and only one.

        :param select_statement: A select Executable SQLAlchemy statement, usually filtering by 'id'
        :return: The model object if only one is found, return None otherwise
        """
        try:
            result = await self.session.execute(select_statement)
            result = result.scalar_one()
        except Exception as e:
            result = None

        # TODO: maybe handle exceptions to return default values

        return result

    async def get_by_id(self, sql_model: Type[SQLModel], object_id: Any) -> SQLModel | None:
        """
        Created by: Lucas Penha de Moura - 09/02/2024
            Get element by ID.
            Generic method to get a register from any model filtering by ID
        :param sql_model: The model to fetch from
        :param object_id: The ID to be fetched from the model
        :return: The objected fetched, if any. None otherwise
        """
        stmt = select(sql_model).where(sql_model.id == object_id)

        obj: SQLModel = await self.get_only_one(stmt)

        return obj

    async def get_all(self, select_statement: Executable,
                      unique_result: bool = False,
                      raise_exception: bool = False) -> list[RowMapping] | None:
        """
        Created by: Lucas Penha de Moura - 09/02/2024
           Get one register, and one only, if none or more than one is found raise an exception

        :param select_statement: A select Executable SQLAlchemy statement
        :param unique_result: If true, apply unique to the query, used when query contains joins ***(investigate reason)***
        :param raise_exception: If true, raise an exception if no data is found, if false, return None

        :return: The list of objected fetched, if any. If none can raise exception if param is set
        """
        result = await self.session.execute(select_statement)
        if unique_result:
            result = result.unique()

        result = result.mappings().all()

        if result:
            return list(result)

        if raise_exception:
            # TODO: adjust detail to show model name
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No data found in model')

        return None

    def get_from_tvf(self, sql_model: Type[SQLModel], *args: Any) -> List[Any]:
        """Query from table valued function.

        This is a wrapper function that can be used to retrieve data from
        table valued functions.

        Examples:
            from app.models.base import SQLModel

            class MyModel(SQLModel):
                __tablename__ = "function"
                __table_args__ = {"schema": "schema"}

                x: Mapped[int] = mapped_column("x", primary_key=True)
                y: Mapped[str] = mapped_column("y")
                z: Mapped[float] = mapped_column("z")

            # equivalent to "SELECT x, y, z FROM schema.function(1, 'AAA')"
            BaseDataManager(session).get_from_tvf(MyModel, 1, "AAA")
        """

        return self.get_all(self.select_from_tvf(sql_model, *args))

    @staticmethod
    def select_from_tvf(model: Type[SQLModel], *args: Any) -> Executable:
        fn = getattr(getattr(func, model.schema()), model.table_name())
        stmt = select(fn(*args).table_valued(*model.fields()))
        return select(model).from_statement(stmt)
