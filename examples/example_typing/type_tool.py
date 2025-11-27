#!/usr/bin/env python3
"""Typing Example - Type checking CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Type checking tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    c = subs.add_parser("check")
    c.add_argument("typename")
    c.add_argument("value")

    args = parser.parse_args()
    if args.cmd == "check":
        if args.typename == "int":
            print("valid int")
        elif args.typename == "float":
            print("valid float")
        elif args.typename == "str":
            print("valid str")


if __name__ == "__main__":
    main()
