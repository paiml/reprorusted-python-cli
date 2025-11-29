#!/usr/bin/env python3
"""Abs Example - Absolute value operations CLI.

Examples:
    >>> compute_abs_int(-5)
    5
    >>> compute_abs_int(5)
    5
    >>> compute_abs_float(-3.14)
    3.14
    >>> compute_abs_float(2.71)
    2.71
"""

import argparse


def compute_abs_int(x: int) -> int:
    """Compute absolute value of integer.

    >>> compute_abs_int(-10)
    10
    >>> compute_abs_int(0)
    0
    >>> compute_abs_int(42)
    42
    """
    if x < 0:
        return -x
    return x


def compute_abs_float(x: float) -> float:
    """Compute absolute value of float.

    >>> compute_abs_float(-2.5)
    2.5
    >>> compute_abs_float(0.0)
    0.0
    >>> compute_abs_float(1.5)
    1.5
    """
    if x < 0:
        return -x
    return x


def main():
    parser = argparse.ArgumentParser(description="Absolute value tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    i = subs.add_parser("int")
    i.add_argument("x", type=int)
    f = subs.add_parser("float")
    f.add_argument("x", type=float)

    args = parser.parse_args()
    if args.cmd == "int":
        print(compute_abs_int(args.x))
    elif args.cmd == "float":
        print(compute_abs_float(args.x))


if __name__ == "__main__":
    main()
