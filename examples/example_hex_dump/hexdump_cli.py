#!/usr/bin/env python3
"""Hex dump utility CLI.

Display and convert binary data in various formats.
"""

import argparse
import sys


def format_hex_line(
    offset: int,
    data: bytes,
    bytes_per_line: int = 16,
    show_ascii: bool = True,
) -> str:
    """Format a single line of hex dump."""
    parts = []

    # Offset
    parts.append(f"{offset:08x}")

    # Hex bytes
    hex_parts = []
    for i, byte in enumerate(data):
        hex_parts.append(f"{byte:02x}")
        if i == 7:
            hex_parts.append("")  # Extra space at midpoint

    # Pad if needed
    if len(data) < bytes_per_line:
        for i in range(len(data), bytes_per_line):
            hex_parts.append("  ")
            if i == 7:
                hex_parts.append("")

    parts.append(" ".join(hex_parts))

    # ASCII representation
    if show_ascii:
        ascii_chars = []
        for byte in data:
            if 32 <= byte < 127:
                ascii_chars.append(chr(byte))
            else:
                ascii_chars.append(".")
        parts.append("|" + "".join(ascii_chars) + "|")

    return "  ".join(parts)


def hexdump(
    data: bytes,
    bytes_per_line: int = 16,
    show_ascii: bool = True,
    start_offset: int = 0,
) -> list[str]:
    """Generate hex dump of data."""
    lines = []
    offset = start_offset

    for i in range(0, len(data), bytes_per_line):
        chunk = data[i : i + bytes_per_line]
        lines.append(format_hex_line(offset, chunk, bytes_per_line, show_ascii))
        offset += bytes_per_line

    return lines


def hexdump_c_array(
    data: bytes,
    name: str = "data",
    bytes_per_line: int = 12,
) -> list[str]:
    """Generate C array from binary data."""
    lines = []
    lines.append(f"unsigned char {name}[] = {{")

    for i in range(0, len(data), bytes_per_line):
        chunk = data[i : i + bytes_per_line]
        hex_values = [f"0x{b:02x}" for b in chunk]
        line = "    " + ", ".join(hex_values)
        if i + bytes_per_line < len(data):
            line += ","
        lines.append(line)

    lines.append("};")
    lines.append(f"unsigned int {name}_len = {len(data)};")

    return lines


def parse_hex(hex_str: str) -> bytes:
    """Parse hex string to bytes."""
    # Remove common prefixes and separators
    hex_str = hex_str.replace("0x", "").replace("0X", "")
    hex_str = hex_str.replace(" ", "").replace(":", "").replace("-", "")
    hex_str = hex_str.replace("\n", "").replace("\r", "")

    return bytes.fromhex(hex_str)


def bytes_to_hex(data: bytes, separator: str = " ") -> str:
    """Convert bytes to hex string."""
    return separator.join(f"{b:02x}" for b in data)


def find_pattern(data: bytes, pattern: bytes) -> list[int]:
    """Find all occurrences of pattern in data."""
    positions = []
    start = 0
    while True:
        pos = data.find(pattern, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def extract_strings(data: bytes, min_length: int = 4) -> list[tuple[int, str]]:
    """Extract printable ASCII strings from binary data."""
    strings = []
    current = []
    start_pos = 0

    for i, byte in enumerate(data):
        if 32 <= byte < 127:
            if not current:
                start_pos = i
            current.append(chr(byte))
        else:
            if len(current) >= min_length:
                strings.append((start_pos, "".join(current)))
            current = []

    if len(current) >= min_length:
        strings.append((start_pos, "".join(current)))

    return strings


def main() -> int:
    parser = argparse.ArgumentParser(description="Hex dump utility")
    parser.add_argument("input", nargs="?", help="Input file (- for stdin)")
    parser.add_argument("-n", "--length", type=int, help="Number of bytes to read")
    parser.add_argument("-s", "--skip", type=int, default=0, help="Skip bytes at start")
    parser.add_argument("-c", "--columns", type=int, default=16, help="Bytes per line")
    parser.add_argument("--no-ascii", action="store_true", help="Don't show ASCII column")
    parser.add_argument(
        "-r", "--reverse", action="store_true", help="Reverse: convert hex to binary"
    )
    parser.add_argument("-C", "--c-array", metavar="NAME", help="Output as C array")
    parser.add_argument(
        "--strings",
        type=int,
        nargs="?",
        const=4,
        metavar="LEN",
        help="Extract strings (min length)",
    )
    parser.add_argument("--find", metavar="HEX", help="Find hex pattern in data")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    # Read input
    if args.input is None or args.input == "-":
        if args.reverse:
            data = sys.stdin.read()
        else:
            data = sys.stdin.buffer.read()
    else:
        if args.reverse:
            with open(args.input) as f:
                data = f.read()
        else:
            with open(args.input, "rb") as f:
                data = f.read()

    # Apply skip and length
    if not args.reverse:
        if args.skip > 0:
            data = data[args.skip :]
        if args.length:
            data = data[: args.length]

    # Process
    if args.reverse:
        try:
            result = parse_hex(data)
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(result)
            else:
                sys.stdout.buffer.write(result)
            return 0
        except ValueError as e:
            print(f"Invalid hex: {e}", file=sys.stderr)
            return 1

    if args.strings is not None:
        strings = extract_strings(data, args.strings)
        output = "\n".join(f"{offset:08x}  {s}" for offset, s in strings)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
        return 0

    if args.find:
        try:
            pattern = parse_hex(args.find)
        except ValueError as e:
            print(f"Invalid pattern: {e}", file=sys.stderr)
            return 1

        positions = find_pattern(data, pattern)
        if positions:
            print(f"Found {len(positions)} occurrence(s):")
            for pos in positions:
                print(f"  0x{pos:08x}")
        else:
            print("Pattern not found")
        return 0

    if args.c_array:
        lines = hexdump_c_array(data, args.c_array, args.columns)
        output = "\n".join(lines)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
        return 0

    # Default: hex dump
    lines = hexdump(
        data,
        bytes_per_line=args.columns,
        show_ascii=not args.no_ascii,
        start_offset=args.skip,
    )
    output = "\n".join(lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
