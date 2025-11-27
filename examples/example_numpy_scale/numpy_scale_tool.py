#!/usr/bin/env python3
"""NumPy Scale Example - Scalar multiplication CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Scalar multiplication tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s3 = subs.add_parser("scale3")
    s3.add_argument("a", type=float)
    s3.add_argument("b", type=float)
    s3.add_argument("c", type=float)
    s3.add_argument("scalar", type=float)

    s4 = subs.add_parser("scale4")
    s4.add_argument("a", type=float)
    s4.add_argument("b", type=float)
    s4.add_argument("c", type=float)
    s4.add_argument("d", type=float)
    s4.add_argument("scalar", type=float)

    s2 = subs.add_parser("scale2")
    s2.add_argument("a", type=float)
    s2.add_argument("b", type=float)
    s2.add_argument("scalar", type=float)

    args = parser.parse_args()
    if args.cmd == "scale3":
        arr = np.array([args.a, args.b, args.c])
        result = arr * args.scalar
        print(" ".join(str(x) for x in result))
    elif args.cmd == "scale4":
        arr = np.array([args.a, args.b, args.c, args.d])
        result = arr * args.scalar
        print(" ".join(str(x) for x in result))
    elif args.cmd == "scale2":
        arr = np.array([args.a, args.b])
        result = arr * args.scalar
        print(" ".join(str(x) for x in result))


if __name__ == "__main__":
    main()
