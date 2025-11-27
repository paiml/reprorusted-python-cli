#!/usr/bin/env python3
"""NumPy Normalize Example - Unit vector normalization CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Unit vector normalization tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    n3 = subs.add_parser("norm3")
    n3.add_argument("a", type=float)
    n3.add_argument("b", type=float)
    n3.add_argument("c", type=float)

    n2 = subs.add_parser("norm2")
    n2.add_argument("a", type=float)
    n2.add_argument("b", type=float)

    n4 = subs.add_parser("norm4")
    n4.add_argument("a", type=float)
    n4.add_argument("b", type=float)
    n4.add_argument("c", type=float)
    n4.add_argument("d", type=float)

    args = parser.parse_args()
    if args.cmd == "norm3":
        arr = np.array([args.a, args.b, args.c])
        norm = np.linalg.norm(arr)
        result = arr / norm if norm > 0 else arr
        print(" ".join(str(round(x, 2)) for x in result))
    elif args.cmd == "norm2":
        arr = np.array([args.a, args.b])
        norm = np.linalg.norm(arr)
        result = arr / norm if norm > 0 else arr
        print(" ".join(str(round(x, 2)) for x in result))
    elif args.cmd == "norm4":
        arr = np.array([args.a, args.b, args.c, args.d])
        norm = np.linalg.norm(arr)
        result = arr / norm if norm > 0 else arr
        print(" ".join(str(round(x, 2)) for x in result))


if __name__ == "__main__":
    main()
