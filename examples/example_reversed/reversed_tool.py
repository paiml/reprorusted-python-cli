#!/usr/bin/env python3
"""Reversed Example - Reverse operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Reverse tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("string")
    s.add_argument("text")
    d = subs.add_parser("digits")
    d.add_argument("num", type=int)
    w = subs.add_parser("words")
    w.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "string":
        result = ""
        i = len(args.text) - 1
        while i >= 0:
            result = result + args.text[i]
            i = i - 1
        print(result)
    elif args.cmd == "digits":
        n = args.num
        result = 0
        while n > 0:
            result = result * 10 + n % 10
            n = n // 10
        print(result)
    elif args.cmd == "words":
        parts = args.text.split("_")
        result = parts[2] + "_" + parts[1] + "_" + parts[0]
        print(result)


if __name__ == "__main__":
    main()
