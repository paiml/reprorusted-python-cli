#!/usr/bin/env python3
"""Time Example - Time conversion CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Time conversion tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("seconds")
    s.add_argument("secs", type=int)
    m = subs.add_parser("minutes")
    m.add_argument("secs", type=int)
    h = subs.add_parser("hours")
    h.add_argument("secs", type=int)

    args = parser.parse_args()
    if args.cmd == "seconds":
        print(args.secs // 60)
    elif args.cmd == "minutes":
        print(args.secs // 60)
    elif args.cmd == "hours":
        print(args.secs // 3600)


if __name__ == "__main__":
    main()
