#!/usr/bin/env python3
"""Tuple Unpack Comprehension CLI.

Tuple unpacking patterns in comprehensions.
"""

import argparse
import sys


def enumerate_to_pairs(items: list[str]) -> list[tuple[int, str]]:
    """Convert enumerate to list of pairs."""
    return [(i, v) for i, v in enumerate(items)]


def enumerate_filtered(items: list[str], prefix: str) -> list[tuple[int, str]]:
    """Enumerate with filter on value."""
    return [(i, v) for i, v in enumerate(items) if v.startswith(prefix)]


def enumerate_transformed(items: list[int]) -> list[tuple[int, int]]:
    """Enumerate with transformed values."""
    return [(i, v * 2) for i, v in enumerate(items)]


def zip_to_pairs(list1: list[int], list2: list[str]) -> list[tuple[int, str]]:
    """Zip two lists to pairs."""
    return [(a, b) for a, b in zip(list1, list2, strict=False)]


def zip_with_sum(list1: list[int], list2: list[int]) -> list[int]:
    """Zip and sum pairs."""
    return [a + b for a, b in zip(list1, list2, strict=False)]


def zip_filtered(list1: list[int], list2: list[int]) -> list[tuple[int, int]]:
    """Zip with filter."""
    return [(a, b) for a, b in zip(list1, list2, strict=False) if a < b]


def zip_three_lists(l1: list[int], l2: list[int], l3: list[int]) -> list[tuple[int, int, int]]:
    """Zip three lists."""
    return [(a, b, c) for a, b, c in zip(l1, l2, l3, strict=False)]


def dict_items_to_list(d: dict[str, int]) -> list[tuple[str, int]]:
    """Convert dict items to list."""
    return list(d.items())


def dict_items_filtered(d: dict[str, int], min_val: int) -> list[tuple[str, int]]:
    """Dict items filtered by value."""
    return [(k, v) for k, v in d.items() if v >= min_val]


def dict_items_transformed(d: dict[str, int]) -> list[tuple[str, int]]:
    """Transform dict items."""
    return [(k.upper(), v * 2) for k, v in d.items()]


def dict_keys_from_items(d: dict[str, int]) -> list[str]:
    """Extract keys using items unpacking."""
    return [k for k, _ in d.items()]


def dict_values_from_items(d: dict[str, int]) -> list[int]:
    """Extract values using items unpacking."""
    return [v for _, v in d.items()]


def swap_pairs(pairs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Swap elements in pairs."""
    return [(b, a) for a, b in pairs]


def unpack_nested_pairs(pairs: list[tuple[tuple[int, int], str]]) -> list[tuple[int, int, str]]:
    """Unpack nested tuples."""
    return [(x, y, s) for (x, y), s in pairs]


def unpack_triple(triples: list[tuple[int, int, int]]) -> list[int]:
    """Sum elements from triples."""
    return [a + b + c for a, b, c in triples]


def filter_by_first(pairs: list[tuple[int, str]], threshold: int) -> list[str]:
    """Filter pairs and extract second element."""
    return [s for n, s in pairs if n > threshold]


def filter_by_second(pairs: list[tuple[str, int]], threshold: int) -> list[str]:
    """Filter pairs by second element."""
    return [s for s, n in pairs if n > threshold]


def combine_with_index(items: list[str]) -> list[str]:
    """Combine index with item."""
    return [f"{i}:{v}" for i, v in enumerate(items)]


def enumerate_with_start(items: list[str], start: int) -> list[tuple[int, str]]:
    """Enumerate with custom start."""
    return [(i, v) for i, v in enumerate(items, start=start)]


def multi_zip_sum(lists: list[list[int]]) -> list[int]:
    """Sum corresponding elements from multiple lists."""
    if not lists:
        return []
    return [sum(vals) for vals in zip(*lists, strict=False)]


def enumerate_dict_values(d: dict[str, list[int]]) -> list[tuple[str, int, int]]:
    """Enumerate values in dict of lists."""
    return [(k, i, v) for k, lst in d.items() for i, v in enumerate(lst)]


def zip_with_enumerate(list1: list[str], list2: list[int]) -> list[tuple[int, str, int]]:
    """Combine zip and enumerate."""
    return [(i, s, n) for i, (s, n) in enumerate(zip(list1, list2, strict=False))]


def range_pairs(n: int) -> list[tuple[int, int]]:
    """Generate pairs from range."""
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def adjacent_pairs(items: list[int]) -> list[tuple[int, int]]:
    """Get adjacent pairs."""
    return [(a, b) for a, b in zip(items[:-1], items[1:], strict=False)]


def adjacent_differences(items: list[int]) -> list[int]:
    """Calculate differences between adjacent elements."""
    return [b - a for a, b in zip(items[:-1], items[1:], strict=False)]


def running_pairs(items: list[int]) -> list[tuple[int, int, int]]:
    """Pairs with running index."""
    return [(i, a, b) for i, (a, b) in enumerate(zip(items[:-1], items[1:], strict=False))]


def dict_invert(d: dict[str, int]) -> dict[int, str]:
    """Invert dictionary using comprehension."""
    return {v: k for k, v in d.items()}


def dict_filter_transform(d: dict[str, int]) -> dict[str, int]:
    """Filter and transform dict."""
    return {k.upper(): v * 2 for k, v in d.items() if v > 0}


def group_pairs_by_first(pairs: list[tuple[str, int]]) -> dict[str, list[int]]:
    """Group pairs by first element."""
    keys = {k for k, _ in pairs}
    return {k: [v for key, v in pairs if key == k] for k in keys}


def merge_dicts_comprehension(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """Merge dicts using comprehension."""
    return {k: v for d in [d1, d2] for k, v in d.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Tuple unpack comprehension CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # enumerate
    enum_p = subparsers.add_parser("enumerate", help="Enumerate items")
    enum_p.add_argument("items", nargs="+")
    enum_p.add_argument("--start", type=int, default=0)

    # zip
    zip_p = subparsers.add_parser("zip", help="Zip lists")
    zip_p.add_argument("--list1", required=True)
    zip_p.add_argument("--list2", required=True)

    # adjacent
    adj_p = subparsers.add_parser("adjacent", help="Adjacent pairs")
    adj_p.add_argument("items", type=int, nargs="+")

    args = parser.parse_args()

    if args.command == "enumerate":
        result = enumerate_with_start(args.items, args.start)
        for i, v in result:
            print(f"{i}: {v}")

    elif args.command == "zip":
        import ast

        list1 = ast.literal_eval(args.list1)
        list2 = ast.literal_eval(args.list2)
        result = zip_to_pairs(list1, list2)
        print(result)

    elif args.command == "adjacent":
        result = adjacent_pairs(args.items)
        print(result)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
