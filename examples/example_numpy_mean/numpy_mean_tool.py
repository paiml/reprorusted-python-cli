#!/usr/bin/env python3
"""NumPy Mean Example - Mean reduction CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Mean reduction tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    m3 = subs.add_parser("mean3")
    m3.add_argument("a", type=float)
    m3.add_argument("b", type=float)
    m3.add_argument("c", type=float)

    m4 = subs.add_parser("mean4")
    m4.add_argument("a", type=float)
    m4.add_argument("b", type=float)
    m4.add_argument("c", type=float)
    m4.add_argument("d", type=float)

    m5 = subs.add_parser("mean5")
    m5.add_argument("a", type=float)
    m5.add_argument("b", type=float)
    m5.add_argument("c", type=float)
    m5.add_argument("d", type=float)
    m5.add_argument("e", type=float)

    args = parser.parse_args()
    if args.cmd == "mean3":
        arr = np.array([args.a, args.b, args.c])
        print(np.mean(arr))
    elif args.cmd == "mean4":
        arr = np.array([args.a, args.b, args.c, args.d])
        print(np.mean(arr))
    elif args.cmd == "mean5":
        arr = np.array([args.a, args.b, args.c, args.d, args.e])
        print(np.mean(arr))


if __name__ == "__main__":
    main()
