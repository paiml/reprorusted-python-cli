#!/usr/bin/env python3
"""Int Float Example - Type conversion CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Type conversion tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    t = subs.add_parser("toint")
    t.add_argument("x", type=float)
    f = subs.add_parser("tofloat")
    f.add_argument("x", type=int)
    p = subs.add_parser("parse")
    p.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "toint":
        print(int(args.x))
    elif args.cmd == "tofloat":
        print(float(args.x))
    elif args.cmd == "parse":
        print(int(args.text))


if __name__ == "__main__":
    main()
