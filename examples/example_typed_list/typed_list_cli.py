#!/usr/bin/env python3
"""Typed List CLI.

List operations with type hints.
"""

import argparse
import sys


def create_empty_list() -> list[int]:
    """Create empty typed list."""
    return []


def create_list(items: list[int]) -> list[int]:
    """Create list from items."""
    return list(items)


def append(lst: list[int], item: int) -> list[int]:
    """Append item to list (returns new list)."""
    return lst + [item]


def prepend(lst: list[int], item: int) -> list[int]:
    """Prepend item to list."""
    return [item] + lst


def insert_at(lst: list[int], index: int, item: int) -> list[int]:
    """Insert item at index."""
    result = lst.copy()
    result.insert(index, item)
    return result


def remove_item(lst: list[int], item: int) -> list[int]:
    """Remove first occurrence of item."""
    result = lst.copy()
    if item in result:
        result.remove(item)
    return result


def remove_at(lst: list[int], index: int) -> list[int]:
    """Remove item at index."""
    if 0 <= index < len(lst):
        return lst[:index] + lst[index + 1 :]
    return lst.copy()


def pop_last(lst: list[int]) -> tuple[int | None, list[int]]:
    """Pop last item, return (item, new_list)."""
    if not lst:
        return (None, [])
    return (lst[-1], lst[:-1])


def pop_first(lst: list[int]) -> tuple[int | None, list[int]]:
    """Pop first item, return (item, new_list)."""
    if not lst:
        return (None, [])
    return (lst[0], lst[1:])


def get_item(lst: list[int], index: int) -> int | None:
    """Get item at index, None if out of bounds."""
    if 0 <= index < len(lst):
        return lst[index]
    return None


def get_first(lst: list[int]) -> int | None:
    """Get first item."""
    return lst[0] if lst else None


def get_last(lst: list[int]) -> int | None:
    """Get last item."""
    return lst[-1] if lst else None


def set_item(lst: list[int], index: int, value: int) -> list[int]:
    """Set item at index."""
    result = lst.copy()
    if 0 <= index < len(result):
        result[index] = value
    return result


def list_size(lst: list[int]) -> int:
    """Get list size."""
    return len(lst)


def is_empty(lst: list[int]) -> bool:
    """Check if list is empty."""
    return len(lst) == 0


def contains(lst: list[int], item: int) -> bool:
    """Check if list contains item."""
    return item in lst


def index_of(lst: list[int], item: int) -> int:
    """Get index of item, -1 if not found."""
    try:
        return lst.index(item)
    except ValueError:
        return -1


def count_item(lst: list[int], item: int) -> int:
    """Count occurrences of item."""
    return lst.count(item)


def slice_list(lst: list[int], start: int, end: int) -> list[int]:
    """Slice list from start to end."""
    return lst[start:end]


def take(lst: list[int], n: int) -> list[int]:
    """Take first n items."""
    return lst[:n]


def drop(lst: list[int], n: int) -> list[int]:
    """Drop first n items."""
    return lst[n:]


def take_last(lst: list[int], n: int) -> list[int]:
    """Take last n items."""
    return lst[-n:] if n > 0 else []


def drop_last(lst: list[int], n: int) -> list[int]:
    """Drop last n items."""
    return lst[:-n] if n > 0 else lst.copy()


def reverse_list(lst: list[int]) -> list[int]:
    """Reverse list."""
    return lst[::-1]


def sort_asc(lst: list[int]) -> list[int]:
    """Sort ascending."""
    return sorted(lst)


def sort_desc(lst: list[int]) -> list[int]:
    """Sort descending."""
    return sorted(lst, reverse=True)


def concat(lst1: list[int], lst2: list[int]) -> list[int]:
    """Concatenate two lists."""
    return lst1 + lst2


def extend(lst: list[int], items: list[int]) -> list[int]:
    """Extend list with items."""
    return lst + items


def repeat(lst: list[int], n: int) -> list[int]:
    """Repeat list n times."""
    return lst * n


def flatten(nested: list[list[int]]) -> list[int]:
    """Flatten nested list."""
    result: list[int] = []
    for inner in nested:
        result.extend(inner)
    return result


def filter_gt(lst: list[int], threshold: int) -> list[int]:
    """Filter items greater than threshold."""
    return [x for x in lst if x > threshold]


def filter_lt(lst: list[int], threshold: int) -> list[int]:
    """Filter items less than threshold."""
    return [x for x in lst if x < threshold]


def filter_even(lst: list[int]) -> list[int]:
    """Filter even numbers."""
    return [x for x in lst if x % 2 == 0]


def filter_odd(lst: list[int]) -> list[int]:
    """Filter odd numbers."""
    return [x for x in lst if x % 2 != 0]


def map_double(lst: list[int]) -> list[int]:
    """Double all values."""
    return [x * 2 for x in lst]


def map_square(lst: list[int]) -> list[int]:
    """Square all values."""
    return [x * x for x in lst]


def map_add(lst: list[int], n: int) -> list[int]:
    """Add n to all values."""
    return [x + n for x in lst]


def map_multiply(lst: list[int], n: int) -> list[int]:
    """Multiply all values by n."""
    return [x * n for x in lst]


def sum_list(lst: list[int]) -> int:
    """Sum all values."""
    return sum(lst)


def product_list(lst: list[int]) -> int:
    """Product of all values."""
    result = 1
    for x in lst:
        result *= x
    return result


def max_list(lst: list[int]) -> int | None:
    """Maximum value."""
    return max(lst) if lst else None


def min_list(lst: list[int]) -> int | None:
    """Minimum value."""
    return min(lst) if lst else None


def mean_list(lst: list[int]) -> float | None:
    """Average value."""
    return sum(lst) / len(lst) if lst else None


def unique(lst: list[int]) -> list[int]:
    """Get unique values (preserves order)."""
    seen: set[int] = set()
    result: list[int] = []
    for x in lst:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result


def deduplicate(lst: list[int]) -> list[int]:
    """Remove consecutive duplicates."""
    if not lst:
        return []
    result = [lst[0]]
    for x in lst[1:]:
        if x != result[-1]:
            result.append(x)
    return result


def zip_lists(lst1: list[int], lst2: list[int]) -> list[tuple[int, int]]:
    """Zip two lists."""
    return list(zip(lst1, lst2, strict=False))


def enumerate_list(lst: list[int]) -> list[tuple[int, int]]:
    """Enumerate list."""
    return list(enumerate(lst))


def range_list(start: int, end: int, step: int = 1) -> list[int]:
    """Create list from range."""
    return list(range(start, end, step))


def main() -> int:
    parser = argparse.ArgumentParser(description="Typed list CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # create
    create_p = subparsers.add_parser("create", help="Create list")
    create_p.add_argument("items", nargs="*", type=int, help="Items")

    # append
    append_p = subparsers.add_parser("append", help="Append item")
    append_p.add_argument("list", help="Comma-separated list")
    append_p.add_argument("item", type=int, help="Item to append")

    # stats
    stats_p = subparsers.add_parser("stats", help="Show stats")
    stats_p.add_argument("list", help="Comma-separated list")

    # sort
    sort_p = subparsers.add_parser("sort", help="Sort list")
    sort_p.add_argument("list", help="Comma-separated list")
    sort_p.add_argument("--desc", action="store_true", help="Descending")

    args = parser.parse_args()

    def parse_list(s: str) -> list[int]:
        return [int(x.strip()) for x in s.split(",") if x.strip()]

    if args.command == "create":
        lst = create_list(args.items)
        print(lst)

    elif args.command == "append":
        lst = parse_list(args.list)
        result = append(lst, args.item)
        print(result)

    elif args.command == "stats":
        lst = parse_list(args.list)
        print(f"Size: {list_size(lst)}")
        print(f"Sum: {sum_list(lst)}")
        print(f"Max: {max_list(lst)}")
        print(f"Min: {min_list(lst)}")
        print(f"Mean: {mean_list(lst)}")

    elif args.command == "sort":
        lst = parse_list(args.list)
        result = sort_desc(lst) if args.desc else sort_asc(lst)
        print(result)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
