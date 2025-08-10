"""Shared logging utilities for WhatsMyName scripts."""

import logging

from rich.logging import RichHandler


def setup_logging() -> logging.Logger:
    """Configure logging with rich tracebacks for readable output (locally and in CI)."""
    logging.basicConfig(
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True)],
        force=True,
    )
    return logging.getLogger(__name__)
