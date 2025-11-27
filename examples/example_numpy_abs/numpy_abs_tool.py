#!/usr/bin/env python3
"""NumPy Abs Example - Element-wise abs CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Element-wise abs tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s3 = subs.add_parser("abs3")
    s3.add_argument("a", type=float)
    s3.add_argument("b", type=float)
    s3.add_argument("c", type=float)

    s4 = subs.add_parser("abs4")
    s4.add_argument("a", type=float)
    s4.add_argument("b", type=float)
    s4.add_argument("c", type=float)
    s4.add_argument("d", type=float)

    s2 = subs.add_parser("abs2")
    s2.add_argument("a", type=float)
    s2.add_argument("b", type=float)

    args = parser.parse_args()
    if args.cmd == "abs3":
        arr = np.array([args.a, args.b, args.c])
        result = np.abs(arr)
        print(" ".join(str(x) for x in result))
    elif args.cmd == "abs4":
        arr = np.array([args.a, args.b, args.c, args.d])
        result = np.abs(arr)
        print(" ".join(str(x) for x in result))
    elif args.cmd == "abs2":
        arr = np.array([args.a, args.b])
        result = np.abs(arr)
        print(" ".join(str(x) for x in result))


if __name__ == "__main__":
    main()
