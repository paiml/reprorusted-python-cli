#!/usr/bin/env python3
"""Math Example - Basic math functions CLI."""

import argparse
import math


def main():
    parser = argparse.ArgumentParser(description="Math functions tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("sin")
    s.add_argument("x", type=float)
    c = subs.add_parser("cos")
    c.add_argument("x", type=float)
    sq = subs.add_parser("sqrt")
    sq.add_argument("x", type=float)
    ce = subs.add_parser("ceil")
    ce.add_argument("x", type=float)
    fl = subs.add_parser("floor")
    fl.add_argument("x", type=float)

    args = parser.parse_args()
    if args.cmd == "sin":
        print(math.sin(args.x))
    elif args.cmd == "cos":
        print(math.cos(args.x))
    elif args.cmd == "sqrt":
        print(math.sqrt(args.x))
    elif args.cmd == "ceil":
        print(math.ceil(args.x))
    elif args.cmd == "floor":
        print(math.floor(args.x))


if __name__ == "__main__":
    main()
