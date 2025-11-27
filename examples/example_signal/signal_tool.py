#!/usr/bin/env python3
"""Signal Example - Signal info CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Signal info tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    n = subs.add_parser("name")
    n.add_argument("num", type=int)
    nu = subs.add_parser("number")
    nu.add_argument("name")
    subs.add_parser("list")

    args = parser.parse_args()
    if args.cmd == "name":
        if args.num == 9:
            print("SIGKILL")
        elif args.num == 15:
            print("SIGTERM")
        elif args.num == 2:
            print("SIGINT")
    elif args.cmd == "number":
        if args.name == "KILL":
            print(9)
        elif args.name == "TERM":
            print(15)
        elif args.name == "INT":
            print(2)
    elif args.cmd == "list":
        print("SIGINT SIGTERM SIGKILL")


if __name__ == "__main__":
    main()
