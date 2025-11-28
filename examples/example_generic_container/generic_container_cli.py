"""Generic Container Patterns CLI.

Demonstrates generic container types like Box, Option, and Vec patterns.
"""

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class Box(Generic[T]):
    """A simple wrapper container."""

    value: T

    def unwrap(self) -> T:
        """Get the contained value."""
        return self.value

    def map(self, f: Callable[[T], U]) -> "Box[U]":
        """Apply function to contained value."""
        return Box(f(self.value))

    def flat_map(self, f: Callable[[T], "Box[U]"]) -> "Box[U]":
        """Apply function returning Box and flatten."""
        return f(self.value)


class Option(ABC, Generic[T]):
    """Option type representing optional values."""

    @abstractmethod
    def is_some(self) -> bool:
        """Check if contains a value."""
        ...

    @abstractmethod
    def is_none(self) -> bool:
        """Check if empty."""
        ...

    @abstractmethod
    def unwrap(self) -> T:
        """Get value or raise."""
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Get value or return default."""
        ...

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Option[U]":
        """Apply function if Some."""
        ...


@dataclass
class Some(Option[T]):
    """Option containing a value."""

    value: T

    def is_some(self) -> bool:
        return True

    def is_none(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value

    def map(self, f: Callable[[T], U]) -> Option[U]:
        return Some(f(self.value))

    def flat_map(self, f: Callable[[T], Option[U]]) -> Option[U]:
        return f(self.value)

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        if predicate(self.value):
            return self
        return NoneValue()


class NoneValue(Option[Any]):
    """Option representing no value."""

    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def unwrap(self) -> Any:
        raise ValueError("Called unwrap on None")

    def unwrap_or(self, default: T) -> T:
        return default

    def map(self, f: Callable[[Any], U]) -> Option[U]:
        return NoneValue()

    def flat_map(self, f: Callable[[Any], Option[U]]) -> Option[U]:
        return NoneValue()

    def filter(self, predicate: Callable[[Any], bool]) -> Option[Any]:
        return self


def option_from(value: T | None) -> Option[T]:
    """Create Option from nullable value."""
    if value is None:
        return NoneValue()
    return Some(value)


@dataclass
class Vec(Generic[T]):
    """Generic vector container."""

    items: list[T]

    def __init__(self, items: list[T] | None = None) -> None:
        self.items = items if items is not None else []

    def __len__(self) -> int:
        return len(self.items)

    def push(self, item: T) -> None:
        """Add item to end."""
        self.items.append(item)

    def pop(self) -> Option[T]:
        """Remove and return last item."""
        if self.items:
            return Some(self.items.pop())
        return NoneValue()

    def get(self, index: int) -> Option[T]:
        """Get item at index."""
        if 0 <= index < len(self.items):
            return Some(self.items[index])
        return NoneValue()

    def first(self) -> Option[T]:
        """Get first item."""
        return self.get(0)

    def last(self) -> Option[T]:
        """Get last item."""
        if self.items:
            return self.get(len(self.items) - 1)
        return NoneValue()

    def map(self, f: Callable[[T], U]) -> "Vec[U]":
        """Apply function to all items."""
        return Vec([f(item) for item in self.items])

    def filter(self, predicate: Callable[[T], bool]) -> "Vec[T]":
        """Filter items by predicate."""
        return Vec([item for item in self.items if predicate(item)])

    def fold(self, initial: U, f: Callable[[U, T], U]) -> U:
        """Fold items into single value."""
        result = initial
        for item in self.items:
            result = f(result, item)
        return result

    def find(self, predicate: Callable[[T], bool]) -> Option[T]:
        """Find first item matching predicate."""
        for item in self.items:
            if predicate(item):
                return Some(item)
        return NoneValue()

    def any(self, predicate: Callable[[T], bool]) -> bool:
        """Check if any item matches predicate."""
        return any(predicate(item) for item in self.items)

    def all(self, predicate: Callable[[T], bool]) -> bool:
        """Check if all items match predicate."""
        return all(predicate(item) for item in self.items)

    def iter(self) -> "VecIterator[T]":
        """Get iterator over items."""
        return VecIterator(self.items)


@dataclass
class VecIterator(Generic[T]):
    """Iterator over Vec items."""

    items: list[T]
    index: int = 0

    def __iter__(self) -> "VecIterator[T]":
        return self

    def __next__(self) -> T:
        if self.index >= len(self.items):
            raise StopIteration
        item = self.items[self.index]
        self.index += 1
        return item

    def next(self) -> Option[T]:
        """Get next item as Option."""
        if self.index >= len(self.items):
            return NoneValue()
        item = self.items[self.index]
        self.index += 1
        return Some(item)


@dataclass
class Pair(Generic[T, U]):
    """Generic pair of two values."""

    first: T
    second: U

    def swap(self) -> "Pair[U, T]":
        """Swap the pair elements."""
        return Pair(self.second, self.first)

    def map_first(self, f: Callable[[T], Any]) -> "Pair[Any, U]":
        """Map function over first element."""
        return Pair(f(self.first), self.second)

    def map_second(self, f: Callable[[U], Any]) -> "Pair[T, Any]":
        """Map function over second element."""
        return Pair(self.first, f(self.second))


@dataclass
class Triple(Generic[T, U]):
    """Generic triple of three values."""

    first: T
    second: U
    third: Any

    def to_tuple(self) -> tuple[T, U, Any]:
        """Convert to tuple."""
        return (self.first, self.second, self.third)


def zip_with(vec1: Vec[T], vec2: Vec[U], f: Callable[[T, U], Any]) -> Vec[Any]:
    """Zip two vectors with a combining function."""
    result: list[Any] = []
    for i in range(min(len(vec1), len(vec2))):
        a = vec1.get(i).unwrap()
        b = vec2.get(i).unwrap()
        result.append(f(a, b))
    return Vec(result)


def flatten(nested: Vec[Vec[T]]) -> Vec[T]:
    """Flatten nested Vec."""
    result: list[T] = []
    for inner in nested.items:
        result.extend(inner.items)
    return Vec(result)


def partition(vec: Vec[T], predicate: Callable[[T], bool]) -> Pair[Vec[T], Vec[T]]:
    """Partition Vec into two based on predicate."""
    left: list[T] = []
    right: list[T] = []
    for item in vec.items:
        if predicate(item):
            left.append(item)
        else:
            right.append(item)
    return Pair(Vec(left), Vec(right))


def simulate_container(operations: list[str]) -> list[str]:
    """Simulate container operations."""
    results = []
    vec: Vec[int] = Vec()
    opt: Option[int] = NoneValue()

    for op in operations:
        parts = op.split(":")
        cmd = parts[0]

        if cmd == "push":
            vec.push(int(parts[1]))
            results.append("ok")
        elif cmd == "pop":
            result = vec.pop()
            results.append(str(result.unwrap_or(-1)))
        elif cmd == "get":
            result = vec.get(int(parts[1]))
            results.append(str(result.unwrap_or(-1)))
        elif cmd == "len":
            results.append(str(len(vec)))
        elif cmd == "some":
            opt = Some(int(parts[1]))
            results.append("ok")
        elif cmd == "none":
            opt = NoneValue()
            results.append("ok")
        elif cmd == "unwrap":
            results.append(str(opt.unwrap_or(-1)))
        elif cmd == "is_some":
            results.append("1" if opt.is_some() else "0")
        elif cmd == "first":
            results.append(str(vec.first().unwrap_or(-1)))
        elif cmd == "last":
            results.append(str(vec.last().unwrap_or(-1)))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: generic_container_cli.py <command> [args...]")
        print("Commands: box, option, vec")
        return 1

    cmd = sys.argv[1]

    if cmd == "box":
        if len(sys.argv) < 3:
            print("Usage: box <value>", file=sys.stderr)
            return 1
        box = Box(sys.argv[2])
        print(f"Box({box.unwrap()})")

    elif cmd == "option":
        if len(sys.argv) < 3:
            opt: Option[str] = NoneValue()
        else:
            opt = Some(sys.argv[2])

        if opt.is_some():
            print(f"Some({opt.unwrap()})")
        else:
            print("None")

    elif cmd == "vec":
        vec: Vec[str] = Vec()
        for arg in sys.argv[2:]:
            vec.push(arg)
        print(f"Vec({', '.join(vec.items)})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
