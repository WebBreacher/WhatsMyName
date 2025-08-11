"""Hashing utilities for WhatsMyName JSON data files."""

import sys
import hashlib
from pathlib import Path
from typing import Optional

from wmn_base import WMNBase
from wmn_exceptions import WMNError


class WMNDataHasher(WMNBase):
    """Generates and updates SHA256 hash files for WhatsMyName JSON data."""

    def __init__(self) -> None:
        super().__init__()

    def compute_sha256(self, file_path: Path) -> str:
        """Compute the SHA256 hex digest for the given file path."""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    def write_hash_file(self, target_file: Path) -> bool:
        """Compute and write the `.sha256` file for the given target file."""
        hash_file = target_file.with_suffix(target_file.suffix + ".sha256")

        try:
            new_hash = self.compute_sha256(target_file)
        except (FileNotFoundError, PermissionError, OSError) as error:
            self.logger.error("Cannot read %s: %s", target_file, error)
            raise WMNError(f"Missing or unreadable input file: {target_file}") from error

        previous_hash: Optional[str] = None
        if hash_file.exists():
            try:
                previous_hash = hash_file.read_text(encoding="utf-8").strip()
            except OSError as error:
                self.logger.warning(
                    "Could not read previous hash for %s: %s", target_file.name, error
                )

        if previous_hash != new_hash:
            self.write_text(hash_file, new_hash + "\n")
            if previous_hash is None:
                self.logger.info("Generated new hash for %s", target_file.name)
            else:
                self.logger.info(
                    "Hash updated for %s: %s... -> %s...",
                    target_file.name,
                    previous_hash[:8],
                    new_hash[:8],
                )
            return True
        return False

    def run_hashing(self) -> bool:
        """Run hashing for data and schema files, logging outcomes."""
        try:
            targets = [self.data_path, self.schema_path]
            any_changes = False
            for target in targets:
                changed = self.write_hash_file(target)
                any_changes = any_changes or changed
            
            if any_changes:
                self.logger.info("SHA256 hash files updated successfully")
            else:
                self.logger.info("SHA256 hash files are up to date")
            return True
        except WMNError as error:
            self.logger.error("%s", error)
            return False
        except Exception:
            self.logger.exception("Unexpected error during hashing")
            return False



def main() -> None:
    """Entry point for command-line execution."""
    hasher = WMNDataHasher()
    
    if not hasher.run_hashing():
        sys.exit(1)


if __name__ == "__main__":
    main()

