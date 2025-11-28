#!/usr/bin/env python3
"""Typed Tuple CLI.

Tuple operations with type hints.
"""

import argparse
import sys


def create_empty_tuple() -> tuple[()]:
    """Create empty tuple."""
    return ()


def create_pair(a: int, b: int) -> tuple[int, int]:
    """Create pair tuple."""
    return (a, b)


def create_triple(a: int, b: int, c: int) -> tuple[int, int, int]:
    """Create triple tuple."""
    return (a, b, c)


def create_tuple(*items: int) -> tuple[int, ...]:
    """Create tuple from items."""
    return tuple(items)


def from_list(items: list[int]) -> tuple[int, ...]:
    """Create tuple from list."""
    return tuple(items)


def to_list(t: tuple[int, ...]) -> list[int]:
    """Convert tuple to list."""
    return list(t)


def get_first(t: tuple[int, ...]) -> int | None:
    """Get first element."""
    return t[0] if t else None


def get_second(t: tuple[int, int, ...]) -> int | None:
    """Get second element."""
    return t[1] if len(t) > 1 else None


def get_last(t: tuple[int, ...]) -> int | None:
    """Get last element."""
    return t[-1] if t else None


def get_at(t: tuple[int, ...], index: int) -> int | None:
    """Get element at index."""
    if 0 <= index < len(t):
        return t[index]
    return None


def tuple_size(t: tuple[int, ...]) -> int:
    """Get tuple size."""
    return len(t)


def is_empty(t: tuple[int, ...]) -> bool:
    """Check if tuple is empty."""
    return len(t) == 0


def contains(t: tuple[int, ...], item: int) -> bool:
    """Check if tuple contains item."""
    return item in t


def index_of(t: tuple[int, ...], item: int) -> int:
    """Get index of item, -1 if not found."""
    try:
        return t.index(item)
    except ValueError:
        return -1


def count_item(t: tuple[int, ...], item: int) -> int:
    """Count occurrences of item."""
    return t.count(item)


def slice_tuple(t: tuple[int, ...], start: int, end: int) -> tuple[int, ...]:
    """Slice tuple from start to end."""
    return t[start:end]


def concat(t1: tuple[int, ...], t2: tuple[int, ...]) -> tuple[int, ...]:
    """Concatenate two tuples."""
    return t1 + t2


def repeat(t: tuple[int, ...], n: int) -> tuple[int, ...]:
    """Repeat tuple n times."""
    return t * n


def reverse_tuple(t: tuple[int, ...]) -> tuple[int, ...]:
    """Reverse tuple."""
    return t[::-1]


def sort_tuple(t: tuple[int, ...]) -> tuple[int, ...]:
    """Sort tuple."""
    return tuple(sorted(t))


def sort_desc(t: tuple[int, ...]) -> tuple[int, ...]:
    """Sort tuple descending."""
    return tuple(sorted(t, reverse=True))


def min_tuple(t: tuple[int, ...]) -> int | None:
    """Get minimum value."""
    return min(t) if t else None


def max_tuple(t: tuple[int, ...]) -> int | None:
    """Get maximum value."""
    return max(t) if t else None


def sum_tuple(t: tuple[int, ...]) -> int:
    """Sum all values."""
    return sum(t)


def product_tuple(t: tuple[int, ...]) -> int:
    """Product of all values."""
    result = 1
    for x in t:
        result *= x
    return result


def mean_tuple(t: tuple[int, ...]) -> float | None:
    """Average of values."""
    return sum(t) / len(t) if t else None


def unique_tuple(t: tuple[int, ...]) -> tuple[int, ...]:
    """Get unique values (preserves order)."""
    seen: set[int] = set()
    result: list[int] = []
    for x in t:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return tuple(result)


def filter_gt(t: tuple[int, ...], threshold: int) -> tuple[int, ...]:
    """Filter values greater than threshold."""
    return tuple(x for x in t if x > threshold)


def filter_even(t: tuple[int, ...]) -> tuple[int, ...]:
    """Filter even values."""
    return tuple(x for x in t if x % 2 == 0)


def filter_odd(t: tuple[int, ...]) -> tuple[int, ...]:
    """Filter odd values."""
    return tuple(x for x in t if x % 2 != 0)


def map_double(t: tuple[int, ...]) -> tuple[int, ...]:
    """Double all values."""
    return tuple(x * 2 for x in t)


def map_square(t: tuple[int, ...]) -> tuple[int, ...]:
    """Square all values."""
    return tuple(x * x for x in t)


def zip_tuples(t1: tuple[int, ...], t2: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    """Zip two tuples."""
    return tuple(zip(t1, t2, strict=False))


def enumerate_tuple(t: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    """Enumerate tuple."""
    return tuple(enumerate(t))


def unpack_pair(t: tuple[int, int]) -> tuple[int, int]:
    """Unpack pair tuple."""
    return (t[0], t[1])


def swap_pair(t: tuple[int, int]) -> tuple[int, int]:
    """Swap pair elements."""
    return (t[1], t[0])


def compare_tuples(t1: tuple[int, ...], t2: tuple[int, ...]) -> int:
    """Compare tuples lexicographically (-1, 0, 1)."""
    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    return 0


def take(t: tuple[int, ...], n: int) -> tuple[int, ...]:
    """Take first n elements."""
    return t[:n]


def drop(t: tuple[int, ...], n: int) -> tuple[int, ...]:
    """Drop first n elements."""
    return t[n:]


def take_while_positive(t: tuple[int, ...]) -> tuple[int, ...]:
    """Take while elements are positive."""
    result: list[int] = []
    for x in t:
        if x <= 0:
            break
        result.append(x)
    return tuple(result)


def split_at(t: tuple[int, ...], index: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Split tuple at index."""
    return (t[:index], t[index:])


def partition(t: tuple[int, ...], pivot: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Partition into (< pivot, >= pivot)."""
    less = tuple(x for x in t if x < pivot)
    greater_eq = tuple(x for x in t if x >= pivot)
    return (less, greater_eq)


def main() -> int:
    parser = argparse.ArgumentParser(description="Typed tuple CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # create
    create_p = subparsers.add_parser("create", help="Create tuple")
    create_p.add_argument("items", nargs="*", type=int, help="Items")

    # pair
    pair_p = subparsers.add_parser("pair", help="Create pair")
    pair_p.add_argument("a", type=int, help="First element")
    pair_p.add_argument("b", type=int, help="Second element")

    # stats
    stats_p = subparsers.add_parser("stats", help="Show stats")
    stats_p.add_argument("tuple", help="Comma-separated tuple")

    args = parser.parse_args()

    def parse_tuple(s: str) -> tuple[int, ...]:
        return tuple(int(x.strip()) for x in s.split(",") if x.strip())

    if args.command == "create":
        t = create_tuple(*args.items)
        print(t)

    elif args.command == "pair":
        t = create_pair(args.a, args.b)
        print(t)

    elif args.command == "stats":
        t = parse_tuple(args.tuple)
        print(f"Size: {tuple_size(t)}")
        print(f"Sum: {sum_tuple(t)}")
        print(f"Max: {max_tuple(t)}")
        print(f"Min: {min_tuple(t)}")
        print(f"Mean: {mean_tuple(t)}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
