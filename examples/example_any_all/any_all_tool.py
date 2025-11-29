#!/usr/bin/env python3
"""Any All Example - Any/all operations CLI.

Examples:
    >>> check_any(0, 0, 1, 0)
    True
    >>> check_all(1, 1, 1, 1)
    True
"""

import argparse


def check_any(a: int, b: int, c: int, d: int) -> bool:
    """Check if any value is truthy.

    >>> check_any(0, 0, 0, 0)
    False
    >>> check_any(1, 0, 0, 0)
    True
    >>> check_any(0, 0, 0, 1)
    True
    """
    return a != 0 or b != 0 or c != 0 or d != 0


def check_all(a: int, b: int, c: int, d: int) -> bool:
    """Check if all values are truthy.

    >>> check_all(1, 1, 1, 1)
    True
    >>> check_all(1, 1, 1, 0)
    False
    >>> check_all(0, 0, 0, 0)
    False
    """
    return a != 0 and b != 0 and c != 0 and d != 0


def main():
    parser = argparse.ArgumentParser(description="Any/all operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("any")
    a.add_argument("a", type=int)
    a.add_argument("b", type=int)
    a.add_argument("c", type=int)
    a.add_argument("d", type=int)
    al = subs.add_parser("all")
    al.add_argument("a", type=int)
    al.add_argument("b", type=int)
    al.add_argument("c", type=int)
    al.add_argument("d", type=int)

    args = parser.parse_args()
    if args.cmd == "any":
        print("true" if check_any(args.a, args.b, args.c, args.d) else "false")
    elif args.cmd == "all":
        print("true" if check_all(args.a, args.b, args.c, args.d) else "false")


if __name__ == "__main__":
    main()
