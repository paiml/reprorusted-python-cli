#!/usr/bin/env python3
"""Bin Example - Binary operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Binary operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    t = subs.add_parser("tobin")
    t.add_argument("num", type=int)
    f = subs.add_parser("frombin")
    f.add_argument("binstr")
    b = subs.add_parser("bits")
    b.add_argument("num", type=int)

    args = parser.parse_args()
    if args.cmd == "tobin":
        print(format(args.num, "b"))
    elif args.cmd == "frombin":
        print(int(args.binstr, 2))
    elif args.cmd == "bits":
        count = 0
        n = args.num
        while n > 0:
            count = count + 1
            n = n // 2
        print(count)


if __name__ == "__main__":
    main()
