#!/usr/bin/env python3
"""Ascii Example - ASCII operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="ASCII operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    u = subs.add_parser("upper")
    u.add_argument("code", type=int)
    lo = subs.add_parser("lower")
    lo.add_argument("code", type=int)
    d = subs.add_parser("digit")
    d.add_argument("n", type=int)

    args = parser.parse_args()
    if args.cmd == "upper":
        print(chr(args.code))
    elif args.cmd == "lower":
        print(chr(args.code))
    elif args.cmd == "digit":
        print(ord("0") + args.n)


if __name__ == "__main__":
    main()
