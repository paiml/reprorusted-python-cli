#!/usr/bin/env python3
"""Strip Example - String strip operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String strip tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    b = subs.add_parser("both")
    b.add_argument("text")
    le = subs.add_parser("left")
    le.add_argument("text")
    r = subs.add_parser("right")
    r.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "both":
        print(args.text.strip("_"))
    elif args.cmd == "left":
        print(args.text.lstrip("_"))
    elif args.cmd == "right":
        print(args.text.rstrip("_"))


if __name__ == "__main__":
    main()
