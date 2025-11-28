#!/usr/bin/env python3
"""Bencode codec CLI.

Encode and decode BitTorrent bencode format.
"""

import argparse
import json
import sys


def encode_int(value: int) -> bytes:
    """Encode integer to bencode."""
    return f"i{value}e".encode("ascii")


def encode_bytes(value: bytes) -> bytes:
    """Encode bytes to bencode."""
    return f"{len(value)}:".encode("ascii") + value


def encode_string(value: str) -> bytes:
    """Encode string to bencode."""
    encoded = value.encode("utf-8")
    return f"{len(encoded)}:".encode("ascii") + encoded


def encode_list(value: list) -> bytes:
    """Encode list to bencode."""
    result = b"l"
    for item in value:
        result += bencode_encode(item)
    result += b"e"
    return result


def encode_dict(value: dict) -> bytes:
    """Encode dict to bencode.

    Keys must be strings and are sorted.
    """
    result = b"d"
    for key in sorted(value.keys()):
        result += encode_string(str(key))
        result += bencode_encode(value[key])
    result += b"e"
    return result


def bencode_encode(value) -> bytes:
    """Encode Python value to bencode."""
    if isinstance(value, int):
        return encode_int(value)
    if isinstance(value, bytes):
        return encode_bytes(value)
    if isinstance(value, str):
        return encode_string(value)
    if isinstance(value, list):
        return encode_list(value)
    if isinstance(value, dict):
        return encode_dict(value)
    raise ValueError(f"Cannot encode type: {type(value)}")


class BencodeDecoder:
    """Stateful bencode decoder."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def decode(self):
        """Decode next value."""
        if self.pos >= len(self.data):
            raise ValueError("Unexpected end of data")

        byte = self.data[self.pos]

        if byte == ord("i"):
            return self.decode_int()
        if byte == ord("l"):
            return self.decode_list()
        if byte == ord("d"):
            return self.decode_dict()
        if ord("0") <= byte <= ord("9"):
            return self.decode_string()

        raise ValueError(f"Invalid bencode at position {self.pos}")

    def decode_int(self) -> int:
        """Decode bencode integer."""
        self.pos += 1  # Skip 'i'
        end = self.data.index(ord("e"), self.pos)
        value = int(self.data[self.pos : end].decode("ascii"))
        self.pos = end + 1
        return value

    def decode_string(self) -> str:
        """Decode bencode string."""
        colon = self.data.index(ord(":"), self.pos)
        length = int(self.data[self.pos : colon].decode("ascii"))
        self.pos = colon + 1
        value = self.data[self.pos : self.pos + length]
        self.pos += length

        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            # Return hex for binary data
            return value.hex()

    def decode_list(self) -> list:
        """Decode bencode list."""
        self.pos += 1  # Skip 'l'
        result = []
        while self.data[self.pos] != ord("e"):
            result.append(self.decode())
        self.pos += 1  # Skip 'e'
        return result

    def decode_dict(self) -> dict:
        """Decode bencode dict."""
        self.pos += 1  # Skip 'd'
        result = {}
        while self.data[self.pos] != ord("e"):
            key = self.decode_string()
            value = self.decode()
            result[key] = value
        self.pos += 1  # Skip 'e'
        return result


def bencode_decode(data: bytes):
    """Decode bencode data to Python value."""
    decoder = BencodeDecoder(data)
    return decoder.decode()


def validate_bencode(data: bytes) -> tuple[bool, str]:
    """Validate bencode data.

    Returns (is_valid, error_message).
    """
    try:
        bencode_decode(data)
        return True, ""
    except Exception as e:
        return False, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Encode and decode bencode format")
    parser.add_argument("input", nargs="?", help="Input file (- for stdin)")
    parser.add_argument("-e", "--encode", action="store_true", help="Encode JSON to bencode")
    parser.add_argument("-d", "--decode", action="store_true", help="Decode bencode to JSON")
    parser.add_argument("--validate", action="store_true", help="Validate bencode data")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    # Read input
    if args.input is None or args.input == "-":
        if args.encode:
            data = sys.stdin.read()
        else:
            data = sys.stdin.buffer.read()
    else:
        if args.encode:
            with open(args.input) as f:
                data = f.read()
        else:
            with open(args.input, "rb") as f:
                data = f.read()

    # Process
    if args.validate:
        if isinstance(data, str):
            data = data.encode("utf-8")
        valid, error = validate_bencode(data)
        if valid:
            print("Valid bencode")
            return 0
        print(f"Invalid: {error}", file=sys.stderr)
        return 1

    if args.encode:
        try:
            obj = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            return 1

        result = bencode_encode(obj)

        if args.output:
            with open(args.output, "wb") as f:
                f.write(result)
        else:
            sys.stdout.buffer.write(result)
            sys.stdout.buffer.write(b"\n")

    elif args.decode:
        try:
            obj = bencode_decode(data)
        except Exception as e:
            print(f"Decode error: {e}", file=sys.stderr)
            return 1

        result = json.dumps(obj, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
        else:
            print(result)

    else:
        # Default: detect and show info
        if isinstance(data, str):
            data = data.encode("utf-8")

        valid, error = validate_bencode(data)
        if valid:
            obj = bencode_decode(data)
            print(f"Type: {type(obj).__name__}")
            if isinstance(obj, dict):
                print(f"Keys: {list(obj.keys())}")
            elif isinstance(obj, list):
                print(f"Length: {len(obj)}")
        else:
            print(f"Invalid bencode: {error}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
