#!/usr/bin/env python3
"""Struct Pack CLI.

Binary data packing and unpacking using struct module.
"""

import argparse
import struct
import sys


def pack_byte(value: int) -> bytes:
    """Pack a single byte."""
    return struct.pack("B", value)


def unpack_byte(data: bytes) -> int:
    """Unpack a single byte."""
    return struct.unpack("B", data)[0]


def pack_short(value: int, big_endian: bool = False) -> bytes:
    """Pack a 16-bit integer."""
    fmt = ">h" if big_endian else "<h"
    return struct.pack(fmt, value)


def unpack_short(data: bytes, big_endian: bool = False) -> int:
    """Unpack a 16-bit integer."""
    fmt = ">h" if big_endian else "<h"
    return struct.unpack(fmt, data)[0]


def pack_int(value: int, big_endian: bool = False) -> bytes:
    """Pack a 32-bit integer."""
    fmt = ">i" if big_endian else "<i"
    return struct.pack(fmt, value)


def unpack_int(data: bytes, big_endian: bool = False) -> int:
    """Unpack a 32-bit integer."""
    fmt = ">i" if big_endian else "<i"
    return struct.unpack(fmt, data)[0]


def pack_long(value: int, big_endian: bool = False) -> bytes:
    """Pack a 64-bit integer."""
    fmt = ">q" if big_endian else "<q"
    return struct.pack(fmt, value)


def unpack_long(data: bytes, big_endian: bool = False) -> int:
    """Unpack a 64-bit integer."""
    fmt = ">q" if big_endian else "<q"
    return struct.unpack(fmt, data)[0]


def pack_float(value: float, big_endian: bool = False) -> bytes:
    """Pack a 32-bit float."""
    fmt = ">f" if big_endian else "<f"
    return struct.pack(fmt, value)


def unpack_float(data: bytes, big_endian: bool = False) -> float:
    """Unpack a 32-bit float."""
    fmt = ">f" if big_endian else "<f"
    return struct.unpack(fmt, data)[0]


def pack_double(value: float, big_endian: bool = False) -> bytes:
    """Pack a 64-bit double."""
    fmt = ">d" if big_endian else "<d"
    return struct.pack(fmt, value)


def unpack_double(data: bytes, big_endian: bool = False) -> float:
    """Unpack a 64-bit double."""
    fmt = ">d" if big_endian else "<d"
    return struct.unpack(fmt, data)[0]


def pack_bool(value: bool) -> bytes:
    """Pack a boolean."""
    return struct.pack("?", value)


def unpack_bool(data: bytes) -> bool:
    """Unpack a boolean."""
    return struct.unpack("?", data)[0]


def pack_char(value: str) -> bytes:
    """Pack a single character."""
    return struct.pack("c", value.encode("ascii"))


def unpack_char(data: bytes) -> str:
    """Unpack a single character."""
    return struct.unpack("c", data)[0].decode("ascii")


def pack_string(value: str, length: int) -> bytes:
    """Pack a fixed-length string."""
    encoded = value.encode("ascii")[:length]
    padded = encoded.ljust(length, b"\x00")
    return struct.pack(f"{length}s", padded)


def unpack_string(data: bytes) -> str:
    """Unpack a null-terminated string."""
    return data.rstrip(b"\x00").decode("ascii")


def pack_unsigned_int(value: int, big_endian: bool = False) -> bytes:
    """Pack an unsigned 32-bit integer."""
    fmt = ">I" if big_endian else "<I"
    return struct.pack(fmt, value)


def unpack_unsigned_int(data: bytes, big_endian: bool = False) -> int:
    """Unpack an unsigned 32-bit integer."""
    fmt = ">I" if big_endian else "<I"
    return struct.unpack(fmt, data)[0]


def pack_point(x: float, y: float) -> bytes:
    """Pack a 2D point (two floats)."""
    return struct.pack("<ff", x, y)


def unpack_point(data: bytes) -> tuple[float, float]:
    """Unpack a 2D point."""
    return struct.unpack("<ff", data)


def pack_color(r: int, g: int, b: int, a: int) -> bytes:
    """Pack RGBA color (4 bytes)."""
    return struct.pack("BBBB", r, g, b, a)


def unpack_color(data: bytes) -> tuple[int, int, int, int]:
    """Unpack RGBA color."""
    return struct.unpack("BBBB", data)


def pack_header(version: int, flags: int, length: int) -> bytes:
    """Pack a simple header (short, byte, int)."""
    return struct.pack("<hBI", version, flags, length)


def unpack_header(data: bytes) -> tuple[int, int, int]:
    """Unpack a simple header."""
    return struct.unpack("<hBI", data)


def calculate_struct_size(fmt: str) -> int:
    """Calculate the size of a struct format."""
    return struct.calcsize(fmt)


def pack_array_int(values: list[int]) -> bytes:
    """Pack an array of integers."""
    count = len(values)
    fmt = f"<{count}i"
    return struct.pack(fmt, *values)


def unpack_array_int(data: bytes, count: int) -> list[int]:
    """Unpack an array of integers."""
    fmt = f"<{count}i"
    return list(struct.unpack(fmt, data))


def pack_array_float(values: list[float]) -> bytes:
    """Pack an array of floats."""
    count = len(values)
    fmt = f"<{count}f"
    return struct.pack(fmt, *values)


def unpack_array_float(data: bytes, count: int) -> list[float]:
    """Unpack an array of floats."""
    fmt = f"<{count}f"
    return list(struct.unpack(fmt, data))


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string."""
    return data.hex()


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string to bytes."""
    return bytes.fromhex(hex_str)


def swap_endian_short(value: int) -> int:
    """Swap endianness of a 16-bit value."""
    packed_le = struct.pack("<h", value)
    return struct.unpack(">h", packed_le)[0]


def swap_endian_int(value: int) -> int:
    """Swap endianness of a 32-bit value."""
    packed_le = struct.pack("<i", value)
    return struct.unpack(">i", packed_le)[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Struct pack CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # pack
    pack_p = subparsers.add_parser("pack", help="Pack values")
    pack_p.add_argument("type", choices=["byte", "short", "int", "float"])
    pack_p.add_argument("value", type=float)
    pack_p.add_argument("--big-endian", action="store_true")

    # unpack
    unpack_p = subparsers.add_parser("unpack", help="Unpack hex data")
    unpack_p.add_argument("type", choices=["byte", "short", "int", "float"])
    unpack_p.add_argument("hex_data")
    unpack_p.add_argument("--big-endian", action="store_true")

    # size
    size_p = subparsers.add_parser("size", help="Calculate struct size")
    size_p.add_argument("format")

    args = parser.parse_args()

    if args.command == "pack":
        if args.type == "byte":
            result = pack_byte(int(args.value))
        elif args.type == "short":
            result = pack_short(int(args.value), args.big_endian)
        elif args.type == "int":
            result = pack_int(int(args.value), args.big_endian)
        else:
            result = pack_float(args.value, args.big_endian)
        print(f"Packed: {bytes_to_hex(result)}")

    elif args.command == "unpack":
        data = hex_to_bytes(args.hex_data)
        if args.type == "byte":
            value = unpack_byte(data)
        elif args.type == "short":
            value = unpack_short(data, args.big_endian)
        elif args.type == "int":
            value = unpack_int(data, args.big_endian)
        else:
            value = unpack_float(data, args.big_endian)
        print(f"Unpacked: {value}")

    elif args.command == "size":
        size = calculate_struct_size(args.format)
        print(f"Size: {size} bytes")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
