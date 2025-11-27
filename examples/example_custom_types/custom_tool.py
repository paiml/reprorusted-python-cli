#!/usr/bin/env python3
"""Custom Types Example - Custom argument type CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Custom types tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    p = subs.add_parser("port")
    p.add_argument("value", type=int)
    pc = subs.add_parser("percent")
    pc.add_argument("value", type=int)
    b = subs.add_parser("bytes")
    b.add_argument("value", type=int)

    args = parser.parse_args()
    if args.cmd == "port":
        if args.value >= 1 and args.value <= 65535:
            print(f"Valid port: {args.value}")
    elif args.cmd == "percent":
        print(args.value / 100.0)
    elif args.cmd == "bytes":
        print(f"{args.value / 1024} KB")


if __name__ == "__main__":
    main()
