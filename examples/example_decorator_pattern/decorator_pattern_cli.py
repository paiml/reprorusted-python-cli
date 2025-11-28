#!/usr/bin/env python3
"""Decorator Pattern CLI.

Function decorator patterns (wrapper functions).
"""

import argparse
import sys
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def timing_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that measures execution time."""

    def wrapper(*args: object, **kwargs: object) -> T:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f}s")
        return result

    return wrapper


def logging_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that logs function calls."""

    def wrapper(*args: object, **kwargs: object) -> T:
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result

    return wrapper


def retry_decorator(max_retries: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that retries on failure."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: object, **kwargs: object) -> T:
            last_error: Exception | None = None
            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
            if last_error:
                raise last_error
            raise RuntimeError("No attempts made")

        return wrapper

    return decorator


def cache_decorator(func: Callable[[int], int]) -> Callable[[int], int]:
    """Simple memoization decorator for single int arg."""
    cache: dict[int, int] = {}

    def wrapper(n: int) -> int:
        if n not in cache:
            cache[n] = func(n)
        return cache[n]

    return wrapper


def validate_positive(func: Callable[[int], int]) -> Callable[[int], int]:
    """Decorator that validates positive input."""

    def wrapper(n: int) -> int:
        if n < 0:
            raise ValueError(f"Expected positive, got {n}")
        return func(n)

    return wrapper


def validate_non_empty(func: Callable[[str], str]) -> Callable[[str], str]:
    """Decorator that validates non-empty string."""

    def wrapper(s: str) -> str:
        if not s:
            raise ValueError("Expected non-empty string")
        return func(s)

    return wrapper


def count_calls(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that counts function calls."""
    count = [0]

    def wrapper(*args: object, **kwargs: object) -> T:
        count[0] += 1
        return func(*args, **kwargs)

    wrapper.call_count = lambda: count[0]  # type: ignore
    return wrapper


def once(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that only allows one call."""
    called = [False]
    result: list[T] = []

    def wrapper(*args: object, **kwargs: object) -> T:
        if not called[0]:
            called[0] = True
            result.append(func(*args, **kwargs))
        return result[0]

    return wrapper


def deprecated(message: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that marks function as deprecated."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: object, **kwargs: object) -> T:
            print(f"Warning: {func.__name__} is deprecated. {message}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def trace(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that traces function entry/exit."""

    def wrapper(*args: object, **kwargs: object) -> T:
        print(f"-> Entering {func.__name__}")
        result = func(*args, **kwargs)
        print(f"<- Exiting {func.__name__}")
        return result

    return wrapper


def type_check_int(func: Callable[[int, int], int]) -> Callable[[int, int], int]:
    """Type checking decorator for int, int -> int."""

    def wrapper(a: int, b: int) -> int:
        if not isinstance(a, int) or not isinstance(b, int):
            raise TypeError("Arguments must be integers")
        result = func(a, b)
        if not isinstance(result, int):
            raise TypeError("Result must be integer")
        return result

    return wrapper


def clamp_result(min_val: int, max_val: int) -> Callable[[Callable[..., int]], Callable[..., int]]:
    """Decorator that clamps result to range."""

    def decorator(func: Callable[..., int]) -> Callable[..., int]:
        def wrapper(*args: object, **kwargs: object) -> int:
            result = func(*args, **kwargs)
            return max(min_val, min(max_val, result))

        return wrapper

    return decorator


# Example functions to decorate
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def factorial(n: int) -> int:
    """Calculate factorial."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n: int) -> int:
    """Calculate fibonacci (naive)."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def process_text(text: str) -> str:
    """Process text."""
    return text.upper()


# Decorated versions
timed_add = timing_decorator(add)
logged_multiply = logging_decorator(multiply)
cached_fibonacci = cache_decorator(fibonacci)
validated_factorial = validate_positive(factorial)
traced_process = trace(process_text)


# Manual decoration examples
def apply_decorator(
    func: Callable[[int], int], decorator: Callable[[Callable[[int], int]], Callable[[int], int]]
) -> Callable[[int], int]:
    """Apply a decorator to a function."""
    return decorator(func)


def chain_decorators(
    func: Callable[[int], int],
    decorators: list[Callable[[Callable[[int], int]], Callable[[int], int]]],
) -> Callable[[int], int]:
    """Apply multiple decorators in order."""
    result = func
    for dec in decorators:
        result = dec(result)
    return result


def make_decorator_with_args(prefix: str) -> Callable[[Callable[[str], str]], Callable[[str], str]]:
    """Create a decorator with arguments."""

    def decorator(func: Callable[[str], str]) -> Callable[[str], str]:
        def wrapper(s: str) -> str:
            return f"{prefix}: {func(s)}"

        return wrapper

    return decorator


def conditional_decorator(
    condition: bool, decorator: Callable[[Callable[..., T]], Callable[..., T]]
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Apply decorator only if condition is true."""

    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        if condition:
            return decorator(func)
        return func

    return wrapper


def main() -> int:
    parser = argparse.ArgumentParser(description="Decorator pattern CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # timed
    timed_p = subparsers.add_parser("timed", help="Timed addition")
    timed_p.add_argument("a", type=int)
    timed_p.add_argument("b", type=int)

    # logged
    logged_p = subparsers.add_parser("logged", help="Logged multiply")
    logged_p.add_argument("a", type=int)
    logged_p.add_argument("b", type=int)

    # cached
    cached_p = subparsers.add_parser("cached", help="Cached fibonacci")
    cached_p.add_argument("n", type=int)

    # validated
    val_p = subparsers.add_parser("validated", help="Validated factorial")
    val_p.add_argument("n", type=int)

    args = parser.parse_args()

    if args.command == "timed":
        result = timed_add(args.a, args.b)
        print(f"Result: {result}")

    elif args.command == "logged":
        result = logged_multiply(args.a, args.b)
        print(f"Result: {result}")

    elif args.command == "cached":
        result = cached_fibonacci(args.n)
        print(f"fib({args.n}) = {result}")

    elif args.command == "validated":
        try:
            result = validated_factorial(args.n)
            print(f"{args.n}! = {result}")
        except ValueError as e:
            print(f"Error: {e}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
