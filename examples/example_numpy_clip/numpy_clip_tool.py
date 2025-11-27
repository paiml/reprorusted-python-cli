#!/usr/bin/env python3
"""NumPy Clip Example - Clip/clamp CLI."""

import argparse
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Clip/clamp tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    c3 = subs.add_parser("clip3")
    c3.add_argument("a", type=float)
    c3.add_argument("b", type=float)
    c3.add_argument("c", type=float)
    c3.add_argument("lo", type=float)
    c3.add_argument("hi", type=float)

    c4 = subs.add_parser("clip4")
    c4.add_argument("a", type=float)
    c4.add_argument("b", type=float)
    c4.add_argument("c", type=float)
    c4.add_argument("d", type=float)
    c4.add_argument("lo", type=float)
    c4.add_argument("hi", type=float)

    c2 = subs.add_parser("clip2")
    c2.add_argument("a", type=float)
    c2.add_argument("b", type=float)
    c2.add_argument("lo", type=float)
    c2.add_argument("hi", type=float)

    args = parser.parse_args()
    if args.cmd == "clip3":
        arr = np.array([args.a, args.b, args.c])
        result = np.clip(arr, args.lo, args.hi)
        print(" ".join(str(x) for x in result))
    elif args.cmd == "clip4":
        arr = np.array([args.a, args.b, args.c, args.d])
        result = np.clip(arr, args.lo, args.hi)
        print(" ".join(str(x) for x in result))
    elif args.cmd == "clip2":
        arr = np.array([args.a, args.b])
        result = np.clip(arr, args.lo, args.hi)
        print(" ".join(str(x) for x in result))


if __name__ == "__main__":
    main()
