#!/usr/bin/env python3
"""TOML file reader CLI.

Parse and query TOML configuration files (subset implementation).
"""

import argparse
import sys


def parse_value(value: str) -> str | int | float | bool | list:
    """Parse a TOML value string into Python type."""
    value = value.strip()

    # Boolean
    if value == "true":
        return True
    if value == "false":
        return False

    # Integer
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)

    # Float
    if "." in value:
        try:
            return float(value)
        except ValueError:
            pass

    # Array
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        items = []
        for item in inner.split(","):
            items.append(parse_value(item.strip()))
        return items

    # String (quoted)
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]

    # Bare string
    return value


def parse_toml(content: str) -> dict:
    """Parse TOML content into nested dict."""
    result: dict = {}
    current_section: list[str] = []

    for line in content.split("\n"):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Table header [section] or [section.subsection]
        if line.startswith("[") and line.endswith("]"):
            header = line[1:-1]
            current_section = header.split(".")
            # Initialize nested structure
            target = result
            for part in current_section:
                if part not in target:
                    target[part] = {}
                target = target[part]
            continue

        # Key = value pair
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Navigate to current section
            target = result
            for part in current_section:
                target = target[part]

            target[key] = parse_value(value)

    return result


def get_nested(data: dict, path: str) -> str | int | float | bool | list | dict | None:
    """Get a nested value using dot notation."""
    parts = path.split(".")
    current = data

    for part in parts:
        if not isinstance(current, dict):
            return None
        if part not in current:
            return None
        current = current[part]

    return current


def list_keys(data: dict, path: str = "") -> list[str]:
    """List all keys at a given path."""
    if path:
        target = get_nested(data, path)
        if not isinstance(target, dict):
            return []
    else:
        target = data

    return list(target.keys())


def flatten_toml(data: dict, prefix: str = "") -> list[tuple[str, str]]:
    """Flatten TOML data into list of (key, value) pairs."""
    result = []

    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            result.extend(flatten_toml(value, full_key))
        else:
            result.append((full_key, str(value)))

    return result


def format_value(value: str | int | float | bool | list) -> str:
    """Format a Python value as TOML."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, list):
        items = [format_value(v) for v in value]
        return "[" + ", ".join(items) + "]"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="TOML file reader and query tool")
    parser.add_argument("input", nargs="?", help="Input TOML file (- for stdin)")
    parser.add_argument("--get", metavar="PATH", help="Get value at path (e.g., database.host)")
    parser.add_argument(
        "--keys", metavar="PATH", nargs="?", const="", help="List keys at path (empty for root)"
    )
    parser.add_argument("--flatten", action="store_true", help="Output all key=value pairs")
    parser.add_argument("--sections", action="store_true", help="List top-level sections")

    args = parser.parse_args()

    # Read input
    if args.input is None or args.input == "-":
        content = sys.stdin.read()
    else:
        with open(args.input) as f:
            content = f.read()

    data = parse_toml(content)

    # Perform operation
    if args.get:
        value = get_nested(data, args.get)
        if value is None:
            return 1
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"{k} = {format_value(v)}")
        else:
            print(value)
    elif args.keys is not None:
        for key in list_keys(data, args.keys):
            print(key)
    elif args.flatten:
        for key, value in flatten_toml(data):
            print(f"{key} = {value}")
    elif args.sections:
        for key in data.keys():
            if isinstance(data[key], dict):
                print(key)
    else:
        # Default: print flattened
        for key, value in flatten_toml(data):
            print(f"{key} = {value}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
