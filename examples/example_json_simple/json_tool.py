#!/usr/bin/env python3
"""JSON Example - JSON string operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="JSON string tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    e = subs.add_parser("escape")
    e.add_argument("text")
    u = subs.add_parser("unescape")
    u.add_argument("text")
    v = subs.add_parser("validate")
    v.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "escape":
        result = args.text.replace('"', '\\"')
        print(result)
    elif args.cmd == "unescape":
        result = args.text.replace('\\"', '"')
        print(result)
    elif args.cmd == "validate":
        if "{" in args.text and "}" in args.text:
            print("valid")
        else:
            print("invalid")


if __name__ == "__main__":
    main()
