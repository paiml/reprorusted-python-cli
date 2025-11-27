#!/usr/bin/env python3
"""Sum Example - Summation operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Sum tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("add")
    a.add_argument("a", type=int)
    a.add_argument("b", type=int)
    a.add_argument("c", type=int)
    a.add_argument("d", type=int)
    a.add_argument("e", type=int)
    p = subs.add_parser("product")
    p.add_argument("a", type=int)
    p.add_argument("b", type=int)
    p.add_argument("c", type=int)
    av = subs.add_parser("average")
    av.add_argument("a", type=int)
    av.add_argument("b", type=int)
    av.add_argument("c", type=int)

    args = parser.parse_args()
    if args.cmd == "add":
        print(args.a + args.b + args.c + args.d + args.e)
    elif args.cmd == "product":
        print(args.a * args.b * args.c)
    elif args.cmd == "average":
        total = args.a + args.b + args.c
        print(total / 3)


if __name__ == "__main__":
    main()
