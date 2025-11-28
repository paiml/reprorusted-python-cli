#!/usr/bin/env python3
"""
Walrus Operator CLI - Tests assignment expressions (:=)

This example demonstrates Python 3.8+ walrus operator patterns:
- Assignment in if conditions
- Assignment in while loops
- Assignment in list comprehensions

Purpose: Validate depyler handles block scoping correctly (E0425).
"""

import argparse


def check_length(text: str) -> int:
    """Return length if > 5, else 0."""
    if (n := len(text)) > 5:
        return n
    return 0


def count_words(text: str) -> int:
    """Count words using walrus in comprehension."""
    words = text.split()
    # Walrus in comprehension - use length for filtering
    long_words = [(w, length) for w in words if (length := len(w)) > 3]
    return len(long_words)


def find_first_long(text: str, min_len: int) -> str:
    """Find first word longer than min_len."""
    words = text.split()
    for word in words:
        if (n := len(word)) >= min_len:
            return f"{word}({n})"
    return "none"


def main():
    """Main entry point with walrus operator examples."""
    parser = argparse.ArgumentParser(
        description="Walrus operator examples",
        prog="walrus_cli.py",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Subcommand: check
    check_parser = subparsers.add_parser(
        "check",
        help="Check if text length > 5",
    )
    check_parser.add_argument(
        "text",
        help="Text to check",
    )

    # Subcommand: count
    count_parser = subparsers.add_parser(
        "count",
        help="Count words with length > 3",
    )
    count_parser.add_argument(
        "text",
        help="Text to analyze",
    )

    # Subcommand: find
    find_parser = subparsers.add_parser(
        "find",
        help="Find first long word",
    )
    find_parser.add_argument(
        "text",
        help="Text to search",
    )
    find_parser.add_argument(
        "--min-len",
        type=int,
        default=5,
        help="Minimum word length (default: 5)",
    )

    args = parser.parse_args()

    if args.command == "check":
        result = check_length(args.text)
        if result > 0:
            print(f"Length: {result}")
        else:
            print("Too short")
    elif args.command == "count":
        count = count_words(args.text)
        print(f"Long words: {count}")
    elif args.command == "find":
        found = find_first_long(args.text, args.min_len)
        print(f"Found: {found}")


if __name__ == "__main__":
    main()
