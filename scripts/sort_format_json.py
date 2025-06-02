import json

data_path = 'wmn-data.json'
schema_path = 'wmn-data-schema.json'

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
    with open(path, 'r', encoding='utf-8') as f:
        raw_content = f.read()
        data = json.loads(raw_content)
    formatted = json.dumps(data, indent=2, ensure_ascii=False)
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

updated_data_formatted = json.dumps(data, indent=2, ensure_ascii=False)

# Write wmn-data.json if changed
if data_raw.strip() != updated_data_formatted.strip():
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(updated_data_formatted)
    print("Updated and sorted wmn-data.json.")
    changed = True
else:
    print("wmn-data.json already formatted.")

# Write formatted wmn-data-schema.json if changed
if schema_raw.strip() != schema_formatted.strip():
    with open(schema_path, 'w', encoding='utf-8') as f:
        f.write(schema_formatted)
    print("Formatted wmn-data-schema.json.")
    changed = True
else:
    print("wmn-data-schema.json already formatted.")

if not changed:
    print("No changes made.")
