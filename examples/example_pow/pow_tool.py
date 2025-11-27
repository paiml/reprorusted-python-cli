#!/usr/bin/env python3
"""Pow Example - Power operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Power operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("square")
    s.add_argument("x", type=int)
    c = subs.add_parser("cube")
    c.add_argument("x", type=int)
    p = subs.add_parser("power")
    p.add_argument("base", type=int)
    p.add_argument("exp", type=int)

    args = parser.parse_args()
    if args.cmd == "square":
        print(args.x * args.x)
    elif args.cmd == "cube":
        print(args.x * args.x * args.x)
    elif args.cmd == "power":
        result = 1
        i = 0
        while i < args.exp:
            result = result * args.base
            i = i + 1
        print(result)


if __name__ == "__main__":
    main()
