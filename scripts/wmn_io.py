"""Shared IO helpers for WhatsMyName scripts."""

import json
from pathlib import Path
from typing import Any, Optional, Tuple

from wmn_exceptions import WMNError
from wmn_constants import DEFAULT_JSON_ENCODING


def read_json(
    file_path: Path,
    json_indent: Optional[int] = None,
) -> Tuple[dict[str, Any], Optional[str], Optional[str]]:
    """Read a JSON file with robust error handling."""
    try:
        if not file_path.exists() or not file_path.is_file():
            raise WMNError(f"File not found or not a file: {file_path}")

        raw_content = file_path.read_text(encoding=DEFAULT_JSON_ENCODING)

        try:
            data: dict[str, Any] = json.loads(raw_content)
        except json.JSONDecodeError as error:
            raise WMNError(f"Invalid JSON in {file_path}: {error}") from error

        formatted: Optional[str] = None
        if json_indent is not None:
            formatted = json.dumps(
                data,
                indent=json_indent,
                ensure_ascii=False,
            )

        return data, raw_content, formatted

    except Exception as error:
        raise WMNError(f"File loading error: {error}") from error


def write_text(file_path: Path, content: str) -> None:
    """Write text to a file with consistent error handling."""
    try:
        file_path.write_text(content, encoding=DEFAULT_JSON_ENCODING)
    except Exception as error:
        raise WMNError(f"File writing error: {error}") from error


