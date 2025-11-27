#!/usr/bin/env python3
"""NumPy Norm Example - Vector norm CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Vector norm tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    l2 = subs.add_parser("l2")
    l2.add_argument("a", type=float)
    l2.add_argument("b", type=float)

    l1 = subs.add_parser("l1")
    l1.add_argument("a", type=float)
    l1.add_argument("b", type=float)
    l1.add_argument("c", type=float)

    li = subs.add_parser("linf")
    li.add_argument("a", type=float)
    li.add_argument("b", type=float)
    li.add_argument("c", type=float)

    args = parser.parse_args()
    if args.cmd == "l2":
        arr = np.array([args.a, args.b])
        print(np.linalg.norm(arr))
    elif args.cmd == "l1":
        arr = np.array([args.a, args.b, args.c])
        print(np.linalg.norm(arr, ord=1))
    elif args.cmd == "linf":
        arr = np.array([args.a, args.b, args.c])
        print(np.linalg.norm(arr, ord=np.inf))


if __name__ == "__main__":
    main()
