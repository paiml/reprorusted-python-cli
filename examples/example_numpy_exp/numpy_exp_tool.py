#!/usr/bin/env python3
"""NumPy Exp Example - Element-wise exp CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Element-wise exp tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s3 = subs.add_parser("exp3")
    s3.add_argument("a", type=float)
    s3.add_argument("b", type=float)
    s3.add_argument("c", type=float)

    s2 = subs.add_parser("exp2")
    s2.add_argument("a", type=float)
    s2.add_argument("b", type=float)

    s1 = subs.add_parser("exp1")
    s1.add_argument("a", type=float)

    args = parser.parse_args()
    if args.cmd == "exp3":
        arr = np.array([args.a, args.b, args.c])
        result = np.exp(arr)
        print(" ".join(str(round(x, 3)) for x in result))
    elif args.cmd == "exp2":
        arr = np.array([args.a, args.b])
        result = np.exp(arr)
        print(" ".join(str(round(x, 3)) for x in result))
    elif args.cmd == "exp1":
        result = np.exp(args.a)
        print(round(result, 3))


if __name__ == "__main__":
    main()
