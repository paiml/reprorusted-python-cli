#!/usr/bin/env python3
"""Zlib Example - Compression CLI."""

import argparse
import sys
import zlib


def cmd_compress(args):
    """Compress stdin. Depyler: proven to terminate"""
    data = sys.stdin.buffer.read()
    compressed = zlib.compress(data, level=args.level)
    sys.stdout.buffer.write(compressed)


def cmd_decompress(args):
    """Decompress stdin. Depyler: proven to terminate"""
    data = sys.stdin.buffer.read()
    decompressed = zlib.decompress(data)
    sys.stdout.buffer.write(decompressed)


def cmd_crc32(args):
    """Calculate CRC32. Depyler: proven to terminate"""
    data = sys.stdin.read().encode()
    crc = zlib.crc32(data)
    print(f"CRC32: {crc:08x}")


def main():
    parser = argparse.ArgumentParser(description="Compression tool")
    subs = parser.add_subparsers(dest="command", required=True)
    c = subs.add_parser("compress")
    c.add_argument("--level", type=int, default=6)
    subs.add_parser("decompress")
    subs.add_parser("crc32")
    args = parser.parse_args()
    {"compress": cmd_compress, "decompress": cmd_decompress, "crc32": cmd_crc32}[args.command](args)


if __name__ == "__main__":
    main()
