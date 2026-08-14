import json
import sys

from jsonschema import Draft7Validator

DATA_FILE = "wmn-data.json"
SCHEMA_FILE = "wmn-data-schema.json"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: {path} is not valid JSON: {e.msg} at line {e.lineno} column {e.colno}")
            sys.exit(1)


def check_categories_match_cat_enum(data, schema):
    categories = set(data.get("categories", []))
    cat_enum = set(
        schema.get("properties", {})
        .get("sites", {})
        .get("items", {})
        .get("properties", {})
        .get("cat", {})
        .get("enum", [])
    )
    if categories == cat_enum:
        return None

    missing_from_enum = categories - cat_enum
    missing_from_categories = cat_enum - categories
    details = []
    if missing_from_enum:
        details.append(f"in categories but not in cat enum: {sorted(missing_from_enum)}")
    if missing_from_categories:
        details.append(f"in cat enum but not in categories: {sorted(missing_from_categories)}")
    return "categories array and cat enum are out of sync (" + "; ".join(details) + ")"


def main():
    data = load_json(DATA_FILE)
    schema = load_json(SCHEMA_FILE)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    category_sync_error = check_categories_match_cat_enum(data, schema)

    if not errors and not category_sync_error:
        print(f"{DATA_FILE} is valid against {SCHEMA_FILE}.")
        return 0

    for error in errors:
        path = list(error.path)
        site_name = None
        if len(path) >= 2 and path[0] == "sites":
            site_name = data["sites"][path[1]].get("name")
        location = f"sites[{path[1]}] ({site_name})" if site_name else "/".join(str(p) for p in path)
        print(f"ERROR at {location}: {error.message}")

    if category_sync_error:
        print(f"ERROR: {category_sync_error}")

    total_errors = len(errors) + (1 if category_sync_error else 0)
    print(f"\n{total_errors} error(s) found in {DATA_FILE}.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
