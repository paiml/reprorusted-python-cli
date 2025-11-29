#!/usr/bin/env python3
"""Join Example - String join operations CLI.

Examples:
    >>> join_underscore("a", "b", "c")
    'a_b_c'
    >>> join_dash("x", "y", "z")
    'x-y-z'
    >>> join_dot("1", "2", "3")
    '1.2.3'
"""

import argparse


def join_underscore(a: str, b: str, c: str) -> str:
    """Join three strings with underscores.

    >>> join_underscore("hello", "world", "test")
    'hello_world_test'
    >>> join_underscore("", "x", "")
    '_x_'
    """
    return a + "_" + b + "_" + c


def join_dash(a: str, b: str, c: str) -> str:
    """Join three strings with dashes.

    >>> join_dash("foo", "bar", "baz")
    'foo-bar-baz'
    >>> join_dash("2025", "11", "29")
    '2025-11-29'
    """
    return a + "-" + b + "-" + c


def join_dot(a: str, b: str, c: str) -> str:
    """Join three strings with dots.

    >>> join_dot("192", "168", "1")
    '192.168.1'
    >>> join_dot("a", "b", "c")
    'a.b.c'
    """
    return a + "." + b + "." + c


def main():
    parser = argparse.ArgumentParser(description="String join tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    u = subs.add_parser("underscore")
    u.add_argument("a")
    u.add_argument("b")
    u.add_argument("c")
    d = subs.add_parser("dash")
    d.add_argument("a")
    d.add_argument("b")
    d.add_argument("c")
    dt = subs.add_parser("dot")
    dt.add_argument("a")
    dt.add_argument("b")
    dt.add_argument("c")

    args = parser.parse_args()
    if args.cmd == "underscore":
        print(join_underscore(args.a, args.b, args.c))
    elif args.cmd == "dash":
        print(join_dash(args.a, args.b, args.c))
    elif args.cmd == "dot":
        print(join_dot(args.a, args.b, args.c))


if __name__ == "__main__":
    main()
