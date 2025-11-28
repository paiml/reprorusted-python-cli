#!/usr/bin/env python3
"""
Typed Dictionary CLI - Tests explicit type annotations

This example demonstrates typed dictionary patterns:
- dict with explicit type hints: dict[str, int]
- Nested dicts with types
- list with type hints: list[str]

Purpose: Validate depyler handles type inference correctly (E0308/E0282).
"""

import argparse


def create_word_counts(text: str) -> dict[str, int]:
    """Count word occurrences with typed dict."""
    counts: dict[str, int] = {}
    for word in text.split():
        word_lower = word.lower()
        if word_lower in counts:
            counts[word_lower] = counts[word_lower] + 1
        else:
            counts[word_lower] = 1
    return counts


def get_unique_words(text: str) -> list[str]:
    """Get unique words as typed list."""
    words: list[str] = []
    seen: dict[str, bool] = {}
    for word in text.split():
        word_lower = word.lower()
        if word_lower not in seen:
            seen[word_lower] = True
            words.append(word_lower)
    return words


def format_counts(counts: dict[str, int]) -> str:
    """Format counts for display."""
    items: list[str] = []
    for word in sorted(counts.keys()):
        items.append(f"{word}:{counts[word]}")
    return ",".join(items)


def main():
    """Main entry point with typed dict examples."""
    parser = argparse.ArgumentParser(
        description="Typed dictionary examples",
        prog="dict_typed_cli.py",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Subcommand: count
    count_parser = subparsers.add_parser(
        "count",
        help="Count word occurrences",
    )
    count_parser.add_argument(
        "text",
        help="Text to analyze",
    )

    # Subcommand: unique
    unique_parser = subparsers.add_parser(
        "unique",
        help="Get unique words",
    )
    unique_parser.add_argument(
        "text",
        help="Text to analyze",
    )

    # Subcommand: stats
    stats_parser = subparsers.add_parser(
        "stats",
        help="Get text statistics",
    )
    stats_parser.add_argument(
        "text",
        help="Text to analyze",
    )

    args = parser.parse_args()

    if args.command == "count":
        counts = create_word_counts(args.text)
        result = format_counts(counts)
        print(f"Counts: {result}")
    elif args.command == "unique":
        words = get_unique_words(args.text)
        print(f"Unique: {','.join(words)}")
    elif args.command == "stats":
        counts = create_word_counts(args.text)
        unique = get_unique_words(args.text)
        total = sum(counts.values())
        print(f"Total: {total}")
        print(f"Unique: {len(unique)}")


if __name__ == "__main__":
    main()
