#!/usr/bin/env python3
"""Bitwise Operations CLI.

Bitwise operations and bit manipulation patterns.
"""

import argparse
import sys


def bit_and(a: int, b: int) -> int:
    """Bitwise AND."""
    return a & b


def bit_or(a: int, b: int) -> int:
    """Bitwise OR."""
    return a | b


def bit_xor(a: int, b: int) -> int:
    """Bitwise XOR."""
    return a ^ b


def bit_not(a: int) -> int:
    """Bitwise NOT (complement)."""
    return ~a


def left_shift(value: int, count: int) -> int:
    """Left shift."""
    return value << count


def right_shift(value: int, count: int) -> int:
    """Right shift (arithmetic)."""
    return value >> count


def unsigned_right_shift(value: int, count: int, bits: int = 32) -> int:
    """Unsigned right shift (logical)."""
    mask = (1 << bits) - 1
    return (value & mask) >> count


def set_bit(value: int, position: int) -> int:
    """Set bit at position."""
    return value | (1 << position)


def clear_bit(value: int, position: int) -> int:
    """Clear bit at position."""
    return value & ~(1 << position)


def toggle_bit(value: int, position: int) -> int:
    """Toggle bit at position."""
    return value ^ (1 << position)


def check_bit(value: int, position: int) -> bool:
    """Check if bit is set at position."""
    return (value & (1 << position)) != 0


def count_set_bits(value: int) -> int:
    """Count number of set bits (popcount)."""
    count = 0
    while value:
        count += value & 1
        value >>= 1
    return count


def count_set_bits_fast(value: int) -> int:
    """Count set bits using Brian Kernighan's algorithm."""
    count = 0
    while value:
        value &= value - 1
        count += 1
    return count


def is_power_of_two(value: int) -> bool:
    """Check if value is power of two."""
    return value > 0 and (value & (value - 1)) == 0


def next_power_of_two(value: int) -> int:
    """Find next power of two >= value."""
    if value <= 1:
        return 1
    value -= 1
    value |= value >> 1
    value |= value >> 2
    value |= value >> 4
    value |= value >> 8
    value |= value >> 16
    return value + 1


def lowest_set_bit(value: int) -> int:
    """Get lowest set bit."""
    if value == 0:
        return 0
    return value & (-value)


def highest_set_bit(value: int) -> int:
    """Get position of highest set bit."""
    if value == 0:
        return -1
    position = 0
    while value > 1:
        value >>= 1
        position += 1
    return position


def swap_bits(value: int, pos1: int, pos2: int) -> int:
    """Swap bits at two positions."""
    bit1 = (value >> pos1) & 1
    bit2 = (value >> pos2) & 1
    if bit1 != bit2:
        value = toggle_bit(value, pos1)
        value = toggle_bit(value, pos2)
    return value


def reverse_bits(value: int, bits: int = 8) -> int:
    """Reverse bit order."""
    result = 0
    for _ in range(bits):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result


def rotate_left(value: int, count: int, bits: int = 32) -> int:
    """Rotate bits left."""
    count %= bits
    mask = (1 << bits) - 1
    return ((value << count) | (value >> (bits - count))) & mask


def rotate_right(value: int, count: int, bits: int = 32) -> int:
    """Rotate bits right."""
    count %= bits
    mask = (1 << bits) - 1
    return ((value >> count) | (value << (bits - count))) & mask


def extract_bits(value: int, start: int, length: int) -> int:
    """Extract bits from position start with given length."""
    mask = (1 << length) - 1
    return (value >> start) & mask


def insert_bits(value: int, bits: int, start: int, length: int) -> int:
    """Insert bits at position start with given length."""
    mask = (1 << length) - 1
    cleared = value & ~(mask << start)
    return cleared | ((bits & mask) << start)


def parity(value: int) -> int:
    """Calculate parity (0 if even number of 1s, 1 if odd)."""
    p = 0
    while value:
        p ^= value & 1
        value >>= 1
    return p


def leading_zeros(value: int, bits: int = 32) -> int:
    """Count leading zeros."""
    if value == 0:
        return bits
    count = 0
    mask = 1 << (bits - 1)
    while (value & mask) == 0:
        count += 1
        mask >>= 1
    return count


def trailing_zeros(value: int) -> int:
    """Count trailing zeros."""
    if value == 0:
        return 32
    count = 0
    while (value & 1) == 0:
        count += 1
        value >>= 1
    return count


def sign_extend(value: int, from_bits: int, to_bits: int = 32) -> int:
    """Sign extend from smaller bit width to larger."""
    sign_bit = 1 << (from_bits - 1)
    if value & sign_bit:
        mask = ((1 << to_bits) - 1) ^ ((1 << from_bits) - 1)
        return value | mask
    return value


def gray_encode(n: int) -> int:
    """Convert to Gray code."""
    return n ^ (n >> 1)


def gray_decode(gray: int) -> int:
    """Convert from Gray code."""
    n = gray
    mask = n
    while mask:
        mask >>= 1
        n ^= mask
    return n


def interleave_bits(x: int, y: int) -> int:
    """Interleave bits of x and y (Morton code)."""
    result = 0
    for i in range(16):
        result |= ((x >> i) & 1) << (2 * i)
        result |= ((y >> i) & 1) << (2 * i + 1)
    return result


def deinterleave_bits(z: int) -> tuple[int, int]:
    """Deinterleave Morton code back to x and y."""
    x = 0
    y = 0
    for i in range(16):
        x |= ((z >> (2 * i)) & 1) << i
        y |= ((z >> (2 * i + 1)) & 1) << i
    return (x, y)


def to_binary_string(value: int, bits: int = 8) -> str:
    """Convert to binary string with leading zeros."""
    return format(value & ((1 << bits) - 1), f"0{bits}b")


def from_binary_string(s: str) -> int:
    """Convert binary string to integer."""
    return int(s, 2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bitwise operations CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # binary
    bin_p = subparsers.add_parser("binary", help="Show binary representation")
    bin_p.add_argument("value", type=int)
    bin_p.add_argument("--bits", type=int, default=8)

    # popcount
    pop_p = subparsers.add_parser("popcount", help="Count set bits")
    pop_p.add_argument("value", type=int)

    # power2
    pow_p = subparsers.add_parser("power2", help="Check/find power of 2")
    pow_p.add_argument("value", type=int)
    pow_p.add_argument("--next", action="store_true")

    # shift
    shift_p = subparsers.add_parser("shift", help="Shift operations")
    shift_p.add_argument("value", type=int)
    shift_p.add_argument("count", type=int)
    shift_p.add_argument("--left", action="store_true")
    shift_p.add_argument("--rotate", action="store_true")

    args = parser.parse_args()

    if args.command == "binary":
        print(to_binary_string(args.value, args.bits))

    elif args.command == "popcount":
        print(f"Set bits: {count_set_bits(args.value)}")

    elif args.command == "power2":
        if args.next:
            print(f"Next power of 2: {next_power_of_two(args.value)}")
        else:
            print(f"Is power of 2: {is_power_of_two(args.value)}")

    elif args.command == "shift":
        if args.rotate:
            if args.left:
                result = rotate_left(args.value, args.count)
            else:
                result = rotate_right(args.value, args.count)
            print(f"Rotated: {result}")
        else:
            if args.left:
                result = left_shift(args.value, args.count)
            else:
                result = right_shift(args.value, args.count)
            print(f"Shifted: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
