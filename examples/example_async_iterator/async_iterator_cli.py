#!/usr/bin/env python3
"""Async Iterator CLI.

Async iterators and async generators.
"""

import argparse
import asyncio
import sys
from collections.abc import AsyncIterator


class AsyncRange:
    """Async range iterator."""

    def __init__(self, start: int, end: int, step: int = 1) -> None:
        self._start: int = start
        self._end: int = end
        self._step: int = step
        self._current: int = start

    def __aiter__(self) -> "AsyncRange":
        return self

    async def __anext__(self) -> int:
        if (self._step > 0 and self._current >= self._end) or (
            self._step < 0 and self._current <= self._end
        ):
            raise StopAsyncIteration
        value = self._current
        self._current += self._step
        return value


class AsyncCounter:
    """Async counter with limit."""

    def __init__(self, limit: int) -> None:
        self._limit: int = limit
        self._count: int = 0

    def __aiter__(self) -> "AsyncCounter":
        return self

    async def __anext__(self) -> int:
        if self._count >= self._limit:
            raise StopAsyncIteration
        value = self._count
        self._count += 1
        return value


class AsyncFilter:
    """Async filtering iterator."""

    def __init__(self, iterable: AsyncIterator[int], min_value: int) -> None:
        self._iterable: AsyncIterator[int] = iterable
        self._min_value: int = min_value

    def __aiter__(self) -> "AsyncFilter":
        return self

    async def __anext__(self) -> int:
        async for item in self._iterable:
            if item >= self._min_value:
                return item
        raise StopAsyncIteration


class AsyncMap:
    """Async mapping iterator."""

    def __init__(self, iterable: AsyncIterator[int], addend: int) -> None:
        self._iterable: AsyncIterator[int] = iterable
        self._addend: int = addend

    def __aiter__(self) -> "AsyncMap":
        return self

    async def __anext__(self) -> int:
        async for item in self._iterable:
            return item + self._addend
        raise StopAsyncIteration


class AsyncTake:
    """Async iterator that takes first n items."""

    def __init__(self, iterable: AsyncIterator[int], n: int) -> None:
        self._iterable: AsyncIterator[int] = iterable
        self._remaining: int = n

    def __aiter__(self) -> "AsyncTake":
        return self

    async def __anext__(self) -> int:
        if self._remaining <= 0:
            raise StopAsyncIteration
        self._remaining -= 1
        return await self._iterable.__anext__()


class AsyncSkip:
    """Async iterator that skips first n items."""

    def __init__(self, iterable: AsyncIterator[int], n: int) -> None:
        self._iterable: AsyncIterator[int] = iterable
        self._to_skip: int = n
        self._skipped: bool = False

    def __aiter__(self) -> "AsyncSkip":
        return self

    async def __anext__(self) -> int:
        if not self._skipped:
            for _ in range(self._to_skip):
                try:
                    await self._iterable.__anext__()
                except StopAsyncIteration:
                    raise
            self._skipped = True
        return await self._iterable.__anext__()


async def async_generator_range(start: int, end: int) -> AsyncIterator[int]:
    """Async generator for range."""
    for i in range(start, end):
        yield i


async def async_generator_squares(limit: int) -> AsyncIterator[int]:
    """Async generator for squares."""
    for i in range(limit):
        yield i * i


async def async_generator_fibonacci(limit: int) -> AsyncIterator[int]:
    """Async generator for Fibonacci sequence."""
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b


async def async_generator_filter(source: AsyncIterator[int], threshold: int) -> AsyncIterator[int]:
    """Async generator that filters values."""
    async for item in source:
        if item >= threshold:
            yield item


async def async_generator_map(source: AsyncIterator[int], addend: int) -> AsyncIterator[int]:
    """Async generator that transforms values."""
    async for item in source:
        yield item + addend


async def async_generator_take(source: AsyncIterator[int], n: int) -> AsyncIterator[int]:
    """Async generator that takes first n items."""
    count = 0
    async for item in source:
        if count >= n:
            break
        yield item
        count += 1


async def async_generator_skip(source: AsyncIterator[int], n: int) -> AsyncIterator[int]:
    """Async generator that skips first n items."""
    count = 0
    async for item in source:
        if count >= n:
            yield item
        count += 1


async def async_generator_chain(
    first: AsyncIterator[int], second: AsyncIterator[int]
) -> AsyncIterator[int]:
    """Chain two async iterators."""
    async for item in first:
        yield item
    async for item in second:
        yield item


async def async_generator_enumerate(source: AsyncIterator[int]) -> AsyncIterator[tuple[int, int]]:
    """Async enumerate."""
    index = 0
    async for item in source:
        yield (index, item)
        index += 1


async def async_generator_zip(
    first: AsyncIterator[int], second: AsyncIterator[int]
) -> AsyncIterator[tuple[int, int]]:
    """Async zip of two iterators."""
    while True:
        try:
            a = await first.__anext__()
            b = await second.__anext__()
            yield (a, b)
        except StopAsyncIteration:
            break


async def collect_async(iterator: AsyncIterator[int]) -> list[int]:
    """Collect async iterator into list."""
    result: list[int] = []
    async for item in iterator:
        result.append(item)
    return result


async def sum_async(iterator: AsyncIterator[int]) -> int:
    """Sum values from async iterator."""
    total = 0
    async for item in iterator:
        total += item
    return total


async def count_async(iterator: AsyncIterator[int]) -> int:
    """Count items in async iterator."""
    count = 0
    async for _ in iterator:
        count += 1
    return count


async def any_async(iterator: AsyncIterator[int], value: int) -> bool:
    """Check if any item equals value."""
    async for item in iterator:
        if item == value:
            return True
    return False


async def all_positive_async(iterator: AsyncIterator[int]) -> bool:
    """Check if all items are positive."""
    async for item in iterator:
        if item <= 0:
            return False
    return True


async def first_async(iterator: AsyncIterator[int]) -> int:
    """Get first item or -1 if empty."""
    async for item in iterator:
        return item
    return -1


async def last_async(iterator: AsyncIterator[int]) -> int:
    """Get last item or -1 if empty."""
    result = -1
    async for item in iterator:
        result = item
    return result


def run_async(coro: object) -> object:
    """Run async function synchronously."""
    return asyncio.run(coro)  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Async iterator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # range
    range_p = subparsers.add_parser("range", help="Async range")
    range_p.add_argument("start", type=int)
    range_p.add_argument("end", type=int)

    # squares
    squares_p = subparsers.add_parser("squares", help="Async squares")
    squares_p.add_argument("limit", type=int)

    # fibonacci
    fib_p = subparsers.add_parser("fibonacci", help="Async fibonacci")
    fib_p.add_argument("limit", type=int)

    args = parser.parse_args()

    if args.command == "range":
        result = run_async(collect_async(async_generator_range(args.start, args.end)))
        print(f"Range: {result}")

    elif args.command == "squares":
        result = run_async(collect_async(async_generator_squares(args.limit)))
        print(f"Squares: {result}")

    elif args.command == "fibonacci":
        result = run_async(collect_async(async_generator_fibonacci(args.limit)))
        print(f"Fibonacci: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
