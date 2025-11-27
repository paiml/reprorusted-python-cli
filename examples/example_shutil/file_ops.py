#!/usr/bin/env python3
"""Shutil Example - File operations CLI."""

import argparse
import shutil


def cmd_copy(args):
    """Copy file. Depyler: proven to terminate"""
    shutil.copy2(args.src, args.dst)
    print(f"Copied: {args.src} -> {args.dst}")


def cmd_move(args):
    """Move file. Depyler: proven to terminate"""
    shutil.move(args.src, args.dst)
    print(f"Moved: {args.src} -> {args.dst}")


def main():
    parser = argparse.ArgumentParser(description="File operations tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cp = subparsers.add_parser("copy")
    cp.add_argument("src")
    cp.add_argument("dst")

    mv = subparsers.add_parser("move")
    mv.add_argument("src")
    mv.add_argument("dst")

    args = parser.parse_args()
    if args.command == "copy":
        cmd_copy(args)
    elif args.command == "move":
        cmd_move(args)


if __name__ == "__main__":
    main()
