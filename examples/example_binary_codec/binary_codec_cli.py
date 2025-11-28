#!/usr/bin/env python3
"""Binary Codec CLI.

Binary encoding/decoding utilities (base64, hex, etc).
"""

import argparse
import base64
import sys


def encode_hex(data: bytes) -> str:
    """Encode bytes to hex string."""
    return data.hex()


def decode_hex(hex_str: str) -> bytes:
    """Decode hex string to bytes."""
    return bytes.fromhex(hex_str)


def encode_hex_upper(data: bytes) -> str:
    """Encode bytes to uppercase hex string."""
    return data.hex().upper()


def encode_base64(data: bytes) -> str:
    """Encode bytes to base64 string."""
    return base64.b64encode(data).decode("ascii")


def decode_base64(b64_str: str) -> bytes:
    """Decode base64 string to bytes."""
    return base64.b64decode(b64_str)


def encode_base64_url(data: bytes) -> str:
    """Encode bytes to URL-safe base64."""
    return base64.urlsafe_b64encode(data).decode("ascii")


def decode_base64_url(b64_str: str) -> bytes:
    """Decode URL-safe base64 string."""
    return base64.urlsafe_b64decode(b64_str)


def encode_base32(data: bytes) -> str:
    """Encode bytes to base32 string."""
    return base64.b32encode(data).decode("ascii")


def decode_base32(b32_str: str) -> bytes:
    """Decode base32 string to bytes."""
    return base64.b32decode(b32_str)


def encode_base16(data: bytes) -> str:
    """Encode bytes to base16 (hex) string."""
    return base64.b16encode(data).decode("ascii")


def decode_base16(b16_str: str) -> bytes:
    """Decode base16 (hex) string to bytes."""
    return base64.b16decode(b16_str)


def bytes_to_binary_string(data: bytes) -> str:
    """Convert bytes to binary string representation."""
    return " ".join(format(b, "08b") for b in data)


def binary_string_to_bytes(bin_str: str) -> bytes:
    """Convert binary string to bytes."""
    parts = bin_str.split()
    return bytes(int(p, 2) for p in parts)


def bytes_to_int_list(data: bytes) -> list[int]:
    """Convert bytes to list of integers."""
    return list(data)


def int_list_to_bytes(values: list[int]) -> bytes:
    """Convert list of integers to bytes."""
    return bytes(values)


def encode_ascii_hex(text: str) -> str:
    """Encode ASCII text to hex representation."""
    return text.encode("ascii").hex()


def decode_ascii_hex(hex_str: str) -> str:
    """Decode hex to ASCII text."""
    return bytes.fromhex(hex_str).decode("ascii")


def encode_utf8_hex(text: str) -> str:
    """Encode UTF-8 text to hex representation."""
    return text.encode("utf-8").hex()


def decode_utf8_hex(hex_str: str) -> str:
    """Decode hex to UTF-8 text."""
    return bytes.fromhex(hex_str).decode("utf-8")


def escape_bytes(data: bytes) -> str:
    """Escape non-printable bytes as \\xNN."""
    result = []
    for b in data:
        if 32 <= b < 127:
            result.append(chr(b))
        else:
            result.append(f"\\x{b:02x}")
    return "".join(result)


def unescape_bytes(text: str) -> bytes:
    """Unescape \\xNN sequences to bytes."""
    result = bytearray()
    i = 0
    while i < len(text):
        if text[i : i + 2] == "\\x" and i + 4 <= len(text):
            hex_chars = text[i + 2 : i + 4]
            try:
                result.append(int(hex_chars, 16))
                i += 4
                continue
            except ValueError:
                pass
        result.append(ord(text[i]))
        i += 1
    return bytes(result)


def run_length_encode(data: bytes) -> bytes:
    """Simple run-length encoding."""
    if len(data) == 0:
        return b""
    result = bytearray()
    current = data[0]
    count = 1
    for i in range(1, len(data)):
        if data[i] == current and count < 255:
            count += 1
        else:
            result.append(count)
            result.append(current)
            current = data[i]
            count = 1
    result.append(count)
    result.append(current)
    return bytes(result)


def run_length_decode(data: bytes) -> bytes:
    """Simple run-length decoding."""
    result = bytearray()
    i = 0
    while i + 1 < len(data):
        count = data[i]
        value = data[i + 1]
        result.extend([value] * count)
        i += 2
    return bytes(result)


def xor_cipher(data: bytes, key: bytes) -> bytes:
    """XOR cipher with repeating key."""
    result = bytearray(len(data))
    key_len = len(key)
    if key_len == 0:
        return bytes(data)
    for i in range(len(data)):
        result[i] = data[i] ^ key[i % key_len]
    return bytes(result)


def caesar_cipher(data: bytes, shift: int) -> bytes:
    """Caesar cipher on byte values."""
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = (data[i] + shift) & 0xFF
    return bytes(result)


def caesar_decipher(data: bytes, shift: int) -> bytes:
    """Reverse Caesar cipher."""
    return caesar_cipher(data, -shift)


def bit_reverse_bytes(data: bytes) -> bytes:
    """Reverse bits in each byte."""
    result = bytearray(len(data))
    for i, b in enumerate(data):
        reversed_byte = 0
        for j in range(8):
            if b & (1 << j):
                reversed_byte |= 1 << (7 - j)
        result[i] = reversed_byte
    return bytes(result)


def nibble_swap(data: bytes) -> bytes:
    """Swap high and low nibbles in each byte."""
    result = bytearray(len(data))
    for i, b in enumerate(data):
        result[i] = ((b & 0x0F) << 4) | ((b >> 4) & 0x0F)
    return bytes(result)


def invert_bytes(data: bytes) -> bytes:
    """Invert all bytes (NOT operation)."""
    result = bytearray(len(data))
    for i, b in enumerate(data):
        result[i] = (~b) & 0xFF
    return bytes(result)


def calculate_crc8(data: bytes, polynomial: int = 0x07) -> int:
    """Calculate CRC-8 checksum."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ polynomial) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def calculate_crc16(data: bytes, polynomial: int = 0x8005) -> int:
    """Calculate CRC-16 checksum."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1
    return crc


def hamming_encode_nibble(nibble: int) -> int:
    """Encode a nibble with Hamming(7,4) code."""
    d = [(nibble >> i) & 1 for i in range(4)]
    p1 = d[0] ^ d[1] ^ d[3]
    p2 = d[0] ^ d[2] ^ d[3]
    p3 = d[1] ^ d[2] ^ d[3]
    return p1 | (p2 << 1) | (d[0] << 2) | (p3 << 3) | (d[1] << 4) | (d[2] << 5) | (d[3] << 6)


def hamming_decode_byte(encoded: int) -> tuple[int, int]:
    """Decode Hamming(7,4) code, return (data, errors)."""
    p1 = ((encoded >> 0) ^ (encoded >> 2) ^ (encoded >> 4) ^ (encoded >> 6)) & 1
    p2 = ((encoded >> 1) ^ (encoded >> 2) ^ (encoded >> 5) ^ (encoded >> 6)) & 1
    p3 = ((encoded >> 3) ^ (encoded >> 4) ^ (encoded >> 5) ^ (encoded >> 6)) & 1
    error_pos = p1 | (p2 << 1) | (p3 << 2)
    if error_pos:
        encoded ^= 1 << (error_pos - 1)
    data = (
        ((encoded >> 2) & 1)
        | (((encoded >> 4) & 1) << 1)
        | (((encoded >> 5) & 1) << 2)
        | (((encoded >> 6) & 1) << 3)
    )
    return (data, 1 if error_pos else 0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Binary codec CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # hex
    hex_p = subparsers.add_parser("hex", help="Hex encode/decode")
    hex_p.add_argument("action", choices=["encode", "decode"])
    hex_p.add_argument("data")

    # base64
    b64_p = subparsers.add_parser("base64", help="Base64 encode/decode")
    b64_p.add_argument("action", choices=["encode", "decode"])
    b64_p.add_argument("data")
    b64_p.add_argument("--url-safe", action="store_true")

    # rle
    rle_p = subparsers.add_parser("rle", help="Run-length encode/decode")
    rle_p.add_argument("action", choices=["encode", "decode"])
    rle_p.add_argument("hex_data")

    # xor
    xor_p = subparsers.add_parser("xor", help="XOR cipher")
    xor_p.add_argument("hex_data")
    xor_p.add_argument("hex_key")

    # crc
    crc_p = subparsers.add_parser("crc", help="Calculate CRC")
    crc_p.add_argument("hex_data")
    crc_p.add_argument("--bits", type=int, choices=[8, 16], default=8)

    args = parser.parse_args()

    if args.command == "hex":
        if args.action == "encode":
            data = args.data.encode("utf-8")
            print(encode_hex(data))
        else:
            data = decode_hex(args.data)
            print(data.decode("utf-8", errors="replace"))

    elif args.command == "base64":
        if args.action == "encode":
            data = args.data.encode("utf-8")
            if args.url_safe:
                print(encode_base64_url(data))
            else:
                print(encode_base64(data))
        else:
            if args.url_safe:
                data = decode_base64_url(args.data)
            else:
                data = decode_base64(args.data)
            print(data.decode("utf-8"))

    elif args.command == "rle":
        if args.action == "encode":
            data = bytes.fromhex(args.hex_data)
            result = run_length_encode(data)
            print(result.hex())
        else:
            data = bytes.fromhex(args.hex_data)
            result = run_length_decode(data)
            print(result.hex())

    elif args.command == "xor":
        data = bytes.fromhex(args.hex_data)
        key = bytes.fromhex(args.hex_key)
        result = xor_cipher(data, key)
        print(result.hex())

    elif args.command == "crc":
        data = bytes.fromhex(args.hex_data)
        if args.bits == 8:
            print(f"{calculate_crc8(data):02x}")
        else:
            print(f"{calculate_crc16(data):04x}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
