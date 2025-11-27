#!/usr/bin/env python3
"""Regex Example - Simple pattern matching CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Pattern matching tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    m = subs.add_parser("match")
    m.add_argument("pattern")
    m.add_argument("text")
    c = subs.add_parser("count")
    c.add_argument("char")
    c.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "match":
        if args.pattern in args.text:
            print("yes")
        else:
            print("no")
    elif args.cmd == "count":
        print(args.text.count(args.char))


if __name__ == "__main__":
    main()
