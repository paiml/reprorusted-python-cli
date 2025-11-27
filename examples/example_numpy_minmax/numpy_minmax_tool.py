#!/usr/bin/env python3
"""NumPy Minmax Example - Min-max normalization CLI."""

import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Min-max normalization tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    m3 = subs.add_parser("minmax3")
    m3.add_argument("a", type=float)
    m3.add_argument("b", type=float)
    m3.add_argument("c", type=float)

    m4 = subs.add_parser("minmax4")
    m4.add_argument("a", type=float)
    m4.add_argument("b", type=float)
    m4.add_argument("c", type=float)
    m4.add_argument("d", type=float)

    m2 = subs.add_parser("minmax2")
    m2.add_argument("a", type=float)
    m2.add_argument("b", type=float)

    args = parser.parse_args()
    if args.cmd == "minmax3":
        arr = np.array([args.a, args.b, args.c])
        min_val = np.min(arr)
        max_val = np.max(arr)
        denom = max_val - min_val
        result = (arr - min_val) / denom if denom > 0 else arr * 0
        print(" ".join(str(round(x, 2)) for x in result))
    elif args.cmd == "minmax4":
        arr = np.array([args.a, args.b, args.c, args.d])
        min_val = np.min(arr)
        max_val = np.max(arr)
        denom = max_val - min_val
        result = (arr - min_val) / denom if denom > 0 else arr * 0
        print(" ".join(str(round(x, 2)) for x in result))
    elif args.cmd == "minmax2":
        arr = np.array([args.a, args.b])
        min_val = np.min(arr)
        max_val = np.max(arr)
        denom = max_val - min_val
        result = (arr - min_val) / denom if denom > 0 else arr * 0
        print(" ".join(str(round(x, 2)) for x in result))


if __name__ == "__main__":
    main()
