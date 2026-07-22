"""Logging utility with rich formatting."""
import logging
import sys
from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with rich output."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
        )
        handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger
