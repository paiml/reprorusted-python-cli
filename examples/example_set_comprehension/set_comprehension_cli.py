#!/usr/bin/env python3
"""Set Comprehension CLI.

Set comprehension patterns with transforms and filtering.
"""

import argparse
import sys


def unique_squares(items: list[int]) -> set[int]:
    """Get unique squares of items."""
    return {x * x for x in items}


def unique_lengths(words: list[str]) -> set[int]:
    """Get unique lengths of words."""
    return {len(w) for w in words}


def unique_first_chars(words: list[str]) -> set[str]:
    """Get unique first characters."""
    return {w[0] for w in words if w}


def unique_last_chars(words: list[str]) -> set[str]:
    """Get unique last characters."""
    return {w[-1] for w in words if w}


def even_numbers(items: list[int]) -> set[int]:
    """Get unique even numbers."""
    return {x for x in items if x % 2 == 0}


def odd_numbers(items: list[int]) -> set[int]:
    """Get unique odd numbers."""
    return {x for x in items if x % 2 == 1}


def positive_numbers(items: list[int]) -> set[int]:
    """Get unique positive numbers."""
    return {x for x in items if x > 0}


def negative_numbers(items: list[int]) -> set[int]:
    """Get unique negative numbers."""
    return {x for x in items if x < 0}


def divisible_by(items: list[int], divisor: int) -> set[int]:
    """Get numbers divisible by divisor."""
    return {x for x in items if x % divisor == 0}


def in_range(items: list[int], min_val: int, max_val: int) -> set[int]:
    """Get numbers in range."""
    return {x for x in items if min_val <= x <= max_val}


def vowels_in_text(text: str) -> set[str]:
    """Get unique vowels in text."""
    return {c for c in text.lower() if c in "aeiou"}


def consonants_in_text(text: str) -> set[str]:
    """Get unique consonants in text."""
    return {c for c in text.lower() if c.isalpha() and c not in "aeiou"}


def digits_in_text(text: str) -> set[str]:
    """Get unique digits in text."""
    return {c for c in text if c.isdigit()}


def uppercase_chars(text: str) -> set[str]:
    """Get unique uppercase characters."""
    return {c for c in text if c.isupper()}


def lowercase_chars(text: str) -> set[str]:
    """Get unique lowercase characters."""
    return {c for c in text if c.islower()}


def words_with_length(words: list[str], length: int) -> set[str]:
    """Get words with specific length."""
    return {w for w in words if len(w) == length}


def words_starting_with(words: list[str], prefix: str) -> set[str]:
    """Get words starting with prefix."""
    return {w for w in words if w.startswith(prefix)}


def words_ending_with(words: list[str], suffix: str) -> set[str]:
    """Get words ending with suffix."""
    return {w for w in words if w.endswith(suffix)}


def words_containing(words: list[str], substring: str) -> set[str]:
    """Get words containing substring."""
    return {w for w in words if substring in w}


def flatten_to_set(lists: list[list[int]]) -> set[int]:
    """Flatten list of lists to set."""
    return {x for lst in lists for x in lst}


def cross_product_set(list1: list[int], list2: list[int]) -> set[tuple[int, int]]:
    """Cartesian product as set of tuples."""
    return {(x, y) for x in list1 for y in list2}


def pair_sums(items: list[int]) -> set[int]:
    """Get all possible pair sums."""
    return {x + y for x in items for y in items}


def pair_products(items: list[int]) -> set[int]:
    """Get all possible pair products."""
    return {x * y for x in items for y in items}


def symmetric_difference_comprehension(set1: set[int], set2: set[int]) -> set[int]:
    """Symmetric difference using comprehension."""
    return {x for x in set1 if x not in set2} | {x for x in set2 if x not in set1}


def intersection_comprehension(set1: set[int], set2: set[int]) -> set[int]:
    """Intersection using comprehension."""
    return {x for x in set1 if x in set2}


def difference_comprehension(set1: set[int], set2: set[int]) -> set[int]:
    """Difference using comprehension."""
    return {x for x in set1 if x not in set2}


def common_elements(lists: list[list[int]]) -> set[int]:
    """Get elements common to all lists."""
    if not lists:
        return set()
    result = set(lists[0])
    for lst in lists[1:]:
        result = {x for x in result if x in lst}
    return result


def unique_from_dict_values(d: dict[str, list[int]]) -> set[int]:
    """Get unique values from dict of lists."""
    return {x for values in d.values() for x in values}


def unique_from_dict_keys(d: dict[str, int]) -> set[str]:
    """Get unique keys (already unique but with transform)."""
    return {k.upper() for k in d.keys()}


def prime_factors(n: int) -> set[int]:
    """Get prime factors of n."""
    factors: set[int] = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def perfect_squares_in_range(start: int, end: int) -> set[int]:
    """Get perfect squares in range."""
    return {i * i for i in range(1, end) if start <= i * i <= end}


def multiples_set(base: int, count: int) -> set[int]:
    """Get first count multiples of base."""
    return {base * i for i in range(1, count + 1)}


def string_transforms(text: str) -> set[str]:
    """Get various transforms of text."""
    return {text.lower(), text.upper(), text.title(), text.swapcase()}


def word_lengths_distribution(words: list[str]) -> set[int]:
    """Get distribution of word lengths."""
    return {len(w) for w in words}


def main() -> int:
    parser = argparse.ArgumentParser(description="Set comprehension CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # squares
    sq_p = subparsers.add_parser("squares", help="Unique squares")
    sq_p.add_argument("items", type=int, nargs="+")

    # vowels
    vow_p = subparsers.add_parser("vowels", help="Vowels in text")
    vow_p.add_argument("text")

    # filter
    filt_p = subparsers.add_parser("filter", help="Filter numbers")
    filt_p.add_argument("items", type=int, nargs="+")
    filt_p.add_argument("--even", action="store_true")
    filt_p.add_argument("--odd", action="store_true")

    # words
    word_p = subparsers.add_parser("words", help="Filter words")
    word_p.add_argument("words", nargs="+")
    word_p.add_argument("--prefix")
    word_p.add_argument("--suffix")

    args = parser.parse_args()

    if args.command == "squares":
        result = unique_squares(args.items)
        print(sorted(result))

    elif args.command == "vowels":
        result = vowels_in_text(args.text)
        print(sorted(result))

    elif args.command == "filter":
        if args.even:
            result = even_numbers(args.items)
        elif args.odd:
            result = odd_numbers(args.items)
        else:
            result = set(args.items)
        print(sorted(result))

    elif args.command == "words":
        words = set(args.words)
        if args.prefix:
            words = words_starting_with(list(words), args.prefix)
        if args.suffix:
            words = words_ending_with(list(words), args.suffix)
        print(sorted(words))

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
