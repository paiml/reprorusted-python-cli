#!/usr/bin/env python3
"""Async Basic CLI.

Basic async/await patterns and coroutine functions.
"""

import argparse
import asyncio
import sys


async def async_identity(value: int) -> int:
    """Simple async identity function."""
    return value


async def async_add(a: int, b: int) -> int:
    """Async addition."""
    return a + b


async def async_multiply(a: int, b: int) -> int:
    """Async multiplication."""
    return a * b


async def async_delay(delay_ms: int) -> int:
    """Async function with delay."""
    await asyncio.sleep(delay_ms / 1000.0)
    return delay_ms


async def async_chain(value: int) -> int:
    """Chain multiple async operations."""
    v1 = await async_identity(value)
    v2 = await async_add(v1, 10)
    v3 = await async_multiply(v2, 2)
    return v3


async def async_conditional(value: int) -> str:
    """Async with conditional logic."""
    result = await async_identity(value)
    if result > 0:
        return "positive"
    elif result < 0:
        return "negative"
    else:
        return "zero"


async def async_loop(count: int) -> int:
    """Async loop accumulator."""
    total = 0
    for i in range(count):
        total = await async_add(total, i)
    return total


async def async_early_return(values: list[int]) -> int:
    """Async with early return."""
    for value in values:
        result = await async_identity(value)
        if result < 0:
            return result
    return 0


async def async_try_operation(value: int) -> int:
    """Async operation that may fail."""
    if value < 0:
        raise ValueError(f"Negative value: {value}")
    return await async_identity(value * 2)


async def async_safe_operation(value: int) -> tuple[bool, int]:
    """Async operation with error handling."""
    try:
        result = await async_try_operation(value)
        return (True, result)
    except ValueError:
        return (False, 0)


async def async_map(values: list[int], transform: int) -> list[int]:
    """Async map operation."""
    results: list[int] = []
    for v in values:
        result = await async_add(v, transform)
        results.append(result)
    return results


async def async_filter_positive(values: list[int]) -> list[int]:
    """Async filter for positive values."""
    results: list[int] = []
    for v in values:
        val = await async_identity(v)
        if val > 0:
            results.append(val)
    return results


async def async_reduce(values: list[int], initial: int) -> int:
    """Async reduce/fold operation."""
    accumulator = initial
    for v in values:
        accumulator = await async_add(accumulator, v)
    return accumulator


async def async_find_first(values: list[int], target: int) -> int:
    """Async find first matching value."""
    for i, v in enumerate(values):
        val = await async_identity(v)
        if val == target:
            return i
    return -1


async def async_any_match(values: list[int], target: int) -> bool:
    """Async check if any value matches."""
    for v in values:
        val = await async_identity(v)
        if val == target:
            return True
    return False


async def async_all_positive(values: list[int]) -> bool:
    """Async check if all values are positive."""
    for v in values:
        val = await async_identity(v)
        if val <= 0:
            return False
    return True


async def async_count_matching(values: list[int], predicate_value: int) -> int:
    """Async count values greater than predicate."""
    count = 0
    for v in values:
        val = await async_identity(v)
        if val > predicate_value:
            count += 1
    return count


async def async_partition(values: list[int], pivot: int) -> tuple[list[int], list[int]]:
    """Async partition values around pivot."""
    less: list[int] = []
    greater_or_equal: list[int] = []
    for v in values:
        val = await async_identity(v)
        if val < pivot:
            less.append(val)
        else:
            greater_or_equal.append(val)
    return (less, greater_or_equal)


async def async_sum_squares(values: list[int]) -> int:
    """Async sum of squares."""
    total = 0
    for v in values:
        squared = await async_multiply(v, v)
        total = await async_add(total, squared)
    return total


async def async_fibonacci(n: int) -> int:
    """Async fibonacci calculation."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, await async_add(a, b)
    return b


async def async_factorial(n: int) -> int:
    """Async factorial calculation."""
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result = await async_multiply(result, i)
    return result


def run_async(coro: object) -> object:
    """Run async function synchronously."""
    return asyncio.run(coro)  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Async basic CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # chain
    chain_p = subparsers.add_parser("chain", help="Chain async operations")
    chain_p.add_argument("value", type=int)

    # sum
    sum_p = subparsers.add_parser("sum", help="Async sum")
    sum_p.add_argument("values", type=int, nargs="+")

    # fibonacci
    fib_p = subparsers.add_parser("fibonacci", help="Async fibonacci")
    fib_p.add_argument("n", type=int)

    # factorial
    fact_p = subparsers.add_parser("factorial", help="Async factorial")
    fact_p.add_argument("n", type=int)

    args = parser.parse_args()

    if args.command == "chain":
        result = run_async(async_chain(args.value))
        print(f"Result: {result}")

    elif args.command == "sum":
        result = run_async(async_reduce(args.values, 0))
        print(f"Sum: {result}")

    elif args.command == "fibonacci":
        result = run_async(async_fibonacci(args.n))
        print(f"Fibonacci({args.n}): {result}")

    elif args.command == "factorial":
        result = run_async(async_factorial(args.n))
        print(f"Factorial({args.n}): {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
