#!/usr/bin/env python3
"""Isdigit Example - String type check operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String type check tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    d = subs.add_parser("digit")
    d.add_argument("text")
    a = subs.add_parser("alpha")
    a.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "digit":
        result = True
        i = 0
        while i < len(args.text):
            c = args.text[i]
            if c < "0" or c > "9":
                result = False
            i = i + 1
        if result:
            print("true")
        else:
            print("false")
    elif args.cmd == "alpha":
        result = True
        i = 0
        while i < len(args.text):
            c = args.text[i]
            is_lower = c >= "a" and c <= "z"
            is_upper = c >= "A" and c <= "Z"
            if not is_lower and not is_upper:
                result = False
            i = i + 1
        if result:
            print("true")
        else:
            print("false")


if __name__ == "__main__":
    main()
