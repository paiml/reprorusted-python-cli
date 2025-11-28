#!/usr/bin/env python3
"""Environment Variable Manager CLI.

Manage environment variables with validation and type conversion.
"""

import argparse
import os
import sys
from dataclasses import dataclass
from enum import Enum, auto


class VarType(Enum):
    """Environment variable types."""

    STRING = auto()
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    LIST = auto()
    PATH = auto()


@dataclass
class EnvVar:
    """Environment variable definition."""

    name: str
    var_type: VarType
    default: str | None = None
    required: bool = False
    description: str = ""


@dataclass
class ValidationError:
    """Validation error."""

    name: str
    message: str


def parse_bool(value: str) -> bool:
    """Parse boolean from string."""
    lower = value.lower()
    if lower in ("true", "1", "yes", "on", "y"):
        return True
    if lower in ("false", "0", "no", "off", "n"):
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def parse_list(value: str, separator: str = ",") -> list[str]:
    """Parse list from string."""
    if not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]


def convert_value(value: str, var_type: VarType) -> any:
    """Convert string value to target type."""
    if var_type == VarType.STRING:
        return value
    if var_type == VarType.INT:
        return int(value)
    if var_type == VarType.FLOAT:
        return float(value)
    if var_type == VarType.BOOL:
        return parse_bool(value)
    if var_type == VarType.LIST:
        return parse_list(value)
    if var_type == VarType.PATH:
        return os.path.expanduser(os.path.expandvars(value))
    return value


def get_env(name: str, var_type: VarType = VarType.STRING, default: str | None = None) -> any:
    """Get environment variable with type conversion."""
    value = os.environ.get(name)
    if value is None:
        if default is not None:
            value = default
        else:
            return None

    return convert_value(value, var_type)


def set_env(name: str, value: any) -> None:
    """Set environment variable."""
    if isinstance(value, bool):
        os.environ[name] = "true" if value else "false"
    elif isinstance(value, list):
        os.environ[name] = ",".join(str(v) for v in value)
    else:
        os.environ[name] = str(value)


def unset_env(name: str) -> bool:
    """Unset environment variable. Returns True if was set."""
    if name in os.environ:
        del os.environ[name]
        return True
    return False


def list_env(prefix: str = "") -> dict[str, str]:
    """List environment variables with optional prefix filter."""
    result = {}
    for name, value in os.environ.items():
        if not prefix or name.startswith(prefix):
            result[name] = value
    return result


def validate_schema(schema: list[EnvVar]) -> list[ValidationError]:
    """Validate environment variables against schema."""
    errors = []

    for var in schema:
        value = os.environ.get(var.name)

        if value is None:
            if var.required:
                errors.append(
                    ValidationError(var.name, f"Required variable '{var.name}' is not set")
                )
            continue

        try:
            convert_value(value, var.var_type)
        except ValueError as e:
            errors.append(ValidationError(var.name, f"Invalid value for '{var.name}': {e}"))

    return errors


def parse_schema_line(line: str) -> EnvVar | None:
    """Parse schema line: NAME:type[:default][:required][:description]"""
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = line.split(":", 4)
    if len(parts) < 2:
        return None

    name = parts[0].strip()
    type_str = parts[1].strip().upper()

    type_map = {
        "STRING": VarType.STRING,
        "STR": VarType.STRING,
        "INT": VarType.INT,
        "INTEGER": VarType.INT,
        "FLOAT": VarType.FLOAT,
        "BOOL": VarType.BOOL,
        "BOOLEAN": VarType.BOOL,
        "LIST": VarType.LIST,
        "PATH": VarType.PATH,
    }

    var_type = type_map.get(type_str, VarType.STRING)
    default = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
    required = len(parts) > 3 and parts[3].strip().lower() in ("true", "required", "yes", "1")
    description = parts[4].strip() if len(parts) > 4 else ""

    return EnvVar(name, var_type, default, required, description)


def parse_schema(content: str) -> list[EnvVar]:
    """Parse schema from string content."""
    schema = []
    for line in content.split("\n"):
        var = parse_schema_line(line)
        if var:
            schema.append(var)
    return schema


def interpolate(value: str, env: dict[str, str] | None = None) -> str:
    """Interpolate environment variables in string.

    Supports ${VAR} and $VAR syntax.
    """
    if env is None:
        env = dict(os.environ)

    result = []
    i = 0

    while i < len(value):
        if value[i] == "$":
            if i + 1 < len(value) and value[i + 1] == "{":
                # ${VAR} syntax
                end = value.find("}", i + 2)
                if end != -1:
                    var_name = value[i + 2 : end]
                    default = None
                    if ":-" in var_name:
                        var_name, default = var_name.split(":-", 1)
                    var_value = env.get(var_name, default or "")
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


def format_env_export(env: dict[str, str]) -> str:
    """Format environment as export statements."""
    lines = []
    for name, value in sorted(env.items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'export {name}="{escaped}"')
    return "\n".join(lines)


def format_env_json(env: dict[str, str]) -> str:
    """Format environment as JSON."""
    import json

    return json.dumps(env, indent=2, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Environment variable manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # get command
    get_parser = subparsers.add_parser("get", help="Get variable")
    get_parser.add_argument("name", help="Variable name")
    get_parser.add_argument(
        "--type", "-t", choices=["string", "int", "float", "bool", "list", "path"], default="string"
    )
    get_parser.add_argument("--default", "-d", help="Default value")

    # set command
    set_parser = subparsers.add_parser("set", help="Set variable")
    set_parser.add_argument("name", help="Variable name")
    set_parser.add_argument("value", help="Variable value")

    # unset command
    unset_parser = subparsers.add_parser("unset", help="Unset variable")
    unset_parser.add_argument("name", help="Variable name")

    # list command
    list_parser = subparsers.add_parser("list", help="List variables")
    list_parser.add_argument("--prefix", "-p", default="", help="Filter by prefix")
    list_parser.add_argument("--format", "-f", choices=["plain", "export", "json"], default="plain")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate against schema")
    validate_parser.add_argument("schema", help="Schema file or inline schema")

    # interpolate command
    interp_parser = subparsers.add_parser("interpolate", help="Interpolate variables in text")
    interp_parser.add_argument("text", nargs="?", help="Text to interpolate")

    args = parser.parse_args()

    if args.command == "get":
        type_map = {
            "string": VarType.STRING,
            "int": VarType.INT,
            "float": VarType.FLOAT,
            "bool": VarType.BOOL,
            "list": VarType.LIST,
            "path": VarType.PATH,
        }
        value = get_env(args.name, type_map[args.type], args.default)
        if value is None:
            print(f"Variable {args.name} not set", file=sys.stderr)
            return 1
        if isinstance(value, list):
            for item in value:
                print(item)
        else:
            print(value)
        return 0

    if args.command == "set":
        set_env(args.name, args.value)
        print(f"{args.name}={args.value}")
        return 0

    if args.command == "unset":
        if unset_env(args.name):
            print(f"Unset {args.name}")
        else:
            print(f"{args.name} was not set")
        return 0

    if args.command == "list":
        env = list_env(args.prefix)
        if args.format == "export":
            print(format_env_export(env))
        elif args.format == "json":
            print(format_env_json(env))
        else:
            for name, value in sorted(env.items()):
                print(f"{name}={value}")
        return 0

    if args.command == "validate":
        if os.path.isfile(args.schema):
            with open(args.schema) as f:
                content = f.read()
        else:
            content = args.schema

        schema = parse_schema(content)
        errors = validate_schema(schema)

        if errors:
            for error in errors:
                print(f"Error: {error.message}", file=sys.stderr)
            return 1

        print("Validation passed")
        return 0

    if args.command == "interpolate":
        if args.text:
            text = args.text
        else:
            text = sys.stdin.read()

        result = interpolate(text)
        print(result)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
