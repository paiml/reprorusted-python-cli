#!/usr/bin/env python3
"""Typed Optional CLI.

Optional and Union type operations.
"""

import argparse
import sys
from typing import TypeVar

T = TypeVar("T")


def is_none(value: int | None) -> bool:
    """Check if value is None."""
    return value is None


def is_some(value: int | None) -> bool:
    """Check if value is not None."""
    return value is not None


def unwrap(value: int | None) -> int:
    """Unwrap optional value, raise if None."""
    if value is None:
        raise ValueError("Cannot unwrap None")
    return value


def unwrap_or(value: int | None, default: int) -> int:
    """Unwrap optional value or return default."""
    return value if value is not None else default


def unwrap_or_else(value: int | None, default_fn: callable) -> int:
    """Unwrap optional or call function for default."""
    return value if value is not None else default_fn()


def map_optional(value: int | None, fn: callable) -> int | None:
    """Map function over optional value."""
    return fn(value) if value is not None else None


def flat_map_optional(value: int | None, fn: callable) -> int | None:
    """Flat map function over optional value."""
    if value is None:
        return None
    return fn(value)


def filter_optional(value: int | None, predicate: callable) -> int | None:
    """Filter optional value by predicate."""
    if value is None:
        return None
    return value if predicate(value) else None


def and_then(value: int | None, fn: callable) -> int | None:
    """Chain optional operations."""
    if value is None:
        return None
    return fn(value)


def or_else(value: int | None, fn: callable) -> int | None:
    """Provide alternative if None."""
    if value is not None:
        return value
    return fn()


def zip_optional(a: int | None, b: int | None) -> tuple[int, int] | None:
    """Zip two optionals into optional tuple."""
    if a is None or b is None:
        return None
    return (a, b)


def first_some(*values: int | None) -> int | None:
    """Return first non-None value."""
    for v in values:
        if v is not None:
            return v
    return None


def all_some(*values: int | None) -> list[int] | None:
    """Return list if all values are Some, else None."""
    result = []
    for v in values:
        if v is None:
            return None
        result.append(v)
    return result


def any_some(*values: int | None) -> bool:
    """Check if any value is Some."""
    return any(v is not None for v in values)


def none_of(*values: int | None) -> bool:
    """Check if all values are None."""
    return all(v is None for v in values)


def count_some(*values: int | None) -> int:
    """Count non-None values."""
    return sum(1 for v in values if v is not None)


def filter_none(values: list[int | None]) -> list[int]:
    """Filter out None values from list."""
    return [v for v in values if v is not None]


def replace_none(values: list[int | None], default: int) -> list[int]:
    """Replace None values with default."""
    return [v if v is not None else default for v in values]


def optional_add(a: int | None, b: int | None) -> int | None:
    """Add two optional values."""
    if a is None or b is None:
        return None
    return a + b


def optional_multiply(a: int | None, b: int | None) -> int | None:
    """Multiply two optional values."""
    if a is None or b is None:
        return None
    return a * b


def safe_divide(a: int, b: int) -> int | None:
    """Divide, return None if divisor is zero."""
    if b == 0:
        return None
    return a // b


def safe_sqrt(n: int) -> float | None:
    """Square root, return None if negative."""
    if n < 0:
        return None
    return n**0.5


def safe_index(lst: list[int], index: int) -> int | None:
    """Get list item, return None if out of bounds."""
    if 0 <= index < len(lst):
        return lst[index]
    return None


def safe_head(lst: list[int]) -> int | None:
    """Get first item, return None if empty."""
    return lst[0] if lst else None


def safe_tail(lst: list[int]) -> list[int] | None:
    """Get tail, return None if empty."""
    return lst[1:] if lst else None


def safe_parse_int(s: str) -> int | None:
    """Parse int, return None if invalid."""
    try:
        return int(s)
    except ValueError:
        return None


def safe_parse_float(s: str) -> float | None:
    """Parse float, return None if invalid."""
    try:
        return float(s)
    except ValueError:
        return None


def safe_get_key(d: dict[str, int], key: str) -> int | None:
    """Get dict value, return None if missing."""
    return d.get(key)


def option_to_result(value: int | None, error: str) -> tuple[int | None, str | None]:
    """Convert optional to result (value, error) tuple."""
    if value is not None:
        return (value, None)
    return (None, error)


def result_to_option(result: tuple[int | None, str | None]) -> int | None:
    """Convert result to optional (discard error)."""
    return result[0]


def expect(value: int | None, message: str) -> int:
    """Unwrap with custom error message."""
    if value is None:
        raise ValueError(message)
    return value


def ok_or(value: int | None, error: str) -> tuple[int | None, str | None]:
    """Convert optional to result with error."""
    if value is not None:
        return (value, None)
    return (None, error)


def transpose_list(values: list[int | None]) -> list[int] | None:
    """Transpose list of optionals to optional list."""
    result = []
    for v in values:
        if v is None:
            return None
        result.append(v)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Typed optional CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # unwrap
    unwrap_p = subparsers.add_parser("unwrap", help="Unwrap value")
    unwrap_p.add_argument("value", nargs="?", help="Value or 'none'")
    unwrap_p.add_argument("--default", type=int, help="Default value")

    # safe-div
    div_p = subparsers.add_parser("safe-div", help="Safe division")
    div_p.add_argument("a", type=int, help="Dividend")
    div_p.add_argument("b", type=int, help="Divisor")

    # parse
    parse_p = subparsers.add_parser("parse", help="Safe parse int")
    parse_p.add_argument("value", help="Value to parse")

    # filter
    filter_p = subparsers.add_parser("filter", help="Filter None values")
    filter_p.add_argument("values", nargs="+", help="Values (use 'none' for None)")

    args = parser.parse_args()

    def parse_optional(s: str) -> int | None:
        if s.lower() == "none":
            return None
        try:
            return int(s)
        except ValueError:
            return None

    if args.command == "unwrap":
        value = parse_optional(args.value) if args.value else None
        if args.default is not None:
            result = unwrap_or(value, args.default)
            print(f"Result: {result}")
        else:
            try:
                result = unwrap(value)
                print(f"Result: {result}")
            except ValueError as e:
                print(f"Error: {e}")
                return 1

    elif args.command == "safe-div":
        result = safe_divide(args.a, args.b)
        if result is not None:
            print(f"Result: {result}")
        else:
            print("Cannot divide by zero")

    elif args.command == "parse":
        result = safe_parse_int(args.value)
        if result is not None:
            print(f"Parsed: {result}")
        else:
            print("Invalid integer")

    elif args.command == "filter":
        values = [parse_optional(v) for v in args.values]
        filtered = filter_none(values)
        print(f"Filtered: {filtered}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
