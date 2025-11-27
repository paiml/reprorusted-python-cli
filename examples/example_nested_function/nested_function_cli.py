#!/usr/bin/env python3
"""Nested Function CLI.

Nested function definitions with type annotations.
"""

import argparse
import sys


def calculate_with_helpers(values: list[int]) -> dict[str, int]:
    """Calculate statistics using nested helpers."""

    def sum_values(lst: list[int]) -> int:
        total = 0
        for x in lst:
            total += x
        return total

    def average(lst: list[int]) -> int:
        if not lst:
            return 0
        return sum_values(lst) // len(lst)

    def minimum(lst: list[int]) -> int:
        if not lst:
            return 0
        result = lst[0]
        for x in lst[1:]:
            if x < result:
                result = x
        return result

    def maximum(lst: list[int]) -> int:
        if not lst:
            return 0
        result = lst[0]
        for x in lst[1:]:
            if x > result:
                result = x
        return result

    return {
        "sum": sum_values(values),
        "avg": average(values),
        "min": minimum(values),
        "max": maximum(values),
    }


def process_string(text: str) -> dict[str, object]:
    """Process string using nested functions."""

    def count_chars(s: str) -> int:
        return len(s)

    def count_words(s: str) -> int:
        return len(s.split())

    def count_lines(s: str) -> int:
        return len(s.splitlines()) if s else 0

    def first_word(s: str) -> str:
        parts = s.split()
        return parts[0] if parts else ""

    def last_word(s: str) -> str:
        parts = s.split()
        return parts[-1] if parts else ""

    return {
        "chars": count_chars(text),
        "words": count_words(text),
        "lines": count_lines(text),
        "first": first_word(text),
        "last": last_word(text),
    }


def recursive_with_helper(n: int) -> int:
    """Calculate factorial using nested recursive function."""

    def factorial(x: int) -> int:
        if x <= 1:
            return 1
        return x * factorial(x - 1)

    return factorial(n)


def fibonacci_with_cache(n: int) -> int:
    """Calculate fibonacci using nested function with cache."""
    cache: dict[int, int] = {}

    def fib(x: int) -> int:
        if x in cache:
            return cache[x]
        if x <= 1:
            result = x
        else:
            result = fib(x - 1) + fib(x - 2)
        cache[x] = result
        return result

    return fib(n)


def binary_search_nested(items: list[int], target: int) -> int:
    """Binary search using nested function."""

    def search(low: int, high: int) -> int:
        if low > high:
            return -1
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            return search(mid + 1, high)
        else:
            return search(low, mid - 1)

    return search(0, len(items) - 1)


def merge_sort_nested(items: list[int]) -> list[int]:
    """Merge sort using nested functions."""

    def merge(left: list[int], right: list[int]) -> list[int]:
        result: list[int] = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def sort(lst: list[int]) -> list[int]:
        if len(lst) <= 1:
            return lst.copy()
        mid = len(lst) // 2
        left = sort(lst[:mid])
        right = sort(lst[mid:])
        return merge(left, right)

    return sort(items)


def validate_with_rules(value: str) -> tuple[bool, list[str]]:
    """Validate value using nested rule functions."""

    def check_length(s: str) -> str | None:
        if len(s) < 3:
            return "too short"
        if len(s) > 20:
            return "too long"
        return None

    def check_alphanumeric(s: str) -> str | None:
        if not s.isalnum():
            return "not alphanumeric"
        return None

    def check_starts_with_letter(s: str) -> str | None:
        if s and not s[0].isalpha():
            return "must start with letter"
        return None

    errors: list[str] = []
    for check in [check_length, check_alphanumeric, check_starts_with_letter]:
        error = check(value)
        if error:
            errors.append(error)

    return (len(errors) == 0, errors)


def tree_operations(tree: dict[str, object]) -> dict[str, int]:
    """Tree operations using nested functions."""

    def count_nodes(node: dict[str, object]) -> int:
        count = 1
        children = node.get("children", [])
        if isinstance(children, list):
            for child in children:
                if isinstance(child, dict):
                    count += count_nodes(child)
        return count

    def max_depth(node: dict[str, object], depth: int) -> int:
        children = node.get("children", [])
        if not children or not isinstance(children, list):
            return depth
        max_child = depth
        for child in children:
            if isinstance(child, dict):
                child_depth = max_depth(child, depth + 1)
                if child_depth > max_child:
                    max_child = child_depth
        return max_child

    def sum_values(node: dict[str, object]) -> int:
        total = 0
        value = node.get("value")
        if isinstance(value, int):
            total = value
        children = node.get("children", [])
        if isinstance(children, list):
            for child in children:
                if isinstance(child, dict):
                    total += sum_values(child)
        return total

    return {
        "nodes": count_nodes(tree),
        "depth": max_depth(tree, 1),
        "sum": sum_values(tree),
    }


def expression_parser(expr: str) -> int:
    """Simple expression parser using nested functions."""
    pos = [0]

    def peek() -> str:
        if pos[0] < len(expr):
            return expr[pos[0]]
        return ""

    def consume() -> str:
        c = peek()
        pos[0] += 1
        return c

    def skip_spaces() -> None:
        while peek() == " ":
            consume()

    def parse_number() -> int:
        skip_spaces()
        num_str = ""
        while peek().isdigit():
            num_str += consume()
        return int(num_str) if num_str else 0

    def parse_term() -> int:
        return parse_number()

    def parse_expr() -> int:
        left = parse_term()
        while True:
            skip_spaces()
            if not peek() or peek() not in "+-":
                break
            op = consume()
            skip_spaces()
            right = parse_term()
            if op == "+":
                left = left + right
            else:
                left = left - right
        return left

    return parse_expr()


def main() -> int:
    parser = argparse.ArgumentParser(description="Nested function CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # stats
    stats_p = subparsers.add_parser("stats", help="Calculate statistics")
    stats_p.add_argument("values", type=int, nargs="+")

    # factorial
    fact_p = subparsers.add_parser("factorial", help="Calculate factorial")
    fact_p.add_argument("n", type=int)

    # fib
    fib_p = subparsers.add_parser("fib", help="Calculate fibonacci")
    fib_p.add_argument("n", type=int)

    # sort
    sort_p = subparsers.add_parser("sort", help="Merge sort")
    sort_p.add_argument("values", type=int, nargs="+")

    # validate
    val_p = subparsers.add_parser("validate", help="Validate string")
    val_p.add_argument("value")

    args = parser.parse_args()

    if args.command == "stats":
        result = calculate_with_helpers(args.values)
        for k, v in result.items():
            print(f"{k}: {v}")

    elif args.command == "factorial":
        result = recursive_with_helper(args.n)
        print(f"{args.n}! = {result}")

    elif args.command == "fib":
        result = fibonacci_with_cache(args.n)
        print(f"fib({args.n}) = {result}")

    elif args.command == "sort":
        result = merge_sort_nested(args.values)
        print(result)

    elif args.command == "validate":
        valid, errors = validate_with_rules(args.value)
        if valid:
            print("Valid")
        else:
            print(f"Invalid: {', '.join(errors)}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
