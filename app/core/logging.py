import logging
import sys
import os

from logging.handlers import RotatingFileHandler

from app.core.config import settings

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "invoice-service.log")

def setup_logging():
    os.makedirs(LOG_DIR, exist_ok= True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s |"
        "%(name)s | "
        "%(message)s |"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes= 5 * 1024 * 1024,
        backupCount= 5
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

