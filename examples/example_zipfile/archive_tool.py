#!/usr/bin/env python3
"""Zipfile Example - Archive manipulation CLI."""

import argparse
import os
import zipfile


def cmd_list(args):
    """List zip contents. Depyler: proven to terminate"""
    with zipfile.ZipFile(args.archive, "r") as z:
        for name in z.namelist():
            print(name)


def cmd_create(args):
    """Create zip archive. Depyler: proven to terminate"""
    with zipfile.ZipFile(args.output, "w") as z:
        for f in args.files:
            z.write(f, os.path.basename(f))
    print(f"Created: {args.output}")


def main():
    parser = argparse.ArgumentParser(description="Archive tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lst = subparsers.add_parser("list")
    lst.add_argument("archive")

    create = subparsers.add_parser("create")
    create.add_argument("output")
    create.add_argument("files", nargs="+")

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "create":
        cmd_create(args)


if __name__ == "__main__":
    main()
