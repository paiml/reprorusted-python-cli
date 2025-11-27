#!/usr/bin/env python3
"""Format Example - String formatting CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String formatting tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    pl = subs.add_parser("padleft")
    pl.add_argument("text")
    pl.add_argument("width", type=int)
    pr = subs.add_parser("padright")
    pr.add_argument("text")
    pr.add_argument("width", type=int)
    c = subs.add_parser("center")
    c.add_argument("text")
    c.add_argument("width", type=int)

    args = parser.parse_args()
    if args.cmd == "padleft":
        result = args.text
        while len(result) < args.width:
            result = " " + result
        print(result)
    elif args.cmd == "padright":
        result = args.text
        while len(result) < args.width:
            result = result + " "
        print(result)
    elif args.cmd == "center":
        result = args.text
        left = True
        while len(result) < args.width:
            if left:
                result = " " + result
            else:
                result = result + " "
            left = not left
        print(result)


if __name__ == "__main__":
    main()
