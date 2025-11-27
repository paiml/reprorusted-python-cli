#!/usr/bin/env python3
"""Enum Example - Simple value mapping CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Enum-like operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    c = subs.add_parser("color")
    c.add_argument("name")

    s = subs.add_parser("status")
    s.add_argument("name")

    args = parser.parse_args()
    if args.cmd == "color":
        if args.name == "RED":
            print(1)
        elif args.name == "GREEN":
            print(2)
        elif args.name == "BLUE":
            print(3)
    elif args.cmd == "status":
        if args.name == "PENDING":
            print(1)
        elif args.name == "RUNNING":
            print(2)
        elif args.name == "COMPLETE":
            print(3)
        elif args.name == "FAILED":
            print(4)


if __name__ == "__main__":
    main()
