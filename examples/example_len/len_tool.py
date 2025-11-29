#!/usr/bin/env python3
"""Len Example - Length operations CLI.

Examples:
    >>> string_length("hello")
    5
    >>> digit_count(12345)
    5
    >>> word_count("a_b_c")
    3
"""

import argparse


def string_length(text: str) -> int:
    """Get length of string.

    >>> string_length("")
    0
    >>> string_length("hello")
    5
    >>> string_length("hello world")
    11
    """
    return len(text)


def digit_count(num: int) -> int:
    """Count digits in integer.

    >>> digit_count(0)
    1
    >>> digit_count(123)
    3
    >>> digit_count(-456)
    3
    """
    count = 0
    n = num
    if n < 0:
        n = -n
    if n == 0:
        count = 1
    else:
        while n > 0:
            count = count + 1
            n = n // 10
    return count


def word_count(text: str) -> int:
    """Count underscore-separated words.

    >>> word_count("hello")
    1
    >>> word_count("a_b")
    2
    >>> word_count("one_two_three")
    3
    """
    count = 1
    i = 0
    while i < len(text):
        if text[i] == "_":
            count = count + 1
        i = i + 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Length tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("string")
    s.add_argument("text")
    d = subs.add_parser("digits")
    d.add_argument("num", type=int)
    w = subs.add_parser("words")
    w.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "string":
        print(string_length(args.text))
    elif args.cmd == "digits":
        print(digit_count(args.num))
    elif args.cmd == "words":
        print(word_count(args.text))


if __name__ == "__main__":
    main()
