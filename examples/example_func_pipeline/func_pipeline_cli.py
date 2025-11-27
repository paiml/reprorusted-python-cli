"""Functional Pipeline CLI.

Demonstrates function composition and pipeline patterns.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def pipe(*funcs: Callable) -> Callable:
    """Create a pipeline that applies functions left to right.

    pipe(f, g, h)(x) == h(g(f(x)))
    """

    def pipeline(value):
        result = value
        for func in funcs:
            result = func(result)
        return result

    return pipeline


def compose(*funcs: Callable) -> Callable:
    """Create a composition that applies functions right to left.

    compose(f, g, h)(x) == f(g(h(x)))
    """

    def composed(value):
        result = value
        for func in reversed(funcs):
            result = func(result)
        return result

    return composed


def identity(x: T) -> T:
    """Identity function."""
    return x


def constant(value: T) -> Callable[..., T]:
    """Return a function that always returns value."""

    def const(*args, **kwargs):
        return value

    return const


def flip(f: Callable[[T, U], V]) -> Callable[[U, T], V]:
    """Flip the arguments of a binary function."""

    def flipped(b: U, a: T) -> V:
        return f(a, b)

    return flipped


def apply(f: Callable[[T], U], x: T) -> U:
    """Apply a function to a value."""
    return f(x)


def tap(f: Callable[[T], None]) -> Callable[[T], T]:
    """Execute a side effect and return the original value."""

    def tapped(x: T) -> T:
        f(x)
        return x

    return tapped


@dataclass
class Pipeline(Generic[T]):
    """Fluent pipeline builder."""

    value: T

    def map(self, f: Callable[[T], U]) -> "Pipeline[U]":
        """Apply a function to the value."""
        return Pipeline(f(self.value))

    def tap(self, f: Callable[[T], None]) -> "Pipeline[T]":
        """Execute a side effect."""
        f(self.value)
        return self

    def filter(self, pred: Callable[[T], bool]) -> "Pipeline[T | None]":
        """Filter based on predicate."""
        if pred(self.value):
            return Pipeline(self.value)
        return Pipeline(None)

    def get(self) -> T:
        """Get the final value."""
        return self.value

    def get_or(self, default: T) -> T:
        """Get value or default if None."""
        return self.value if self.value is not None else default


def pipeline(value: T) -> Pipeline[T]:
    """Create a pipeline starting with value."""
    return Pipeline(value)


# Common transformations
def add(n: int) -> Callable[[int], int]:
    """Create a function that adds n."""
    return lambda x: x + n


def multiply(n: int) -> Callable[[int], int]:
    """Create a function that multiplies by n."""
    return lambda x: x * n


def negate(x: int) -> int:
    """Negate a number."""
    return -x


def double(x: int) -> int:
    """Double a number."""
    return x * 2


def square(x: int) -> int:
    """Square a number."""
    return x * x


def is_even(x: int) -> bool:
    """Check if number is even."""
    return x % 2 == 0


def is_positive(x: int) -> bool:
    """Check if number is positive."""
    return x > 0


# String transformations
def upper(s: str) -> str:
    """Convert to uppercase."""
    return s.upper()


def lower(s: str) -> str:
    """Convert to lowercase."""
    return s.lower()


def strip(s: str) -> str:
    """Strip whitespace."""
    return s.strip()


def reverse(s: str) -> str:
    """Reverse a string."""
    return s[::-1]


def prefix(p: str) -> Callable[[str], str]:
    """Add prefix to string."""
    return lambda s: p + s


def suffix(s: str) -> Callable[[str], str]:
    """Add suffix to string."""
    return lambda x: x + s


def split_by(sep: str) -> Callable[[str], list[str]]:
    """Split string by separator."""
    return lambda s: s.split(sep)


def join_by(sep: str) -> Callable[[list[str]], str]:
    """Join list by separator."""
    return lambda lst: sep.join(lst)


# List transformations
def map_list(f: Callable[[T], U]) -> Callable[[list[T]], list[U]]:
    """Map function over list."""
    return lambda lst: [f(x) for x in lst]


def filter_list(pred: Callable[[T], bool]) -> Callable[[list[T]], list[T]]:
    """Filter list by predicate."""
    return lambda lst: [x for x in lst if pred(x)]


def reduce_list(f: Callable[[T, T], T], initial: T) -> Callable[[list[T]], T]:
    """Reduce list with function."""

    def reducer(lst: list[T]) -> T:
        result = initial
        for x in lst:
            result = f(result, x)
        return result

    return reducer


def head(lst: list[T]) -> T | None:
    """Get first element."""
    return lst[0] if lst else None


def tail(lst: list[T]) -> list[T]:
    """Get all but first element."""
    return lst[1:] if lst else []


def take(n: int) -> Callable[[list[T]], list[T]]:
    """Take first n elements."""
    return lambda lst: lst[:n]


def drop(n: int) -> Callable[[list[T]], list[T]]:
    """Drop first n elements."""
    return lambda lst: lst[n:]


def simulate_pipeline(operations: list[str]) -> list[str]:
    """Simulate pipeline operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "pipe":
            # pipe:5,double,add(3)
            args = parts[1].split(",")
            value = int(args[0])
            funcs = []
            for a in args[1:]:
                if a == "double":
                    funcs.append(double)
                elif a == "square":
                    funcs.append(square)
                elif a == "negate":
                    funcs.append(negate)
                elif a.startswith("add("):
                    n = int(a[4:-1])
                    funcs.append(add(n))
                elif a.startswith("multiply("):
                    n = int(a[9:-1])
                    funcs.append(multiply(n))
            result = pipe(*funcs)(value)
            results.append(str(result))

        elif cmd == "compose":
            args = parts[1].split(",")
            value = int(args[0])
            funcs = []
            for a in args[1:]:
                if a == "double":
                    funcs.append(double)
                elif a == "square":
                    funcs.append(square)
                elif a.startswith("add("):
                    n = int(a[4:-1])
                    funcs.append(add(n))
            result = compose(*funcs)(value)
            results.append(str(result))

        elif cmd == "string_pipe":
            args = parts[1].split(",")
            value = args[0]
            funcs = []
            for a in args[1:]:
                if a == "upper":
                    funcs.append(upper)
                elif a == "lower":
                    funcs.append(lower)
                elif a == "strip":
                    funcs.append(strip)
                elif a == "reverse":
                    funcs.append(reverse)
            result = pipe(*funcs)(value)
            results.append(result)

        elif cmd == "pipeline":
            # Fluent API: pipeline:5,double,add(3)
            args = parts[1].split(",")
            p = pipeline(int(args[0]))
            for a in args[1:]:
                if a == "double":
                    p = p.map(double)
                elif a.startswith("add("):
                    n = int(a[4:-1])
                    p = p.map(add(n))
            results.append(str(p.get()))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: func_pipeline_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "pipe" and len(sys.argv) > 2:
        # Example: pipe 5 double square
        value = int(sys.argv[2])
        funcs = []
        for arg in sys.argv[3:]:
            if arg == "double":
                funcs.append(double)
            elif arg == "square":
                funcs.append(square)
        result = pipe(*funcs)(value)
        print(f"Result: {result}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
