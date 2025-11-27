#!/usr/bin/env python3
"""Find Example - String find operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String find tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    f = subs.add_parser("first")
    f.add_argument("text")
    f.add_argument("char")
    la = subs.add_parser("last")
    la.add_argument("text")
    la.add_argument("char")

    args = parser.parse_args()
    if args.cmd == "first":
        result = -1
        i = 0
        while i < len(args.text):
            if args.text[i] == args.char:
                result = i
                break
            i = i + 1
        print(result)
    elif args.cmd == "last":
        result = -1
        i = 0
        while i < len(args.text):
            if args.text[i] == args.char:
                result = i
            i = i + 1
        print(result)


if __name__ == "__main__":
    main()
