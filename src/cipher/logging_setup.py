"""Logging configuration for Cipher."""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Configure stdlib logging. Logs to stderr so stdout stays clean for chat output."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )
