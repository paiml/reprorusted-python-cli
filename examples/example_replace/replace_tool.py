#!/usr/bin/env python3
"""Replace Example - String replace operations CLI.

Examples:
    >>> replace_char("hello", "l", "x")
    'hexxo'
    >>> replace_all("abc", "X")
    'XXX'
"""

import argparse


def replace_char(text: str, old: str, new: str) -> str:
    """Replace all occurrences of old with new.

    >>> replace_char("hello", "l", "x")
    'hexxo'
    >>> replace_char("banana", "a", "o")
    'bonono'
    >>> replace_char("test", "x", "y")
    'test'
    """
    return text.replace(old, new)


def replace_all(text: str, new: str) -> str:
    """Replace each character with new.

    >>> replace_all("abc", "X")
    'XXX'
    >>> replace_all("", "X")
    ''
    >>> replace_all("hello", "*")
    '*****'
    """
    result = ""
    i = 0
    while i < len(text):
        result = result + new
        i = i + 1
    return result


def main():
    parser = argparse.ArgumentParser(description="String replace tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    ch = subs.add_parser("char")
    ch.add_argument("text")
    ch.add_argument("old")
    ch.add_argument("new")
    f = subs.add_parser("first")
    f.add_argument("text")
    f.add_argument("new")
    a = subs.add_parser("all")
    a.add_argument("text")
    a.add_argument("new")

    args = parser.parse_args()
    if args.cmd == "char":
        print(replace_char(args.text, args.old, args.new))
    elif args.cmd == "first":
        result = ""
        found = False
        i = 0
        while i < len(args.text):
            if not found and args.text[i] == args.text[0]:
                result = result + args.new
                found = True
            else:
                result = result + args.text[i]
            i = i + 1
        print(result)
    elif args.cmd == "all":
        print(replace_all(args.text, args.new))


if __name__ == "__main__":
    main()
