#!/usr/bin/env python3
"""Math Example - Basic math functions CLI.

Examples:
    >>> compute_sin(0.0)
    0.0
    >>> compute_sqrt(4.0)
    2.0
    >>> compute_ceil(2.3)
    3
    >>> compute_floor(2.7)
    2
"""

import argparse
import math


def compute_sin(x: float) -> float:
    """Compute sine of x radians.

    >>> compute_sin(0.0)
    0.0
    >>> abs(compute_sin(3.14159265359 / 2) - 1.0) < 0.0001
    True
    """
    return math.sin(x)


def compute_cos(x: float) -> float:
    """Compute cosine of x radians.

    >>> compute_cos(0.0)
    1.0
    >>> abs(compute_cos(math.pi) + 1.0) < 0.0001
    True
    """
    return math.cos(x)


def compute_sqrt(x: float) -> float:
    """Compute square root.

    >>> compute_sqrt(0.0)
    0.0
    >>> compute_sqrt(4.0)
    2.0
    >>> compute_sqrt(9.0)
    3.0
    """
    return math.sqrt(x)


def compute_ceil(x: float) -> int:
    """Compute ceiling.

    >>> compute_ceil(2.0)
    2
    >>> compute_ceil(2.1)
    3
    >>> compute_ceil(-2.1)
    -2
    """
    return math.ceil(x)


def compute_floor(x: float) -> int:
    """Compute floor.

    >>> compute_floor(2.0)
    2
    >>> compute_floor(2.9)
    2
    >>> compute_floor(-2.1)
    -3
    """
    return math.floor(x)


def main():
    parser = argparse.ArgumentParser(description="Math functions tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("sin")
    s.add_argument("x", type=float)
    c = subs.add_parser("cos")
    c.add_argument("x", type=float)
    sq = subs.add_parser("sqrt")
    sq.add_argument("x", type=float)
    ce = subs.add_parser("ceil")
    ce.add_argument("x", type=float)
    fl = subs.add_parser("floor")
    fl.add_argument("x", type=float)

    args = parser.parse_args()
    if args.cmd == "sin":
        print(compute_sin(args.x))
    elif args.cmd == "cos":
        print(compute_cos(args.x))
    elif args.cmd == "sqrt":
        print(compute_sqrt(args.x))
    elif args.cmd == "ceil":
        print(compute_ceil(args.x))
    elif args.cmd == "floor":
        print(compute_floor(args.x))


if __name__ == "__main__":
    main()
