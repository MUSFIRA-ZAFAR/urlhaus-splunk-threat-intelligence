import logging
import os
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    os.umask(0o077)
    directory = Path.home() / ".local/state/ti-lab/logs"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    logger = logging.getLogger("ti_collector")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = RotatingFileHandler(
            directory / "collector.log",
            maxBytes=1_048_576,
            backupCount=3,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            "%(asctime)sZ %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def report(*parts):
    message = " ".join(str(part) for part in parts)
    setup_logging().info(message)
    print(message)
