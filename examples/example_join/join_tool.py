#!/usr/bin/env python3
"""Join Example - String join operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String join tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    u = subs.add_parser("underscore")
    u.add_argument("a")
    u.add_argument("b")
    u.add_argument("c")
    d = subs.add_parser("dash")
    d.add_argument("a")
    d.add_argument("b")
    d.add_argument("c")
    dt = subs.add_parser("dot")
    dt.add_argument("a")
    dt.add_argument("b")
    dt.add_argument("c")

    args = parser.parse_args()
    if args.cmd == "underscore":
        print(args.a + "_" + args.b + "_" + args.c)
    elif args.cmd == "dash":
        print(args.a + "-" + args.b + "-" + args.c)
    elif args.cmd == "dot":
        print(args.a + "." + args.b + "." + args.c)


if __name__ == "__main__":
    main()
