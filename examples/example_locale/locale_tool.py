#!/usr/bin/env python3
"""Locale Example - Locale formatting CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Locale formatting tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    c = subs.add_parser("currency")
    c.add_argument("amount", type=int)
    n = subs.add_parser("number")
    n.add_argument("value", type=int)
    p = subs.add_parser("percent")
    p.add_argument("value", type=int)

    args = parser.parse_args()
    if args.cmd == "currency":
        print(f"${args.amount}")
    elif args.cmd == "number":
        print(args.value)
    elif args.cmd == "percent":
        print(f"{args.value}%")


if __name__ == "__main__":
    main()
