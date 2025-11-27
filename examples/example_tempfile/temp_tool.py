#!/usr/bin/env python3
"""Tempfile Example - Temporary file handling CLI."""

import argparse
import tempfile


def cmd_create(args):
    """Create temp file. Depyler: proven to terminate"""
    suffix = args.suffix or ".tmp"
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix) as f:
        f.write(args.content)
        print(f"Created: {f.name}")


def cmd_mkdir(args):
    """Create temp directory. Depyler: proven to terminate"""
    d = tempfile.mkdtemp()
    print(f"Directory: {d}")


def main():
    parser = argparse.ArgumentParser(description="Temp file tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--content", required=True)
    create.add_argument("--suffix")

    subparsers.add_parser("mkdir")

    args = parser.parse_args()
    if args.command == "create":
        cmd_create(args)
    elif args.command == "mkdir":
        cmd_mkdir(args)


if __name__ == "__main__":
    main()
