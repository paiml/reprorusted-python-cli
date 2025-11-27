#!/usr/bin/env python3
"""Divmod Example - Division and modulo operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Divmod tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    c = subs.add_parser("calc")
    c.add_argument("a", type=int)
    c.add_argument("b", type=int)
    q = subs.add_parser("quot")
    q.add_argument("a", type=int)
    q.add_argument("b", type=int)
    r = subs.add_parser("rem")
    r.add_argument("a", type=int)
    r.add_argument("b", type=int)

    args = parser.parse_args()
    if args.cmd == "calc":
        print(f"{args.a // args.b} {args.a % args.b}")
    elif args.cmd == "quot":
        print(args.a // args.b)
    elif args.cmd == "rem":
        print(args.a % args.b)


if __name__ == "__main__":
    main()
