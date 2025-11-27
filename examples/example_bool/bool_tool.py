#!/usr/bin/env python3
"""Bool Example - Boolean operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Boolean operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("and")
    a.add_argument("x", type=int)
    a.add_argument("y", type=int)
    o = subs.add_parser("or")
    o.add_argument("x", type=int)
    o.add_argument("y", type=int)
    n = subs.add_parser("not")
    n.add_argument("x", type=int)

    args = parser.parse_args()
    if args.cmd == "and":
        if args.x != 0 and args.y != 0:
            print("true")
        else:
            print("false")
    elif args.cmd == "or":
        if args.x != 0 or args.y != 0:
            print("true")
        else:
            print("false")
    elif args.cmd == "not":
        if args.x == 0:
            print("true")
        else:
            print("false")


if __name__ == "__main__":
    main()
