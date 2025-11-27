#!/usr/bin/env python3
"""NumPy Mul Example - Element-wise mul CLI."""

import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Element-wise mul tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a3 = subs.add_parser("mul3")
    a3.add_argument("a1", type=float)
    a3.add_argument("a2", type=float)
    a3.add_argument("a3", type=float)
    a3.add_argument("b1", type=float)
    a3.add_argument("b2", type=float)
    a3.add_argument("b3", type=float)

    a2 = subs.add_parser("mul2")
    a2.add_argument("a1", type=float)
    a2.add_argument("a2", type=float)
    a2.add_argument("b1", type=float)
    a2.add_argument("b2", type=float)

    a4 = subs.add_parser("mul4")
    a4.add_argument("a1", type=float)
    a4.add_argument("a2", type=float)
    a4.add_argument("a3", type=float)
    a4.add_argument("a4", type=float)
    a4.add_argument("b1", type=float)
    a4.add_argument("b2", type=float)
    a4.add_argument("b3", type=float)
    a4.add_argument("b4", type=float)

    args = parser.parse_args()
    if args.cmd == "mul3":
        a = np.array([args.a1, args.a2, args.a3])
        b = np.array([args.b1, args.b2, args.b3])
        result = a * b
        print(" ".join(str(x) for x in result))
    elif args.cmd == "mul2":
        a = np.array([args.a1, args.a2])
        b = np.array([args.b1, args.b2])
        result = a * b
        print(" ".join(str(x) for x in result))
    elif args.cmd == "mul4":
        a = np.array([args.a1, args.a2, args.a3, args.a4])
        b = np.array([args.b1, args.b2, args.b3, args.b4])
        result = a * b
        print(" ".join(str(x) for x in result))


if __name__ == "__main__":
    main()
