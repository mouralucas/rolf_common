import logging
import datetime

from rolf_common.backend.nosql_database import NoSqlDatabaseSessionManager
import asyncio


class BaseLogDataManager(logging.Handler):
    def __init__(self, connection_class: NoSqlDatabaseSessionManager, collection_name: str | None = None):
        super().__init__()
        self.db_connection_class: NoSqlDatabaseSessionManager = connection_class
        self.collection: str = collection_name or 'logs'

    def emit(self, record):
        """
        Created by: Lucas Penha de Moura - 21/11/2024
            Implement the synchronous emit method from logging.Handler using the async event loop
        """
        try:
            log_entry = self._format_record(record)

            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self._emit_with_session(log_entry), loop
                )
            else:
                loop.run_until_complete(self._emit_with_session(log_entry))
        except Exception as e:
            self.handleError(record)

    async def _emit_with_session(self, log_entry):
        """
        Created by: Lucas Penha de Moura - 21/11/2024
            Insert the new log into specified collection asynchronously
        """
        async with self.db_connection_class.session() as session:
            await session[self.collection].insert_one(log_entry)

    def _format_record(self, record):
        """
        Created by: Lucas Penha de Moura - 21/11/2024
            Create the json to be inserted into the database
        """
        return {
            "timestamp": datetime.datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "extra": record.__dict__.get("extra", {})  # Inclui campos adicionais
        }