#!/usr/bin/env python3
"""Config Example - Key-value parsing CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Config parsing tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    k = subs.add_parser("key")
    k.add_argument("pair")
    v = subs.add_parser("value")
    v.add_argument("pair")
    c = subs.add_parser("count")
    c.add_argument("data")

    args = parser.parse_args()
    if args.cmd == "key":
        parts = args.pair.split("=")
        print(parts[0])
    elif args.cmd == "value":
        parts = args.pair.split("=")
        print(parts[1])
    elif args.cmd == "count":
        print(len(args.data.split(",")))


if __name__ == "__main__":
    main()
