#!/usr/bin/env python3
"""Split Example - String split operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String split tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    u = subs.add_parser("underscore")
    u.add_argument("text")
    d = subs.add_parser("dash")
    d.add_argument("text")
    dt = subs.add_parser("dot")
    dt.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "underscore":
        parts = args.text.split("_")
        print(parts[0] + " " + parts[1] + " " + parts[2])
    elif args.cmd == "dash":
        parts = args.text.split("-")
        print(parts[0] + " " + parts[1] + " " + parts[2])
    elif args.cmd == "dot":
        parts = args.text.split(".")
        print(parts[0] + " " + parts[1] + " " + parts[2])


if __name__ == "__main__":
    main()
