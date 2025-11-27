#!/usr/bin/env python3
"""Abs Example - Absolute value operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Absolute value tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    i = subs.add_parser("int")
    i.add_argument("x", type=int)
    f = subs.add_parser("float")
    f.add_argument("x", type=float)

    args = parser.parse_args()
    if args.cmd == "int":
        if args.x < 0:
            print(-args.x)
        else:
            print(args.x)
    elif args.cmd == "float":
        if args.x < 0:
            print(-args.x)
        else:
            print(args.x)


if __name__ == "__main__":
    main()
