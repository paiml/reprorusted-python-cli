"""Reactive Streams CLI.

Demonstrates reactive streams with operators.
"""

import sys
from collections.abc import Callable, Iterator
from typing import Any, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Stream(Generic[T]):
    """Lazy stream with operators."""

    def __init__(self, source: Iterator[T] | Callable[[], Iterator[T]]) -> None:
        if callable(source):
            self._source = source
        else:
            self._source = lambda: source

    def __iter__(self) -> Iterator[T]:
        return self._source()

    def map(self, fn: Callable[[T], U]) -> "Stream[U]":
        def gen() -> Iterator[U]:
            for item in self._source():
                yield fn(item)

        return Stream(gen)

    def filter(self, pred: Callable[[T], bool]) -> "Stream[T]":
        def gen() -> Iterator[T]:
            for item in self._source():
                if pred(item):
                    yield item

        return Stream(gen)

    def take(self, n: int) -> "Stream[T]":
        def gen() -> Iterator[T]:
            count = 0
            for item in self._source():
                if count >= n:
                    break
                yield item
                count += 1

        return Stream(gen)

    def skip(self, n: int) -> "Stream[T]":
        def gen() -> Iterator[T]:
            count = 0
            for item in self._source():
                if count >= n:
                    yield item
                count += 1

        return Stream(gen)

    def flat_map(self, fn: Callable[[T], "Stream[U]"]) -> "Stream[U]":
        def gen() -> Iterator[U]:
            for item in self._source():
                yield from fn(item)

        return Stream(gen)

    def scan(self, fn: Callable[[T, T], T], initial: T) -> "Stream[T]":
        def gen() -> Iterator[T]:
            acc = initial
            for item in self._source():
                acc = fn(acc, item)
                yield acc

        return Stream(gen)

    def distinct(self) -> "Stream[T]":
        def gen() -> Iterator[T]:
            seen: set[Any] = set()
            for item in self._source():
                key = item
                if key not in seen:
                    seen.add(key)
                    yield item

        return Stream(gen)

    def chunk(self, size: int) -> "Stream[list[T]]":
        def gen() -> Iterator[list[T]]:
            batch: list[T] = []
            for item in self._source():
                batch.append(item)
                if len(batch) >= size:
                    yield batch
                    batch = []
            if batch:
                yield batch

        return Stream(gen)

    def window(self, size: int) -> "Stream[list[T]]":
        def gen() -> Iterator[list[T]]:
            window: list[T] = []
            for item in self._source():
                window.append(item)
                if len(window) > size:
                    window.pop(0)
                if len(window) == size:
                    yield list(window)

        return Stream(gen)

    def enumerate(self) -> "Stream[tuple[int, T]]":
        def gen() -> Iterator[tuple[int, T]]:
            yield from enumerate(self._source())

        return Stream(gen)

    def zip_with(self, other: "Stream[U]") -> "Stream[tuple[T, U]]":
        def gen() -> Iterator[tuple[T, U]]:
            yield from zip(self._source(), other._source(), strict=False)

        return Stream(gen)

    def foreach(self, fn: Callable[[T], None]) -> None:
        for item in self._source():
            fn(item)

    def collect(self) -> list[T]:
        return list(self._source())

    def reduce(self, fn: Callable[[T, T], T], initial: T) -> T:
        acc = initial
        for item in self._source():
            acc = fn(acc, item)
        return acc

    def count(self) -> int:
        return sum(1 for _ in self._source())

    def first(self) -> T | None:
        for item in self._source():
            return item
        return None

    def last(self) -> T | None:
        result = None
        for item in self._source():
            result = item
        return result

    def any(self, pred: Callable[[T], bool]) -> bool:
        for item in self._source():
            if pred(item):
                return True
        return False

    def all(self, pred: Callable[[T], bool]) -> bool:
        for item in self._source():
            if not pred(item):
                return False
        return True


def stream(iterable: list[T] | range) -> Stream[T]:
    """Create a stream from an iterable."""
    return Stream(iter(iterable))


def repeat(value: T, times: int | None = None) -> Stream[T]:
    """Create a stream that repeats a value."""

    def gen() -> Iterator[T]:
        count = 0
        while times is None or count < times:
            yield value
            count += 1

    return Stream(gen)


def iterate(fn: Callable[[T], T], initial: T) -> Stream[T]:
    """Create infinite stream by repeatedly applying function."""

    def gen() -> Iterator[T]:
        current = initial
        while True:
            yield current
            current = fn(current)

    return Stream(gen)


def concat(*streams: Stream[T]) -> Stream[T]:
    """Concatenate multiple streams."""

    def gen() -> Iterator[T]:
        for s in streams:
            yield from s

    return Stream(gen)


def merge(*streams: Stream[T]) -> Stream[T]:
    """Merge streams (interleaved)."""

    def gen() -> Iterator[T]:
        iters = [iter(s) for s in streams]
        while iters:
            next_iters = []
            for it in iters:
                try:
                    yield next(it)
                    next_iters.append(it)
                except StopIteration:
                    pass
            iters = next_iters

    return Stream(gen)


def simulate_stream(operations: list[str]) -> list[str]:
    """Simulate stream operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "map":
            values = [int(x) for x in parts[1].split(",")]
            result = stream(values).map(lambda x: x * 2).collect()
            results.append(str(result))
        elif cmd == "filter":
            values = [int(x) for x in parts[1].split(",")]
            result = stream(values).filter(lambda x: x % 2 == 0).collect()
            results.append(str(result))
        elif cmd == "take":
            n = int(parts[1])
            result = stream(range(100)).take(n).collect()
            results.append(str(result))
        elif cmd == "chunk":
            values = [int(x) for x in parts[1].split(",")]
            result = stream(values).chunk(3).collect()
            results.append(str(result))
        elif cmd == "reduce":
            values = [int(x) for x in parts[1].split(",")]
            result = stream(values).reduce(lambda a, b: a + b, 0)
            results.append(str(result))
        elif cmd == "distinct":
            values = [int(x) for x in parts[1].split(",")]
            result = stream(values).distinct().collect()
            results.append(str(result))
        elif cmd == "scan":
            values = [int(x) for x in parts[1].split(",")]
            result = stream(values).scan(lambda a, b: a + b, 0).collect()
            results.append(str(result))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: event_stream_cli.py <command>")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        result = (
            stream(range(1, 20)).filter(lambda x: x % 2 == 0).map(lambda x: x * x).take(5).collect()
        )
        print(f"Result: {result}")

        # Running sum
        sums = stream([1, 2, 3, 4, 5]).scan(lambda a, b: a + b, 0).collect()
        print(f"Running sums: {sums}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
