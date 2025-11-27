#!/usr/bin/env python3
"""Hash2 Example - Hash operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Hash operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    d = subs.add_parser("djb2")
    d.add_argument("text")
    f = subs.add_parser("fnv")
    f.add_argument("text")
    s = subs.add_parser("simple")
    s.add_argument("text")

    args = parser.parse_args()
    if args.cmd == "djb2":
        h = 5381
        i = 0
        while i < len(args.text):
            h = ((h * 33) + ord(args.text[i])) % (2**32)
            i = i + 1
        print(h)
    elif args.cmd == "fnv":
        h = 2166136261
        i = 0
        while i < len(args.text):
            h = (h * 16777619) % (2**32)
            h = h ^ ord(args.text[i])
            i = i + 1
        print(h)
    elif args.cmd == "simple":
        h = 0
        i = 0
        while i < len(args.text):
            h = h + ord(args.text[i])
            i = i + 1
        print(h)


if __name__ == "__main__":
    main()
