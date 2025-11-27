#!/usr/bin/env python3
"""Heapq Example - Heap min/max CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Heap operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    m = subs.add_parser("min")
    m.add_argument("a", type=int)
    m.add_argument("b", type=int)
    m.add_argument("c", type=int)

    mx = subs.add_parser("max")
    mx.add_argument("a", type=int)
    mx.add_argument("b", type=int)
    mx.add_argument("c", type=int)

    args = parser.parse_args()
    if args.cmd == "min":
        print(min(args.a, min(args.b, args.c)))
    elif args.cmd == "max":
        print(max(args.a, max(args.b, args.c)))


if __name__ == "__main__":
    main()
