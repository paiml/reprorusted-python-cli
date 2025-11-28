#!/usr/bin/env python3
"""INI file parser CLI.

Parse, query, and modify INI configuration files.
"""

import argparse
import sys


def parse_ini(content: str) -> dict:
    """Parse INI content into nested dict."""
    result: dict = {}
    current_section = ""

    for line in content.split("\n"):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#") or line.startswith(";"):
            continue

        # Section header
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            if current_section not in result:
                result[current_section] = {}
            continue

        # Key=value pair
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            if current_section:
                result[current_section][key] = value
            else:
                # Global section (no header)
                if "" not in result:
                    result[""] = {}
                result[""][key] = value

    return result


def format_ini(data: dict) -> str:
    """Format dict back to INI format."""
    lines = []

    # Global section first (if any)
    if "" in data:
        for key, value in data[""].items():
            lines.append(f"{key} = {value}")
        if data[""]:
            lines.append("")

    # Named sections
    for section, values in data.items():
        if section == "":
            continue
        lines.append(f"[{section}]")
        for key, value in values.items():
            lines.append(f"{key} = {value}")
        lines.append("")

    return "\n".join(lines)


def get_value(data: dict, section: str, key: str) -> str:
    """Get a value from parsed INI data."""
    if section not in data:
        return ""
    if key not in data[section]:
        return ""
    return data[section][key]


def set_value(data: dict, section: str, key: str, value: str) -> dict:
    """Set a value in parsed INI data."""
    if section not in data:
        data[section] = {}
    data[section][key] = value
    return data


def list_sections(data: dict) -> list:
    """List all sections in INI data."""
    return [s for s in data.keys() if s != ""]


def list_keys(data: dict, section: str) -> list:
    """List all keys in a section."""
    if section not in data:
        return []
    return list(data[section].keys())


def main() -> int:
    parser = argparse.ArgumentParser(description="INI file parser and editor")
    parser.add_argument("input", nargs="?", help="Input INI file (- for stdin)")
    parser.add_argument("--get", metavar="SECTION.KEY", help="Get a specific value")
    parser.add_argument("--set", metavar="SECTION.KEY=VALUE", help="Set a value")
    parser.add_argument("--sections", action="store_true", help="List all sections")
    parser.add_argument("--keys", metavar="SECTION", help="List keys in a section")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    # Read input
    if args.input is None or args.input == "-":
        content = sys.stdin.read()
    else:
        with open(args.input) as f:
            content = f.read()

    data = parse_ini(content)

    # Perform operation
    if args.get:
        if "." in args.get:
            section, key = args.get.split(".", 1)
        else:
            section, key = "", args.get
        value = get_value(data, section, key)
        print(value)
    elif args.set:
        if "=" not in args.set:
            print("Error: --set requires SECTION.KEY=VALUE format", file=sys.stderr)
            return 1
        path, value = args.set.split("=", 1)
        if "." in path:
            section, key = path.split(".", 1)
        else:
            section, key = "", path
        data = set_value(data, section, key, value)
        output = format_ini(data)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
    elif args.sections:
        for section in list_sections(data):
            print(section)
    elif args.keys:
        for key in list_keys(data, args.keys):
            print(key)
    else:
        # Default: pretty print
        output = format_ini(data)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
