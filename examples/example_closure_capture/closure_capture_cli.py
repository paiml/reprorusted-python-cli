#!/usr/bin/env python3
"""Closure Capture CLI.

Closures capturing outer variables patterns.
"""

import argparse
import sys
from collections.abc import Callable


def make_adder(n: int) -> Callable[[int], int]:
    """Create function that adds n."""

    def adder(x: int) -> int:
        return x + n

    return adder


def make_multiplier(n: int) -> Callable[[int], int]:
    """Create function that multiplies by n."""

    def multiplier(x: int) -> int:
        return x * n

    return multiplier


def make_power(exp: int) -> Callable[[int], int]:
    """Create function that raises to power exp."""

    def power(x: int) -> int:
        return x**exp

    return power


def make_range_checker(min_val: int, max_val: int) -> Callable[[int], bool]:
    """Create range checker function."""

    def checker(x: int) -> bool:
        return min_val <= x <= max_val

    return checker


def make_prefix_formatter(prefix: str) -> Callable[[str], str]:
    """Create string formatter with prefix."""

    def formatter(s: str) -> str:
        return f"{prefix}{s}"

    return formatter


def make_suffix_formatter(suffix: str) -> Callable[[str], str]:
    """Create string formatter with suffix."""

    def formatter(s: str) -> str:
        return f"{s}{suffix}"

    return formatter


def make_counter() -> Callable[[], int]:
    """Create counter that increments each call."""
    count = [0]  # Use list to allow mutation in closure

    def counter() -> int:
        count[0] += 1
        return count[0]

    return counter


def make_accumulator(initial: int) -> tuple[Callable[[int], int], Callable[[], int]]:
    """Create accumulator with add and get functions."""
    total = [initial]

    def add(x: int) -> int:
        total[0] += x
        return total[0]

    def get() -> int:
        return total[0]

    return (add, get)


def make_threshold_filter(threshold: int) -> Callable[[list[int]], list[int]]:
    """Create filter for values above threshold."""

    def filter_fn(items: list[int]) -> list[int]:
        return [x for x in items if x > threshold]

    return filter_fn


def make_validator(rules: list[Callable[[str], bool]]) -> Callable[[str], bool]:
    """Create validator that checks all rules."""

    def validate(value: str) -> bool:
        return all(rule(value) for rule in rules)

    return validate


def make_transformer_chain(fns: list[Callable[[int], int]]) -> Callable[[int], int]:
    """Create chain of transformers."""

    def transform(x: int) -> int:
        result = x
        for fn in fns:
            result = fn(result)
        return result

    return transform


def make_cache() -> tuple[Callable[[str, int], None], Callable[[str], int | None]]:
    """Create simple cache with set and get."""
    cache: dict[str, int] = {}

    def set_value(key: str, value: int) -> None:
        cache[key] = value

    def get_value(key: str) -> int | None:
        return cache.get(key)

    return (set_value, get_value)


def make_rate_limiter(max_calls: int) -> Callable[[], bool]:
    """Create rate limiter that allows max_calls."""
    calls = [0]

    def check() -> bool:
        if calls[0] >= max_calls:
            return False
        calls[0] += 1
        return True

    return check


def make_toggler(initial: bool) -> Callable[[], bool]:
    """Create toggle function."""
    state = [initial]

    def toggle() -> bool:
        state[0] = not state[0]
        return state[0]

    return toggle


def make_once() -> Callable[[Callable[[], int]], Callable[[], int]]:
    """Create function that runs inner function only once."""

    def once_wrapper(fn: Callable[[], int]) -> Callable[[], int]:
        called = [False]
        result: list[int] = []

        def wrapped() -> int:
            if not called[0]:
                called[0] = True
                result.append(fn())
            return result[0]

        return wrapped

    return once_wrapper


def make_comparator(key: str) -> Callable[[dict[str, int], dict[str, int]], int]:
    """Create comparator function for dict key."""

    def compare(a: dict[str, int], b: dict[str, int]) -> int:
        va = a.get(key, 0)
        vb = b.get(key, 0)
        if va < vb:
            return -1
        elif va > vb:
            return 1
        return 0

    return compare


def make_default_factory(default: int) -> Callable[[dict[str, int], str], int]:
    """Create function that gets with default."""

    def getter(d: dict[str, int], key: str) -> int:
        return d.get(key, default)

    return getter


def make_bounded_counter(
    min_val: int, max_val: int
) -> tuple[Callable[[], int], Callable[[], int], Callable[[], int]]:
    """Create bounded counter with inc, dec, get."""
    value = [min_val]

    def inc() -> int:
        if value[0] < max_val:
            value[0] += 1
        return value[0]

    def dec() -> int:
        if value[0] > min_val:
            value[0] -= 1
        return value[0]

    def get() -> int:
        return value[0]

    return (inc, dec, get)


def make_string_builder() -> tuple[Callable[[str], None], Callable[[], str]]:
    """Create string builder with append and build."""
    parts: list[str] = []

    def append(s: str) -> None:
        parts.append(s)

    def build() -> str:
        return "".join(parts)

    return (append, build)


def compose(f: Callable[[int], int], g: Callable[[int], int]) -> Callable[[int], int]:
    """Compose two functions: (f . g)(x) = f(g(x))."""

    def composed(x: int) -> int:
        return f(g(x))

    return composed


def apply_n_times(f: Callable[[int], int], n: int) -> Callable[[int], int]:
    """Apply function n times."""

    def applied(x: int) -> int:
        result = x
        for _ in range(n):
            result = f(result)
        return result

    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description="Closure capture CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # adder
    add_p = subparsers.add_parser("adder", help="Create adder")
    add_p.add_argument("n", type=int)
    add_p.add_argument("x", type=int)

    # multiplier
    mul_p = subparsers.add_parser("multiplier", help="Create multiplier")
    mul_p.add_argument("n", type=int)
    mul_p.add_argument("x", type=int)

    # counter
    cnt_p = subparsers.add_parser("counter", help="Test counter")
    cnt_p.add_argument("--calls", type=int, default=3)

    # filter
    filt_p = subparsers.add_parser("filter", help="Filter numbers")
    filt_p.add_argument("threshold", type=int)
    filt_p.add_argument("items", type=int, nargs="+")

    args = parser.parse_args()

    if args.command == "adder":
        adder = make_adder(args.n)
        print(f"{args.x} + {args.n} = {adder(args.x)}")

    elif args.command == "multiplier":
        multiplier = make_multiplier(args.n)
        print(f"{args.x} * {args.n} = {multiplier(args.x)}")

    elif args.command == "counter":
        counter = make_counter()
        for _ in range(args.calls):
            print(f"Count: {counter()}")

    elif args.command == "filter":
        filter_fn = make_threshold_filter(args.threshold)
        result = filter_fn(args.items)
        print(f"Filtered: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
