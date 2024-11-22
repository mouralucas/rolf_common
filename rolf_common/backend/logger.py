import logging

internal_handler = None
logger = logging.getLogger("loger_handler")
logger.setLevel(logging.INFO)


def set_log_handler(handler):
    global internal_handler

    internal_handler = handler

    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger():

    if not internal_handler:
        return
        # raise ValueError("The logging handler was not set")
    return logger
