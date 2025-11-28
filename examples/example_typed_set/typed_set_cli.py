#!/usr/bin/env python3
"""Typed Set CLI.

Set operations with type hints.
"""

import argparse
import sys


def create_empty_set() -> set[int]:
    """Create empty typed set."""
    return set()


def create_set(items: list[int]) -> set[int]:
    """Create set from items."""
    return set(items)


def add_item(s: set[int], item: int) -> set[int]:
    """Add item to set (returns new set)."""
    result = s.copy()
    result.add(item)
    return result


def remove_item(s: set[int], item: int) -> set[int]:
    """Remove item from set (returns new set)."""
    result = s.copy()
    result.discard(item)
    return result


def pop_item(s: set[int]) -> tuple[int | None, set[int]]:
    """Pop arbitrary item, return (item, new_set)."""
    if not s:
        return (None, set())
    result = s.copy()
    item = result.pop()
    return (item, result)


def contains(s: set[int], item: int) -> bool:
    """Check if set contains item."""
    return item in s


def set_size(s: set[int]) -> int:
    """Get set size."""
    return len(s)


def is_empty(s: set[int]) -> bool:
    """Check if set is empty."""
    return len(s) == 0


def clear_set(s: set[int]) -> set[int]:
    """Return empty set."""
    return set()


def copy_set(s: set[int]) -> set[int]:
    """Copy set."""
    return s.copy()


def union(s1: set[int], s2: set[int]) -> set[int]:
    """Union of two sets."""
    return s1 | s2


def intersection(s1: set[int], s2: set[int]) -> set[int]:
    """Intersection of two sets."""
    return s1 & s2


def difference(s1: set[int], s2: set[int]) -> set[int]:
    """Difference of two sets (s1 - s2)."""
    return s1 - s2


def symmetric_difference(s1: set[int], s2: set[int]) -> set[int]:
    """Symmetric difference of two sets."""
    return s1 ^ s2


def is_subset(s1: set[int], s2: set[int]) -> bool:
    """Check if s1 is subset of s2."""
    return s1 <= s2


def is_superset(s1: set[int], s2: set[int]) -> bool:
    """Check if s1 is superset of s2."""
    return s1 >= s2


def is_proper_subset(s1: set[int], s2: set[int]) -> bool:
    """Check if s1 is proper subset of s2."""
    return s1 < s2


def is_proper_superset(s1: set[int], s2: set[int]) -> bool:
    """Check if s1 is proper superset of s2."""
    return s1 > s2


def is_disjoint(s1: set[int], s2: set[int]) -> bool:
    """Check if sets have no common elements."""
    return s1.isdisjoint(s2)


def to_list(s: set[int]) -> list[int]:
    """Convert set to sorted list."""
    return sorted(s)


def to_frozenset(s: set[int]) -> frozenset[int]:
    """Convert to frozenset."""
    return frozenset(s)


def from_range(start: int, end: int) -> set[int]:
    """Create set from range."""
    return set(range(start, end))


def filter_gt(s: set[int], threshold: int) -> set[int]:
    """Filter items greater than threshold."""
    return {x for x in s if x > threshold}


def filter_lt(s: set[int], threshold: int) -> set[int]:
    """Filter items less than threshold."""
    return {x for x in s if x < threshold}


def filter_even(s: set[int]) -> set[int]:
    """Filter even numbers."""
    return {x for x in s if x % 2 == 0}


def filter_odd(s: set[int]) -> set[int]:
    """Filter odd numbers."""
    return {x for x in s if x % 2 != 0}


def map_double(s: set[int]) -> set[int]:
    """Double all values."""
    return {x * 2 for x in s}


def map_square(s: set[int]) -> set[int]:
    """Square all values."""
    return {x * x for x in s}


def sum_set(s: set[int]) -> int:
    """Sum all values."""
    return sum(s)


def max_set(s: set[int]) -> int | None:
    """Maximum value."""
    return max(s) if s else None


def min_set(s: set[int]) -> int | None:
    """Minimum value."""
    return min(s) if s else None


def power_set(s: set[int]) -> list[set[int]]:
    """Generate power set (all subsets)."""
    items = list(s)
    n = len(items)
    result: list[set[int]] = []
    for i in range(2**n):
        subset: set[int] = set()
        for j in range(n):
            if i & (1 << j):
                subset.add(items[j])
        result.append(subset)
    return result


def partition(s: set[int], pivot: int) -> tuple[set[int], set[int]]:
    """Partition set into (< pivot, >= pivot)."""
    less = {x for x in s if x < pivot}
    greater_eq = {x for x in s if x >= pivot}
    return (less, greater_eq)


def intersects(s1: set[int], s2: set[int]) -> bool:
    """Check if sets have any common elements."""
    return not s1.isdisjoint(s2)


def jaccard_similarity(s1: set[int], s2: set[int]) -> float:
    """Calculate Jaccard similarity coefficient."""
    if not s1 and not s2:
        return 1.0
    intersection_size = len(s1 & s2)
    union_size = len(s1 | s2)
    return intersection_size / union_size


def main() -> int:
    parser = argparse.ArgumentParser(description="Typed set CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # create
    create_p = subparsers.add_parser("create", help="Create set")
    create_p.add_argument("items", nargs="*", type=int, help="Items")

    # union
    union_p = subparsers.add_parser("union", help="Union of sets")
    union_p.add_argument("set1", help="First set (comma-separated)")
    union_p.add_argument("set2", help="Second set (comma-separated)")

    # intersect
    intersect_p = subparsers.add_parser("intersect", help="Intersection")
    intersect_p.add_argument("set1", help="First set")
    intersect_p.add_argument("set2", help="Second set")

    # diff
    diff_p = subparsers.add_parser("diff", help="Difference")
    diff_p.add_argument("set1", help="First set")
    diff_p.add_argument("set2", help="Second set")

    args = parser.parse_args()

    def parse_set(s: str) -> set[int]:
        return {int(x.strip()) for x in s.split(",") if x.strip()}

    if args.command == "create":
        s = create_set(args.items)
        print(sorted(s))

    elif args.command == "union":
        s1 = parse_set(args.set1)
        s2 = parse_set(args.set2)
        result = union(s1, s2)
        print(sorted(result))

    elif args.command == "intersect":
        s1 = parse_set(args.set1)
        s2 = parse_set(args.set2)
        result = intersection(s1, s2)
        print(sorted(result))

    elif args.command == "diff":
        s1 = parse_set(args.set1)
        s2 = parse_set(args.set2)
        result = difference(s1, s2)
        print(sorted(result))

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
