#!/usr/bin/env python3
"""Any All Example - Any/all operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Any/all operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("any")
    a.add_argument("a", type=int)
    a.add_argument("b", type=int)
    a.add_argument("c", type=int)
    a.add_argument("d", type=int)
    al = subs.add_parser("all")
    al.add_argument("a", type=int)
    al.add_argument("b", type=int)
    al.add_argument("c", type=int)
    al.add_argument("d", type=int)

    args = parser.parse_args()
    if args.cmd == "any":
        if args.a != 0 or args.b != 0 or args.c != 0 or args.d != 0:
            print("true")
        else:
            print("false")
    elif args.cmd == "all":
        if args.a != 0 and args.b != 0 and args.c != 0 and args.d != 0:
            print("true")
        else:
            print("false")


if __name__ == "__main__":
    main()
