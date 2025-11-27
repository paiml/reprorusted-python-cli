#!/usr/bin/env python3
"""Decimal Example - Decimal arithmetic CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Decimal arithmetic tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("add")
    a.add_argument("x", type=float)
    a.add_argument("y", type=float)
    m = subs.add_parser("mul")
    m.add_argument("x", type=float)
    m.add_argument("y", type=float)
    r = subs.add_parser("round")
    r.add_argument("x", type=float)
    r.add_argument("places", type=int)

    args = parser.parse_args()
    if args.cmd == "add":
        print(args.x + args.y)
    elif args.cmd == "mul":
        print(args.x * args.y)
    elif args.cmd == "round":
        print(round(args.x, args.places))


if __name__ == "__main__":
    main()
