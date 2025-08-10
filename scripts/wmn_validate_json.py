"""Validation utilities for WhatsMyName JSON data files."""

import sys
from typing import Any, Optional
from collections import Counter

from jsonschema import validators
from jsonschema.exceptions import SchemaError

from wmn_base import WMNBase
from wmn_exceptions import WMNError


class WMNDataValidator(WMNBase):
    """Main validator class for WhatsMyName JSON data."""

    def __init__(self) -> None:
        super().__init__()
        self.schema: Optional[dict[str, Any]] = None
        self.data: Optional[dict[str, Any]] = None
    
    def load_files(self) -> None:
        """Load both schema and data files."""
        self.schema = self.read_json(self.schema_path)[0]
        self.data = self.read_json(self.data_path)[0]
        self.logger.info("Loaded schema and data files.")
    
    def validate_schema(self) -> bool:
        """Validate JSON data against the provided schema."""
        if self.schema is None or self.data is None:
            raise WMNError("Schema and data must be loaded before validation")
    
        try:
            validator_cls = validators.validator_for(self.schema)
            validator_cls.check_schema(self.schema)
            validator_instance = validator_cls(self.schema)

            errors = sorted(
                validator_instance.iter_errors(self.data),
                key=lambda e: tuple(str(p) for p in e.absolute_path),
            )

            if errors:
                for err in errors:
                    absolute_path = list(err.absolute_path)
                    path_str = " -> ".join(map(str, absolute_path)) or "<root>"
                    message_str = str(err.message).replace("\n", " ").strip()

                    index = next(
                        (
                            absolute_path[i + 1]
                            for i, part in enumerate(absolute_path)
                            if part == "sites"
                            and i + 1 < len(absolute_path)
                            and isinstance(absolute_path[i + 1], int)
                        ),
                        None,
                    )

                    name = None
                    if index is not None and isinstance(self.data, dict):
                        sites = self.data.get("sites")
                        if (
                            isinstance(sites, list)
                            and 0 <= index < len(sites)
                            and isinstance(sites[index], dict)
                        ):
                            name_candidate = sites[index].get("name")
                            if isinstance(name_candidate, str) and name_candidate.strip():
                                name = name_candidate

                    self.logger.error(
                        "path=%s | name=%s | message=%s",
                        path_str,
                        name or "N/A",
                        message_str,
                    )

                self.logger.error("JSON schema validation failed with %d error(s)", len(errors))
                return False

            self.logger.info("JSON schema validation successful")
            return True

        except SchemaError as error:
            raise WMNError(f"Invalid JSON schema: {error}") from error
        except Exception:
            self.logger.exception("Unexpected error during schema validation")
            return False
    
    def validate_duplicates(self) -> list[str]:
        """Run additional validation checks beyond schema validation."""
        if self.data is None:
            raise WMNError("Data must be loaded before duplicate validation")
        
        sites = self.data["sites"]

        self.logger.info("Checking %d sites for duplicates...", len(sites))

        name_counts: Counter[str] = Counter(site["name"] for site in sites)
        return [name for name, count in name_counts.items() if count > 1]
    
    def run_validation(self) -> bool:
        """Run complete validation process."""
        try:
            self.load_files()
            
            if not self.validate_schema():
                return False
            
            duplicate_names = self.validate_duplicates()
            
            if duplicate_names:
                self.logger.error(
                    "Duplicate site 'name' values found: %s", duplicate_names
                )
                return False
            
            self.logger.info("All validations passed successfully")
            return True
        except WMNError as error:
            self.logger.error("%s", error)
            return False
        except Exception:
            self.logger.exception("Unexpected error during validation")
            return False


def main() -> None:
    """Main function to run the validation process."""
    validator = WMNDataValidator()
    
    if not validator.run_validation():
        sys.exit(1)


if __name__ == "__main__":
    main()
