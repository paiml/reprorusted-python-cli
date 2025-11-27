#!/usr/bin/env python3
"""Array Example - Aggregate operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Array operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("sum")
    s.add_argument("a", type=int)
    s.add_argument("b", type=int)
    s.add_argument("c", type=int)

    p = subs.add_parser("product")
    p.add_argument("a", type=int)
    p.add_argument("b", type=int)
    p.add_argument("c", type=int)

    args = parser.parse_args()
    if args.cmd == "sum":
        print(args.a + args.b + args.c)
    elif args.cmd == "product":
        print(args.a * args.b * args.c)


if __name__ == "__main__":
    main()
