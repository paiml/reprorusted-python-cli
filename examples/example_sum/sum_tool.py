#!/usr/bin/env python3
"""Sum Example - Summation operations CLI.

Examples:
    >>> sum_five(1, 2, 3, 4, 5)
    15
    >>> product_three(2, 3, 4)
    24
    >>> average_three(3, 6, 9)
    6.0
"""

import argparse


def sum_five(a: int, b: int, c: int, d: int, e: int) -> int:
    """Sum of five integers.

    >>> sum_five(1, 1, 1, 1, 1)
    5
    >>> sum_five(0, 0, 0, 0, 0)
    0
    >>> sum_five(10, 20, 30, 40, 50)
    150
    """
    return a + b + c + d + e


def product_three(a: int, b: int, c: int) -> int:
    """Product of three integers.

    >>> product_three(1, 2, 3)
    6
    >>> product_three(0, 5, 5)
    0
    >>> product_three(2, 2, 2)
    8
    """
    return a * b * c


def average_three(a: int, b: int, c: int) -> float:
    """Average of three integers.

    >>> average_three(1, 2, 3)
    2.0
    >>> average_three(10, 20, 30)
    20.0
    >>> average_three(0, 0, 0)
    0.0
    """
    total = a + b + c
    return total / 3


def main():
    parser = argparse.ArgumentParser(description="Sum tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("add")
    a.add_argument("a", type=int)
    a.add_argument("b", type=int)
    a.add_argument("c", type=int)
    a.add_argument("d", type=int)
    a.add_argument("e", type=int)
    p = subs.add_parser("product")
    p.add_argument("a", type=int)
    p.add_argument("b", type=int)
    p.add_argument("c", type=int)
    av = subs.add_parser("average")
    av.add_argument("a", type=int)
    av.add_argument("b", type=int)
    av.add_argument("c", type=int)

    args = parser.parse_args()
    if args.cmd == "add":
        print(sum_five(args.a, args.b, args.c, args.d, args.e))
    elif args.cmd == "product":
        print(product_three(args.a, args.b, args.c))
    elif args.cmd == "average":
        print(average_three(args.a, args.b, args.c))


if __name__ == "__main__":
    main()
