"""
Logging configuration for MarketPulse AI.
Ensures structured, timestamped logs across data pipelines, models, and API endpoints with UTF-8 support.
"""

import logging
import sys

def setup_logger(name: str = "marketpulseai") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()
