#!/usr/bin/env python3
"""NumPy Log Example - Element-wise log CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Element-wise log tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s3 = subs.add_parser("log3")
    s3.add_argument("a", type=float)
    s3.add_argument("b", type=float)
    s3.add_argument("c", type=float)

    s2 = subs.add_parser("log2")
    s2.add_argument("a", type=float)
    s2.add_argument("b", type=float)

    s1 = subs.add_parser("log1")
    s1.add_argument("a", type=float)

    args = parser.parse_args()
    if args.cmd == "log3":
        arr = np.array([args.a, args.b, args.c])
        result = np.log(arr)
        print(" ".join(str(round(x, 3)) for x in result))
    elif args.cmd == "log2":
        arr = np.array([args.a, args.b])
        result = np.log(arr)
        print(" ".join(str(round(x, 3)) for x in result))
    elif args.cmd == "log1":
        result = np.log(args.a)
        print(round(result, 3))


if __name__ == "__main__":
    main()
