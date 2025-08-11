"""Utilities to format WhatsMyName data and schema JSON files."""

import json
import sys
from typing import Any, Optional

from wmn_base import WMNBase
from wmn_constants import DEFAULT_JSON_INDENT
from wmn_exceptions import WMNError


class WMNDataFormatter(WMNBase):
    """Main formatter class for WhatsMyName JSON data."""

    def __init__(self, json_indent: int = DEFAULT_JSON_INDENT) -> None:
        """Initialize formatter with file paths and configuration."""
        super().__init__()
        self.json_indent = json_indent
        self.data: Optional[dict[str, Any]] = None
        self.schema: Optional[dict[str, Any]] = None
        self.data_raw: Optional[str] = None
        self.schema_raw: Optional[str] = None
        self.data_formatted: Optional[str] = None
        self.schema_formatted: Optional[str] = None
    
    def load_files(self) -> None:
        """Load both data and schema files."""
        self.data, self.data_raw, self.data_formatted = self.read_json(self.data_path, self.json_indent)
        self.schema, self.schema_raw, self.schema_formatted = self.read_json(self.schema_path, self.json_indent)
    
    def sort_array_alphabetically(self, array: list[str]) -> list[str]:
        """Sort an array of strings alphabetically (case-insensitive)."""
        return sorted(array, key=str.casefold)
    
    @staticmethod
    def reorder_object_keys(
        site_data: dict[str, Any], key_order: list[str]
    ) -> dict[str, Any]:
        """Reorder object keys according to the specified order."""
        reordered = {key: site_data[key] for key in key_order if key in site_data}
        for key in site_data:
            if key not in key_order:
                reordered[key] = site_data[key]
        return reordered
    
    def sort_headers(self, site_data: dict[str, Any]) -> None:
        """Sort headers dictionary in-place (case-insensitive)."""
        headers = site_data.get("headers")
        if isinstance(headers, dict):
            site_data["headers"] = dict(
                sorted(
                    headers.items(),
                    key=lambda item: item[0].casefold(),
                )
            )
    
    def format_data(self) -> dict[str, Any]:
        """Format and sort the data according to schema."""
        if self.data is None or self.schema is None:
            raise WMNError("Data and schema must be loaded before formatting")
                
        if isinstance(self.data.get("authors"), list):
            self.data["authors"] = self.sort_array_alphabetically(self.data["authors"])

        if isinstance(self.data.get("categories"), list):
            self.data["categories"] = self.sort_array_alphabetically(self.data["categories"])

        site_schema = self.schema.get("properties", {}).get("sites", {}).get("items", {})
        key_order = list(site_schema.get("properties", {}).keys())

        if isinstance(self.data.get("sites"), list):
            self.data["sites"].sort(
                key=lambda site_data: str(site_data.get("name", "")).casefold()
            )
            
            for site_data in self.data["sites"]:
                self.sort_headers(site_data)
            
            self.data["sites"] = [self.reorder_object_keys(site_data, key_order) for site_data in self.data["sites"]]

        return self.data
    
    def run_formatting(self) -> bool:
        """Run complete formatting workflow."""
        try:
            self.load_files()
            
            formatted_data = self.format_data()
            updated_data_formatted = json.dumps(
                formatted_data,
                indent=self.json_indent,
                ensure_ascii=False,
            )

            changed = False

            if self.data_raw.strip() != updated_data_formatted.strip():
                self.write_text(self.data_path, updated_data_formatted)
                self.logger.info("Updated and sorted wmn-data.json")
                changed = True
            

            if self.schema_formatted is not None and self.schema_raw.strip() != self.schema_formatted.strip():
                self.write_text(self.schema_path, self.schema_formatted)
                self.logger.info("Formatted wmn-data-schema.json")
                changed = True
            
            
            if changed:
                self.logger.info("JSON files updated and formatted successfully")
            else:
                self.logger.info("JSON files are already formatted")
            
            return True
        except WMNError as error:
            self.logger.error("%s", error)
            return False
        except Exception:
            self.logger.exception("Unexpected error during formatting")
            return False


def main() -> None:
    """Main function to run the formatting workflow."""
    formatter = WMNDataFormatter()
    
    if not formatter.run_formatting():
        sys.exit(1)


if __name__ == "__main__":
    main()
