#!/usr/bin/env python3
"""Count Example - String count operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String count tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    ch = subs.add_parser("char")
    ch.add_argument("text")
    ch.add_argument("target")
    v = subs.add_parser("vowels")
    v.add_argument("text")
    co = subs.add_parser("consonants")
    co.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "char":
        count = 0
        i = 0
        while i < len(args.text):
            if args.text[i] == args.target:
                count = count + 1
            i = i + 1
        print(count)
    elif args.cmd == "vowels":
        count = 0
        i = 0
        while i < len(args.text):
            c = args.text[i]
            if c == "a" or c == "e" or c == "i" or c == "o" or c == "u":
                count = count + 1
            i = i + 1
        print(count)
    elif args.cmd == "consonants":
        count = 0
        i = 0
        while i < len(args.text):
            c = args.text[i]
            is_vowel = c == "a" or c == "e" or c == "i" or c == "o" or c == "u"
            is_alpha = c >= "a" and c <= "z"
            if is_alpha and not is_vowel:
                count = count + 1
            i = i + 1
        print(count)


if __name__ == "__main__":
    main()
