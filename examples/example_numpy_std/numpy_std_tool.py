#!/usr/bin/env python3
"""NumPy Std Example - Std reduction CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Std reduction tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s3 = subs.add_parser("std3")
    s3.add_argument("a", type=float)
    s3.add_argument("b", type=float)
    s3.add_argument("c", type=float)

    s4 = subs.add_parser("std4")
    s4.add_argument("a", type=float)
    s4.add_argument("b", type=float)
    s4.add_argument("c", type=float)
    s4.add_argument("d", type=float)

    s5 = subs.add_parser("std5")
    s5.add_argument("a", type=float)
    s5.add_argument("b", type=float)
    s5.add_argument("c", type=float)
    s5.add_argument("d", type=float)
    s5.add_argument("e", type=float)

    args = parser.parse_args()
    if args.cmd == "std3":
        arr = np.array([args.a, args.b, args.c])
        print(round(np.std(arr), 3))
    elif args.cmd == "std4":
        arr = np.array([args.a, args.b, args.c, args.d])
        print(round(np.std(arr), 3))
    elif args.cmd == "std5":
        arr = np.array([args.a, args.b, args.c, args.d, args.e])
        print(round(np.std(arr), 3))


if __name__ == "__main__":
    main()
