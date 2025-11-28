#!/usr/bin/env python3
"""Dotenv Parser CLI.

Parse and manipulate .env files.
"""

import argparse
import os
import sys
from dataclasses import dataclass
from enum import Enum, auto


class QuoteStyle(Enum):
    """Quote styles for values."""

    NONE = auto()
    SINGLE = auto()
    DOUBLE = auto()


@dataclass
class EnvEntry:
    """Environment file entry."""

    key: str
    value: str
    quote_style: QuoteStyle = QuoteStyle.NONE
    comment: str = ""
    exported: bool = False


@dataclass
class ParseResult:
    """Parse result with entries and errors."""

    entries: list[EnvEntry]
    errors: list[tuple[int, str]]


def parse_value(value: str) -> tuple[str, QuoteStyle]:
    """Parse value and determine quote style."""
    value = value.strip()

    if not value:
        return "", QuoteStyle.NONE

    # Double quoted
    if value.startswith('"'):
        end = find_closing_quote(value, '"')
        if end > 0:
            inner = value[1:end]
            inner = process_escape_sequences(inner)
            return inner, QuoteStyle.DOUBLE
        return value[1:], QuoteStyle.DOUBLE

    # Single quoted (no escape processing)
    if value.startswith("'"):
        end = find_closing_quote(value, "'")
        if end > 0:
            return value[1:end], QuoteStyle.SINGLE
        return value[1:], QuoteStyle.SINGLE

    # Unquoted - strip inline comment
    comment_idx = value.find(" #")
    if comment_idx > 0:
        value = value[:comment_idx].strip()

    return value, QuoteStyle.NONE


def find_closing_quote(s: str, quote: str) -> int:
    """Find closing quote, respecting escapes for double quotes."""
    i = 1
    while i < len(s):
        if s[i] == quote:
            if quote == '"' and i > 0 and s[i - 1] == "\\":
                i += 1
                continue
            return i
        i += 1
    return -1


def process_escape_sequences(s: str) -> str:
    """Process escape sequences in double-quoted strings."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            next_char = s[i + 1]
            if next_char == "n":
                result.append("\n")
            elif next_char == "t":
                result.append("\t")
            elif next_char == "r":
                result.append("\r")
            elif next_char == '"':
                result.append('"')
            elif next_char == "\\":
                result.append("\\")
            elif next_char == "$":
                result.append("$")
            else:
                result.append(s[i : i + 2])
            i += 2
        else:
            result.append(s[i])
            i += 1
    return "".join(result)


def parse(content: str) -> ParseResult:
    """Parse .env content."""
    entries = []
    errors = []

    for line_num, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Comment line
        if stripped.startswith("#"):
            continue

        # Check for export prefix
        exported = False
        if stripped.startswith("export "):
            exported = True
            stripped = stripped[7:].strip()

        # Find = separator
        eq_idx = stripped.find("=")
        if eq_idx <= 0:
            errors.append((line_num, f"Invalid line: {line}"))
            continue

        key = stripped[:eq_idx].strip()
        value_part = stripped[eq_idx + 1 :]

        # Validate key
        if not is_valid_key(key):
            errors.append((line_num, f"Invalid key: {key}"))
            continue

        value, quote_style = parse_value(value_part)

        entries.append(EnvEntry(key=key, value=value, quote_style=quote_style, exported=exported))

    return ParseResult(entries=entries, errors=errors)


def is_valid_key(key: str) -> bool:
    """Check if key is valid."""
    if not key:
        return False
    if not (key[0].isalpha() or key[0] == "_"):
        return False
    return all(c.isalnum() or c == "_" for c in key)


def interpolate(value: str, env: dict[str, str]) -> str:
    """Interpolate variables in value."""
    result = []
    i = 0

    while i < len(value):
        if value[i] == "$":
            if i + 1 < len(value) and value[i + 1] == "{":
                # ${VAR} syntax
                end = value.find("}", i + 2)
                if end != -1:
                    var_expr = value[i + 2 : end]
                    var_value = resolve_var_expr(var_expr, env)
                    result.append(var_value)
                    i = end + 1
                    continue
            elif i + 1 < len(value) and (value[i + 1].isalpha() or value[i + 1] == "_"):
                # $VAR syntax
                j = i + 1
                while j < len(value) and (value[j].isalnum() or value[j] == "_"):
                    j += 1
                var_name = value[i + 1 : j]
                var_value = env.get(var_name, "")
                result.append(var_value)
                i = j
                continue

        result.append(value[i])
        i += 1

    return "".join(result)


def resolve_var_expr(expr: str, env: dict[str, str]) -> str:
    """Resolve variable expression with default value support."""
    # ${VAR:-default}
    if ":-" in expr:
        var_name, default = expr.split(":-", 1)
        return env.get(var_name, default)

    # ${VAR:=default} - set default
    if ":=" in expr:
        var_name, default = expr.split(":=", 1)
        if var_name not in env:
            env[var_name] = default
        return env.get(var_name, default)

    # ${VAR:?error}
    if ":?" in expr:
        var_name, error = expr.split(":?", 1)
        if var_name not in env:
            raise ValueError(error or f"Variable {var_name} is not set")
        return env[var_name]

    # ${VAR:+alt}
    if ":+" in expr:
        var_name, alt = expr.split(":+", 1)
        if var_name in env and env[var_name]:
            return alt
        return ""

    return env.get(expr, "")


def to_dict(entries: list[EnvEntry], interpolate_vars: bool = False) -> dict[str, str]:
    """Convert entries to dictionary."""
    result = {}

    for entry in entries:
        value = entry.value
        if interpolate_vars:
            value = interpolate(value, result)
        result[entry.key] = value

    return result


def format_value(value: str, quote_style: QuoteStyle) -> str:
    """Format value with appropriate quoting."""
    if quote_style == QuoteStyle.DOUBLE:
        escaped = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )
        return f'"{escaped}"'
    if quote_style == QuoteStyle.SINGLE:
        return f"'{value}'"

    # Unquoted - check if quoting needed
    if needs_quoting(value):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    return value


def needs_quoting(value: str) -> bool:
    """Check if value needs quoting."""
    if not value:
        return False
    if value[0].isspace() or value[-1].isspace():
        return True
    if any(c in value for c in " \t\n\r#'\"$`"):
        return True
    return False


def serialize(entries: list[EnvEntry]) -> str:
    """Serialize entries to .env format."""
    lines = []

    for entry in entries:
        prefix = "export " if entry.exported else ""
        value = format_value(entry.value, entry.quote_style)
        line = f"{prefix}{entry.key}={value}"

        if entry.comment:
            line += f"  # {entry.comment}"

        lines.append(line)

    return "\n".join(lines)


def merge(base: list[EnvEntry], override: list[EnvEntry]) -> list[EnvEntry]:
    """Merge two entry lists, override taking precedence."""
    result = {e.key: e for e in base}

    for entry in override:
        result[entry.key] = entry

    return list(result.values())


def diff(entries1: list[EnvEntry], entries2: list[EnvEntry]) -> dict:
    """Find differences between two entry lists."""
    dict1 = {e.key: e.value for e in entries1}
    dict2 = {e.key: e.value for e in entries2}

    all_keys = set(dict1.keys()) | set(dict2.keys())

    result = {"added": {}, "removed": {}, "changed": {}}

    for key in all_keys:
        if key not in dict1:
            result["added"][key] = dict2[key]
        elif key not in dict2:
            result["removed"][key] = dict1[key]
        elif dict1[key] != dict2[key]:
            result["changed"][key] = {"from": dict1[key], "to": dict2[key]}

    return result


def validate_entries(entries: list[EnvEntry]) -> list[str]:
    """Validate entries."""
    errors = []

    for entry in entries:
        if not is_valid_key(entry.key):
            errors.append(f"Invalid key: {entry.key}")

        # Check for common issues
        if entry.key.startswith("_"):
            # Warning - underscore prefix is valid but unusual
            pass

    return errors


def load_into_env(entries: list[EnvEntry], override: bool = False) -> None:
    """Load entries into os.environ."""
    for entry in entries:
        if override or entry.key not in os.environ:
            os.environ[entry.key] = entry.value


def main() -> int:
    parser = argparse.ArgumentParser(description="Dotenv parser")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # parse command
    parse_parser = subparsers.add_parser("parse", help="Parse .env file")
    parse_parser.add_argument("file", help=".env file")
    parse_parser.add_argument("--format", "-f", choices=["json", "shell", "env"], default="env")
    parse_parser.add_argument(
        "--interpolate", "-i", action="store_true", help="Interpolate variables"
    )

    # get command
    get_parser = subparsers.add_parser("get", help="Get value")
    get_parser.add_argument("file", help=".env file")
    get_parser.add_argument("key", help="Variable name")

    # set command
    set_parser = subparsers.add_parser("set", help="Set value")
    set_parser.add_argument("file", help=".env file")
    set_parser.add_argument("key", help="Variable name")
    set_parser.add_argument("value", help="Value")

    # merge command
    merge_parser = subparsers.add_parser("merge", help="Merge .env files")
    merge_parser.add_argument("files", nargs="+", help=".env files to merge")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Diff two .env files")
    diff_parser.add_argument("file1", help="First .env file")
    diff_parser.add_argument("file2", help="Second .env file")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate .env file")
    validate_parser.add_argument("file", help=".env file")

    args = parser.parse_args()

    if args.command == "parse":
        with open(args.file) as f:
            content = f.read()

        result = parse(content)

        if result.errors:
            for line_num, msg in result.errors:
                print(f"Line {line_num}: {msg}", file=sys.stderr)

        env_dict = to_dict(result.entries, args.interpolate)

        if args.format == "json":
            import json

            print(json.dumps(env_dict, indent=2))
        elif args.format == "shell":
            for key, value in env_dict.items():
                escaped = value.replace("'", "'\"'\"'")
                print(f"export {key}='{escaped}'")
        else:
            print(serialize(result.entries))

        return 0

    if args.command == "get":
        with open(args.file) as f:
            content = f.read()

        result = parse(content)
        env_dict = to_dict(result.entries)

        if args.key in env_dict:
            print(env_dict[args.key])
            return 0
        else:
            print(f"Key '{args.key}' not found", file=sys.stderr)
            return 1

    if args.command == "set":
        with open(args.file) as f:
            content = f.read()

        result = parse(content)

        # Find and update or add entry
        found = False
        for entry in result.entries:
            if entry.key == args.key:
                entry.value = args.value
                found = True
                break

        if not found:
            result.entries.append(EnvEntry(key=args.key, value=args.value))

        print(serialize(result.entries))
        return 0

    if args.command == "merge":
        merged = []
        for file_path in args.files:
            with open(file_path) as f:
                content = f.read()
            result = parse(content)
            merged = merge(merged, result.entries)

        print(serialize(merged))
        return 0

    if args.command == "diff":
        with open(args.file1) as f:
            content1 = f.read()
        with open(args.file2) as f:
            content2 = f.read()

        result1 = parse(content1)
        result2 = parse(content2)

        differences = diff(result1.entries, result2.entries)

        import json

        print(json.dumps(differences, indent=2))
        return 0

    if args.command == "validate":
        with open(args.file) as f:
            content = f.read()

        result = parse(content)

        if result.errors:
            for line_num, msg in result.errors:
                print(f"Line {line_num}: {msg}", file=sys.stderr)
            return 1

        errors = validate_entries(result.entries)
        if errors:
            for error in errors:
                print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"Valid: {len(result.entries)} entries")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
