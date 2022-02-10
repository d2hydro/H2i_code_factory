"""Example script to read and validate metadata.json."""

import json
from pathlib import Path
from jsonschema import validate

metadata_json = Path(r"..\data\de_tol_small\metadata.json")
schema_json = Path(r"..\json-schemas\metadata-schema.json")


metadata = json.loads(metadata_json.read_text())
schema = json.loads(schema_json.read_text())

validate(instance=metadata, schema=schema)
