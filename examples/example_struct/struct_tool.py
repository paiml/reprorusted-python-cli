#!/usr/bin/env python3
"""Struct Example - Binary packing CLI."""

import argparse
import struct


def cmd_pack(args):
    """Pack values to binary. Depyler: proven to terminate"""
    values = [int(v) if v.lstrip("-").isdigit() else float(v) for v in args.values]
    packed = struct.pack(args.format, *values)
    print(packed.hex())


def cmd_size(args):
    """Get struct size. Depyler: proven to terminate"""
    size = struct.calcsize(args.format)
    print(f"Size: {size} bytes")


def main():
    parser = argparse.ArgumentParser(description="Struct tool")
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("pack")
    p.add_argument("format")
    p.add_argument("values", nargs="+")
    s = subs.add_parser("size")
    s.add_argument("format")
    args = parser.parse_args()
    {"pack": cmd_pack, "size": cmd_size}[args.command](args)


if __name__ == "__main__":
    main()
