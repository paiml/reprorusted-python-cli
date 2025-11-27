#!/usr/bin/env python3
"""Gzip Example - Compression info CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Compression info tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    r = subs.add_parser("ratio")
    r.add_argument("original", type=int)
    r.add_argument("compressed", type=int)
    s = subs.add_parser("savings")
    s.add_argument("original", type=int)
    s.add_argument("compressed", type=int)

    args = parser.parse_args()
    if args.cmd == "ratio":
        print(args.original / args.compressed)
    elif args.cmd == "savings":
        print((args.original - args.compressed) * 100 / args.original)


if __name__ == "__main__":
    main()
