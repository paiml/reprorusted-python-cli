#!/usr/bin/env python3
"""Dict Comprehension CLI.

Dictionary comprehension patterns with filtering and transformation.
"""

import argparse
import sys


def squares_dict(n: int) -> dict[int, int]:
    """Create dict of number to its square."""
    return {i: i * i for i in range(n)}


def cubes_dict(n: int) -> dict[int, int]:
    """Create dict of number to its cube."""
    return {i: i * i * i for i in range(n)}


def even_squares(n: int) -> dict[int, int]:
    """Dict of even numbers to their squares."""
    return {i: i * i for i in range(n) if i % 2 == 0}


def odd_cubes(n: int) -> dict[int, int]:
    """Dict of odd numbers to their cubes."""
    return {i: i * i * i for i in range(n) if i % 2 == 1}


def char_to_ord(text: str) -> dict[str, int]:
    """Map characters to their ordinal values."""
    return {c: ord(c) for c in text}


def char_to_ord_unique(text: str) -> dict[str, int]:
    """Map unique characters to ordinal values."""
    return {c: ord(c) for c in set(text)}


def word_to_length(words: list[str]) -> dict[str, int]:
    """Map words to their lengths."""
    return {w: len(w) for w in words}


def word_to_length_filtered(words: list[str], min_len: int) -> dict[str, int]:
    """Map words with minimum length."""
    return {w: len(w) for w in words if len(w) >= min_len}


def first_char_to_word(words: list[str]) -> dict[str, str]:
    """Map first character to word (last one wins)."""
    return {w[0]: w for w in words if w}


def index_to_value(items: list[str]) -> dict[int, str]:
    """Map index to value."""
    return dict(enumerate(items))


def value_to_index(items: list[str]) -> dict[str, int]:
    """Map value to index (last occurrence)."""
    return {v: i for i, v in enumerate(items)}


def filter_by_value(d: dict[str, int], min_val: int) -> dict[str, int]:
    """Filter dict by minimum value."""
    return {k: v for k, v in d.items() if v >= min_val}


def filter_by_key(d: dict[str, int], prefix: str) -> dict[str, int]:
    """Filter dict by key prefix."""
    return {k: v for k, v in d.items() if k.startswith(prefix)}


def transform_keys(d: dict[str, int]) -> dict[str, int]:
    """Transform keys to uppercase."""
    return {k.upper(): v for k, v in d.items()}


def transform_values(d: dict[str, int], multiplier: int) -> dict[str, int]:
    """Transform values by multiplier."""
    return {k: v * multiplier for k, v in d.items()}


def transform_both(d: dict[str, int]) -> dict[str, int]:
    """Transform both keys and values."""
    return {k.upper(): v * 2 for k, v in d.items()}


def invert_dict(d: dict[str, int]) -> dict[int, str]:
    """Invert key-value pairs."""
    return {v: k for k, v in d.items()}


def invert_dict_list(d: dict[str, int]) -> dict[int, list[str]]:
    """Invert dict, grouping keys with same value."""
    values = set(d.values())
    return {v: [k for k, val in d.items() if val == v] for v in values}


def merge_dicts(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """Merge two dicts."""
    return {**d1, **d2}


def merge_with_transform(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """Merge dicts, summing overlapping keys."""
    all_keys = set(d1.keys()) | set(d2.keys())
    return {k: d1.get(k, 0) + d2.get(k, 0) for k in all_keys}


def zip_to_dict(keys: list[str], values: list[int]) -> dict[str, int]:
    """Create dict from parallel lists."""
    return dict(zip(keys, values, strict=False))


def enumerate_to_dict(items: list[str]) -> dict[str, int]:
    """Create dict from enumeration."""
    return {v: i for i, v in enumerate(items)}


def conditional_value(items: list[int]) -> dict[int, str]:
    """Dict with conditional values."""
    return {i: "even" if i % 2 == 0 else "odd" for i in items}


def nested_key_extraction(d: dict[str, dict[str, int]], inner_key: str) -> dict[str, int]:
    """Extract inner key from nested dict."""
    return {k: v[inner_key] for k, v in d.items() if inner_key in v}


def flatten_nested_dict(d: dict[str, dict[str, int]]) -> dict[str, int]:
    """Flatten nested dict with composite keys."""
    return {f"{k1}.{k2}": v for k1, inner in d.items() for k2, v in inner.items()}


def group_by_length(words: list[str]) -> dict[int, list[str]]:
    """Group words by length."""
    lengths = {len(w) for w in words}
    return {length: [w for w in words if len(w) == length] for length in lengths}


def group_by_first_char(words: list[str]) -> dict[str, list[str]]:
    """Group words by first character."""
    chars = {w[0] for w in words if w}
    return {c: [w for w in words if w and w[0] == c] for c in chars}


def count_occurrences(items: list[str]) -> dict[str, int]:
    """Count occurrences of each item."""
    unique = set(items)
    return {item: items.count(item) for item in unique}


def dict_from_pairs(pairs: list[tuple[str, int]]) -> dict[str, int]:
    """Create dict from list of pairs."""
    return dict(pairs)


def filter_none_values(d: dict[str, int | None]) -> dict[str, int]:
    """Remove None values from dict."""
    return {k: v for k, v in d.items() if v is not None}


def default_dict_like(keys: list[str], default: int) -> dict[str, int]:
    """Create dict with default values."""
    return dict.fromkeys(keys, default)


def range_dict(start: int, end: int, step: int) -> dict[int, int]:
    """Create dict from range with squares."""
    return {i: i * i for i in range(start, end, step)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dict comprehension CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # squares
    sq_p = subparsers.add_parser("squares", help="Generate squares dict")
    sq_p.add_argument("n", type=int)

    # char-ord
    co_p = subparsers.add_parser("char-ord", help="Character to ordinal")
    co_p.add_argument("text")

    # word-len
    wl_p = subparsers.add_parser("word-len", help="Word to length")
    wl_p.add_argument("words", nargs="+")
    wl_p.add_argument("--min-len", type=int, default=0)

    # group
    gr_p = subparsers.add_parser("group", help="Group by length")
    gr_p.add_argument("words", nargs="+")

    args = parser.parse_args()

    if args.command == "squares":
        result = squares_dict(args.n)
        print(result)

    elif args.command == "char-ord":
        result = char_to_ord_unique(args.text)
        print(result)

    elif args.command == "word-len":
        result = word_to_length_filtered(args.words, args.min_len)
        print(result)

    elif args.command == "group":
        result = group_by_length(args.words)
        print(result)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
