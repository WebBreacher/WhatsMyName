import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
data_path = REPO_ROOT / 'wmn-data.json'
schema_path = REPO_ROOT / 'wmn-data-schema.json'

def sort_array_alphabetically(arr):
    return sorted(arr, key=str.lower)

def reorder_object_keys(obj, key_order):
    reordered = {k: obj[k] for k in key_order if k in obj}
    for k in obj:
        if k not in key_order:
            reordered[k] = obj[k]
    return reordered

def sort_headers(site):
    headers = site.get("headers")
    if isinstance(headers, dict):
        site["headers"] = dict(sorted(headers.items(), key=lambda item: item[0].lower()))

def load_and_format_json(path):
    raw_content = path.read_text(encoding='utf-8')
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        sys.exit(f"{path.name} contains invalid JSON: {exc}")
    formatted = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return data, raw_content, formatted

data, data_raw, data_formatted = load_and_format_json(data_path)
schema, schema_raw, schema_formatted = load_and_format_json(schema_path)

changed = False

# Sort authors and categories
if isinstance(data.get('authors'), list):
    data['authors'] = sort_array_alphabetically(data['authors'])

if isinstance(data.get('categories'), list):
    data['categories'] = sort_array_alphabetically(data['categories'])

# Sort and reorder sites
site_schema = schema.get('properties', {}).get('sites', {}).get('items', {})
key_order = list(site_schema.get('properties', {}).keys())

if isinstance(data.get('sites'), list):
    data['sites'].sort(key=lambda site: site.get('name', '').lower())
    for site in data['sites']:
        sort_headers(site)
    data['sites'] = [reorder_object_keys(site, key_order) for site in data['sites']]

updated_data_formatted = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

# Write wmn-data.json if changed
if data_raw.replace('\r\n', '\n') != updated_data_formatted:
    data_path.write_text(updated_data_formatted, encoding='utf-8')
    print("Updated and sorted wmn-data.json.")
    changed = True
else:
    print("wmn-data.json already formatted.")

# Write formatted wmn-data-schema.json if changed
if schema_raw.replace('\r\n', '\n') != schema_formatted:
    schema_path.write_text(schema_formatted, encoding='utf-8')
    print("Formatted wmn-data-schema.json.")
    changed = True
else:
    print("wmn-data-schema.json already formatted.")

if not changed:
    print("No changes made.")
