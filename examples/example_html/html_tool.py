#!/usr/bin/env python3
"""HTML Example - HTML escape/unescape CLI."""

import argparse
import html
import re
import sys


def cmd_escape(args):
    """Escape HTML. Depyler: proven to terminate"""
    text = sys.stdin.read()
    print(html.escape(text))


def cmd_unescape(args):
    """Unescape HTML. Depyler: proven to terminate"""
    text = sys.stdin.read()
    print(html.unescape(text))


def cmd_strip(args):
    """Strip HTML tags. Depyler: proven to terminate"""
    text = sys.stdin.read()
    clean = re.sub(r"<[^>]+>", "", text)
    print(clean)


def main():
    parser = argparse.ArgumentParser(description="HTML tool")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("escape")
    subs.add_parser("unescape")
    subs.add_parser("strip")
    args = parser.parse_args()
    {"escape": cmd_escape, "unescape": cmd_unescape, "strip": cmd_strip}[args.command](args)


if __name__ == "__main__":
    main()
