"""
Structured Logger Configuration.
Menyediakan logger terstandarisasi untuk seluruh aplikasi.
Dilarang menggunakan print().
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "venture_engine", level: Optional[int] = None) -> logging.Logger:
    """Mengonfigurasi dan mengembalikan instance logger standar.

    Args:
        name: Nama modul untuk logger.
        level: Logging level (default INFO jika tidak dispesifikasikan).

    Returns:
        logging.Logger yang telah dikonfigurasi dengan format standar.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level or logging.INFO)
        logger.propagate = False
    return logger


# Global default logger instance
logger: logging.Logger = setup_logger()
