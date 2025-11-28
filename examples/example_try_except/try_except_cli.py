#!/usr/bin/env python3
"""Try/Except CLI.

Basic try/except/finally patterns for exception handling.
"""

import argparse
import sys


def safe_divide(a: float, b: float) -> float | None:
    """Safely divide two numbers, return None on error."""
    try:
        return a / b
    except ZeroDivisionError:
        return None


def safe_int(value: str) -> int | None:
    """Safely convert string to int."""
    try:
        return int(value)
    except ValueError:
        return None


def safe_float(value: str) -> float | None:
    """Safely convert string to float."""
    try:
        return float(value)
    except ValueError:
        return None


def safe_index(lst: list[int], idx: int) -> int | None:
    """Safely get list element by index."""
    try:
        return lst[idx]
    except IndexError:
        return None


def safe_key(d: dict[str, int], key: str) -> int | None:
    """Safely get dict value by key."""
    try:
        return d[key]
    except KeyError:
        return None


def divide_with_default(a: float, b: float, default: float) -> float:
    """Divide with default value on error."""
    try:
        return a / b
    except ZeroDivisionError:
        return default


def parse_int_with_default(value: str, default: int) -> int:
    """Parse int with default value on error."""
    try:
        return int(value)
    except ValueError:
        return default


def try_multiple_exceptions(value: str, idx: int) -> str:
    """Handle multiple exception types."""
    try:
        num = int(value)
        chars = list(str(num))
        return chars[idx]
    except ValueError:
        return "invalid_number"
    except IndexError:
        return "invalid_index"


def try_except_else(value: str) -> str:
    """Try/except with else clause."""
    try:
        num = int(value)
    except ValueError:
        return "error"
    else:
        return f"success: {num}"


def try_finally_cleanup(value: str) -> tuple[int | None, bool]:
    """Try/finally for cleanup."""
    cleaned = False
    result: int | None = None
    try:
        result = int(value)
    except ValueError:
        result = None
    finally:
        cleaned = True
    return (result, cleaned)


def try_except_finally_all(value: str) -> tuple[str, bool]:
    """Try/except/else/finally all together."""
    status = ""
    finalized = False
    try:
        num = int(value)
    except ValueError:
        status = "error"
    else:
        status = f"ok:{num}"
    finally:
        finalized = True
    return (status, finalized)


def nested_try_except(outer: str, inner: str) -> str:
    """Nested try/except blocks."""
    try:
        outer_val = int(outer)
        try:
            inner_val = int(inner)
            return f"both:{outer_val + inner_val}"
        except ValueError:
            return f"inner_error:{outer_val}"
    except ValueError:
        return "outer_error"


def reraise_exception(value: str) -> int:
    """Catch and re-raise exception."""
    try:
        return int(value)
    except ValueError:
        raise


def catch_and_convert(value: str) -> int:
    """Catch one exception, raise another."""
    try:
        return int(value)
    except ValueError as err:
        raise RuntimeError(f"Cannot parse: {value}") from err


def safe_pop(lst: list[int]) -> int | None:
    """Safely pop from list."""
    try:
        return lst.pop()
    except IndexError:
        return None


def safe_get_nested(d: dict[str, dict[str, int]], k1: str, k2: str) -> int | None:
    """Safely get nested dict value."""
    try:
        return d[k1][k2]
    except KeyError:
        return None


def accumulate_with_errors(values: list[str]) -> tuple[int, int]:
    """Accumulate valid integers, count errors."""
    total = 0
    errors = 0
    for v in values:
        try:
            total += int(v)
        except ValueError:
            errors += 1
    return (total, errors)


def first_valid_int(values: list[str]) -> int | None:
    """Return first valid integer from list."""
    for v in values:
        try:
            return int(v)
        except ValueError:
            continue
    return None


def all_valid_ints(values: list[str]) -> list[int]:
    """Return all valid integers from list."""
    result: list[int] = []
    for v in values:
        try:
            result.append(int(v))
        except ValueError:
            pass
    return result


def count_valid_floats(values: list[str]) -> int:
    """Count valid floats in list."""
    count = 0
    for v in values:
        try:
            float(v)
            count += 1
        except ValueError:
            pass
    return count


def safe_slice(lst: list[int], start: int, end: int) -> list[int]:
    """Safely slice list."""
    try:
        return lst[start:end]
    except (IndexError, TypeError):
        return []


def parse_or_zero(value: str) -> int:
    """Parse int or return zero."""
    try:
        return int(value)
    except ValueError:
        return 0


def division_result(a: float, b: float) -> str:
    """Return division result as string with error handling."""
    try:
        result = a / b
        return f"result:{result:.2f}"
    except ZeroDivisionError:
        return "error:division_by_zero"
    except OverflowError:
        return "error:overflow"


def main() -> int:
    parser = argparse.ArgumentParser(description="Try/except patterns CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # divide
    div_p = subparsers.add_parser("divide", help="Safe division")
    div_p.add_argument("a", type=float)
    div_p.add_argument("b", type=float)

    # parse
    parse_p = subparsers.add_parser("parse", help="Parse integer")
    parse_p.add_argument("value")
    parse_p.add_argument("--default", type=int, default=0)

    # multi
    multi_p = subparsers.add_parser("multi", help="Multiple exceptions")
    multi_p.add_argument("value")
    multi_p.add_argument("index", type=int)

    # accumulate
    acc_p = subparsers.add_parser("accumulate", help="Accumulate valid ints")
    acc_p.add_argument("values", nargs="+")

    args = parser.parse_args()

    if args.command == "divide":
        result = safe_divide(args.a, args.b)
        if result is None:
            print("Error: division by zero")
        else:
            print(f"Result: {result}")

    elif args.command == "parse":
        result = parse_int_with_default(args.value, args.default)
        print(f"Parsed: {result}")

    elif args.command == "multi":
        result = try_multiple_exceptions(args.value, args.index)
        print(f"Result: {result}")

    elif args.command == "accumulate":
        total, errors = accumulate_with_errors(args.values)
        print(f"Total: {total}, Errors: {errors}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
