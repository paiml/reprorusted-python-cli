#!/usr/bin/env python3
"""JSON Basic CLI.

JSON serialization and deserialization operations.
"""

import argparse
import json
import sys


def to_json(data: dict | list) -> str:
    """Convert data to JSON string."""
    return json.dumps(data)


def to_json_pretty(data: dict | list, indent: int = 2) -> str:
    """Convert data to pretty JSON string."""
    return json.dumps(data, indent=indent)


def from_json(s: str) -> dict | list:
    """Parse JSON string to data."""
    return json.loads(s)


def to_json_sorted(data: dict) -> str:
    """Convert to JSON with sorted keys."""
    return json.dumps(data, sort_keys=True)


def to_json_compact(data: dict | list) -> str:
    """Convert to compact JSON (no spaces)."""
    return json.dumps(data, separators=(",", ":"))


def read_json_file(path: str) -> dict | list:
    """Read JSON from file."""
    with open(path) as f:
        return json.load(f)


def write_json_file(path: str, data: dict | list, indent: int | None = 2) -> None:
    """Write JSON to file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)


def get_value(data: dict, key: str) -> any:
    """Get value from JSON object by key."""
    return data.get(key)


def get_nested(data: dict, *keys: str) -> any:
    """Get nested value using path of keys."""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        elif isinstance(result, list) and key.isdigit():
            idx = int(key)
            result = result[idx] if 0 <= idx < len(result) else None
        else:
            return None
    return result


def set_value(data: dict, key: str, value: any) -> dict:
    """Set value in JSON object (returns new dict)."""
    result = data.copy()
    result[key] = value
    return result


def merge_json(d1: dict, d2: dict) -> dict:
    """Merge two JSON objects."""
    return {**d1, **d2}


def deep_merge(d1: dict, d2: dict) -> dict:
    """Deep merge two JSON objects."""
    result = d1.copy()
    for key, value in d2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def json_keys(data: dict) -> list[str]:
    """Get all keys from JSON object."""
    return list(data.keys())


def json_values(data: dict) -> list:
    """Get all values from JSON object."""
    return list(data.values())


def flatten_json(data: dict, prefix: str = "") -> dict[str, any]:
    """Flatten nested JSON to flat dict with dot notation keys."""
    result: dict[str, any] = {}
    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_json(value, new_key))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    result.update(flatten_json(item, f"{new_key}.{i}"))
                else:
                    result[f"{new_key}.{i}"] = item
        else:
            result[new_key] = value
    return result


def unflatten_json(data: dict[str, any]) -> dict:
    """Unflatten dot-notation dict to nested JSON."""
    result: dict = {}
    for key, value in data.items():
        parts = key.split(".")
        current = result
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                # Check if next part is numeric
                next_part = parts[i + 1]
                if next_part.isdigit():
                    current[part] = []
                else:
                    current[part] = {}
            current = current[part]
        # Handle final part
        final_part = parts[-1]
        if isinstance(current, list):
            idx = int(final_part)
            while len(current) <= idx:
                current.append(None)
            current[idx] = value
        else:
            current[final_part] = value
    return result


def filter_keys(data: dict, keys: list[str]) -> dict:
    """Filter JSON object to only include specified keys."""
    return {k: v for k, v in data.items() if k in keys}


def exclude_keys(data: dict, keys: list[str]) -> dict:
    """Exclude specified keys from JSON object."""
    return {k: v for k, v in data.items() if k not in keys}


def is_valid_json(s: str) -> bool:
    """Check if string is valid JSON."""
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False


def json_type(data: any) -> str:
    """Get JSON type of value."""
    if data is None:
        return "null"
    elif isinstance(data, bool):
        return "boolean"
    elif isinstance(data, int):
        return "integer"
    elif isinstance(data, float):
        return "number"
    elif isinstance(data, str):
        return "string"
    elif isinstance(data, list):
        return "array"
    elif isinstance(data, dict):
        return "object"
    return "unknown"


def count_keys(data: dict) -> int:
    """Count total keys in nested JSON."""
    count = len(data)
    for value in data.values():
        if isinstance(value, dict):
            count += count_keys(value)
    return count


def find_values(data: dict | list, key: str) -> list:
    """Find all values for a key in nested JSON."""
    results: list = []
    if isinstance(data, dict):
        if key in data:
            results.append(data[key])
        for value in data.values():
            if isinstance(value, (dict, list)):
                results.extend(find_values(value, key))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                results.extend(find_values(item, key))
    return results


def transform_values(data: dict, fn: callable) -> dict:
    """Transform all leaf values in JSON."""
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = transform_values(value, fn)
        elif isinstance(value, list):
            result[key] = [
                fn(item) if not isinstance(item, (dict, list)) else item for item in value
            ]
        else:
            result[key] = fn(value)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="JSON basic CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # parse
    parse_p = subparsers.add_parser("parse", help="Parse JSON string")
    parse_p.add_argument("json", help="JSON string")

    # format
    format_p = subparsers.add_parser("format", help="Format JSON")
    format_p.add_argument("json", help="JSON string")
    format_p.add_argument("--indent", type=int, default=2, help="Indent")

    # get
    get_p = subparsers.add_parser("get", help="Get value by path")
    get_p.add_argument("json", help="JSON string")
    get_p.add_argument("path", help="Dot-notation path")

    # validate
    validate_p = subparsers.add_parser("validate", help="Validate JSON")
    validate_p.add_argument("json", help="JSON string")

    # flatten
    flatten_p = subparsers.add_parser("flatten", help="Flatten JSON")
    flatten_p.add_argument("json", help="JSON string")

    args = parser.parse_args()

    if args.command == "parse":
        try:
            data = from_json(args.json)
            print(to_json_pretty(data))
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return 1

    elif args.command == "format":
        try:
            data = from_json(args.json)
            print(to_json_pretty(data, args.indent))
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return 1

    elif args.command == "get":
        try:
            data = from_json(args.json)
            parts = args.path.split(".")
            value = get_nested(data, *parts)
            print(to_json(value) if isinstance(value, (dict, list)) else value)
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return 1

    elif args.command == "validate":
        if is_valid_json(args.json):
            print("Valid JSON")
        else:
            print("Invalid JSON")
            return 1

    elif args.command == "flatten":
        try:
            data = from_json(args.json)
            if isinstance(data, dict):
                flat = flatten_json(data)
                print(to_json_pretty(flat))
            else:
                print("Can only flatten objects")
                return 1
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return 1

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
