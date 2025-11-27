#!/usr/bin/env python3
"""
Counter Example - Word/character frequency CLI

Demonstrates:
- collections.Counter
- most_common()
- Counter arithmetic
- stdin processing

This validates depyler's ability to transpile Counter
to Rust (HashMap with frequency counting).
"""

import argparse
import sys
from collections import Counter


def cmd_count(args):
    """Count word frequencies. Depyler: proven to terminate"""
    text = sys.stdin.read()
    words = text.split()
    counter = Counter(words)
    for word, count in counter.items():
        print(f"{word}: {count}")


def cmd_top(args):
    """Show top N words. Depyler: proven to terminate"""
    text = sys.stdin.read()
    words = text.split()
    counter = Counter(words)
    for word, count in counter.most_common(args.n):
        print(f"{word}: {count}")


def cmd_chars(args):
    """Count character frequencies. Depyler: proven to terminate"""
    text = sys.stdin.read().strip()
    counter = Counter(text)
    for char, count in counter.most_common():
        if char.strip():
            print(f"'{char}': {count}")


def main():
    """Main entry point. Depyler: proven to terminate"""
    parser = argparse.ArgumentParser(description="Word/character frequency counter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("count", help="Count word frequencies")

    top_parser = subparsers.add_parser("top", help="Show top N words")
    top_parser.add_argument("n", type=int, help="Number of top words")

    subparsers.add_parser("chars", help="Count character frequencies")

    args = parser.parse_args()

    if args.command == "count":
        cmd_count(args)
    elif args.command == "top":
        cmd_top(args)
    elif args.command == "chars":
        cmd_chars(args)


if __name__ == "__main__":
    main()
