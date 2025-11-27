#!/usr/bin/env python3
"""Startswith Example - String prefix/suffix operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="String prefix/suffix tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("starts")
    s.add_argument("text")
    s.add_argument("prefix")
    e = subs.add_parser("ends")
    e.add_argument("text")
    e.add_argument("suffix")

    args = parser.parse_args()
    if args.cmd == "starts":
        if len(args.prefix) > len(args.text):
            print("false")
        else:
            match = True
            i = 0
            while i < len(args.prefix):
                if args.text[i] != args.prefix[i]:
                    match = False
                i = i + 1
            if match:
                print("true")
            else:
                print("false")
    elif args.cmd == "ends":
        if len(args.suffix) > len(args.text):
            print("false")
        else:
            match = True
            offset = len(args.text) - len(args.suffix)
            i = 0
            while i < len(args.suffix):
                if args.text[offset + i] != args.suffix[i]:
                    match = False
                i = i + 1
            if match:
                print("true")
            else:
                print("false")


if __name__ == "__main__":
    main()
