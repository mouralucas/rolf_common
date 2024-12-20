from contextlib import asynccontextmanager
from typing import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession

from rolf_common.backend.settings import settings

class NoSqlDatabaseSessionManager:
    def __init__(self, host: str, db_name: str):
        self._uri = host
        self._db_name = db_name
        self._client = None

    async def initialize(self):
        if self._client is None:
            self._client = AsyncIOMotorClient(self._uri)

    async def close(self):
        if self._client:
            self._client.close()
            print("MongoDB connection closed")

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if not self._client:
            raise RuntimeError("MongoDB client is not initialized")

        db = self._client[self._db_name]
        try:
            yield db
        except Exception as e:
            raise
        finally:
            pass


_db_connection: NoSqlDatabaseSessionManager | None = None

def set_db_connection(connection: NoSqlDatabaseSessionManager):
    """
    Created by: Lucas Penha de Moura - 20/11/2024

        Create a global variable to store the NoSQL Database connection class
    """
    global _db_connection
    _db_connection = connection


def get_db_connection() -> NoSqlDatabaseSessionManager:
    """
    Created by: Lucas Penha de Moura - 20/11/2024

        Get the NoSQL Database connection class
    """
    if _db_connection is None:
        pass
        # raise RuntimeError("A conexão com o banco de dados não foi configurada.")
    return _db_connection
