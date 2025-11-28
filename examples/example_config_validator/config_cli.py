#!/usr/bin/env python3
"""Configuration Validator CLI.

Validate configuration dictionaries against rules.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum, auto


class RuleType(Enum):
    """Validation rule types."""

    REQUIRED = auto()
    TYPE = auto()
    MIN = auto()
    MAX = auto()
    MIN_LENGTH = auto()
    MAX_LENGTH = auto()
    PATTERN = auto()
    ENUM = auto()
    CUSTOM = auto()


class ValueType(Enum):
    """Configuration value types."""

    STRING = auto()
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    LIST = auto()
    DICT = auto()
    ANY = auto()


@dataclass
class Rule:
    """Validation rule."""

    rule_type: RuleType
    value: any = None


@dataclass
class FieldSchema:
    """Field schema definition."""

    name: str
    value_type: ValueType = ValueType.ANY
    rules: list[Rule] = field(default_factory=list)
    nested: dict[str, "FieldSchema"] | None = None


@dataclass
class ValidationError:
    """Validation error."""

    path: str
    message: str
    rule_type: RuleType | None = None


def get_value_type(value: any) -> ValueType:
    """Get ValueType for a Python value."""
    if isinstance(value, bool):
        return ValueType.BOOL
    if isinstance(value, int):
        return ValueType.INT
    if isinstance(value, float):
        return ValueType.FLOAT
    if isinstance(value, str):
        return ValueType.STRING
    if isinstance(value, list):
        return ValueType.LIST
    if isinstance(value, dict):
        return ValueType.DICT
    return ValueType.ANY


def type_matches(value: any, expected: ValueType) -> bool:
    """Check if value matches expected type."""
    if expected == ValueType.ANY:
        return True

    actual = get_value_type(value)

    # Allow int for float
    if expected == ValueType.FLOAT and actual == ValueType.INT:
        return True

    return actual == expected


def validate_field(value: any, schema: FieldSchema, path: str) -> list[ValidationError]:
    """Validate a field against its schema."""
    errors = []

    for rule in schema.rules:
        if rule.rule_type == RuleType.REQUIRED:
            if value is None:
                errors.append(
                    ValidationError(path, f"Field '{path}' is required", RuleType.REQUIRED)
                )
                return errors

        if value is None:
            continue

        if rule.rule_type == RuleType.TYPE:
            if not type_matches(value, schema.value_type):
                errors.append(
                    ValidationError(
                        path,
                        f"Expected {schema.value_type.name.lower()}, got {get_value_type(value).name.lower()}",
                        RuleType.TYPE,
                    )
                )

        elif rule.rule_type == RuleType.MIN:
            if isinstance(value, (int, float)) and value < rule.value:
                errors.append(
                    ValidationError(
                        path, f"Value {value} is less than minimum {rule.value}", RuleType.MIN
                    )
                )

        elif rule.rule_type == RuleType.MAX:
            if isinstance(value, (int, float)) and value > rule.value:
                errors.append(
                    ValidationError(
                        path, f"Value {value} is greater than maximum {rule.value}", RuleType.MAX
                    )
                )

        elif rule.rule_type == RuleType.MIN_LENGTH:
            if hasattr(value, "__len__") and len(value) < rule.value:
                errors.append(
                    ValidationError(
                        path,
                        f"Length {len(value)} is less than minimum {rule.value}",
                        RuleType.MIN_LENGTH,
                    )
                )

        elif rule.rule_type == RuleType.MAX_LENGTH:
            if hasattr(value, "__len__") and len(value) > rule.value:
                errors.append(
                    ValidationError(
                        path,
                        f"Length {len(value)} is greater than maximum {rule.value}",
                        RuleType.MAX_LENGTH,
                    )
                )

        elif rule.rule_type == RuleType.PATTERN:
            import re

            if isinstance(value, str) and not re.match(rule.value, value):
                errors.append(
                    ValidationError(
                        path, f"Value does not match pattern '{rule.value}'", RuleType.PATTERN
                    )
                )

        elif rule.rule_type == RuleType.ENUM:
            if value not in rule.value:
                errors.append(
                    ValidationError(path, f"Value must be one of: {rule.value}", RuleType.ENUM)
                )

    # Validate nested fields
    if schema.nested and isinstance(value, dict):
        for field_name, field_schema in schema.nested.items():
            field_value = value.get(field_name)
            field_path = f"{path}.{field_name}" if path else field_name
            errors.extend(validate_field(field_value, field_schema, field_path))

    return errors


def validate(config: dict, schema: dict[str, FieldSchema]) -> list[ValidationError]:
    """Validate configuration against schema."""
    errors = []

    for field_name, field_schema in schema.items():
        value = config.get(field_name)
        errors.extend(validate_field(value, field_schema, field_name))

    return errors


def create_field(
    value_type: ValueType = ValueType.ANY,
    required: bool = False,
    min_val: float | None = None,
    max_val: float | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | None = None,
    enum: list | None = None,
    nested: dict[str, "FieldSchema"] | None = None,
) -> FieldSchema:
    """Create a field schema with rules."""
    rules = []

    if required:
        rules.append(Rule(RuleType.REQUIRED))

    rules.append(Rule(RuleType.TYPE))

    if min_val is not None:
        rules.append(Rule(RuleType.MIN, min_val))
    if max_val is not None:
        rules.append(Rule(RuleType.MAX, max_val))
    if min_length is not None:
        rules.append(Rule(RuleType.MIN_LENGTH, min_length))
    if max_length is not None:
        rules.append(Rule(RuleType.MAX_LENGTH, max_length))
    if pattern is not None:
        rules.append(Rule(RuleType.PATTERN, pattern))
    if enum is not None:
        rules.append(Rule(RuleType.ENUM, enum))

    return FieldSchema("", value_type, rules, nested)


def parse_type(type_str: str) -> ValueType:
    """Parse type string to ValueType."""
    type_map = {
        "string": ValueType.STRING,
        "str": ValueType.STRING,
        "int": ValueType.INT,
        "integer": ValueType.INT,
        "float": ValueType.FLOAT,
        "number": ValueType.FLOAT,
        "bool": ValueType.BOOL,
        "boolean": ValueType.BOOL,
        "list": ValueType.LIST,
        "array": ValueType.LIST,
        "dict": ValueType.DICT,
        "object": ValueType.DICT,
        "any": ValueType.ANY,
    }
    return type_map.get(type_str.lower(), ValueType.ANY)


def parse_schema_dict(schema_dict: dict) -> dict[str, FieldSchema]:
    """Parse schema from dictionary."""
    result = {}

    for field_name, field_def in schema_dict.items():
        if isinstance(field_def, str):
            # Simple type definition
            result[field_name] = create_field(parse_type(field_def))
        elif isinstance(field_def, dict):
            # Complex definition
            value_type = parse_type(field_def.get("type", "any"))
            required = field_def.get("required", False)
            min_val = field_def.get("min")
            max_val = field_def.get("max")
            min_length = field_def.get("minLength")
            max_length = field_def.get("maxLength")
            pattern = field_def.get("pattern")
            enum = field_def.get("enum")

            nested = None
            if "properties" in field_def:
                nested = parse_schema_dict(field_def["properties"])

            field_schema = create_field(
                value_type,
                required,
                min_val,
                max_val,
                min_length,
                max_length,
                pattern,
                enum,
                nested,
            )
            field_schema.name = field_name
            result[field_name] = field_schema

    return result


def merge_configs(base: dict, override: dict) -> dict:
    """Deep merge two configurations."""
    result = dict(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def flatten_config(config: dict, prefix: str = "") -> dict[str, any]:
    """Flatten nested config to dot notation."""
    result = {}

    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            result.update(flatten_config(value, full_key))
        else:
            result[full_key] = value

    return result


def unflatten_config(flat: dict[str, any]) -> dict:
    """Unflatten dot notation to nested dict."""
    result = {}

    for key, value in flat.items():
        parts = key.split(".")
        current = result

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    return result


def diff_configs(config1: dict, config2: dict) -> dict:
    """Find differences between two configurations."""
    flat1 = flatten_config(config1)
    flat2 = flatten_config(config2)

    all_keys = set(flat1.keys()) | set(flat2.keys())

    diff = {"added": {}, "removed": {}, "changed": {}}

    for key in all_keys:
        if key not in flat1:
            diff["added"][key] = flat2[key]
        elif key not in flat2:
            diff["removed"][key] = flat1[key]
        elif flat1[key] != flat2[key]:
            diff["changed"][key] = {"from": flat1[key], "to": flat2[key]}

    return diff


def main() -> int:
    parser = argparse.ArgumentParser(description="Configuration validator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate config against schema")
    validate_parser.add_argument("config", help="Config file (JSON)")
    validate_parser.add_argument("--schema", "-s", required=True, help="Schema file (JSON)")

    # merge command
    merge_parser = subparsers.add_parser("merge", help="Merge configurations")
    merge_parser.add_argument("base", help="Base config file")
    merge_parser.add_argument("override", help="Override config file")

    # flatten command
    flatten_parser = subparsers.add_parser("flatten", help="Flatten config to dot notation")
    flatten_parser.add_argument("config", help="Config file")

    # unflatten command
    unflatten_parser = subparsers.add_parser("unflatten", help="Unflatten dot notation config")
    unflatten_parser.add_argument("config", help="Flat config file")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Diff two configurations")
    diff_parser.add_argument("config1", help="First config file")
    diff_parser.add_argument("config2", help="Second config file")

    args = parser.parse_args()

    if args.command == "validate":
        with open(args.config) as f:
            config = json.load(f)
        with open(args.schema) as f:
            schema_dict = json.load(f)

        schema = parse_schema_dict(schema_dict)
        errors = validate(config, schema)

        if errors:
            for error in errors:
                print(f"Error at '{error.path}': {error.message}", file=sys.stderr)
            return 1

        print("Configuration is valid")
        return 0

    if args.command == "merge":
        with open(args.base) as f:
            base = json.load(f)
        with open(args.override) as f:
            override = json.load(f)

        result = merge_configs(base, override)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "flatten":
        with open(args.config) as f:
            config = json.load(f)

        flat = flatten_config(config)
        print(json.dumps(flat, indent=2))
        return 0

    if args.command == "unflatten":
        with open(args.config) as f:
            flat = json.load(f)

        config = unflatten_config(flat)
        print(json.dumps(config, indent=2))
        return 0

    if args.command == "diff":
        with open(args.config1) as f:
            config1 = json.load(f)
        with open(args.config2) as f:
            config2 = json.load(f)

        diff = diff_configs(config1, config2)
        print(json.dumps(diff, indent=2))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
