#!/usr/bin/env python3
"""Cmath Example - Complex math CLI."""

import argparse
import math


def main():
    parser = argparse.ArgumentParser(description="Complex math tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("abs")
    a.add_argument("real", type=float)
    a.add_argument("imag", type=float)
    p = subs.add_parser("phase")
    p.add_argument("real", type=float)
    p.add_argument("imag", type=float)
    po = subs.add_parser("polar")
    po.add_argument("real", type=float)
    po.add_argument("imag", type=float)

    args = parser.parse_args()
    if args.cmd == "abs":
        print(math.sqrt(args.real * args.real + args.imag * args.imag))
    elif args.cmd == "phase":
        print(math.atan2(args.imag, args.real))
    elif args.cmd == "polar":
        r = math.sqrt(args.real * args.real + args.imag * args.imag)
        theta = math.atan2(args.imag, args.real)
        print(f"{r} {theta}")


if __name__ == "__main__":
    main()
