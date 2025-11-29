#!/usr/bin/env python3
"""Pow Example - Power operations CLI.

Examples:
    >>> square(5)
    25
    >>> cube(3)
    27
    >>> power(2, 10)
    1024
"""

import argparse


def square(x: int) -> int:
    """Compute square of integer.

    >>> square(0)
    0
    >>> square(4)
    16
    >>> square(-3)
    9
    """
    return x * x


def cube(x: int) -> int:
    """Compute cube of integer.

    >>> cube(0)
    0
    >>> cube(2)
    8
    >>> cube(-2)
    -8
    """
    return x * x * x


def power(base: int, exp: int) -> int:
    """Compute base raised to exp.

    >>> power(2, 0)
    1
    >>> power(2, 3)
    8
    >>> power(3, 4)
    81
    """
    result = 1
    i = 0
    while i < exp:
        result = result * base
        i = i + 1
    return result


def main():
    parser = argparse.ArgumentParser(description="Power operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("square")
    s.add_argument("x", type=int)
    c = subs.add_parser("cube")
    c.add_argument("x", type=int)
    p = subs.add_parser("power")
    p.add_argument("base", type=int)
    p.add_argument("exp", type=int)

    args = parser.parse_args()
    if args.cmd == "square":
        print(square(args.x))
    elif args.cmd == "cube":
        print(cube(args.x))
    elif args.cmd == "power":
        print(power(args.base, args.exp))


if __name__ == "__main__":
    main()
