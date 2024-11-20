import logging

from rolf_common.backend.nosql_database import NoSqlDatabaseSessionManager


class BaseLogDataManager(logging.Handler):
    def __init__(self, connection_class: NoSqlDatabaseSessionManager, collection_name: str | None = None):
        super().__init__()
        self.db_connection_class: NoSqlDatabaseSessionManager = connection_class
        self.collection: str = collection_name or 'logs'
        # self.collection = client[db_name][collection_name]

    async def emit(self, record):
        with self.db_connection_class.session() as session:
            log_entry = self.format(record)

            if isinstance(log_entry, str):  # Converte string para JSON
                log_entry = {"message": log_entry}

            session[self.collection].insert_one(log_entry)

