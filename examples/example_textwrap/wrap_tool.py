#!/usr/bin/env python3
"""Textwrap Example - Text formatting CLI."""

import argparse
import sys
import textwrap


def cmd_wrap(args):
    """Wrap text. Depyler: proven to terminate"""
    text = sys.stdin.read()
    for line in textwrap.wrap(text, width=args.width):
        print(line)


def cmd_fill(args):
    """Fill text. Depyler: proven to terminate"""
    text = sys.stdin.read()
    print(textwrap.fill(text, width=args.width))


def cmd_dedent(args):
    """Dedent text. Depyler: proven to terminate"""
    text = sys.stdin.read()
    print(textwrap.dedent(text))


def cmd_indent(args):
    """Indent text. Depyler: proven to terminate"""
    text = sys.stdin.read()
    print(textwrap.indent(text, args.prefix))


def main():
    parser = argparse.ArgumentParser(description="Text wrapping tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    wrap = subparsers.add_parser("wrap")
    wrap.add_argument("--width", type=int, default=70)

    fill = subparsers.add_parser("fill")
    fill.add_argument("--width", type=int, default=70)

    subparsers.add_parser("dedent")

    indent = subparsers.add_parser("indent")
    indent.add_argument("--prefix", default="  ")

    args = parser.parse_args()
    {"wrap": cmd_wrap, "fill": cmd_fill, "dedent": cmd_dedent, "indent": cmd_indent}[args.command](
        args
    )


if __name__ == "__main__":
    main()
