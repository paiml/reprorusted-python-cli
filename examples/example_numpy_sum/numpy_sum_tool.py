#!/usr/bin/env python3
"""NumPy Sum Example - Sum reduction CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Sum reduction tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s3 = subs.add_parser("sum3")
    s3.add_argument("a", type=float)
    s3.add_argument("b", type=float)
    s3.add_argument("c", type=float)

    s4 = subs.add_parser("sum4")
    s4.add_argument("a", type=float)
    s4.add_argument("b", type=float)
    s4.add_argument("c", type=float)
    s4.add_argument("d", type=float)

    s5 = subs.add_parser("sum5")
    s5.add_argument("a", type=float)
    s5.add_argument("b", type=float)
    s5.add_argument("c", type=float)
    s5.add_argument("d", type=float)
    s5.add_argument("e", type=float)

    args = parser.parse_args()
    if args.cmd == "sum3":
        arr = np.array([args.a, args.b, args.c])
        print(np.sum(arr))
    elif args.cmd == "sum4":
        arr = np.array([args.a, args.b, args.c, args.d])
        print(np.sum(arr))
    elif args.cmd == "sum5":
        arr = np.array([args.a, args.b, args.c, args.d, args.e])
        print(np.sum(arr))


if __name__ == "__main__":
    main()
