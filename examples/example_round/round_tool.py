#!/usr/bin/env python3
"""Round Example - Rounding operations CLI.

Examples:
    >>> round_nearest(2.4)
    2
    >>> round_nearest(2.6)
    3
    >>> round_floor(2.9)
    2
    >>> round_ceil(2.1)
    3
"""

import argparse
import math


def round_nearest(x: float) -> int:
    """Round to nearest integer.

    >>> round_nearest(0.0)
    0
    >>> round_nearest(2.5)
    2
    >>> round_nearest(3.5)
    4
    >>> round_nearest(-2.5)
    -2
    """
    return round(x)


def round_floor(x: float) -> int:
    """Round down to nearest integer.

    >>> round_floor(2.0)
    2
    >>> round_floor(2.9)
    2
    >>> round_floor(-2.1)
    -3
    """
    return math.floor(x)


def round_ceil(x: float) -> int:
    """Round up to nearest integer.

    >>> round_ceil(2.0)
    2
    >>> round_ceil(2.1)
    3
    >>> round_ceil(-2.9)
    -2
    """
    return math.ceil(x)


def main():
    parser = argparse.ArgumentParser(description="Rounding tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    n = subs.add_parser("nearest")
    n.add_argument("x", type=float)
    f = subs.add_parser("floor")
    f.add_argument("x", type=float)
    c = subs.add_parser("ceil")
    c.add_argument("x", type=float)

    args = parser.parse_args()
    if args.cmd == "nearest":
        print(round_nearest(args.x))
    elif args.cmd == "floor":
        print(round_floor(args.x))
    elif args.cmd == "ceil":
        print(round_ceil(args.x))


if __name__ == "__main__":
    main()
