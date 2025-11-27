#!/usr/bin/env python3
"""NumPy Argmax Example - Argmax index CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Argmax index tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s3 = subs.add_parser("argmax3")
    s3.add_argument("a", type=float)
    s3.add_argument("b", type=float)
    s3.add_argument("c", type=float)

    s4 = subs.add_parser("argmax4")
    s4.add_argument("a", type=float)
    s4.add_argument("b", type=float)
    s4.add_argument("c", type=float)
    s4.add_argument("d", type=float)

    s5 = subs.add_parser("argmax5")
    s5.add_argument("a", type=float)
    s5.add_argument("b", type=float)
    s5.add_argument("c", type=float)
    s5.add_argument("d", type=float)
    s5.add_argument("e", type=float)

    args = parser.parse_args()
    if args.cmd == "argmax3":
        arr = np.array([args.a, args.b, args.c])
        print(np.argmax(arr))
    elif args.cmd == "argmax4":
        arr = np.array([args.a, args.b, args.c, args.d])
        print(np.argmax(arr))
    elif args.cmd == "argmax5":
        arr = np.array([args.a, args.b, args.c, args.d, args.e])
        print(np.argmax(arr))


if __name__ == "__main__":
    main()
