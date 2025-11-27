"""Maybe/Option Monad CLI.

Demonstrates the Maybe monad for handling optional values.
"""

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class Maybe(ABC, Generic[T]):
    """Maybe monad - represents optional values."""

    @abstractmethod
    def is_some(self) -> bool:
        """Check if value is present."""
        pass

    @abstractmethod
    def is_none(self) -> bool:
        """Check if value is absent."""
        pass

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Maybe[U]":
        """Apply function to value if present."""
        pass

    @abstractmethod
    def flat_map(self, f: Callable[[T], "Maybe[U]"]) -> "Maybe[U]":
        """Apply function that returns Maybe."""
        pass

    @abstractmethod
    def filter(self, pred: Callable[[T], bool]) -> "Maybe[T]":
        """Keep value only if predicate is true."""
        pass

    @abstractmethod
    def get(self) -> T:
        """Get value or raise."""
        pass

    @abstractmethod
    def get_or(self, default: T) -> T:
        """Get value or default."""
        pass

    @abstractmethod
    def get_or_else(self, f: Callable[[], T]) -> T:
        """Get value or compute default."""
        pass

    @abstractmethod
    def or_else(self, f: Callable[[], "Maybe[T]"]) -> "Maybe[T]":
        """Return self if Some, otherwise compute alternative."""
        pass

    @abstractmethod
    def to_list(self) -> list[T]:
        """Convert to list (empty or single element)."""
        pass


@dataclass(frozen=True)
class Some(Maybe[T]):
    """Represents a present value."""

    value: T

    def is_some(self) -> bool:
        return True

    def is_none(self) -> bool:
        return False

    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        return Some(f(self.value))

    def flat_map(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return f(self.value)

    def filter(self, pred: Callable[[T], bool]) -> Maybe[T]:
        return self if pred(self.value) else Nothing()

    def get(self) -> T:
        return self.value

    def get_or(self, default: T) -> T:
        return self.value

    def get_or_else(self, f: Callable[[], T]) -> T:
        return self.value

    def or_else(self, f: Callable[[], Maybe[T]]) -> Maybe[T]:
        return self

    def to_list(self) -> list[T]:
        return [self.value]

    def __repr__(self) -> str:
        return f"Some({self.value!r})"


class Nothing(Maybe[T]):
    """Represents an absent value."""

    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        return Nothing()

    def flat_map(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return Nothing()

    def filter(self, pred: Callable[[T], bool]) -> Maybe[T]:
        return Nothing()

    def get(self) -> T:
        raise ValueError("Cannot get value from Nothing")

    def get_or(self, default: T) -> T:
        return default

    def get_or_else(self, f: Callable[[], T]) -> T:
        return f()

    def or_else(self, f: Callable[[], Maybe[T]]) -> Maybe[T]:
        return f()

    def to_list(self) -> list[T]:
        return []

    def __repr__(self) -> str:
        return "Nothing"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Nothing)

    def __hash__(self) -> int:
        return hash("Nothing")


# Constructors
def some(value: T) -> Maybe[T]:
    """Create a Some value."""
    return Some(value)


def nothing() -> Maybe[T]:
    """Create a Nothing value."""
    return Nothing()


def maybe(value: T | None) -> Maybe[T]:
    """Create Maybe from nullable value."""
    if value is None:
        return Nothing()
    return Some(value)


def from_optional(value: T | None) -> Maybe[T]:
    """Create Maybe from optional value."""
    return maybe(value)


# Utility functions
def safe_div(a: float, b: float) -> Maybe[float]:
    """Safe division returning Maybe."""
    if b == 0:
        return Nothing()
    return Some(a / b)


def safe_int(s: str) -> Maybe[int]:
    """Safe string to int conversion."""
    try:
        return Some(int(s))
    except ValueError:
        return Nothing()


def safe_float(s: str) -> Maybe[float]:
    """Safe string to float conversion."""
    try:
        return Some(float(s))
    except ValueError:
        return Nothing()


def safe_head(lst: list[T]) -> Maybe[T]:
    """Get first element safely."""
    if lst:
        return Some(lst[0])
    return Nothing()


def safe_last(lst: list[T]) -> Maybe[T]:
    """Get last element safely."""
    if lst:
        return Some(lst[-1])
    return Nothing()


def safe_get(d: dict[str, T], key: str) -> Maybe[T]:
    """Get dict value safely."""
    if key in d:
        return Some(d[key])
    return Nothing()


def safe_index(lst: list[T], idx: int) -> Maybe[T]:
    """Get list element by index safely."""
    if 0 <= idx < len(lst):
        return Some(lst[idx])
    return Nothing()


# Lifting functions
def lift(f: Callable[[T], U]) -> Callable[[Maybe[T]], Maybe[U]]:
    """Lift a function to work with Maybe."""

    def lifted(m: Maybe[T]) -> Maybe[U]:
        return m.map(f)

    return lifted


def lift2(f: Callable[[T, U], V]) -> Callable[[Maybe[T], Maybe[U]], Maybe[V]]:
    """Lift a binary function to work with Maybe."""

    def lifted(m1: Maybe[T], m2: Maybe[U]) -> Maybe[V]:
        return m1.flat_map(lambda a: m2.map(lambda b: f(a, b)))

    return lifted


# Sequence operations
def sequence(maybes: list[Maybe[T]]) -> Maybe[list[T]]:
    """Convert list of Maybes to Maybe of list."""
    results: list[T] = []
    for m in maybes:
        if m.is_none():
            return Nothing()
        results.append(m.get())
    return Some(results)


def traverse(f: Callable[[T], Maybe[U]], lst: list[T]) -> Maybe[list[U]]:
    """Map function over list, collecting into Maybe."""
    return sequence([f(x) for x in lst])


def cat_maybes(maybes: list[Maybe[T]]) -> list[T]:
    """Extract all Some values from list."""
    return [m.get() for m in maybes if m.is_some()]


def simulate_maybe(operations: list[str]) -> list[str]:
    """Simulate maybe operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "some":
            m = some(int(parts[1]))
            results.append(repr(m))
        elif cmd == "nothing":
            m = nothing()
            results.append(repr(m))
        elif cmd == "maybe":
            val = parts[1] if parts[1] != "None" else None
            m = maybe(int(val) if val else None)
            results.append(repr(m))
        elif cmd == "safe_div":
            a, b = map(float, parts[1].split(","))
            m = safe_div(a, b)
            results.append(repr(m))
        elif cmd == "safe_int":
            m = safe_int(parts[1])
            results.append(repr(m))
        elif cmd == "map":
            val, func = parts[1].split(",")
            m = some(int(val))
            if func == "double":
                m = m.map(lambda x: x * 2)
            results.append(repr(m))
        elif cmd == "filter":
            val, pred = parts[1].split(",")
            m = some(int(val))
            if pred == "even":
                m = m.filter(lambda x: x % 2 == 0)
            results.append(repr(m))
        elif cmd == "get_or":
            val, default = parts[1].split(",")
            if val == "nothing":
                m: Maybe[int] = nothing()
            else:
                m = some(int(val))
            results.append(str(m.get_or(int(default))))
        elif cmd == "sequence":
            vals = parts[1].split(",")
            maybes = [some(int(v)) if v != "nothing" else nothing() for v in vals]
            result = sequence(maybes)
            results.append(repr(result))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: func_maybe_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "safe-div" and len(sys.argv) > 3:
        a, b = float(sys.argv[2]), float(sys.argv[3])
        result = safe_div(a, b)
        print(f"Result: {result}")
    elif cmd == "safe-int" and len(sys.argv) > 2:
        result = safe_int(sys.argv[2])
        print(f"Result: {result}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
