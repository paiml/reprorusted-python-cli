#!/usr/bin/env python3
"""Minmax Example - Min/max operations CLI.

Examples:
    >>> find_min(5, 3, 8, 1, 9)
    1
    >>> find_max(5, 3, 8, 1, 9)
    9
    >>> clamp(15, 0, 10)
    10
"""

import argparse


def find_min(a: int, b: int, c: int, d: int, e: int) -> int:
    """Find minimum of five integers.

    >>> find_min(1, 2, 3, 4, 5)
    1
    >>> find_min(5, 4, 3, 2, 1)
    1
    >>> find_min(3, 1, 4, 1, 5)
    1
    """
    result = a
    if b < result:
        result = b
    if c < result:
        result = c
    if d < result:
        result = d
    if e < result:
        result = e
    return result


def find_max(a: int, b: int, c: int, d: int, e: int) -> int:
    """Find maximum of five integers.

    >>> find_max(1, 2, 3, 4, 5)
    5
    >>> find_max(5, 4, 3, 2, 1)
    5
    >>> find_max(3, 1, 4, 1, 5)
    5
    """
    result = a
    if b > result:
        result = b
    if c > result:
        result = c
    if d > result:
        result = d
    if e > result:
        result = e
    return result


def clamp(val: int, lo: int, hi: int) -> int:
    """Clamp value to range [lo, hi].

    >>> clamp(5, 0, 10)
    5
    >>> clamp(-5, 0, 10)
    0
    >>> clamp(15, 0, 10)
    10
    """
    result = val
    if result < lo:
        result = lo
    if result > hi:
        result = hi
    return result


def main():
    parser = argparse.ArgumentParser(description="Min/max tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    m = subs.add_parser("min")
    m.add_argument("a", type=int)
    m.add_argument("b", type=int)
    m.add_argument("c", type=int)
    m.add_argument("d", type=int)
    m.add_argument("e", type=int)
    x = subs.add_parser("max")
    x.add_argument("a", type=int)
    x.add_argument("b", type=int)
    x.add_argument("c", type=int)
    x.add_argument("d", type=int)
    x.add_argument("e", type=int)
    cl = subs.add_parser("clamp")
    cl.add_argument("val", type=int)
    cl.add_argument("lo", type=int)
    cl.add_argument("hi", type=int)

    args = parser.parse_args()
    if args.cmd == "min":
        print(find_min(args.a, args.b, args.c, args.d, args.e))
    elif args.cmd == "max":
        print(find_max(args.a, args.b, args.c, args.d, args.e))
    elif args.cmd == "clamp":
        print(clamp(args.val, args.lo, args.hi))


if __name__ == "__main__":
    main()
