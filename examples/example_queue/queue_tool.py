#!/usr/bin/env python3
"""Queue Example - Queue-like operations CLI (simplified)."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Queue operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    f = subs.add_parser("first")
    f.add_argument("items", nargs="+")

    lp = subs.add_parser("last")
    lp.add_argument("items", nargs="+")

    args = parser.parse_args()
    if args.cmd == "first":
        print(args.items[0])
    elif args.cmd == "last":
        print(args.items[len(args.items) - 1])


if __name__ == "__main__":
    main()
