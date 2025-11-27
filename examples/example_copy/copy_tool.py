#!/usr/bin/env python3
"""Copy Example - Copy operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Copy operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("shallow")
    s.add_argument("value")
    d = subs.add_parser("deep")
    d.add_argument("value")
    du = subs.add_parser("dup")
    du.add_argument("value")
    du.add_argument("times", type=int)

    args = parser.parse_args()
    if args.cmd == "shallow":
        print(args.value)
    elif args.cmd == "deep":
        print(args.value)
    elif args.cmd == "dup":
        i = 0
        while i < args.times:
            print(args.value)
            i = i + 1


if __name__ == "__main__":
    main()
