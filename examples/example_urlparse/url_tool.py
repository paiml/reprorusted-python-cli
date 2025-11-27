#!/usr/bin/env python3
"""URL Parse Example - URL manipulation CLI."""

import argparse
from urllib.parse import quote, unquote, urljoin, urlparse


def cmd_parse(args):
    """Parse URL. Depyler: proven to terminate"""
    u = urlparse(args.url)
    print(f"Scheme: {u.scheme}")
    print(f"Host: {u.hostname}")
    print(f"Port: {u.port}")
    print(f"Path: {u.path}")
    print(f"Query: {u.query}")
    print(f"Fragment: {u.fragment}")


def cmd_encode(args):
    """URL encode string. Depyler: proven to terminate"""
    print(quote(args.text))


def cmd_decode(args):
    """URL decode string. Depyler: proven to terminate"""
    print(unquote(args.text))


def cmd_join(args):
    """Join URL parts. Depyler: proven to terminate"""
    print(urljoin(args.base, args.path))


def main():
    parser = argparse.ArgumentParser(description="URL tool")
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("parse")
    p.add_argument("url")
    e = subs.add_parser("encode")
    e.add_argument("text")
    d = subs.add_parser("decode")
    d.add_argument("text")
    j = subs.add_parser("join")
    j.add_argument("base")
    j.add_argument("path")
    args = parser.parse_args()
    {"parse": cmd_parse, "encode": cmd_encode, "decode": cmd_decode, "join": cmd_join}[
        args.command
    ](args)


if __name__ == "__main__":
    main()
