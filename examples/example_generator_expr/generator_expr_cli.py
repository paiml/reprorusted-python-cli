#!/usr/bin/env python3
"""Generator Expression CLI.

Generator expressions with chaining patterns.
"""

import argparse
import sys
from collections.abc import Generator, Iterator


def squares_gen(n: int) -> Generator[int, None, None]:
    """Generate squares up to n."""
    return (i * i for i in range(n))


def even_gen(items: list[int]) -> Generator[int, None, None]:
    """Generate even numbers."""
    return (x for x in items if x % 2 == 0)


def odd_gen(items: list[int]) -> Generator[int, None, None]:
    """Generate odd numbers."""
    return (x for x in items if x % 2 == 1)


def filtered_gen(items: list[int], min_val: int, max_val: int) -> Generator[int, None, None]:
    """Generate values in range."""
    return (x for x in items if min_val <= x <= max_val)


def transform_gen(items: list[int], factor: int) -> Generator[int, None, None]:
    """Generate transformed values."""
    return (x * factor for x in items)


def sum_of_squares(n: int) -> int:
    """Sum of squares using generator."""
    return sum(i * i for i in range(n))


def sum_of_even(items: list[int]) -> int:
    """Sum of even numbers using generator."""
    return sum(x for x in items if x % 2 == 0)


def sum_of_odd(items: list[int]) -> int:
    """Sum of odd numbers using generator."""
    return sum(x for x in items if x % 2 == 1)


def product_of_list(items: list[int]) -> int:
    """Product using generator with reduce pattern."""
    result = 1
    for x in (i for i in items):
        result *= x
    return result


def max_of_squares(items: list[int]) -> int:
    """Max of squares using generator."""
    return max(x * x for x in items) if items else 0


def min_of_abs(items: list[int]) -> int:
    """Min of absolute values using generator."""
    return min(abs(x) for x in items) if items else 0


def any_positive(items: list[int]) -> bool:
    """Check if any positive using generator."""
    return any(x > 0 for x in items)


def all_positive(items: list[int]) -> bool:
    """Check if all positive using generator."""
    return all(x > 0 for x in items)


def any_even(items: list[int]) -> bool:
    """Check if any even using generator."""
    return any(x % 2 == 0 for x in items)


def all_even(items: list[int]) -> bool:
    """Check if all even using generator."""
    return all(x % 2 == 0 for x in items)


def count_matching(items: list[int], predicate_val: int) -> int:
    """Count items greater than value."""
    return sum(1 for x in items if x > predicate_val)


def first_matching(items: list[int], min_val: int) -> int | None:
    """Get first item >= min_val."""
    gen = (x for x in items if x >= min_val)
    return next(gen, None)


def last_matching(items: list[int], min_val: int) -> int | None:
    """Get last item >= min_val."""
    matches = [x for x in items if x >= min_val]
    return matches[-1] if matches else None


def enumerate_filtered(items: list[str], prefix: str) -> Generator[tuple[int, str], None, None]:
    """Enumerate with filter."""
    return ((i, v) for i, v in enumerate(items) if v.startswith(prefix))


def zip_filtered(list1: list[int], list2: list[int]) -> Generator[tuple[int, int], None, None]:
    """Zip with filter."""
    return ((a, b) for a, b in zip(list1, list2, strict=False) if a < b)


def chain_generators(g1: Iterator[int], g2: Iterator[int]) -> Generator[int, None, None]:
    """Chain two generators."""
    for x in g1:
        yield x
    for x in g2:
        yield x


def flatten_gen(lists: list[list[int]]) -> Generator[int, None, None]:
    """Flatten using generator."""
    return (x for lst in lists for x in lst)


def nested_gen(matrix: list[list[int]]) -> Generator[tuple[int, int, int], None, None]:
    """Generate (row, col, value) tuples."""
    return ((i, j, matrix[i][j]) for i in range(len(matrix)) for j in range(len(matrix[i])))


def word_lengths_gen(words: list[str]) -> Generator[int, None, None]:
    """Generate word lengths."""
    return (len(w) for w in words)


def char_codes_gen(text: str) -> Generator[int, None, None]:
    """Generate character codes."""
    return (ord(c) for c in text)


def running_sum_gen(items: list[int]) -> Generator[int, None, None]:
    """Generate running sum."""
    total = 0
    for x in items:
        total += x
        yield total


def running_product_gen(items: list[int]) -> Generator[int, None, None]:
    """Generate running product."""
    product = 1
    for x in items:
        product *= x
        yield product


def pairwise_gen(items: list[int]) -> Generator[tuple[int, int], None, None]:
    """Generate adjacent pairs."""
    return ((items[i], items[i + 1]) for i in range(len(items) - 1))


def differences_gen(items: list[int]) -> Generator[int, None, None]:
    """Generate differences between adjacent items."""
    return (items[i + 1] - items[i] for i in range(len(items) - 1))


def take_while_gen(items: list[int], threshold: int) -> Generator[int, None, None]:
    """Take while condition is true."""
    for x in items:
        if x >= threshold:
            break
        yield x


def drop_while_gen(items: list[int], threshold: int) -> Generator[int, None, None]:
    """Drop while condition is true."""
    dropping = True
    for x in items:
        if dropping and x < threshold:
            continue
        dropping = False
        yield x


def unique_gen(items: list[int]) -> Generator[int, None, None]:
    """Generate unique items preserving order."""
    seen: set[int] = set()
    for x in items:
        if x not in seen:
            seen.add(x)
            yield x


def batch_gen(items: list[int], size: int) -> Generator[list[int], None, None]:
    """Generate batches of items."""
    for i in range(0, len(items), size):
        yield items[i : i + size]


def join_with_gen(items: list[str], sep: str) -> str:
    """Join strings using generator."""
    return sep.join(s for s in items)


def collect_to_list(gen: Generator[int, None, None]) -> list[int]:
    """Collect generator to list."""
    return list(gen)


def collect_to_set(gen: Generator[int, None, None]) -> set[int]:
    """Collect generator to set."""
    return set(gen)


def collect_to_tuple(gen: Generator[int, None, None]) -> tuple[int, ...]:
    """Collect generator to tuple."""
    return tuple(gen)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generator expression CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # squares
    sq_p = subparsers.add_parser("squares", help="Sum of squares")
    sq_p.add_argument("n", type=int)

    # filter
    filt_p = subparsers.add_parser("filter", help="Filter numbers")
    filt_p.add_argument("items", type=int, nargs="+")
    filt_p.add_argument("--even", action="store_true")
    filt_p.add_argument("--odd", action="store_true")

    # sum
    sum_p = subparsers.add_parser("sum", help="Sum filtered")
    sum_p.add_argument("items", type=int, nargs="+")
    sum_p.add_argument("--min", type=int, default=None)

    # batch
    batch_p = subparsers.add_parser("batch", help="Batch items")
    batch_p.add_argument("items", type=int, nargs="+")
    batch_p.add_argument("--size", type=int, default=2)

    args = parser.parse_args()

    if args.command == "squares":
        result = sum_of_squares(args.n)
        print(f"Sum of squares: {result}")

    elif args.command == "filter":
        if args.even:
            result = list(even_gen(args.items))
        elif args.odd:
            result = list(odd_gen(args.items))
        else:
            result = args.items
        print(result)

    elif args.command == "sum":
        if args.min is not None:
            total = sum(x for x in args.items if x >= args.min)
        else:
            total = sum(args.items)
        print(f"Sum: {total}")

    elif args.command == "batch":
        batches = list(batch_gen(args.items, args.size))
        for b in batches:
            print(b)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
