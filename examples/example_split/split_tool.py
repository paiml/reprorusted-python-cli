#!/usr/bin/env python3
"""Split Example - String split operations CLI.

Examples:
    >>> split_underscore("a_b_c")
    ['a', 'b', 'c']
    >>> split_dash("x-y-z")
    ['x', 'y', 'z']
    >>> split_dot("1.2.3")
    ['1', '2', '3']
"""

import argparse


def split_underscore(text: str) -> list:
    """Split string by underscores.

    >>> split_underscore("hello_world_test")
    ['hello', 'world', 'test']
    >>> split_underscore("a_b_c")
    ['a', 'b', 'c']
    """
    return text.split("_")


def split_dash(text: str) -> list:
    """Split string by dashes.

    >>> split_dash("foo-bar-baz")
    ['foo', 'bar', 'baz']
    >>> split_dash("2025-11-29")
    ['2025', '11', '29']
    """
    return text.split("-")


def split_dot(text: str) -> list:
    """Split string by dots.

    >>> split_dot("192.168.1.1")
    ['192', '168', '1', '1']
    >>> split_dot("a.b.c")
    ['a', 'b', 'c']
    """
    return text.split(".")


def main():
    parser = argparse.ArgumentParser(description="String split tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    u = subs.add_parser("underscore")
    u.add_argument("text")
    d = subs.add_parser("dash")
    d.add_argument("text")
    dt = subs.add_parser("dot")
    dt.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "underscore":
        parts = split_underscore(args.text)
        print(parts[0] + " " + parts[1] + " " + parts[2])
    elif args.cmd == "dash":
        parts = split_dash(args.text)
        print(parts[0] + " " + parts[1] + " " + parts[2])
    elif args.cmd == "dot":
        parts = split_dot(args.text)
        print(parts[0] + " " + parts[1] + " " + parts[2])


if __name__ == "__main__":
    main()
