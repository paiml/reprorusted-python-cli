#!/usr/bin/env python3
"""Itertools Example - Iterator operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Iterator operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    r = subs.add_parser("repeat")
    r.add_argument("item")
    r.add_argument("n", type=int)
    c = subs.add_parser("cycle")
    c.add_argument("item")
    c.add_argument("n", type=int)
    ch = subs.add_parser("chain")
    ch.add_argument("a")
    ch.add_argument("b")

    args = parser.parse_args()
    if args.cmd == "repeat":
        i = 0
        while i < args.n:
            print(args.item)
            i = i + 1
    elif args.cmd == "cycle":
        i = 0
        while i < args.n:
            print(args.item)
            i = i + 1
    elif args.cmd == "chain":
        print(args.a)
        print(args.b)


if __name__ == "__main__":
    main()
