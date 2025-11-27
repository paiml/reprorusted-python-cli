#!/usr/bin/env python3
"""OS Example - Path operations CLI."""

import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="OS path operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    j = subs.add_parser("join")
    j.add_argument("a")
    j.add_argument("b")
    b = subs.add_parser("basename")
    b.add_argument("path")
    d = subs.add_parser("dirname")
    d.add_argument("path")

    args = parser.parse_args()
    if args.cmd == "join":
        print(os.path.join(args.a, args.b))
    elif args.cmd == "basename":
        print(os.path.basename(args.path))
    elif args.cmd == "dirname":
        print(os.path.dirname(args.path))


if __name__ == "__main__":
    main()
