#!/usr/bin/env python3
"""
NamedTuple Example - Typed record structures

Demonstrates typing.NamedTuple for structured data.
"""

import argparse
import math
from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int


class Color(NamedTuple):
    r: int
    g: int
    b: int


def cmd_point(args):
    """Create point. Depyler: proven to terminate"""
    p = Point(x=args.x, y=args.y)
    print(f"Point({p.x}, {p.y})")
    if args.distance:
        dist = math.sqrt(p.x**2 + p.y**2)
        print(f"Distance from origin: {dist:.1f}")


def cmd_color(args):
    """Create color. Depyler: proven to terminate"""
    c = Color(r=args.r, g=args.g, b=args.b)
    print(f"RGB({c.r}, {c.g}, {c.b})")


def main():
    parser = argparse.ArgumentParser(description="Record tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    pt = subparsers.add_parser("point")
    pt.add_argument("x", type=int)
    pt.add_argument("y", type=int)
    pt.add_argument("--distance", action="store_true")

    cl = subparsers.add_parser("color")
    cl.add_argument("r", type=int)
    cl.add_argument("g", type=int)
    cl.add_argument("b", type=int)

    args = parser.parse_args()
    if args.command == "point":
        cmd_point(args)
    elif args.command == "color":
        cmd_color(args)


if __name__ == "__main__":
    main()
