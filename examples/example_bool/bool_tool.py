#!/usr/bin/env python3
"""Bool Example - Boolean operations CLI.

Examples:
    >>> bool_and(1, 1)
    True
    >>> bool_or(0, 1)
    True
    >>> bool_not(0)
    True
"""

import argparse


def bool_and(x: int, y: int) -> bool:
    """Logical AND of two integers as booleans.

    >>> bool_and(1, 1)
    True
    >>> bool_and(1, 0)
    False
    >>> bool_and(0, 0)
    False
    """
    return x != 0 and y != 0


def bool_or(x: int, y: int) -> bool:
    """Logical OR of two integers as booleans.

    >>> bool_or(1, 0)
    True
    >>> bool_or(0, 1)
    True
    >>> bool_or(0, 0)
    False
    """
    return x != 0 or y != 0


def bool_not(x: int) -> bool:
    """Logical NOT of integer as boolean.

    >>> bool_not(0)
    True
    >>> bool_not(1)
    False
    >>> bool_not(5)
    False
    """
    return x == 0


def main():
    parser = argparse.ArgumentParser(description="Boolean operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("and")
    a.add_argument("x", type=int)
    a.add_argument("y", type=int)
    o = subs.add_parser("or")
    o.add_argument("x", type=int)
    o.add_argument("y", type=int)
    n = subs.add_parser("not")
    n.add_argument("x", type=int)

    args = parser.parse_args()
    if args.cmd == "and":
        print("true" if bool_and(args.x, args.y) else "false")
    elif args.cmd == "or":
        print("true" if bool_or(args.x, args.y) else "false")
    elif args.cmd == "not":
        print("true" if bool_not(args.x) else "false")


if __name__ == "__main__":
    main()
