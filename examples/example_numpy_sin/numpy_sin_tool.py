#!/usr/bin/env python3
"""NumPy Sin Example - Trigonometric sin CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Trigonometric sin tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s3 = subs.add_parser("sin3")
    s3.add_argument("a", type=float)
    s3.add_argument("b", type=float)
    s3.add_argument("c", type=float)

    s2 = subs.add_parser("sin2")
    s2.add_argument("a", type=float)
    s2.add_argument("b", type=float)

    s1 = subs.add_parser("sin1")
    s1.add_argument("a", type=float)

    args = parser.parse_args()
    if args.cmd == "sin3":
        arr = np.array([args.a, args.b, args.c])
        result = np.sin(arr)
        print(" ".join(str(round(x, 1)) for x in result))
    elif args.cmd == "sin2":
        arr = np.array([args.a, args.b])
        result = np.sin(arr)
        print(" ".join(str(round(x, 1)) for x in result))
    elif args.cmd == "sin1":
        result = np.sin(args.a)
        print(round(result, 1))


if __name__ == "__main__":
    main()
