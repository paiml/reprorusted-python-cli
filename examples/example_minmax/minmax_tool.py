#!/usr/bin/env python3
"""Minmax Example - Min/max operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Min/max tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    m = subs.add_parser("min")
    m.add_argument("a", type=int)
    m.add_argument("b", type=int)
    m.add_argument("c", type=int)
    m.add_argument("d", type=int)
    m.add_argument("e", type=int)
    x = subs.add_parser("max")
    x.add_argument("a", type=int)
    x.add_argument("b", type=int)
    x.add_argument("c", type=int)
    x.add_argument("d", type=int)
    x.add_argument("e", type=int)
    cl = subs.add_parser("clamp")
    cl.add_argument("val", type=int)
    cl.add_argument("lo", type=int)
    cl.add_argument("hi", type=int)

    args = parser.parse_args()
    if args.cmd == "min":
        result = args.a
        if args.b < result:
            result = args.b
        if args.c < result:
            result = args.c
        if args.d < result:
            result = args.d
        if args.e < result:
            result = args.e
        print(result)
    elif args.cmd == "max":
        result = args.a
        if args.b > result:
            result = args.b
        if args.c > result:
            result = args.c
        if args.d > result:
            result = args.d
        if args.e > result:
            result = args.e
        print(result)
    elif args.cmd == "clamp":
        result = args.val
        if result < args.lo:
            result = args.lo
        if result > args.hi:
            result = args.hi
        print(result)


if __name__ == "__main__":
    main()
