#!/usr/bin/env python3
"""Operator Example - Basic arithmetic CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Arithmetic operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("add")
    a.add_argument("x", type=int)
    a.add_argument("y", type=int)
    s = subs.add_parser("sub")
    s.add_argument("x", type=int)
    s.add_argument("y", type=int)
    m = subs.add_parser("mul")
    m.add_argument("x", type=int)
    m.add_argument("y", type=int)
    d = subs.add_parser("mod")
    d.add_argument("x", type=int)
    d.add_argument("y", type=int)

    args = parser.parse_args()
    if args.cmd == "add":
        print(args.x + args.y)
    elif args.cmd == "sub":
        print(args.x - args.y)
    elif args.cmd == "mul":
        print(args.x * args.y)
    elif args.cmd == "mod":
        print(args.x % args.y)


if __name__ == "__main__":
    main()
