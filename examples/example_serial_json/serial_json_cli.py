"""JSON Schema Validation and Manipulation CLI.

Demonstrates JSON parsing, validation, schema checking, and transformation patterns.
"""

import json
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class SchemaType:
    """Represents a JSON schema type."""

    type_name: str
    required: bool = True
    default: Any = None
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    enum_values: list[Any] | None = None


@dataclass
class Schema:
    """JSON Schema definition."""

    fields: dict[str, SchemaType]
    allow_extra: bool = False


def validate_type(value: Any, schema_type: SchemaType) -> tuple[bool, str]:
    """Validate a value against a schema type."""
    type_map = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }

    expected = type_map.get(schema_type.type_name)
    if expected is None:
        return False, f"Unknown type: {schema_type.type_name}"

    if not isinstance(value, expected):
        return False, f"Expected {schema_type.type_name}, got {type(value).__name__}"

    if schema_type.type_name == "string":
        if schema_type.min_length is not None and len(value) < schema_type.min_length:
            return False, f"String too short: {len(value)} < {schema_type.min_length}"
        if schema_type.max_length is not None and len(value) > schema_type.max_length:
            return False, f"String too long: {len(value)} > {schema_type.max_length}"

    if schema_type.type_name in ("number", "integer"):
        if schema_type.min_value is not None and value < schema_type.min_value:
            return False, f"Value too small: {value} < {schema_type.min_value}"
        if schema_type.max_value is not None and value > schema_type.max_value:
            return False, f"Value too large: {value} > {schema_type.max_value}"

    if schema_type.enum_values is not None and value not in schema_type.enum_values:
        return False, f"Value not in enum: {value}"

    return True, ""


def validate_object(data: dict[str, Any], schema: Schema) -> list[str]:
    """Validate a JSON object against a schema."""
    errors = []

    for field_name, field_type in schema.fields.items():
        if field_name not in data:
            if field_type.required and field_type.default is None:
                errors.append(f"Missing required field: {field_name}")
            continue

        valid, msg = validate_type(data[field_name], field_type)
        if not valid:
            errors.append(f"Field '{field_name}': {msg}")

    if not schema.allow_extra:
        for key in data:
            if key not in schema.fields:
                errors.append(f"Unexpected field: {key}")

    return errors


def json_parse(text: str) -> tuple[Any, str | None]:
    """Parse JSON string safely."""
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, str(e)


def json_stringify(data: Any, pretty: bool = False) -> str:
    """Convert data to JSON string."""
    if pretty:
        return json.dumps(data, indent=2, sort_keys=True)
    return json.dumps(data, separators=(",", ":"))


def json_get(data: Any, path: str) -> Any:
    """Get value at JSON path (dot notation)."""
    if not path:
        return data

    parts = path.split(".")
    current = data

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            except ValueError:
                return None
        else:
            return None

    return current


def json_set(data: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """Set value at JSON path (returns new dict)."""
    result = json.loads(json.dumps(data))
    parts = path.split(".")
    current = result

    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value
    return result


def json_delete(data: dict[str, Any], path: str) -> dict[str, Any]:
    """Delete value at JSON path (returns new dict)."""
    result = json.loads(json.dumps(data))
    parts = path.split(".")
    current = result

    for part in parts[:-1]:
        if part not in current:
            return result
        current = current[part]

    if parts[-1] in current:
        del current[parts[-1]]

    return result


def json_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two JSON objects."""
    result = json.loads(json.dumps(base))

    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = json_merge(result[key], value)
        else:
            result[key] = json.loads(json.dumps(value))

    return result


def json_diff(obj1: Any, obj2: Any, path: str = "") -> list[str]:
    """Find differences between two JSON values."""
    diffs = []

    if type(obj1) is not type(obj2):
        diffs.append(f"{path}: type {type(obj1).__name__} != {type(obj2).__name__}")
        return diffs

    if isinstance(obj1, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in sorted(all_keys):
            new_path = f"{path}.{key}" if path else key
            if key not in obj1:
                diffs.append(f"{new_path}: added")
            elif key not in obj2:
                diffs.append(f"{new_path}: removed")
            else:
                diffs.extend(json_diff(obj1[key], obj2[key], new_path))
    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            diffs.append(f"{path}: length {len(obj1)} != {len(obj2)}")
        else:
            for i, (a, b) in enumerate(zip(obj1, obj2, strict=False)):
                diffs.extend(json_diff(a, b, f"{path}[{i}]"))
    elif obj1 != obj2:
        diffs.append(f"{path}: {obj1!r} != {obj2!r}")

    return diffs


def json_flatten(data: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten nested JSON to dot-notation keys."""
    result = {}

    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            result.update(json_flatten(value, new_key))
    elif isinstance(data, list):
        for i, value in enumerate(data):
            new_key = f"{prefix}[{i}]"
            result.update(json_flatten(value, new_key))
    else:
        result[prefix] = data

    return result


def json_unflatten(data: dict[str, Any]) -> dict[str, Any]:
    """Unflatten dot-notation keys to nested JSON."""
    result: dict[str, Any] = {}

    for key, value in data.items():
        parts = key.replace("[", ".").replace("]", "").split(".")
        current = result

        for i, part in enumerate(parts[:-1]):
            next_part = parts[i + 1]
            is_array = next_part.isdigit()

            if part not in current:
                current[part] = [] if is_array else {}
            current = current[part]

            if is_array and isinstance(current, list):
                idx = int(next_part)
                while len(current) <= idx:
                    current.append({})

        final_part = parts[-1]
        if final_part.isdigit() and isinstance(current, list):
            idx = int(final_part)
            while len(current) <= idx:
                current.append(None)
            current[idx] = value
        else:
            current[final_part] = value

    return result


def json_query(data: list[dict[str, Any]], conditions: dict[str, Any]) -> list[dict[str, Any]]:
    """Query array of objects with conditions."""
    results = []

    for item in data:
        matches = True
        for key, expected in conditions.items():
            actual = json_get(item, key)
            if actual != expected:
                matches = False
                break
        if matches:
            results.append(item)

    return results


def simulate_json(operations: list[str]) -> list[str]:
    """Simulate JSON operations from command strings."""
    results = []
    context: dict[str, Any] = {}

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "parse":
            data, err = json_parse(parts[1])
            if err:
                results.append(f"error:{err}")
            else:
                context["data"] = data
                results.append("ok")
        elif cmd == "stringify":
            results.append(json_stringify(context.get("data", {})))
        elif cmd == "get":
            value = json_get(context.get("data"), parts[1])
            results.append(json.dumps(value))
        elif cmd == "set":
            path_value = parts[1].split("=", 1)
            value, _ = json_parse(path_value[1])
            context["data"] = json_set(context.get("data", {}), path_value[0], value)
            results.append("ok")
        elif cmd == "delete":
            context["data"] = json_delete(context.get("data", {}), parts[1])
            results.append("ok")
        elif cmd == "flatten":
            flat = json_flatten(context.get("data", {}))
            results.append(json_stringify(flat))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: serial_json_cli.py <command> [args...]")
        print("Commands: parse, validate, get, set, merge, diff, flatten")
        return 1

    cmd = sys.argv[1]

    if cmd == "parse":
        text = sys.stdin.read()
        data, err = json_parse(text)
        if err:
            print(f"Error: {err}", file=sys.stderr)
            return 1
        print(json_stringify(data, pretty=True))

    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Usage: validate <schema_json>", file=sys.stderr)
            return 1
        schema_data, _ = json_parse(sys.argv[2])
        data, _ = json_parse(sys.stdin.read())

        fields = {}
        for name, spec in schema_data.get("fields", {}).items():
            fields[name] = SchemaType(
                type_name=spec.get("type", "string"),
                required=spec.get("required", True),
            )
        schema = Schema(fields=fields)
        errors = validate_object(data, schema)

        if errors:
            for err in errors:
                print(err)
            return 1
        print("Valid")

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: get <path>", file=sys.stderr)
            return 1
        data, _ = json_parse(sys.stdin.read())
        value = json_get(data, sys.argv[2])
        print(json_stringify(value, pretty=True))

    elif cmd == "flatten":
        data, _ = json_parse(sys.stdin.read())
        flat = json_flatten(data)
        print(json_stringify(flat, pretty=True))

    return 0


if __name__ == "__main__":
    sys.exit(main())
