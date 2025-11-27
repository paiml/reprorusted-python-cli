#!/usr/bin/env python3
"""Nested Subcommands Example - Two-level subcommand CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Nested subcommands tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    user = subs.add_parser("user")
    user.add_argument("action")
    user.add_argument("name")

    group = subs.add_parser("group")
    group.add_argument("action")
    group.add_argument("name")

    args = parser.parse_args()
    if args.cmd == "user":
        if args.action == "add":
            print(f"Added user: {args.name}")
        elif args.action == "remove":
            print(f"Removed user: {args.name}")
    elif args.cmd == "group":
        if args.action == "create":
            print(f"Created group: {args.name}")
        elif args.action == "delete":
            print(f"Deleted group: {args.name}")


if __name__ == "__main__":
    main()
