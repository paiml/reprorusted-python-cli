#!/usr/bin/env python3
"""Pathlib Example - Path manipulation CLI."""

import argparse
from pathlib import Path


def cmd_info(args):
    """Show path info. Depyler: proven to terminate"""
    p = Path(args.path)
    print(f"Name: {p.name}")
    print(f"Stem: {p.stem}")
    print(f"Suffix: {p.suffix}")
    print(f"Parent: {p.parent}")
    print(f"Exists: {p.exists()}")


def cmd_glob(args):
    """Glob pattern match. Depyler: proven to terminate"""
    p = Path(args.directory)
    for match in p.glob(args.pattern):
        print(match)


def cmd_parts(args):
    """Show path parts. Depyler: proven to terminate"""
    p = Path(args.path)
    for part in p.parts:
        print(part)


def cmd_join(args):
    """Join path components. Depyler: proven to terminate"""
    result = Path(args.parts[0])
    for part in args.parts[1:]:
        result = result / part
    print(result)


def main():
    parser = argparse.ArgumentParser(description="Path manipulation tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    info = subparsers.add_parser("info")
    info.add_argument("path")

    glob = subparsers.add_parser("glob")
    glob.add_argument("directory")
    glob.add_argument("pattern")

    parts = subparsers.add_parser("parts")
    parts.add_argument("path")

    join = subparsers.add_parser("join")
    join.add_argument("parts", nargs="+")

    args = parser.parse_args()
    if args.command == "info":
        cmd_info(args)
    elif args.command == "glob":
        cmd_glob(args)
    elif args.command == "parts":
        cmd_parts(args)
    elif args.command == "join":
        cmd_join(args)


if __name__ == "__main__":
    main()
