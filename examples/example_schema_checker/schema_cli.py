#!/usr/bin/env python3
"""Schema Checker CLI.

JSON Schema-like validation for data structures.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum, auto


class SchemaType(Enum):
    """Schema types."""

    STRING = auto()
    INTEGER = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    ARRAY = auto()
    OBJECT = auto()
    NULL = auto()
    ANY = auto()


@dataclass
class SchemaError:
    """Schema validation error."""

    path: str
    message: str


@dataclass
class Schema:
    """Schema definition."""

    schema_type: SchemaType | list[SchemaType] = SchemaType.ANY
    properties: dict[str, "Schema"] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)
    items: "Schema | None" = None
    minimum: float | None = None
    maximum: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_items: int | None = None
    max_items: int | None = None
    pattern: str | None = None
    enum: list = field(default_factory=list)
    const: any = None
    additional_properties: bool = True
    unique_items: bool = False


def get_type(value: any) -> SchemaType:
    """Get schema type for a value."""
    if value is None:
        return SchemaType.NULL
    if isinstance(value, bool):
        return SchemaType.BOOLEAN
    if isinstance(value, int):
        return SchemaType.INTEGER
    if isinstance(value, float):
        return SchemaType.NUMBER
    if isinstance(value, str):
        return SchemaType.STRING
    if isinstance(value, list):
        return SchemaType.ARRAY
    if isinstance(value, dict):
        return SchemaType.OBJECT
    return SchemaType.ANY


def type_name(t: SchemaType) -> str:
    """Get human-readable type name."""
    return t.name.lower()


def check_type(value: any, expected: SchemaType | list[SchemaType]) -> bool:
    """Check if value matches expected type(s)."""
    actual = get_type(value)

    if isinstance(expected, list):
        return actual in expected

    if expected == SchemaType.ANY:
        return True

    # Integer is valid number
    if expected == SchemaType.NUMBER and actual == SchemaType.INTEGER:
        return True

    return actual == expected


def validate(data: any, schema: Schema, path: str = "") -> list[SchemaError]:
    """Validate data against schema."""
    errors = []

    # Type check
    if not check_type(data, schema.schema_type):
        if isinstance(schema.schema_type, list):
            expected = " or ".join(type_name(t) for t in schema.schema_type)
        else:
            expected = type_name(schema.schema_type)
        actual = type_name(get_type(data))
        errors.append(SchemaError(path or "$", f"Expected {expected}, got {actual}"))
        return errors

    # Const check
    if schema.const is not None and data != schema.const:
        errors.append(SchemaError(path or "$", f"Value must be {schema.const!r}"))

    # Enum check
    if schema.enum and data not in schema.enum:
        errors.append(SchemaError(path or "$", f"Value must be one of: {schema.enum}"))

    # String validations
    if isinstance(data, str):
        if schema.min_length is not None and len(data) < schema.min_length:
            errors.append(
                SchemaError(
                    path or "$",
                    f"String length {len(data)} is less than minimum {schema.min_length}",
                )
            )
        if schema.max_length is not None and len(data) > schema.max_length:
            errors.append(
                SchemaError(
                    path or "$", f"String length {len(data)} exceeds maximum {schema.max_length}"
                )
            )
        if schema.pattern:
            import re

            if not re.match(schema.pattern, data):
                errors.append(
                    SchemaError(path or "$", f"String does not match pattern '{schema.pattern}'")
                )

    # Number validations
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if schema.minimum is not None and data < schema.minimum:
            errors.append(
                SchemaError(path or "$", f"Value {data} is less than minimum {schema.minimum}")
            )
        if schema.maximum is not None and data > schema.maximum:
            errors.append(
                SchemaError(path or "$", f"Value {data} exceeds maximum {schema.maximum}")
            )

    # Array validations
    if isinstance(data, list):
        if schema.min_items is not None and len(data) < schema.min_items:
            errors.append(
                SchemaError(
                    path or "$", f"Array length {len(data)} is less than minimum {schema.min_items}"
                )
            )
        if schema.max_items is not None and len(data) > schema.max_items:
            errors.append(
                SchemaError(
                    path or "$", f"Array length {len(data)} exceeds maximum {schema.max_items}"
                )
            )
        if schema.unique_items:
            seen = []
            for item in data:
                item_str = json.dumps(item, sort_keys=True)
                if item_str in seen:
                    errors.append(SchemaError(path or "$", "Array contains duplicate items"))
                    break
                seen.append(item_str)

        if schema.items:
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]" if path else f"[{i}]"
                errors.extend(validate(item, schema.items, item_path))

    # Object validations
    if isinstance(data, dict):
        # Required properties
        for prop in schema.required:
            if prop not in data:
                prop_path = f"{path}.{prop}" if path else prop
                errors.append(SchemaError(prop_path, f"Required property '{prop}' is missing"))

        # Property validations
        for prop, prop_schema in schema.properties.items():
            if prop in data:
                prop_path = f"{path}.{prop}" if path else prop
                errors.extend(validate(data[prop], prop_schema, prop_path))

        # Additional properties check
        if not schema.additional_properties:
            for prop in data:
                if prop not in schema.properties:
                    prop_path = f"{path}.{prop}" if path else prop
                    errors.append(
                        SchemaError(prop_path, f"Additional property '{prop}' is not allowed")
                    )

    return errors


def parse_type_str(type_str: str | list[str]) -> SchemaType | list[SchemaType]:
    """Parse type string to SchemaType."""
    type_map = {
        "string": SchemaType.STRING,
        "integer": SchemaType.INTEGER,
        "number": SchemaType.NUMBER,
        "boolean": SchemaType.BOOLEAN,
        "array": SchemaType.ARRAY,
        "object": SchemaType.OBJECT,
        "null": SchemaType.NULL,
    }

    if isinstance(type_str, list):
        return [type_map.get(t.lower(), SchemaType.ANY) for t in type_str]

    return type_map.get(type_str.lower(), SchemaType.ANY)


def parse_schema(schema_dict: dict) -> Schema:
    """Parse JSON Schema-like dict to Schema object."""
    schema = Schema()

    if "type" in schema_dict:
        schema.schema_type = parse_type_str(schema_dict["type"])

    if "properties" in schema_dict:
        schema.properties = {k: parse_schema(v) for k, v in schema_dict["properties"].items()}

    if "required" in schema_dict:
        schema.required = schema_dict["required"]

    if "items" in schema_dict:
        schema.items = parse_schema(schema_dict["items"])

    if "minimum" in schema_dict:
        schema.minimum = schema_dict["minimum"]
    if "maximum" in schema_dict:
        schema.maximum = schema_dict["maximum"]

    if "minLength" in schema_dict:
        schema.min_length = schema_dict["minLength"]
    if "maxLength" in schema_dict:
        schema.max_length = schema_dict["maxLength"]

    if "minItems" in schema_dict:
        schema.min_items = schema_dict["minItems"]
    if "maxItems" in schema_dict:
        schema.max_items = schema_dict["maxItems"]

    if "pattern" in schema_dict:
        schema.pattern = schema_dict["pattern"]

    if "enum" in schema_dict:
        schema.enum = schema_dict["enum"]

    if "const" in schema_dict:
        schema.const = schema_dict["const"]

    if "additionalProperties" in schema_dict:
        schema.additional_properties = schema_dict["additionalProperties"]

    if "uniqueItems" in schema_dict:
        schema.unique_items = schema_dict["uniqueItems"]

    return schema


def infer_schema(data: any, strict: bool = False) -> dict:
    """Infer schema from data."""
    if data is None:
        return {"type": "null"}

    if isinstance(data, bool):
        return {"type": "boolean"}

    if isinstance(data, int):
        return {"type": "integer"}

    if isinstance(data, float):
        return {"type": "number"}

    if isinstance(data, str):
        result = {"type": "string"}
        if strict:
            result["minLength"] = len(data)
            result["maxLength"] = len(data)
        return result

    if isinstance(data, list):
        result = {"type": "array"}
        if strict:
            result["minItems"] = len(data)
            result["maxItems"] = len(data)

        if data:
            # Try to find common item schema
            item_schemas = [infer_schema(item, strict) for item in data]
            if all(s == item_schemas[0] for s in item_schemas):
                result["items"] = item_schemas[0]
        return result

    if isinstance(data, dict):
        result = {"type": "object", "properties": {}}
        if strict:
            result["required"] = list(data.keys())
            result["additionalProperties"] = False

        for key, value in data.items():
            result["properties"][key] = infer_schema(value, strict)
        return result

    return {}


def generate_sample(schema: Schema) -> any:
    """Generate sample data from schema."""
    if schema.const is not None:
        return schema.const

    if schema.enum:
        return schema.enum[0]

    schema_type = schema.schema_type
    if isinstance(schema_type, list):
        schema_type = schema_type[0]

    if schema_type == SchemaType.NULL:
        return None

    if schema_type == SchemaType.BOOLEAN:
        return False

    if schema_type == SchemaType.INTEGER:
        if schema.minimum is not None:
            return int(schema.minimum)
        return 0

    if schema_type == SchemaType.NUMBER:
        if schema.minimum is not None:
            return schema.minimum
        return 0.0

    if schema_type == SchemaType.STRING:
        if schema.min_length:
            return "x" * schema.min_length
        return ""

    if schema_type == SchemaType.ARRAY:
        result = []
        count = schema.min_items or 0
        if schema.items:
            for _ in range(count):
                result.append(generate_sample(schema.items))
        return result

    if schema_type == SchemaType.OBJECT:
        result = {}
        for prop in schema.required:
            if prop in schema.properties:
                result[prop] = generate_sample(schema.properties[prop])
        return result

    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="JSON Schema checker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate data against schema")
    validate_parser.add_argument("data", help="Data file (JSON)")
    validate_parser.add_argument("--schema", "-s", required=True, help="Schema file (JSON)")

    # infer command
    infer_parser = subparsers.add_parser("infer", help="Infer schema from data")
    infer_parser.add_argument("data", help="Data file (JSON)")
    infer_parser.add_argument("--strict", action="store_true", help="Generate strict schema")

    # sample command
    sample_parser = subparsers.add_parser("sample", help="Generate sample data from schema")
    sample_parser.add_argument("schema", help="Schema file (JSON)")

    args = parser.parse_args()

    if args.command == "validate":
        with open(args.data) as f:
            data = json.load(f)
        with open(args.schema) as f:
            schema_dict = json.load(f)

        schema = parse_schema(schema_dict)
        errors = validate(data, schema)

        if errors:
            for error in errors:
                print(f"Error at '{error.path}': {error.message}", file=sys.stderr)
            return 1

        print("Validation passed")
        return 0

    if args.command == "infer":
        with open(args.data) as f:
            data = json.load(f)

        schema = infer_schema(data, args.strict)
        print(json.dumps(schema, indent=2))
        return 0

    if args.command == "sample":
        with open(args.schema) as f:
            schema_dict = json.load(f)

        schema = parse_schema(schema_dict)
        sample = generate_sample(schema)
        print(json.dumps(sample, indent=2))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
