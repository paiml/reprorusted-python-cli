#!/usr/bin/env python3
"""Zip Example - Zip operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Zip operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    p = subs.add_parser("pair")
    p.add_argument("a1")
    p.add_argument("a2")
    p.add_argument("a3")
    p.add_argument("b1")
    p.add_argument("b2")
    p.add_argument("b3")
    s = subs.add_parser("sum")
    s.add_argument("a1", type=int)
    s.add_argument("a2", type=int)
    s.add_argument("a3", type=int)
    s.add_argument("b1", type=int)
    s.add_argument("b2", type=int)
    s.add_argument("b3", type=int)
    d = subs.add_parser("diff")
    d.add_argument("a1", type=int)
    d.add_argument("a2", type=int)
    d.add_argument("a3", type=int)
    d.add_argument("b1", type=int)
    d.add_argument("b2", type=int)
    d.add_argument("b3", type=int)

    args = parser.parse_args()
    if args.cmd == "pair":
        print(f"{args.a1}:{args.b1} {args.a2}:{args.b2} {args.a3}:{args.b3}")
    elif args.cmd == "sum":
        r1 = args.a1 + args.b1
        r2 = args.a2 + args.b2
        r3 = args.a3 + args.b3
        print(f"{r1} {r2} {r3}")
    elif args.cmd == "diff":
        r1 = args.a1 - args.b1
        r2 = args.a2 - args.b2
        r3 = args.a3 - args.b3
        print(f"{r1} {r2} {r3}")


if __name__ == "__main__":
    main()
