#!/usr/bin/env python3
"""Typed Dict CLI.

Dictionary operations with type hints.
"""

import argparse
import sys


def create_empty_dict() -> dict[str, int]:
    """Create empty typed dictionary."""
    return {}


def create_dict(items: list[tuple[str, int]]) -> dict[str, int]:
    """Create dictionary from key-value pairs."""
    return dict(items)


def get_value(d: dict[str, int], key: str) -> int | None:
    """Get value by key, return None if not found."""
    return d.get(key)


def get_value_default(d: dict[str, int], key: str, default: int) -> int:
    """Get value by key with default."""
    return d.get(key, default)


def set_value(d: dict[str, int], key: str, value: int) -> dict[str, int]:
    """Set value in dictionary (returns new dict)."""
    result = d.copy()
    result[key] = value
    return result


def remove_key(d: dict[str, int], key: str) -> dict[str, int]:
    """Remove key from dictionary (returns new dict)."""
    result = d.copy()
    result.pop(key, None)
    return result


def has_key(d: dict[str, int], key: str) -> bool:
    """Check if key exists in dictionary."""
    return key in d


def get_keys(d: dict[str, int]) -> list[str]:
    """Get all keys."""
    return list(d.keys())


def get_values(d: dict[str, int]) -> list[int]:
    """Get all values."""
    return list(d.values())


def get_items(d: dict[str, int]) -> list[tuple[str, int]]:
    """Get all key-value pairs."""
    return list(d.items())


def dict_size(d: dict[str, int]) -> int:
    """Get dictionary size."""
    return len(d)


def is_empty(d: dict[str, int]) -> bool:
    """Check if dictionary is empty."""
    return len(d) == 0


def merge_dicts(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """Merge two dictionaries (d2 overrides d1)."""
    return {**d1, **d2}


def update_dict(d: dict[str, int], updates: dict[str, int]) -> dict[str, int]:
    """Update dictionary with new values."""
    result = d.copy()
    result.update(updates)
    return result


def pop_value(d: dict[str, int], key: str) -> tuple[int | None, dict[str, int]]:
    """Pop value from dictionary, return (value, new_dict)."""
    result = d.copy()
    value = result.pop(key, None)
    return (value, result)


def setdefault(d: dict[str, int], key: str, default: int) -> tuple[int, dict[str, int]]:
    """Set default value if key doesn't exist."""
    result = d.copy()
    value = result.setdefault(key, default)
    return (value, result)


def clear_dict(d: dict[str, int]) -> dict[str, int]:
    """Return empty dictionary."""
    return {}


def copy_dict(d: dict[str, int]) -> dict[str, int]:
    """Create shallow copy of dictionary."""
    return d.copy()


def filter_by_value(d: dict[str, int], min_value: int) -> dict[str, int]:
    """Filter dictionary by minimum value."""
    return {k: v for k, v in d.items() if v >= min_value}


def filter_by_keys(d: dict[str, int], keys: list[str]) -> dict[str, int]:
    """Filter dictionary to only include specified keys."""
    return {k: v for k, v in d.items() if k in keys}


def map_values(d: dict[str, int], factor: int) -> dict[str, int]:
    """Multiply all values by factor."""
    return {k: v * factor for k, v in d.items()}


def sum_values(d: dict[str, int]) -> int:
    """Sum all values in dictionary."""
    return sum(d.values())


def max_value(d: dict[str, int]) -> int | None:
    """Get maximum value."""
    if not d:
        return None
    return max(d.values())


def min_value(d: dict[str, int]) -> int | None:
    """Get minimum value."""
    if not d:
        return None
    return min(d.values())


def key_with_max_value(d: dict[str, int]) -> str | None:
    """Get key with maximum value."""
    if not d:
        return None
    return max(d, key=d.get)  # type: ignore


def key_with_min_value(d: dict[str, int]) -> str | None:
    """Get key with minimum value."""
    if not d:
        return None
    return min(d, key=d.get)  # type: ignore


def invert_dict(d: dict[str, int]) -> dict[int, str]:
    """Invert dictionary (swap keys and values)."""
    return {v: k for k, v in d.items()}


def sort_by_key(d: dict[str, int]) -> dict[str, int]:
    """Sort dictionary by keys."""
    return dict(sorted(d.items()))


def sort_by_value(d: dict[str, int]) -> dict[str, int]:
    """Sort dictionary by values."""
    return dict(sorted(d.items(), key=lambda x: x[1]))


def count_by_value(d: dict[str, int]) -> dict[int, int]:
    """Count occurrences of each value."""
    counts: dict[int, int] = {}
    for v in d.values():
        counts[v] = counts.get(v, 0) + 1
    return counts


def group_by_value(d: dict[str, int]) -> dict[int, list[str]]:
    """Group keys by their values."""
    groups: dict[int, list[str]] = {}
    for k, v in d.items():
        if v not in groups:
            groups[v] = []
        groups[v].append(k)
    return groups


def from_keys(keys: list[str], default: int) -> dict[str, int]:
    """Create dictionary from keys with default value."""
    return dict.fromkeys(keys, default)


def zip_to_dict(keys: list[str], values: list[int]) -> dict[str, int]:
    """Create dictionary from two lists."""
    return dict(zip(keys, values, strict=False))


def difference(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """Get keys in d1 but not in d2."""
    return {k: v for k, v in d1.items() if k not in d2}


def intersection(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """Get keys in both d1 and d2 (values from d1)."""
    return {k: v for k, v in d1.items() if k in d2}


def main() -> int:
    parser = argparse.ArgumentParser(description="Typed dict CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # create
    create_p = subparsers.add_parser("create", help="Create dictionary")
    create_p.add_argument("items", nargs="*", help="key=value pairs")

    # get
    get_p = subparsers.add_parser("get", help="Get value")
    get_p.add_argument("key", help="Key")
    get_p.add_argument("--data", required=True, help="Dict as key=value pairs")

    # stats
    stats_p = subparsers.add_parser("stats", help="Show stats")
    stats_p.add_argument("--data", required=True, help="Dict as key=value pairs")

    args = parser.parse_args()

    def parse_dict(s: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for item in s.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                result[k.strip()] = int(v.strip())
        return result

    if args.command == "create":
        items = []
        for item in args.items:
            if "=" in item:
                k, v = item.split("=", 1)
                items.append((k, int(v)))
        d = create_dict(items)
        print(d)

    elif args.command == "get":
        d = parse_dict(args.data)
        value = get_value(d, args.key)
        print(f"Value: {value}")

    elif args.command == "stats":
        d = parse_dict(args.data)
        print(f"Size: {dict_size(d)}")
        print(f"Sum: {sum_values(d)}")
        print(f"Max: {max_value(d)}")
        print(f"Min: {min_value(d)}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
