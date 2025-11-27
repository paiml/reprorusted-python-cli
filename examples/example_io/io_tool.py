#!/usr/bin/env python3
"""IO Example - String IO operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="IO operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    w = subs.add_parser("words")
    w.add_argument("text")
    l = subs.add_parser("lines")
    l.add_argument("text")
    c = subs.add_parser("chars")
    c.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "words":
        print(len(args.text.split()))
    elif args.cmd == "lines":
        print(len(args.text.split("\\n")))
    elif args.cmd == "chars":
        print(len(args.text))


if __name__ == "__main__":
    main()
