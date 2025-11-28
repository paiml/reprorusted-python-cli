#!/usr/bin/env python3
"""Settings Loader CLI.

Load settings from various file formats (INI, JSON, TOML-like).
"""

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum, auto


class FileFormat(Enum):
    """Settings file formats."""

    JSON = auto()
    INI = auto()
    TOML = auto()
    PROPERTIES = auto()


@dataclass
class ParseError:
    """Parsing error."""

    line: int
    message: str


def detect_format(filename: str) -> FileFormat:
    """Detect file format from extension."""
    lower = filename.lower()
    if lower.endswith(".json"):
        return FileFormat.JSON
    if lower.endswith(".ini") or lower.endswith(".cfg"):
        return FileFormat.INI
    if lower.endswith(".toml"):
        return FileFormat.TOML
    if lower.endswith(".properties"):
        return FileFormat.PROPERTIES
    return FileFormat.INI  # Default


def parse_json(content: str) -> tuple[dict, list[ParseError]]:
    """Parse JSON content."""
    try:
        return json.loads(content), []
    except json.JSONDecodeError as e:
        return {}, [ParseError(e.lineno, str(e))]


def parse_ini(content: str) -> tuple[dict, list[ParseError]]:
    """Parse INI content."""
    result = {}
    errors = []
    current_section = None

    for line_num, line in enumerate(content.split("\n"), 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#") or line.startswith(";"):
            continue

        # Section header
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            if section_name:
                current_section = section_name
                if section_name not in result:
                    result[section_name] = {}
            else:
                errors.append(ParseError(line_num, "Empty section name"))
            continue

        # Key-value pair
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]

            # Type conversion
            value = convert_ini_value(value)

            if current_section:
                result[current_section][key] = value
            else:
                result[key] = value
        else:
            errors.append(ParseError(line_num, f"Invalid line: {line}"))

    return result, errors


def convert_ini_value(value: str) -> any:
    """Convert INI string value to appropriate type."""
    # Boolean
    if value.lower() in ("true", "yes", "on", "1"):
        return True
    if value.lower() in ("false", "no", "off", "0"):
        return False

    # Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Float
    try:
        return float(value)
    except ValueError:
        pass

    # List (comma-separated)
    if "," in value:
        return [v.strip() for v in value.split(",")]

    return value


def parse_toml(content: str) -> tuple[dict, list[ParseError]]:
    """Parse simple TOML-like content."""
    result = {}
    errors = []
    current_section = result

    for line_num, line in enumerate(content.split("\n"), 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Table header
        if line.startswith("["):
            if line.startswith("[[") and line.endswith("]]"):
                # Array of tables
                section_name = line[2:-2].strip()
                parts = section_name.split(".")

                # Navigate to parent
                parent = result
                for part in parts[:-1]:
                    if part not in parent:
                        parent[part] = {}
                    parent = parent[part]

                # Create array entry
                if parts[-1] not in parent:
                    parent[parts[-1]] = []
                parent[parts[-1]].append({})
                current_section = parent[parts[-1]][-1]
            elif line.endswith("]"):
                # Regular table
                section_name = line[1:-1].strip()
                parts = section_name.split(".")

                # Navigate/create nested sections
                current = result
                for part in parts:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current_section = current
            continue

        # Key-value pair
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            parsed_value = parse_toml_value(value)
            current_section[key] = parsed_value
        else:
            errors.append(ParseError(line_num, f"Invalid line: {line}"))

    return result, errors


def parse_toml_value(value: str) -> any:
    """Parse TOML value."""
    value = value.strip()

    # String (basic)
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"')

    # String (literal)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]

    # Boolean
    if value == "true":
        return True
    if value == "false":
        return False

    # Array
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        items = []
        for item in split_array_items(inner):
            items.append(parse_toml_value(item.strip()))
        return items

    # Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Float
    try:
        return float(value)
    except ValueError:
        pass

    return value


def split_array_items(s: str) -> list[str]:
    """Split array items respecting nested brackets and quotes."""
    items = []
    current = []
    depth = 0
    in_string = False
    string_char = None

    for char in s:
        if char in ('"', "'") and not in_string:
            in_string = True
            string_char = char
        elif char == string_char and in_string:
            in_string = False
            string_char = None
        elif char == "[" and not in_string:
            depth += 1
        elif char == "]" and not in_string:
            depth -= 1
        elif char == "," and depth == 0 and not in_string:
            items.append("".join(current))
            current = []
            continue

        current.append(char)

    if current:
        items.append("".join(current))

    return items


def parse_properties(content: str) -> tuple[dict, list[ParseError]]:
    """Parse Java properties format."""
    result = {}
    errors = []

    for _line_num, line in enumerate(content.split("\n"), 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#") or line.startswith("!"):
            continue

        # Find separator (= or :)
        sep_idx = -1
        for i, char in enumerate(line):
            if char == "\\":
                continue  # Skip escaped chars
            if char in ("=", ":"):
                sep_idx = i
                break

        if sep_idx > 0:
            key = line[:sep_idx].strip()
            value = line[sep_idx + 1 :].strip()
            result[key] = convert_ini_value(value)
        else:
            # Key without value
            result[line] = ""

    return result, errors


def load(content: str, file_format: FileFormat) -> tuple[dict, list[ParseError]]:
    """Load settings from content."""
    if file_format == FileFormat.JSON:
        return parse_json(content)
    if file_format == FileFormat.INI:
        return parse_ini(content)
    if file_format == FileFormat.TOML:
        return parse_toml(content)
    if file_format == FileFormat.PROPERTIES:
        return parse_properties(content)
    return {}, [ParseError(0, f"Unknown format: {file_format}")]


def dump_json(settings: dict) -> str:
    """Dump settings to JSON."""
    return json.dumps(settings, indent=2)


def dump_ini(settings: dict, section: str = "") -> str:
    """Dump settings to INI format."""
    lines = []

    # Top-level values
    for key, value in settings.items():
        if not isinstance(value, dict):
            if isinstance(value, bool):
                lines.append(f"{key} = {'true' if value else 'false'}")
            elif isinstance(value, list):
                lines.append(f"{key} = {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"{key} = {value}")

    # Sections
    for key, value in settings.items():
        if isinstance(value, dict):
            section_name = f"{section}.{key}" if section else key
            lines.append(f"\n[{section_name}]")
            for k, v in value.items():
                if isinstance(v, dict):
                    lines.append(dump_ini({k: v}, section_name))
                else:
                    if isinstance(v, bool):
                        lines.append(f"{k} = {'true' if v else 'false'}")
                    elif isinstance(v, list):
                        lines.append(f"{k} = {', '.join(str(x) for x in v)}")
                    else:
                        lines.append(f"{k} = {v}")

    return "\n".join(lines)


def dump_toml(settings: dict, prefix: str = "") -> str:
    """Dump settings to TOML format."""
    lines = []
    sections = []

    for key, value in settings.items():
        if isinstance(value, dict):
            sections.append((key, value))
        elif isinstance(value, list):
            formatted = ", ".join(format_toml_value(v) for v in value)
            lines.append(f"{key} = [{formatted}]")
        else:
            lines.append(f"{key} = {format_toml_value(value)}")

    for section_name, section_value in sections:
        full_name = f"{prefix}.{section_name}" if prefix else section_name
        lines.append(f"\n[{full_name}]")
        lines.append(dump_toml(section_value, full_name))

    return "\n".join(lines)


def format_toml_value(value: any) -> str:
    """Format value for TOML output."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, (int, float)):
        return str(value)
    return str(value)


def get_value(settings: dict, path: str) -> any:
    """Get value by dot-notation path."""
    parts = path.split(".")
    current = settings

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None

    return current


def set_value(settings: dict, path: str, value: any) -> dict:
    """Set value by dot-notation path."""
    parts = path.split(".")
    current = settings

    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value
    return settings


def merge_settings(base: dict, override: dict) -> dict:
    """Deep merge settings."""
    result = dict(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_settings(result[key], value)
        else:
            result[key] = value

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Settings loader")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # load command
    load_parser = subparsers.add_parser("load", help="Load settings file")
    load_parser.add_argument("file", help="Settings file")
    load_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "ini", "toml", "properties"],
        help="File format (auto-detected)",
    )
    load_parser.add_argument(
        "--output", "-o", choices=["json", "ini", "toml"], default="json", help="Output format"
    )

    # get command
    get_parser = subparsers.add_parser("get", help="Get value by path")
    get_parser.add_argument("file", help="Settings file")
    get_parser.add_argument("path", help="Dot-notation path")

    # set command
    set_parser = subparsers.add_parser("set", help="Set value by path")
    set_parser.add_argument("file", help="Settings file")
    set_parser.add_argument("path", help="Dot-notation path")
    set_parser.add_argument("value", help="Value to set")

    # merge command
    merge_parser = subparsers.add_parser("merge", help="Merge multiple settings files")
    merge_parser.add_argument("files", nargs="+", help="Settings files to merge")
    merge_parser.add_argument(
        "--output", "-o", choices=["json", "ini", "toml"], default="json", help="Output format"
    )

    # convert command
    convert_parser = subparsers.add_parser("convert", help="Convert between formats")
    convert_parser.add_argument("input", help="Input file")
    convert_parser.add_argument(
        "--to", "-t", required=True, choices=["json", "ini", "toml"], help="Target format"
    )

    args = parser.parse_args()

    format_map = {
        "json": FileFormat.JSON,
        "ini": FileFormat.INI,
        "toml": FileFormat.TOML,
        "properties": FileFormat.PROPERTIES,
    }

    if args.command == "load":
        with open(args.file) as f:
            content = f.read()

        file_format = format_map.get(args.format) if args.format else detect_format(args.file)
        settings, errors = load(content, file_format)

        if errors:
            for err in errors:
                print(f"Line {err.line}: {err.message}", file=sys.stderr)
            return 1

        if args.output == "json":
            print(dump_json(settings))
        elif args.output == "ini":
            print(dump_ini(settings))
        elif args.output == "toml":
            print(dump_toml(settings))

        return 0

    if args.command == "get":
        with open(args.file) as f:
            content = f.read()

        file_format = detect_format(args.file)
        settings, errors = load(content, file_format)

        if errors:
            for err in errors:
                print(f"Line {err.line}: {err.message}", file=sys.stderr)
            return 1

        value = get_value(settings, args.path)
        if value is None:
            print(f"Path '{args.path}' not found", file=sys.stderr)
            return 1

        if isinstance(value, dict):
            print(dump_json(value))
        else:
            print(value)
        return 0

    if args.command == "set":
        with open(args.file) as f:
            content = f.read()

        file_format = detect_format(args.file)
        settings, errors = load(content, file_format)

        if errors:
            for err in errors:
                print(f"Line {err.line}: {err.message}", file=sys.stderr)
            return 1

        # Convert value
        value = convert_ini_value(args.value)
        settings = set_value(settings, args.path, value)

        print(dump_json(settings))
        return 0

    if args.command == "merge":
        result = {}
        for file_path in args.files:
            with open(file_path) as f:
                content = f.read()

            file_format = detect_format(file_path)
            settings, errors = load(content, file_format)

            if errors:
                for err in errors:
                    print(f"{file_path} line {err.line}: {err.message}", file=sys.stderr)
                return 1

            result = merge_settings(result, settings)

        if args.output == "json":
            print(dump_json(result))
        elif args.output == "ini":
            print(dump_ini(result))
        elif args.output == "toml":
            print(dump_toml(result))

        return 0

    if args.command == "convert":
        with open(args.input) as f:
            content = f.read()

        file_format = detect_format(args.input)
        settings, errors = load(content, file_format)

        if errors:
            for err in errors:
                print(f"Line {err.line}: {err.message}", file=sys.stderr)
            return 1

        if args.to == "json":
            print(dump_json(settings))
        elif args.to == "ini":
            print(dump_ini(settings))
        elif args.to == "toml":
            print(dump_toml(settings))

        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
