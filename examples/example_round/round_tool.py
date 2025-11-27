#!/usr/bin/env python3
"""Round Example - Rounding operations CLI."""

import argparse
import math


def main():
    parser = argparse.ArgumentParser(description="Rounding tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    n = subs.add_parser("nearest")
    n.add_argument("x", type=float)
    f = subs.add_parser("floor")
    f.add_argument("x", type=float)
    c = subs.add_parser("ceil")
    c.add_argument("x", type=float)

    args = parser.parse_args()
    if args.cmd == "nearest":
        print(round(args.x))
    elif args.cmd == "floor":
        print(math.floor(args.x))
    elif args.cmd == "ceil":
        print(math.ceil(args.x))


if __name__ == "__main__":
    main()
