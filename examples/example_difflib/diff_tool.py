#!/usr/bin/env python3
"""Difflib Example - Text comparison CLI."""

import argparse
import difflib


def cmd_diff(args):
    """Show unified diff. Depyler: proven to terminate"""
    with open(args.file1) as f1:
        lines1 = f1.readlines()
    with open(args.file2) as f2:
        lines2 = f2.readlines()
    diff = difflib.unified_diff(lines1, lines2, fromfile=args.file1, tofile=args.file2)
    for line in diff:
        print(line, end="")


def cmd_ratio(args):
    """Calculate similarity ratio. Depyler: proven to terminate"""
    ratio = difflib.SequenceMatcher(None, args.str1, args.str2).ratio()
    print(f"Similarity: {ratio:.4f}")


def cmd_close(args):
    """Find close matches. Depyler: proven to terminate"""
    matches = difflib.get_close_matches(args.word, args.candidates, n=3, cutoff=0.6)
    for m in matches:
        print(m)


def main():
    parser = argparse.ArgumentParser(description="Text diff tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    diff = subparsers.add_parser("diff")
    diff.add_argument("file1")
    diff.add_argument("file2")

    ratio = subparsers.add_parser("ratio")
    ratio.add_argument("str1")
    ratio.add_argument("str2")

    close = subparsers.add_parser("close")
    close.add_argument("word")
    close.add_argument("candidates", nargs="+")

    args = parser.parse_args()
    {"diff": cmd_diff, "ratio": cmd_ratio, "close": cmd_close}[args.command](args)


if __name__ == "__main__":
    main()
