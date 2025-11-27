#!/usr/bin/env python3
"""String Example - String operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    u = subs.add_parser("upper")
    u.add_argument("text")
    lp = subs.add_parser("lower")
    lp.add_argument("text")
    t = subs.add_parser("title")
    t.add_argument("text")
    le = subs.add_parser("length")
    le.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "upper":
        print(args.text.upper())
    elif args.cmd == "lower":
        print(args.text.lower())
    elif args.cmd == "title":
        print(args.text.title())
    elif args.cmd == "length":
        print(len(args.text))


if __name__ == "__main__":
    main()
