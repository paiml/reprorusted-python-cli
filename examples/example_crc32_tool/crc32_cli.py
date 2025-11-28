#!/usr/bin/env python3
"""CRC32 checksum calculator CLI.

Calculate and verify CRC32 checksums.
"""

import argparse
import os
import sys

# CRC32 polynomial (IEEE 802.3)
CRC32_POLY = 0xEDB88320

# Pre-computed CRC32 table
CRC32_TABLE: list[int] = []


def init_crc32_table() -> None:
    """Initialize CRC32 lookup table."""
    global CRC32_TABLE
    if CRC32_TABLE:
        return

    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ CRC32_POLY
            else:
                crc >>= 1
        CRC32_TABLE.append(crc)


def crc32_update(crc: int, data: bytes) -> int:
    """Update CRC32 with data."""
    init_crc32_table()
    for byte in data:
        crc = CRC32_TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc


def crc32(data: bytes) -> int:
    """Calculate CRC32 of data."""
    return crc32_update(0xFFFFFFFF, data) ^ 0xFFFFFFFF


def crc32_file(path: str, chunk_size: int = 65536) -> int:
    """Calculate CRC32 of file."""
    crc = 0xFFFFFFFF
    init_crc32_table()

    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            crc = crc32_update(crc, chunk)

    return crc ^ 0xFFFFFFFF


def format_crc32(value: int) -> str:
    """Format CRC32 value as hex string."""
    return f"{value:08x}"


def parse_crc32(hex_str: str) -> int | None:
    """Parse CRC32 from hex string."""
    try:
        return int(hex_str, 16)
    except ValueError:
        return None


def verify_checksum(path: str, expected: int) -> bool:
    """Verify file checksum matches expected."""
    actual = crc32_file(path)
    return actual == expected


def generate_checksum_file(paths: list[str]) -> list[str]:
    """Generate checksum file content."""
    lines = []
    for path in paths:
        if not os.path.isfile(path):
            continue
        checksum = crc32_file(path)
        lines.append(f"{format_crc32(checksum)}  {path}")
    return lines


def parse_checksum_file(content: str) -> list[tuple[int, str]]:
    """Parse checksum file content.

    Returns list of (checksum, path) tuples.
    """
    result = []
    for line in content.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Format: CHECKSUM  FILENAME
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue

        checksum = parse_crc32(parts[0])
        if checksum is None:
            continue

        result.append((checksum, parts[1]))

    return result


def verify_checksum_file(content: str) -> list[tuple[str, bool, str]]:
    """Verify checksums from checksum file.

    Returns list of (path, passed, message) tuples.
    """
    results = []
    entries = parse_checksum_file(content)

    for expected, path in entries:
        if not os.path.exists(path):
            results.append((path, False, "NOT FOUND"))
            continue

        try:
            actual = crc32_file(path)
            if actual == expected:
                results.append((path, True, "OK"))
            else:
                results.append((path, False, f"FAILED (got {format_crc32(actual)})"))
        except OSError as e:
            results.append((path, False, f"ERROR: {e}"))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate and verify CRC32 checksums")
    parser.add_argument("files", nargs="*", help="Files to checksum")
    parser.add_argument("-c", "--check", metavar="FILE", help="Verify checksums from file")
    parser.add_argument("-s", "--string", metavar="TEXT", help="Calculate checksum of string")
    parser.add_argument("--verify", metavar="CHECKSUM", help="Verify file against checksum")
    parser.add_argument("--binary", action="store_true", help="Output raw binary checksum")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (exit code only)")

    args = parser.parse_args()

    # Verify checksums from file
    if args.check:
        try:
            with open(args.check) as f:
                content = f.read()
        except OSError as e:
            print(f"Error reading {args.check}: {e}", file=sys.stderr)
            return 1

        results = verify_checksum_file(content)
        failed = 0

        for path, passed, message in results:
            if not args.quiet:
                print(f"{path}: {message}")
            if not passed:
                failed += 1

        if failed > 0:
            if not args.quiet:
                print(f"\n{failed} failed")
            return 1
        return 0

    # Calculate checksum of string
    if args.string:
        checksum = crc32(args.string.encode("utf-8"))
        if args.binary:
            sys.stdout.buffer.write(checksum.to_bytes(4, "little"))
        else:
            print(format_crc32(checksum))
        return 0

    # Verify specific checksum
    if args.verify:
        if not args.files:
            print("No files specified", file=sys.stderr)
            return 1

        expected = parse_crc32(args.verify)
        if expected is None:
            print(f"Invalid checksum: {args.verify}", file=sys.stderr)
            return 1

        all_passed = True
        for path in args.files:
            if not os.path.isfile(path):
                if not args.quiet:
                    print(f"{path}: NOT FOUND")
                all_passed = False
                continue

            passed = verify_checksum(path, expected)
            if not args.quiet:
                status = "OK" if passed else "FAILED"
                print(f"{path}: {status}")
            if not passed:
                all_passed = False

        return 0 if all_passed else 1

    # Calculate checksums for files
    if not args.files:
        # Read from stdin
        data = sys.stdin.buffer.read()
        checksum = crc32(data)
        if args.binary:
            sys.stdout.buffer.write(checksum.to_bytes(4, "little"))
        else:
            print(format_crc32(checksum))
        return 0

    for path in args.files:
        if not os.path.isfile(path):
            print(f"{path}: NOT FOUND", file=sys.stderr)
            continue

        try:
            checksum = crc32_file(path)
            if args.binary:
                sys.stdout.buffer.write(checksum.to_bytes(4, "little"))
            else:
                print(f"{format_crc32(checksum)}  {path}")
        except OSError as e:
            print(f"{path}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
