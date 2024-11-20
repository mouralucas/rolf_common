import logging
import sys

from rolf_common.backend.nosql_database import get_db_connection
from rolf_common.managers.logs import BaseLogDataManager

logger = logging.getLogger("loger_handler")
logger.setLevel(logging.INFO)

loger_handler = BaseLogDataManager(get_db_connection())
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
loger_handler.setFormatter(formatter)

logger.addHandler(loger_handler)