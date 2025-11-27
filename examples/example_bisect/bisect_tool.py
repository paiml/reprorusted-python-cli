#!/usr/bin/env python3
"""Bisect Example - Binary search CLI."""

import argparse
import bisect


def main():
    parser = argparse.ArgumentParser(description="Binary search tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    lp = subs.add_parser("left")
    lp.add_argument("x", type=int)

    r = subs.add_parser("right")
    r.add_argument("x", type=int)

    args = parser.parse_args()
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    if args.cmd == "left":
        print(bisect.bisect_left(items, args.x))
    elif args.cmd == "right":
        print(bisect.bisect_right(items, args.x))


if __name__ == "__main__":
    main()
