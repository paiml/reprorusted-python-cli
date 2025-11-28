#!/usr/bin/env python3
"""Memoryview Operations CLI.

Working with memoryview for zero-copy buffer access.
"""

import argparse
import sys


def create_bytearray(size: int, fill: int = 0) -> bytearray:
    """Create a bytearray of given size with fill value."""
    return bytearray([fill] * size)


def create_from_list(values: list[int]) -> bytearray:
    """Create a bytearray from list of integers."""
    return bytearray(values)


def get_slice(data: bytearray, start: int, end: int) -> bytes:
    """Get a slice of bytes using memoryview."""
    mv = memoryview(data)
    return bytes(mv[start:end])


def set_slice(data: bytearray, start: int, values: list[int]) -> None:
    """Set a slice of bytes using memoryview."""
    mv = memoryview(data)
    for i, v in enumerate(values):
        if start + i < len(mv):
            mv[start + i] = v


def copy_region(
    src: bytearray, src_start: int, dst: bytearray, dst_start: int, length: int
) -> None:
    """Copy a region from source to destination."""
    mv_src = memoryview(src)
    mv_dst = memoryview(dst)
    for i in range(length):
        if src_start + i < len(mv_src) and dst_start + i < len(mv_dst):
            mv_dst[dst_start + i] = mv_src[src_start + i]


def fill_region(data: bytearray, start: int, length: int, value: int) -> None:
    """Fill a region with a value."""
    mv = memoryview(data)
    for i in range(length):
        if start + i < len(mv):
            mv[start + i] = value


def find_byte(data: bytearray, value: int) -> int:
    """Find first occurrence of a byte value."""
    mv = memoryview(data)
    for i in range(len(mv)):
        if mv[i] == value:
            return i
    return -1


def find_pattern(data: bytearray, pattern: list[int]) -> int:
    """Find first occurrence of a byte pattern."""
    if len(pattern) == 0:
        return 0
    mv = memoryview(data)
    for i in range(len(mv) - len(pattern) + 1):
        found = True
        for j, p in enumerate(pattern):
            if mv[i + j] != p:
                found = False
                break
        if found:
            return i
    return -1


def count_byte(data: bytearray, value: int) -> int:
    """Count occurrences of a byte value."""
    mv = memoryview(data)
    count = 0
    for i in range(len(mv)):
        if mv[i] == value:
            count += 1
    return count


def reverse_bytes(data: bytearray) -> bytearray:
    """Reverse byte order."""
    mv = memoryview(data)
    result = bytearray(len(mv))
    for i in range(len(mv)):
        result[len(mv) - 1 - i] = mv[i]
    return result


def xor_bytes(data1: bytearray, data2: bytearray) -> bytearray:
    """XOR two bytearrays."""
    length = min(len(data1), len(data2))
    mv1 = memoryview(data1)
    mv2 = memoryview(data2)
    result = bytearray(length)
    for i in range(length):
        result[i] = mv1[i] ^ mv2[i]
    return result


def and_bytes(data1: bytearray, data2: bytearray) -> bytearray:
    """AND two bytearrays."""
    length = min(len(data1), len(data2))
    mv1 = memoryview(data1)
    mv2 = memoryview(data2)
    result = bytearray(length)
    for i in range(length):
        result[i] = mv1[i] & mv2[i]
    return result


def or_bytes(data1: bytearray, data2: bytearray) -> bytearray:
    """OR two bytearrays."""
    length = min(len(data1), len(data2))
    mv1 = memoryview(data1)
    mv2 = memoryview(data2)
    result = bytearray(length)
    for i in range(length):
        result[i] = mv1[i] | mv2[i]
    return result


def not_bytes(data: bytearray) -> bytearray:
    """NOT (complement) a bytearray."""
    mv = memoryview(data)
    result = bytearray(len(mv))
    for i in range(len(mv)):
        result[i] = (~mv[i]) & 0xFF
    return result


def compare_bytes(data1: bytearray, data2: bytearray) -> int:
    """Compare two bytearrays lexicographically."""
    mv1 = memoryview(data1)
    mv2 = memoryview(data2)
    min_len = min(len(mv1), len(mv2))
    for i in range(min_len):
        if mv1[i] < mv2[i]:
            return -1
        if mv1[i] > mv2[i]:
            return 1
    if len(mv1) < len(mv2):
        return -1
    if len(mv1) > len(mv2):
        return 1
    return 0


def sum_bytes(data: bytearray) -> int:
    """Sum all byte values."""
    mv = memoryview(data)
    total = 0
    for i in range(len(mv)):
        total += mv[i]
    return total


def checksum_xor(data: bytearray) -> int:
    """Calculate XOR checksum."""
    mv = memoryview(data)
    result = 0
    for i in range(len(mv)):
        result ^= mv[i]
    return result


def checksum_add(data: bytearray) -> int:
    """Calculate additive checksum (mod 256)."""
    mv = memoryview(data)
    result = 0
    for i in range(len(mv)):
        result = (result + mv[i]) & 0xFF
    return result


def rotate_bytes_left(data: bytearray, count: int) -> bytearray:
    """Rotate bytes left."""
    if len(data) == 0:
        return bytearray()
    count = count % len(data)
    mv = memoryview(data)
    result = bytearray(len(mv))
    for i in range(len(mv)):
        result[i] = mv[(i + count) % len(mv)]
    return result


def rotate_bytes_right(data: bytearray, count: int) -> bytearray:
    """Rotate bytes right."""
    if len(data) == 0:
        return bytearray()
    count = count % len(data)
    return rotate_bytes_left(data, len(data) - count)


def interleave_bytes(data1: bytearray, data2: bytearray) -> bytearray:
    """Interleave bytes from two arrays."""
    mv1 = memoryview(data1)
    mv2 = memoryview(data2)
    min_len = min(len(mv1), len(mv2))
    result = bytearray(min_len * 2)
    for i in range(min_len):
        result[i * 2] = mv1[i]
        result[i * 2 + 1] = mv2[i]
    return result


def deinterleave_bytes(data: bytearray) -> tuple[bytearray, bytearray]:
    """Deinterleave bytes into two arrays."""
    mv = memoryview(data)
    length = len(mv) // 2
    result1 = bytearray(length)
    result2 = bytearray(length)
    for i in range(length):
        result1[i] = mv[i * 2]
        result2[i] = mv[i * 2 + 1]
    return (result1, result2)


def pack_nibbles(high: int, low: int) -> int:
    """Pack two nibbles into a byte."""
    return ((high & 0xF) << 4) | (low & 0xF)


def unpack_nibbles(byte: int) -> tuple[int, int]:
    """Unpack a byte into two nibbles."""
    return ((byte >> 4) & 0xF, byte & 0xF)


def swap_nibbles(byte: int) -> int:
    """Swap high and low nibbles of a byte."""
    return ((byte & 0x0F) << 4) | ((byte >> 4) & 0x0F)


def get_memoryview_info(data: bytearray) -> dict[str, object]:
    """Get memoryview properties."""
    mv = memoryview(data)
    return {
        "nbytes": mv.nbytes,
        "readonly": mv.readonly,
        "itemsize": mv.itemsize,
        "ndim": mv.ndim,
        "shape": mv.shape,
        "format": mv.format,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Memoryview operations CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # create
    create_p = subparsers.add_parser("create", help="Create bytearray")
    create_p.add_argument("size", type=int)
    create_p.add_argument("--fill", type=int, default=0)

    # slice
    slice_p = subparsers.add_parser("slice", help="Get slice of hex data")
    slice_p.add_argument("hex_data")
    slice_p.add_argument("start", type=int)
    slice_p.add_argument("end", type=int)

    # xor
    xor_p = subparsers.add_parser("xor", help="XOR two hex values")
    xor_p.add_argument("hex1")
    xor_p.add_argument("hex2")

    # checksum
    chk_p = subparsers.add_parser("checksum", help="Calculate checksum")
    chk_p.add_argument("hex_data")
    chk_p.add_argument("--type", choices=["xor", "add"], default="xor")

    args = parser.parse_args()

    if args.command == "create":
        data = create_bytearray(args.size, args.fill)
        print(f"Created: {data.hex()}")

    elif args.command == "slice":
        data = bytearray.fromhex(args.hex_data)
        result = get_slice(data, args.start, args.end)
        print(f"Slice: {result.hex()}")

    elif args.command == "xor":
        data1 = bytearray.fromhex(args.hex1)
        data2 = bytearray.fromhex(args.hex2)
        result = xor_bytes(data1, data2)
        print(f"XOR result: {result.hex()}")

    elif args.command == "checksum":
        data = bytearray.fromhex(args.hex_data)
        if args.type == "xor":
            result = checksum_xor(data)
        else:
            result = checksum_add(data)
        print(f"Checksum: {result:02x}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
