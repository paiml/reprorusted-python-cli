#!/usr/bin/env python3
"""Base64 Example - Encoding/decoding CLI."""

import argparse
import base64
import sys


def cmd_encode(args):
    """Base64 encode. Depyler: proven to terminate"""
    data = sys.stdin.read().strip()
    encoded = base64.b64encode(data.encode()).decode()
    print(encoded)


def cmd_decode(args):
    """Base64 decode. Depyler: proven to terminate"""
    data = sys.stdin.read().strip()
    decoded = base64.b64decode(data).decode()
    print(decoded)


def cmd_urlsafe_encode(args):
    """URL-safe base64 encode. Depyler: proven to terminate"""
    data = sys.stdin.read().strip()
    encoded = base64.urlsafe_b64encode(data.encode()).decode()
    print(encoded)


def main():
    parser = argparse.ArgumentParser(description="Base64 encoding tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("encode")
    subparsers.add_parser("decode")
    subparsers.add_parser("urlsafe-encode")

    args = parser.parse_args()
    if args.command == "encode":
        cmd_encode(args)
    elif args.command == "decode":
        cmd_decode(args)
    elif args.command == "urlsafe-encode":
        cmd_urlsafe_encode(args)


if __name__ == "__main__":
    main()
