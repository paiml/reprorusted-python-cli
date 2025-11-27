#!/usr/bin/env python3
"""Fractions Example - Fraction operations CLI."""

import argparse
import math


def main():
    parser = argparse.ArgumentParser(description="Fraction operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    g = subs.add_parser("gcd")
    g.add_argument("a", type=int)
    g.add_argument("b", type=int)
    l = subs.add_parser("lcm")
    l.add_argument("a", type=int)
    l.add_argument("b", type=int)
    s = subs.add_parser("simplify")
    s.add_argument("num", type=int)
    s.add_argument("den", type=int)

    args = parser.parse_args()
    if args.cmd == "gcd":
        print(math.gcd(args.a, args.b))
    elif args.cmd == "lcm":
        print(args.a * args.b // math.gcd(args.a, args.b))
    elif args.cmd == "simplify":
        g = math.gcd(args.num, args.den)
        print(f"{args.num // g}/{args.den // g}")


if __name__ == "__main__":
    main()
