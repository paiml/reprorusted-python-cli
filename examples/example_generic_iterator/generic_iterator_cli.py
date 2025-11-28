"""Generic Iterator Pattern CLI.

Demonstrates iterator patterns including map, filter, fold, and lazy evaluation.
"""

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Iter(ABC, Generic[T]):
    """Abstract iterator interface."""

    @abstractmethod
    def next(self) -> tuple[T, bool]:
        """Get next item and success flag."""
        ...

    def collect(self) -> list[T]:
        """Collect all items into a list."""
        result: list[T] = []
        while True:
            item, ok = self.next()
            if not ok:
                break
            result.append(item)
        return result

    def map(self, f: Callable[[T], U]) -> "MapIter[T, U]":
        """Map function over items."""
        return MapIter(self, f)

    def filter(self, predicate: Callable[[T], bool]) -> "FilterIter[T]":
        """Filter items by predicate."""
        return FilterIter(self, predicate)

    def take(self, n: int) -> "TakeIter[T]":
        """Take first n items."""
        return TakeIter(self, n)

    def skip(self, n: int) -> "SkipIter[T]":
        """Skip first n items."""
        return SkipIter(self, n)

    def enumerate(self) -> "EnumerateIter[T]":
        """Enumerate items with index."""
        return EnumerateIter(self)

    def zip_with(self, other: "Iter[U]") -> "ZipIter[T, U]":
        """Zip with another iterator."""
        return ZipIter(self, other)

    def chain(self, other: "Iter[T]") -> "ChainIter[T]":
        """Chain with another iterator."""
        return ChainIter(self, other)

    def fold(self, initial: U, f: Callable[[U, T], U]) -> U:
        """Fold items into single value."""
        result = initial
        while True:
            item, ok = self.next()
            if not ok:
                break
            result = f(result, item)
        return result

    def count(self) -> int:
        """Count items."""
        return self.fold(0, lambda acc, _: acc + 1)

    def find(self, predicate: Callable[[T], bool]) -> tuple[T | None, bool]:
        """Find first item matching predicate."""
        while True:
            item, ok = self.next()
            if not ok:
                return None, False
            if predicate(item):
                return item, True

    def any(self, predicate: Callable[[T], bool]) -> bool:
        """Check if any item matches predicate."""
        _, found = self.find(predicate)
        return found

    def all(self, predicate: Callable[[T], bool]) -> bool:
        """Check if all items match predicate."""
        while True:
            item, ok = self.next()
            if not ok:
                return True
            if not predicate(item):
                return False

    def min(self) -> tuple[T | None, bool]:
        """Find minimum item."""
        result: T | None = None
        found = False
        while True:
            item, ok = self.next()
            if not ok:
                break
            if not found or item < result:  # type: ignore
                result = item
                found = True
        return result, found

    def max(self) -> tuple[T | None, bool]:
        """Find maximum item."""
        result: T | None = None
        found = False
        while True:
            item, ok = self.next()
            if not ok:
                break
            if not found or item > result:  # type: ignore
                result = item
                found = True
        return result, found

    def sum(self: "Iter[int | float]") -> int | float:
        """Sum numeric items."""
        return self.fold(0, lambda acc, x: acc + x)

    def product(self: "Iter[int | float]") -> int | float:
        """Multiply numeric items."""
        return self.fold(1, lambda acc, x: acc * x)


@dataclass
class ListIter(Iter[T]):
    """Iterator over a list."""

    items: list[T]
    index: int = 0

    def next(self) -> tuple[T, bool]:
        if self.index >= len(self.items):
            return None, False  # type: ignore
        item = self.items[self.index]
        self.index += 1
        return item, True


@dataclass
class RangeIter(Iter[int]):
    """Iterator over a range."""

    start: int
    end: int
    step: int = 1
    current: int | None = None

    def __post_init__(self) -> None:
        self.current = self.start

    def next(self) -> tuple[int, bool]:
        if self.current is None:
            self.current = self.start

        if self.step > 0 and self.current >= self.end:
            return 0, False
        if self.step < 0 and self.current <= self.end:
            return 0, False

        value = self.current
        self.current += self.step
        return value, True


@dataclass
class MapIter(Iter[U], Generic[T, U]):
    """Map iterator."""

    source: Iter[T]
    func: Callable[[T], U]

    def next(self) -> tuple[U, bool]:
        item, ok = self.source.next()
        if not ok:
            return None, False  # type: ignore
        return self.func(item), True


@dataclass
class FilterIter(Iter[T]):
    """Filter iterator."""

    source: Iter[T]
    predicate: Callable[[T], bool]

    def next(self) -> tuple[T, bool]:
        while True:
            item, ok = self.source.next()
            if not ok:
                return None, False  # type: ignore
            if self.predicate(item):
                return item, True


@dataclass
class TakeIter(Iter[T]):
    """Take iterator."""

    source: Iter[T]
    n: int
    taken: int = 0

    def next(self) -> tuple[T, bool]:
        if self.taken >= self.n:
            return None, False  # type: ignore
        item, ok = self.source.next()
        if not ok:
            return None, False  # type: ignore
        self.taken += 1
        return item, True


@dataclass
class SkipIter(Iter[T]):
    """Skip iterator."""

    source: Iter[T]
    n: int
    skipped: int = 0

    def next(self) -> tuple[T, bool]:
        while self.skipped < self.n:
            _, ok = self.source.next()
            if not ok:
                return None, False  # type: ignore
            self.skipped += 1

        return self.source.next()


@dataclass
class EnumerateIter(Iter[tuple[int, T]]):
    """Enumerate iterator."""

    source: Iter[T]
    index: int = 0

    def next(self) -> tuple[tuple[int, T], bool]:
        item, ok = self.source.next()
        if not ok:
            return (0, None), False  # type: ignore
        result = (self.index, item)
        self.index += 1
        return result, True


@dataclass
class ZipIter(Iter[tuple[T, U]], Generic[T, U]):
    """Zip iterator."""

    first: Iter[T]
    second: Iter[U]

    def next(self) -> tuple[tuple[T, U], bool]:
        a, ok1 = self.first.next()
        b, ok2 = self.second.next()
        if not ok1 or not ok2:
            return (None, None), False  # type: ignore
        return (a, b), True


@dataclass
class ChainIter(Iter[T]):
    """Chain iterator."""

    first: Iter[T]
    second: Iter[T]
    use_second: bool = False

    def next(self) -> tuple[T, bool]:
        if not self.use_second:
            item, ok = self.first.next()
            if ok:
                return item, True
            self.use_second = True

        return self.second.next()


@dataclass
class RepeatIter(Iter[T]):
    """Repeat single value."""

    value: T
    count: int | None = None
    emitted: int = 0

    def next(self) -> tuple[T, bool]:
        if self.count is not None and self.emitted >= self.count:
            return None, False  # type: ignore
        self.emitted += 1
        return self.value, True


@dataclass
class CycleIter(Iter[T]):
    """Cycle through items repeatedly."""

    items: list[T]
    index: int = 0
    max_cycles: int | None = None
    cycles: int = 0

    def next(self) -> tuple[T, bool]:
        if not self.items:
            return None, False  # type: ignore
        if self.max_cycles is not None and self.cycles >= self.max_cycles:
            return None, False  # type: ignore

        item = self.items[self.index]
        self.index += 1

        if self.index >= len(self.items):
            self.index = 0
            self.cycles += 1

        return item, True


def iter_from_list(items: list[T]) -> ListIter[T]:
    """Create iterator from list."""
    return ListIter(items)


def iter_range(start: int, end: int, step: int = 1) -> RangeIter:
    """Create range iterator."""
    return RangeIter(start, end, step)


def iter_repeat(value: T, count: int | None = None) -> RepeatIter[T]:
    """Create repeat iterator."""
    return RepeatIter(value, count)


def iter_cycle(items: list[T], max_cycles: int | None = None) -> CycleIter[T]:
    """Create cycle iterator."""
    return CycleIter(items, max_cycles=max_cycles)


def partition_iter(iter: Iter[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
    """Partition iterator into two lists."""
    left: list[T] = []
    right: list[T] = []
    while True:
        item, ok = iter.next()
        if not ok:
            break
        if predicate(item):
            left.append(item)
        else:
            right.append(item)
    return left, right


def group_by_iter(iter: Iter[T], key_fn: Callable[[T], Any]) -> dict[Any, list[T]]:
    """Group iterator items by key function."""
    groups: dict[Any, list[T]] = {}
    while True:
        item, ok = iter.next()
        if not ok:
            break
        key = key_fn(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups


def simulate_iterator(operations: list[str]) -> list[str]:
    """Simulate iterator operations."""
    results = []
    current_iter: Iter[int] = ListIter([])

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "list":
            items = [int(x) for x in parts[1].split(",") if x]
            current_iter = ListIter(items)
            results.append("ok")
        elif cmd == "range":
            params = parts[1].split(",")
            start, end = int(params[0]), int(params[1])
            step = int(params[2]) if len(params) > 2 else 1
            current_iter = iter_range(start, end, step)
            results.append("ok")
        elif cmd == "map":
            factor = int(parts[1])
            current_iter = current_iter.map(lambda x, f=factor: x * f)
            results.append("ok")
        elif cmd == "filter":
            threshold = int(parts[1])
            current_iter = current_iter.filter(lambda x, t=threshold: x > t)
            results.append("ok")
        elif cmd == "take":
            current_iter = current_iter.take(int(parts[1]))
            results.append("ok")
        elif cmd == "skip":
            current_iter = current_iter.skip(int(parts[1]))
            results.append("ok")
        elif cmd == "collect":
            items = current_iter.collect()
            results.append(",".join(str(x) for x in items))
        elif cmd == "sum":
            total = current_iter.sum()
            results.append(str(total))
        elif cmd == "count":
            count = current_iter.count()
            results.append(str(count))
        elif cmd == "min":
            val, ok = current_iter.min()
            results.append(str(val) if ok else "none")
        elif cmd == "max":
            val, ok = current_iter.max()
            results.append(str(val) if ok else "none")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: generic_iterator_cli.py <command> [args...]")
        print("Commands: range, list, demo")
        return 1

    cmd = sys.argv[1]

    if cmd == "range":
        if len(sys.argv) < 4:
            print("Usage: range <start> <end>", file=sys.stderr)
            return 1
        start, end = int(sys.argv[2]), int(sys.argv[3])
        items = iter_range(start, end).collect()
        print(", ".join(str(x) for x in items))

    elif cmd == "list":
        if len(sys.argv) < 3:
            print("Usage: list <items>", file=sys.stderr)
            return 1
        items = [int(x) for x in sys.argv[2].split(",")]
        result = iter_from_list(items).map(lambda x: x * 2).filter(lambda x: x > 5).collect()
        print(", ".join(str(x) for x in result))

    elif cmd == "demo":
        # Demonstrate chaining operations
        result = (
            iter_range(1, 11).map(lambda x: x * x).filter(lambda x: x % 2 == 0).take(3).collect()
        )
        print(f"Squares of 1-10, even, first 3: {result}")

        # Sum of range
        total = iter_range(1, 101).sum()
        print(f"Sum of 1-100: {total}")

        # Chain two iterators
        chained = iter_range(1, 4).chain(iter_range(10, 13)).collect()
        print(f"Chained: {chained}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
