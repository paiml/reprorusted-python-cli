#!/usr/bin/env python3
"""Len Example - Length operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Length tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("string")
    s.add_argument("text")
    d = subs.add_parser("digits")
    d.add_argument("num", type=int)
    w = subs.add_parser("words")
    w.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "string":
        print(len(args.text))
    elif args.cmd == "digits":
        count = 0
        n = args.num
        if n < 0:
            n = -n
        if n == 0:
            count = 1
        else:
            while n > 0:
                count = count + 1
                n = n // 10
        print(count)
    elif args.cmd == "words":
        count = 1
        i = 0
        while i < len(args.text):
            if args.text[i] == "_":
                count = count + 1
            i = i + 1
        print(count)


if __name__ == "__main__":
    main()
