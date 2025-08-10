"""Base utilities shared by WhatsMyName scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Tuple

from wmn_constants import DEFAULT_DATA, DEFAULT_SCHEMA
from wmn_io import read_json as io_read_json, write_text as io_write_text
from wmn_logging import setup_logging


class WMNBase:
    """Base class providing common paths and logging."""

    def __init__(self, data_path: str = DEFAULT_DATA, schema_path: str = DEFAULT_SCHEMA) -> None:
        self.data_path = Path(data_path)
        self.schema_path = Path(schema_path)
        self.logger = setup_logging()

    def read_json(
        self,
        file_path: Path,
        json_indent: Optional[int] = None,
    ) -> Tuple[dict[str, Any], Optional[str], Optional[str]]:
        """Read a JSON file via IO helpers, optionally returning a formatted string."""
        return io_read_json(file_path, json_indent)

    def write_text(self, file_path: Path, content: str) -> None:
        """Write the provided content to the given path via IO helpers."""
        io_write_text(file_path, content)


