#!/usr/bin/env python3
"""Repr Example - Representation operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Representation tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("string")
    s.add_argument("text")
    n = subs.add_parser("number")
    n.add_argument("num", type=int)
    e = subs.add_parser("escape")
    e.add_argument("name")

    args = parser.parse_args()
    if args.cmd == "string":
        print(f"'{args.text}'")
    elif args.cmd == "number":
        print(args.num)
    elif args.cmd == "escape":
        if args.name == "tab":
            print(repr("\t"))
        elif args.name == "newline":
            print(repr("\n"))
        else:
            print(repr(args.name))


if __name__ == "__main__":
    main()
