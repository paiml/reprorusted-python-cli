"""Currying and Partial Application CLI.

Demonstrates currying, partial application, and function manipulation.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial, reduce
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def curry2(f: Callable[[T, U], V]) -> Callable[[T], Callable[[U], V]]:
    """Curry a two-argument function."""

    def curried(a: T) -> Callable[[U], V]:
        def inner(b: U) -> V:
            return f(a, b)

        return inner

    return curried


def curry3(f: Callable[[T, U, V], Any]) -> Callable[[T], Callable[[U], Callable[[V], Any]]]:
    """Curry a three-argument function."""

    def c1(a: T) -> Callable[[U], Callable[[V], Any]]:
        def c2(b: U) -> Callable[[V], Any]:
            def c3(c: V) -> Any:
                return f(a, b, c)

            return c3

        return c2

    return c1


def uncurry2(f: Callable[[T], Callable[[U], V]]) -> Callable[[T, U], V]:
    """Uncurry a curried two-argument function."""

    def uncurried(a: T, b: U) -> V:
        return f(a)(b)

    return uncurried


def uncurry3(f: Callable[[T], Callable[[U], Callable[[V], Any]]]) -> Callable[[T, U, V], Any]:
    """Uncurry a curried three-argument function."""

    def uncurried(a: T, b: U, c: V) -> Any:
        return f(a)(b)(c)

    return uncurried


@dataclass
class Curried:
    """Wrapper for auto-currying functions."""

    func: Callable
    arity: int
    args: tuple = ()

    def __call__(self, *args: Any) -> Any:
        new_args = self.args + args
        if len(new_args) >= self.arity:
            return self.func(*new_args)
        return Curried(self.func, self.arity, new_args)

    def __repr__(self) -> str:
        return f"Curried({self.func.__name__}, {len(self.args)}/{self.arity})"


def curry(f: Callable, arity: int | None = None) -> Curried:
    """Auto-curry a function with specified arity."""
    if arity is None:
        # Try to detect arity from signature
        import inspect

        sig = inspect.signature(f)
        arity = len(sig.parameters)
    return Curried(f, arity)


# Partial application helpers
def partial_right(f: Callable, *args: Any) -> Callable:
    """Partial application from the right."""

    def applied(*left_args: Any) -> Any:
        return f(*left_args, *args)

    return applied


def partial_left(f: Callable, *args: Any) -> Callable:
    """Partial application from the left (same as functools.partial)."""
    return partial(f, *args)


def flip(f: Callable[[T, U], V]) -> Callable[[U, T], V]:
    """Flip the arguments of a two-argument function."""

    def flipped(b: U, a: T) -> V:
        return f(a, b)

    return flipped


def const(x: T) -> Callable[..., T]:
    """Return a function that ignores its arguments and returns x."""

    def constant(*args: Any, **kwargs: Any) -> T:
        return x

    return constant


def identity(x: T) -> T:
    """Identity function."""
    return x


# Arithmetic curried functions
@curry
def add(a: int, b: int) -> int:
    """Curried addition."""
    return a + b


@curry
def subtract(a: int, b: int) -> int:
    """Curried subtraction (a - b)."""
    return a - b


@curry
def multiply(a: int, b: int) -> int:
    """Curried multiplication."""
    return a * b


@curry
def divide(a: float, b: float) -> float:
    """Curried division (a / b)."""
    return a / b


@curry
def modulo(a: int, b: int) -> int:
    """Curried modulo (a % b)."""
    return a % b


@curry
def power(base: float, exp: float) -> float:
    """Curried power (base ** exp)."""
    return base**exp


# String curried functions
@curry
def concat(a: str, b: str) -> str:
    """Curried string concatenation."""
    return a + b


@curry
def split(sep: str, s: str) -> list[str]:
    """Curried string split."""
    return s.split(sep)


@curry
def join(sep: str, lst: list[str]) -> str:
    """Curried string join."""
    return sep.join(lst)


@curry
def replace(old: str, new: str, s: str) -> str:
    """Curried string replace."""
    return s.replace(old, new)


@curry
def starts_with(prefix: str, s: str) -> bool:
    """Curried startswith check."""
    return s.startswith(prefix)


@curry
def ends_with(suffix: str, s: str) -> bool:
    """Curried endswith check."""
    return s.endswith(suffix)


# List curried functions
@curry
def map_func(f: Callable[[T], U], lst: list[T]) -> list[U]:
    """Curried map."""
    return [f(x) for x in lst]


@curry
def filter_func(pred: Callable[[T], bool], lst: list[T]) -> list[T]:
    """Curried filter."""
    return [x for x in lst if pred(x)]


@curry
def reduce_func(f: Callable[[T, T], T], initial: T, lst: list[T]) -> T:
    """Curried reduce."""
    return reduce(f, lst, initial)


@curry
def take(n: int, lst: list[T]) -> list[T]:
    """Curried take."""
    return lst[:n]


@curry
def drop(n: int, lst: list[T]) -> list[T]:
    """Curried drop."""
    return lst[n:]


@curry
def nth(n: int, lst: list[T]) -> T:
    """Curried nth element."""
    return lst[n]


# Comparison curried functions
@curry
def equals(a: Any, b: Any) -> bool:
    """Curried equality check."""
    return a == b


@curry
def greater_than(a: Any, b: Any) -> bool:
    """Curried greater than (b > a)."""
    return b > a


@curry
def less_than(a: Any, b: Any) -> bool:
    """Curried less than (b < a)."""
    return b < a


@curry
def clamp(min_val: float, max_val: float, x: float) -> float:
    """Curried clamp."""
    return max(min_val, min(max_val, x))


# Function composition with currying
def compose(*funcs: Callable) -> Callable:
    """Compose functions right to left."""

    def composed(x: Any) -> Any:
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result

    return composed


def pipe(*funcs: Callable) -> Callable:
    """Pipe functions left to right."""

    def piped(x: Any) -> Any:
        result = x
        for f in funcs:
            result = f(result)
        return result

    return piped


# Point-free style helpers
def prop(name: str) -> Callable[[Any], Any]:
    """Get property from object."""
    return lambda obj: getattr(obj, name, obj.get(name) if isinstance(obj, dict) else None)


def invoke(method: str, *args: Any) -> Callable[[Any], Any]:
    """Invoke method on object."""
    return lambda obj: getattr(obj, method)(*args)


def simulate_curry(operations: list[str]) -> list[str]:
    """Simulate currying operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "add":
            args = list(map(int, parts[1].split(",")))
            if len(args) == 2:
                results.append(str(add(args[0])(args[1])))
            else:
                results.append(str(add(args[0])))
        elif cmd == "multiply":
            args = list(map(int, parts[1].split(",")))
            results.append(str(multiply(args[0])(args[1])))
        elif cmd == "add_partial":
            # Create add5 = add(5), then apply to second arg
            n, x = map(int, parts[1].split(","))
            add_n = add(n)
            results.append(str(add_n(x)))
        elif cmd == "compose":
            # compose double, add5 on value
            val = int(parts[1])
            double = multiply(2)
            add5 = add(5)
            f = compose(double, add5)  # double(add5(x))
            results.append(str(f(val)))
        elif cmd == "pipe":
            val = int(parts[1])
            double = multiply(2)
            add5 = add(5)
            f = pipe(double, add5)  # add5(double(x))
            results.append(str(f(val)))
        elif cmd == "map_double":
            lst = list(map(int, parts[1].split(",")))
            double = multiply(2)
            result = map_func(double)(lst)
            results.append(str(result))
        elif cmd == "filter_positive":
            lst = list(map(int, parts[1].split(",")))
            is_positive = greater_than(0)
            result = filter_func(is_positive)(lst)
            results.append(str(result))
        elif cmd == "clamp":
            args = list(map(float, parts[1].split(",")))
            result = clamp(args[0])(args[1])(args[2])
            results.append(str(result))
        elif cmd == "split_join":
            # Split by comma, join by dash
            s = parts[1]
            split_comma = split(",")
            join_dash = join("-")
            f = pipe(split_comma, join_dash)
            results.append(f(s))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: func_curry_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "add" and len(sys.argv) > 3:
        a, b = int(sys.argv[2]), int(sys.argv[3])
        print(f"Result: {add(a)(b)}")
    elif cmd == "add-partial" and len(sys.argv) > 3:
        n, x = int(sys.argv[2]), int(sys.argv[3])
        add_n = add(n)
        print(f"add{n}({x}) = {add_n(x)}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
