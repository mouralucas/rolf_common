import contextlib
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
        print("MongoDB client initialized")

    async def close(self):
        if self._client:
            self._client.close()
            print("MongoDB connection closed")

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if not self._client:
            raise RuntimeError("MongoDB client is not initialized")

        db = self._client[self._db_name]
        try:
            yield db
        except Exception as e:
            print(f"Error in MongoDB session: {e}")
            raise
        finally:
            print("MongoDB session completed")
