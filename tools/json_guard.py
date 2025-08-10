from pathlib import Path
import json
from jsonschema import validate, Draft202012Validator

def load_validated(data_path: Path, schema_path: Path):
    """Load and validate JSON against schema."""
    obj = json.loads(Path(data_path).read_text())
    schema = json.loads(Path(schema_path).read_text())
    Draft202012Validator.check_schema(schema)
    validate(instance=obj, schema=schema)
    return obj 