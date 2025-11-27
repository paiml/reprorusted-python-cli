#!/usr/bin/env python3
"""NumPy Zscore Example - Z-score normalization CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Z-score normalization tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    z3 = subs.add_parser("zscore3")
    z3.add_argument("a", type=float)
    z3.add_argument("b", type=float)
    z3.add_argument("c", type=float)

    z4 = subs.add_parser("zscore4")
    z4.add_argument("a", type=float)
    z4.add_argument("b", type=float)
    z4.add_argument("c", type=float)
    z4.add_argument("d", type=float)

    z2 = subs.add_parser("zscore2")
    z2.add_argument("a", type=float)
    z2.add_argument("b", type=float)

    args = parser.parse_args()
    if args.cmd == "zscore3":
        arr = np.array([args.a, args.b, args.c])
        mean = np.mean(arr)
        std = np.std(arr)
        result = (arr - mean) / std if std > 0 else arr - mean
        print(" ".join(str(round(x, 2)) for x in result))
    elif args.cmd == "zscore4":
        arr = np.array([args.a, args.b, args.c, args.d])
        mean = np.mean(arr)
        std = np.std(arr)
        result = (arr - mean) / std if std > 0 else arr - mean
        print(" ".join(str(round(x, 2)) for x in result))
    elif args.cmd == "zscore2":
        arr = np.array([args.a, args.b])
        mean = np.mean(arr)
        std = np.std(arr)
        result = (arr - mean) / std if std > 0 else arr - mean
        print(" ".join(str(round(x, 2)) for x in result))


if __name__ == "__main__":
    main()
