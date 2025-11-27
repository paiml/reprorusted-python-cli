#!/usr/bin/env python3
"""Random Example - Random number operations CLI."""

import argparse
import random


def main():
    parser = argparse.ArgumentParser(description="Random operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    ri = subs.add_parser("randint")
    ri.add_argument("low", type=int)
    ri.add_argument("high", type=int)
    ch = subs.add_parser("choice")
    ch.add_argument("a")
    ch.add_argument("b")
    ch.add_argument("c")
    ct = subs.add_parser("count")
    ct.add_argument("n", type=int)

    args = parser.parse_args()
    if args.cmd == "randint":
        print(random.randint(args.low, args.high))
    elif args.cmd == "choice":
        items = [args.a, args.b, args.c]
        print(random.choice(items))
    elif args.cmd == "count":
        print(args.n)


if __name__ == "__main__":
    main()
