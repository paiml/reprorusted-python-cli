#!/usr/bin/env python3
"""Enumerate Example - Enumerate operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Enumerate operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    i = subs.add_parser("index")
    i.add_argument("text")
    s = subs.add_parser("start")
    s.add_argument("text")
    s.add_argument("offset", type=int)
    r = subs.add_parser("reverse")
    r.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "index":
        result = ""
        idx = 0
        while idx < len(args.text):
            if idx > 0:
                result = result + " "
            result = result + str(idx) + ":" + args.text[idx]
            idx = idx + 1
        print(result)
    elif args.cmd == "start":
        result = ""
        idx = 0
        while idx < len(args.text):
            if idx > 0:
                result = result + " "
            result = result + str(args.offset + idx) + ":" + args.text[idx]
            idx = idx + 1
        print(result)
    elif args.cmd == "reverse":
        result = ""
        idx = len(args.text) - 1
        first = True
        while idx >= 0:
            if not first:
                result = result + " "
            first = False
            result = result + str(idx) + ":" + args.text[idx]
            idx = idx - 1
        print(result)


if __name__ == "__main__":
    main()
