#!/usr/bin/env python3
"""Replace Example - String replace operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String replace tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    ch = subs.add_parser("char")
    ch.add_argument("text")
    ch.add_argument("old")
    ch.add_argument("new")
    f = subs.add_parser("first")
    f.add_argument("text")
    f.add_argument("new")
    a = subs.add_parser("all")
    a.add_argument("text")
    a.add_argument("new")

    args = parser.parse_args()
    if args.cmd == "char":
        print(args.text.replace(args.old, args.new))
    elif args.cmd == "first":
        result = ""
        found = False
        i = 0
        while i < len(args.text):
            if not found and args.text[i] == args.text[0]:
                result = result + args.new
                found = True
            else:
                result = result + args.text[i]
            i = i + 1
        print(result)
    elif args.cmd == "all":
        result = ""
        i = 0
        while i < len(args.text):
            result = result + args.new
            i = i + 1
        print(result)


if __name__ == "__main__":
    main()
