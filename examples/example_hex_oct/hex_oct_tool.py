#!/usr/bin/env python3
"""Hex Oct Example - Number base conversion CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Number base conversion tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    h = subs.add_parser("hex")
    h.add_argument("num", type=int)
    o = subs.add_parser("oct")
    o.add_argument("num", type=int)
    d = subs.add_parser("dec")
    d.add_argument("hexval")

    args = parser.parse_args()
    if args.cmd == "hex":
        print(format(args.num, "x"))
    elif args.cmd == "oct":
        print(format(args.num, "o"))
    elif args.cmd == "dec":
        print(int(args.hexval, 16))


if __name__ == "__main__":
    main()
