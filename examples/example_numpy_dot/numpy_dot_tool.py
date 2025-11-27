#!/usr/bin/env python3
"""NumPy Dot Example - Dot product operations CLI."""

import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Dot product tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    d3 = subs.add_parser("dot3")
    d3.add_argument("a1", type=float)
    d3.add_argument("a2", type=float)
    d3.add_argument("a3", type=float)
    d3.add_argument("b1", type=float)
    d3.add_argument("b2", type=float)
    d3.add_argument("b3", type=float)

    d4 = subs.add_parser("dot4")
    d4.add_argument("a1", type=float)
    d4.add_argument("a2", type=float)
    d4.add_argument("a3", type=float)
    d4.add_argument("a4", type=float)
    d4.add_argument("b1", type=float)
    d4.add_argument("b2", type=float)
    d4.add_argument("b3", type=float)
    d4.add_argument("b4", type=float)

    d2 = subs.add_parser("dot2")
    d2.add_argument("a1", type=float)
    d2.add_argument("a2", type=float)
    d2.add_argument("b1", type=float)
    d2.add_argument("b2", type=float)

    args = parser.parse_args()
    if args.cmd == "dot3":
        a = np.array([args.a1, args.a2, args.a3])
        b = np.array([args.b1, args.b2, args.b3])
        print(np.dot(a, b))
    elif args.cmd == "dot4":
        a = np.array([args.a1, args.a2, args.a3, args.a4])
        b = np.array([args.b1, args.b2, args.b3, args.b4])
        print(np.dot(a, b))
    elif args.cmd == "dot2":
        a = np.array([args.a1, args.a2])
        b = np.array([args.b1, args.b2])
        print(np.dot(a, b))


if __name__ == "__main__":
    main()
