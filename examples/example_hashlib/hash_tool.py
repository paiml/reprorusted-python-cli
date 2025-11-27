#!/usr/bin/env python3
"""Hashlib Example - Hashing CLI."""

import argparse
import hashlib
import sys


def cmd_md5(args):
    """MD5 hash stdin. Depyler: proven to terminate"""
    data = sys.stdin.read().encode()
    print(hashlib.md5(data).hexdigest())


def cmd_sha256(args):
    """SHA256 hash stdin. Depyler: proven to terminate"""
    data = sys.stdin.read().encode()
    print(hashlib.sha256(data).hexdigest())


def cmd_file(args):
    """Hash file. Depyler: proven to terminate"""
    h = hashlib.new(args.algo)
    with open(args.path, "rb") as f:
        h.update(f.read())
    print(f"{args.algo}: {h.hexdigest()}")


def main():
    parser = argparse.ArgumentParser(description="Hash tool")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("md5")
    subs.add_parser("sha256")
    f = subs.add_parser("file")
    f.add_argument("path")
    f.add_argument("--algo", default="sha256")
    args = parser.parse_args()
    {"md5": cmd_md5, "sha256": cmd_sha256, "file": cmd_file}[args.command](args)


if __name__ == "__main__":
    main()
