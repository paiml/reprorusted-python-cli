#!/usr/bin/env python3
"""Result Mapping CLI.

Result<T,E> pattern mapping from exceptions to explicit error handling.
"""

import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


@dataclass
class Ok:
    """Success result."""

    value: object

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False


@dataclass
class Err:
    """Error result."""

    error: str

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True


Result = Ok | Err


def ok(value: object) -> Ok:
    """Create success result."""
    return Ok(value)


def err(error: str) -> Err:
    """Create error result."""
    return Err(error)


def is_ok(result: Result) -> bool:
    """Check if result is Ok."""
    return isinstance(result, Ok)


def is_err(result: Result) -> bool:
    """Check if result is Err."""
    return isinstance(result, Err)


def unwrap(result: Result) -> object:
    """Unwrap Ok value, raise on Err."""
    if isinstance(result, Ok):
        return result.value
    raise ValueError(f"Called unwrap on Err: {result.error}")


def unwrap_or(result: Result, default: object) -> object:
    """Unwrap Ok value or return default."""
    if isinstance(result, Ok):
        return result.value
    return default


def unwrap_err(result: Result) -> str:
    """Unwrap Err value, raise on Ok."""
    if isinstance(result, Err):
        return result.error
    raise ValueError("Called unwrap_err on Ok")


def map_result(result: Result, f: Callable[[object], object]) -> Result:
    """Map function over Ok value."""
    if isinstance(result, Ok):
        return Ok(f(result.value))
    return result


def map_err(result: Result, f: Callable[[str], str]) -> Result:
    """Map function over Err value."""
    if isinstance(result, Err):
        return Err(f(result.error))
    return result


def and_then(result: Result, f: Callable[[object], Result]) -> Result:
    """Chain Result-returning function."""
    if isinstance(result, Ok):
        return f(result.value)
    return result


def or_else(result: Result, f: Callable[[str], Result]) -> Result:
    """Chain on Err."""
    if isinstance(result, Err):
        return f(result.error)
    return result


def parse_int(value: str) -> Result:
    """Parse string to int, return Result."""
    try:
        return Ok(int(value))
    except ValueError:
        return Err(f"Invalid integer: {value}")


def parse_float(value: str) -> Result:
    """Parse string to float, return Result."""
    try:
        return Ok(float(value))
    except ValueError:
        return Err(f"Invalid float: {value}")


def safe_divide(a: float, b: float) -> Result:
    """Safely divide, return Result."""
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)


def safe_index(lst: list[int], idx: int) -> Result:
    """Safely index list, return Result."""
    if 0 <= idx < len(lst):
        return Ok(lst[idx])
    return Err(f"Index out of bounds: {idx}")


def safe_key(d: dict[str, int], key: str) -> Result:
    """Safely get dict value, return Result."""
    if key in d:
        return Ok(d[key])
    return Err(f"Key not found: {key}")


def chain_parse_and_double(value: str) -> Result:
    """Parse and double value using and_then."""
    return and_then(parse_int(value), lambda x: Ok(x * 2))


def chain_multiple(value: str) -> Result:
    """Chain multiple operations."""
    result = parse_int(value)
    result = and_then(result, lambda x: Ok(x * 2))
    result = and_then(result, lambda x: Ok(x + 10))
    return result


def validate_positive(value: int) -> Result:
    """Validate value is positive."""
    if value > 0:
        return Ok(value)
    return Err(f"Value must be positive: {value}")


def validate_range(value: int, min_val: int, max_val: int) -> Result:
    """Validate value is in range."""
    if min_val <= value <= max_val:
        return Ok(value)
    return Err(f"Value {value} not in range [{min_val}, {max_val}]")


def parse_and_validate(value: str, min_val: int, max_val: int) -> Result:
    """Parse and validate in one chain."""
    result = parse_int(value)
    result = and_then(result, lambda x: validate_range(x, min_val, max_val))
    return result


def collect_results(values: list[str]) -> Result:
    """Parse all values, fail on first error."""
    results: list[int] = []
    for v in values:
        result = parse_int(v)
        if isinstance(result, Err):
            return result
        results.append(result.value)
    return Ok(results)


def collect_ok_values(values: list[str]) -> list[int]:
    """Collect only successful parses."""
    results: list[int] = []
    for v in values:
        result = parse_int(v)
        if isinstance(result, Ok):
            results.append(result.value)
    return results


def partition_results(values: list[str]) -> tuple[list[int], list[str]]:
    """Partition into successes and errors."""
    oks: list[int] = []
    errs: list[str] = []
    for v in values:
        result = parse_int(v)
        if isinstance(result, Ok):
            oks.append(result.value)
        else:
            errs.append(result.error)
    return (oks, errs)


def first_ok(results: list[Result]) -> Result:
    """Return first Ok, or last Err."""
    last_err: Result = Err("No results")
    for r in results:
        if isinstance(r, Ok):
            return r
        last_err = r
    return last_err


def all_ok(results: list[Result]) -> bool:
    """Check if all results are Ok."""
    return all(isinstance(r, Ok) for r in results)


def any_ok(results: list[Result]) -> bool:
    """Check if any result is Ok."""
    return any(isinstance(r, Ok) for r in results)


def count_ok(results: list[Result]) -> int:
    """Count Ok results."""
    return sum(1 for r in results if isinstance(r, Ok))


def count_err(results: list[Result]) -> int:
    """Count Err results."""
    return sum(1 for r in results if isinstance(r, Err))


def try_operations(value: str) -> Result:
    """Try multiple operations, return first success."""
    ops = [
        lambda v: parse_int(v),
        lambda v: Ok(0) if v == "zero" else Err("not zero"),
        lambda v: Ok(-1) if v == "negative" else Err("not negative"),
    ]
    for op in ops:
        result = op(value)
        if isinstance(result, Ok):
            return result
    return Err(f"All operations failed for: {value}")


def result_to_option(result: Result) -> object | None:
    """Convert Result to Option (Ok value or None)."""
    if isinstance(result, Ok):
        return result.value
    return None


def option_to_result(value: object | None, err_msg: str) -> Result:
    """Convert Option to Result."""
    if value is not None:
        return Ok(value)
    return Err(err_msg)


def flatten_result(result: Result) -> Result:
    """Flatten nested Result."""
    if isinstance(result, Ok) and isinstance(result.value, (Ok, Err)):
        return result.value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Result mapping CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # parse
    parse_p = subparsers.add_parser("parse", help="Parse value")
    parse_p.add_argument("value")
    parse_p.add_argument("--type", choices=["int", "float"], default="int")

    # divide
    div_p = subparsers.add_parser("divide", help="Safe divide")
    div_p.add_argument("a", type=float)
    div_p.add_argument("b", type=float)

    # chain
    chain_p = subparsers.add_parser("chain", help="Chain operations")
    chain_p.add_argument("value")

    # validate
    val_p = subparsers.add_parser("validate", help="Parse and validate")
    val_p.add_argument("value")
    val_p.add_argument("--min", type=int, default=0)
    val_p.add_argument("--max", type=int, default=100)

    # collect
    collect_p = subparsers.add_parser("collect", help="Collect results")
    collect_p.add_argument("values", nargs="+")

    args = parser.parse_args()

    if args.command == "parse":
        if args.type == "int":
            result = parse_int(args.value)
        else:
            result = parse_float(args.value)
        if isinstance(result, Ok):
            print(f"Ok: {result.value}")
        else:
            print(f"Err: {result.error}")

    elif args.command == "divide":
        result = safe_divide(args.a, args.b)
        if isinstance(result, Ok):
            print(f"Result: {result.value}")
        else:
            print(f"Error: {result.error}")

    elif args.command == "chain":
        result = chain_multiple(args.value)
        if isinstance(result, Ok):
            print(f"Final: {result.value}")
        else:
            print(f"Error: {result.error}")

    elif args.command == "validate":
        result = parse_and_validate(args.value, args.min, args.max)
        if isinstance(result, Ok):
            print(f"Valid: {result.value}")
        else:
            print(f"Invalid: {result.error}")

    elif args.command == "collect":
        oks, errs = partition_results(args.values)
        print(f"Successes: {oks}")
        print(f"Errors: {len(errs)}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
