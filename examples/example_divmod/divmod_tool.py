#!/usr/bin/env python3
"""Divmod Example - Division and modulo operations CLI.

Examples:
    >>> integer_divide(17, 5)
    3
    >>> modulo(17, 5)
    2
    >>> divmod_pair(17, 5)
    (3, 2)
"""

import argparse


def integer_divide(a: int, b: int) -> int:
    """Integer division (floor division).

    >>> integer_divide(10, 3)
    3
    >>> integer_divide(9, 3)
    3
    >>> integer_divide(-10, 3)
    -4
    """
    return a // b


def modulo(a: int, b: int) -> int:
    """Remainder after integer division.

    >>> modulo(10, 3)
    1
    >>> modulo(9, 3)
    0
    >>> modulo(7, 4)
    3
    """
    return a % b


def divmod_pair(a: int, b: int) -> tuple:
    """Return both quotient and remainder.

    >>> divmod_pair(10, 3)
    (3, 1)
    >>> divmod_pair(20, 7)
    (2, 6)
    """
    return (a // b, a % b)


def main():
    parser = argparse.ArgumentParser(description="Divmod tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    c = subs.add_parser("calc")
    c.add_argument("a", type=int)
    c.add_argument("b", type=int)
    q = subs.add_parser("quot")
    q.add_argument("a", type=int)
    q.add_argument("b", type=int)
    r = subs.add_parser("rem")
    r.add_argument("a", type=int)
    r.add_argument("b", type=int)

    args = parser.parse_args()
    if args.cmd == "calc":
        q, r = divmod_pair(args.a, args.b)
        print(f"{q} {r}")
    elif args.cmd == "quot":
        print(integer_divide(args.a, args.b))
    elif args.cmd == "rem":
        print(modulo(args.a, args.b))


if __name__ == "__main__":
    main()
