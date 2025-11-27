#!/usr/bin/env python3
"""Ord Chr Example - Character code operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Character code tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    o = subs.add_parser("ord")
    o.add_argument("char")
    ch = subs.add_parser("chr")
    ch.add_argument("code", type=int)
    co = subs.add_parser("code")
    co.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "ord":
        print(ord(args.char[0]))
    elif args.cmd == "chr":
        print(chr(args.code))
    elif args.cmd == "code":
        result = ""
        i = 0
        while i < len(args.text):
            if i > 0:
                result = result + " "
            result = result + str(ord(args.text[i]))
            i = i + 1
        print(result)


if __name__ == "__main__":
    main()
