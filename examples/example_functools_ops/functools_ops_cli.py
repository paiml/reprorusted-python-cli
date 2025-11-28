#!/usr/bin/env python3
"""Functools Ops CLI.

Functools patterns: partial, reduce, lru_cache.
"""

import argparse
import sys
from collections.abc import Callable
from functools import lru_cache, partial, reduce


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def power(base: int, exp: int) -> int:
    """Raise base to exp."""
    return base**exp


def format_value(prefix: str, value: int, suffix: str) -> str:
    """Format value with prefix and suffix."""
    return f"{prefix}{value}{suffix}"


# Partial applications
add_10 = partial(add, 10)
multiply_by_2 = partial(multiply, 2)
square = partial(power, exp=2)
cube = partial(power, exp=3)
format_dollars = partial(format_value, "$", suffix="")
format_percent = partial(format_value, "", suffix="%")


def reduce_sum(items: list[int]) -> int:
    """Sum using reduce."""
    return reduce(add, items, 0)


def reduce_product(items: list[int]) -> int:
    """Product using reduce."""
    return reduce(multiply, items, 1)


def reduce_max(items: list[int]) -> int | None:
    """Max using reduce."""
    if not items:
        return None
    return reduce(lambda a, b: a if a > b else b, items)


def reduce_min(items: list[int]) -> int | None:
    """Min using reduce."""
    if not items:
        return None
    return reduce(lambda a, b: a if a < b else b, items)


def reduce_concat(items: list[str]) -> str:
    """Concatenate strings using reduce."""
    return reduce(lambda a, b: a + b, items, "")


def reduce_flatten(lists: list[list[int]]) -> list[int]:
    """Flatten using reduce."""
    return reduce(lambda a, b: a + b, lists, [])


def compose(*funcs: Callable[[int], int]) -> Callable[[int], int]:
    """Compose multiple functions."""

    def composed(x: int) -> int:
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result

    return composed


def pipe(*funcs: Callable[[int], int]) -> Callable[[int], int]:
    """Pipe functions (left to right)."""

    def piped(x: int) -> int:
        result = x
        for f in funcs:
            result = f(result)
        return result

    return piped


@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Fibonacci with LRU cache."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@lru_cache(maxsize=128)
def factorial(n: int) -> int:
    """Factorial with LRU cache."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def clear_caches() -> None:
    """Clear all LRU caches."""
    fibonacci.cache_clear()
    factorial.cache_clear()


def get_cache_info() -> dict[str, object]:
    """Get cache statistics."""
    return {
        "fibonacci": fibonacci.cache_info()._asdict(),
        "factorial": factorial.cache_info()._asdict(),
    }


def apply_partial(func: Callable[[int, int], int], first_arg: int) -> Callable[[int], int]:
    """Create partial application."""
    return partial(func, first_arg)


def curry_2(func: Callable[[int, int], int]) -> Callable[[int], Callable[[int], int]]:
    """Curry a 2-argument function."""

    def curried(a: int) -> Callable[[int], int]:
        def inner(b: int) -> int:
            return func(a, b)

        return inner

    return curried


def uncurry_2(func: Callable[[int], Callable[[int], int]]) -> Callable[[int, int], int]:
    """Uncurry a curried function."""

    def uncurried(a: int, b: int) -> int:
        return func(a)(b)

    return uncurried


def map_reduce(
    items: list[int], mapper: Callable[[int], int], reducer: Callable[[int, int], int], initial: int
) -> int:
    """Map-reduce pattern."""
    mapped = [mapper(x) for x in items]
    return reduce(reducer, mapped, initial)


def filter_reduce(
    items: list[int],
    predicate: Callable[[int], bool],
    reducer: Callable[[int, int], int],
    initial: int,
) -> int:
    """Filter-reduce pattern."""
    filtered = [x for x in items if predicate(x)]
    return reduce(reducer, filtered, initial)


def partition_by(items: list[int], predicate: Callable[[int], bool]) -> tuple[list[int], list[int]]:
    """Partition by predicate."""
    true_list: list[int] = []
    false_list: list[int] = []
    for item in items:
        if predicate(item):
            true_list.append(item)
        else:
            false_list.append(item)
    return (true_list, false_list)


def group_by(items: list[int], key_func: Callable[[int], int]) -> dict[int, list[int]]:
    """Group items by key function."""
    result: dict[int, list[int]] = {}
    for item in items:
        key = key_func(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result


def scan(items: list[int], func: Callable[[int, int], int], initial: int) -> list[int]:
    """Scan (cumulative reduce)."""
    result: list[int] = []
    acc = initial
    for item in items:
        acc = func(acc, item)
        result.append(acc)
    return result


def take_while(items: list[int], predicate: Callable[[int], bool]) -> list[int]:
    """Take while predicate is true."""
    result: list[int] = []
    for item in items:
        if not predicate(item):
            break
        result.append(item)
    return result


def drop_while(items: list[int], predicate: Callable[[int], bool]) -> list[int]:
    """Drop while predicate is true."""
    result: list[int] = []
    dropping = True
    for item in items:
        if dropping and predicate(item):
            continue
        dropping = False
        result.append(item)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Functools ops CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # partial
    part_p = subparsers.add_parser("partial", help="Partial application")
    part_p.add_argument("--add10", type=int)
    part_p.add_argument("--mul2", type=int)
    part_p.add_argument("--square", type=int)

    # reduce
    red_p = subparsers.add_parser("reduce", help="Reduce operations")
    red_p.add_argument("items", type=int, nargs="+")
    red_p.add_argument("--op", choices=["sum", "product", "max", "min"])

    # cached
    cache_p = subparsers.add_parser("cached", help="Cached functions")
    cache_p.add_argument("--fib", type=int)
    cache_p.add_argument("--fact", type=int)

    args = parser.parse_args()

    if args.command == "partial":
        if args.add10 is not None:
            print(f"add_10({args.add10}) = {add_10(args.add10)}")
        if args.mul2 is not None:
            print(f"multiply_by_2({args.mul2}) = {multiply_by_2(args.mul2)}")
        if args.square is not None:
            print(f"square({args.square}) = {square(args.square)}")

    elif args.command == "reduce":
        op = args.op or "sum"
        if op == "sum":
            print(f"Sum: {reduce_sum(args.items)}")
        elif op == "product":
            print(f"Product: {reduce_product(args.items)}")
        elif op == "max":
            print(f"Max: {reduce_max(args.items)}")
        elif op == "min":
            print(f"Min: {reduce_min(args.items)}")

    elif args.command == "cached":
        if args.fib is not None:
            print(f"fib({args.fib}) = {fibonacci(args.fib)}")
        if args.fact is not None:
            print(f"fact({args.fact}) = {factorial(args.fact)}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
