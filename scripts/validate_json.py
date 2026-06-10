import json
import sys

from jsonschema import Draft7Validator

DATA_FILE = "wmn-data.json"
SCHEMA_FILE = "wmn-data-schema.json"


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    with open(SCHEMA_FILE, encoding="utf-8") as f:
        schema = json.load(f)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    if not errors:
        print(f"{DATA_FILE} is valid against {SCHEMA_FILE}.")
        return 0

    for error in errors:
        path = list(error.path)
        site_name = None
        if len(path) >= 2 and path[0] == "sites":
            site_name = data["sites"][path[1]].get("name")
        location = f"sites[{path[1]}] ({site_name})" if site_name else "/".join(str(p) for p in path)
        print(f"ERROR at {location}: {error.message}")

    print(f"\n{len(errors)} error(s) found in {DATA_FILE}.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
