import logging
import inspect
import os
import sys

from datetime import datetime

from api.settings import BASE_DIR


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    log_level = logging.DEBUG if os.environ['ENV_MODE'] == 'dev' else logging.WARNING
    logger.setLevel(log_level)

    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code

    logger_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - {} ({}:{}) - %(message)s'.format(
            func.co_name,
            func.co_filename,
            func.co_firstlineno
        )
    )

    logger_console_handler = logging.StreamHandler(sys.stdout)
    logger_console_handler.setLevel(log_level)
    logger_console_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_console_handler)

    return logger
