#!/usr/bin/env python3
"""Functools Example - Functional operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Functional operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    r = subs.add_parser("reduce")
    r.add_argument("op")
    r.add_argument("a", type=int)
    r.add_argument("b", type=int)
    r.add_argument("c", type=int)
    p = subs.add_parser("partial")
    p.add_argument("base", type=int)
    p.add_argument("add", type=int)

    args = parser.parse_args()
    if args.cmd == "reduce":
        if args.op == "add":
            print(args.a + args.b + args.c)
        elif args.op == "mul":
            print(args.a * args.b * args.c)
    elif args.cmd == "partial":
        print(args.base + args.add)


if __name__ == "__main__":
    main()
