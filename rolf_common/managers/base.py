from datetime import datetime
from pyexpat import model
from typing import Any, List, Sequence, Type

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Executable

from rolf_common.models.base import SQLModel


class BaseDataManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    """Base data manager class responsible for operations over database."""

    async def add_one(self, sql_model: SQLModel) -> SQLModel:
        self.session.add(sql_model)
        await self.session.commit()
        await self.session.refresh(sql_model)

        return sql_model

    async def add_all(self, sql_models: list[SQLModel]) -> list[SQLModel]:
        self.session.add_all(sql_models)
        await self.session.commit()

        # TODO: test if this is a good approach to batch refresh (consider the order created when refreshing)
        # ids = [sql_model.id for sql_model in sql_models]
        # refreshed_models = await self.session.execute(
        #     select(SQLModel).where(SQLModel.id.in_(ids))
        # )
        # refreshed_models = refreshed_models.scalars().all()

        return sql_models

    async def update_one(self, sql_statement: Executable, sql_model: SQLModel) -> SQLModel:
        """
        :Name: update_one
        :Created by: Lucas Penha de Moura - 28/04/2024
            Update one item from a model

        :Params:
            sql_statement: An Executable SQLAlchemy statement - Must be update
            model: A SQLAlchemy model
        """
        if not sql_statement.is_update:
            raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED)

        try:
            sql_model.edited_at = datetime.utcnow()
            await self.session.execute(sql_statement)
            await self.session.commit()
            await self.session.refresh(sql_model)
        except Exception as e:
            raise e

        return sql_model

    async def get_first(self, sql_statement: Executable,
                        raise_exception: bool = False) -> BaseModel | None:
        """
        :Name: get_only_one
        :Created by: Lucas Penha de Moura - 19/02/2024
            Similar to get_only_one, but if none is found can return None or raise an exception, if more than one is found return first element

        :Params:
            select_stmt : An Executable SQLAlchemy statement, usually "select"
            schema : The Pydantic model class to convert the result
            raise_exception : If true, raise an exception if no data is found, if false, return None
        """
        result = await self.session.execute(sql_statement)
        result = result.scalar()

        if raise_exception and result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No data found')

        return result

    async def get_only_one(self, select_statement: Executable) -> SQLModel | None:
        """
        :Name: get_only_one
        :Created by: Lucas Penha de Moura - 09/02/2024

            Get one register, and one only, if none or more than one is found raise an exception

        :Params:
            select_stmt : An Executable SQLAlchemy statement, usually "select"
            schema : The Pydantic model class to convert the result
            return_db_model : If true, return the result from database, without converto to Pydantic class
        """
        try:
            result = await self.session.execute(select_statement)
            result = result.scalar_one()
        except NoResultFound as e:

            result = None
        # TODO: maybe handle exceptions to return default values

        return result

    async def get_by_id(self, sql_model:SQLModel, object_id: Any) -> SQLModel | None:
        stmt = select(sql_model).where(sql_model.id == object_id)

        obj: SQLModel = await self.get_only_one(stmt)

        return obj

    async def get_all(self, select_statement: Executable,
                      unique_result: bool = False,
                      raise_exception: bool = False) -> list[SQLModel] | None:
        """
        :Name: get_all
        :Created by: Lucas Penha de Moura - 09/02/2024

            Get one register, and one only, if none or more than one is found raise an exception

        :Params:
            select_stmt : An Executable SQLAlchemy statement, usually "select"
            unique_result: If true, apply unique to the query, used when query contains joins ***(investigate reason)***
            raise_exception : If true, raise an exception if no data is found, if false, return None
        """
        result = await self.session.scalars(select_statement)
        if unique_result:
            result = result.unique()

        result = result.all()

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
