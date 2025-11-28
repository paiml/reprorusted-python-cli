#!/usr/bin/env python3
"""MessagePack-lite codec CLI.

Simple binary serialization format (subset of MessagePack).
"""

import argparse
import json
import struct
import sys

# Format codes (simplified MessagePack subset)
FMT_NIL = 0xC0
FMT_FALSE = 0xC2
FMT_TRUE = 0xC3
FMT_UINT8 = 0xCC
FMT_UINT16 = 0xCD
FMT_UINT32 = 0xCE
FMT_INT8 = 0xD0
FMT_INT16 = 0xD1
FMT_INT32 = 0xD2
FMT_STR8 = 0xD9
FMT_STR16 = 0xDA
FMT_ARRAY16 = 0xDC
FMT_MAP16 = 0xDE


def encode_nil() -> bytes:
    """Encode None."""
    return bytes([FMT_NIL])


def encode_bool(value: bool) -> bytes:
    """Encode boolean."""
    return bytes([FMT_TRUE if value else FMT_FALSE])


def encode_int(value: int) -> bytes:
    """Encode integer."""
    if 0 <= value <= 127:
        # Positive fixint
        return bytes([value])
    if -32 <= value < 0:
        # Negative fixint
        return bytes([value & 0xFF])
    if 0 <= value <= 255:
        return bytes([FMT_UINT8, value])
    if 0 <= value <= 65535:
        return bytes([FMT_UINT16]) + struct.pack(">H", value)
    if 0 <= value <= 4294967295:
        return bytes([FMT_UINT32]) + struct.pack(">I", value)
    if -128 <= value < 0:
        return bytes([FMT_INT8]) + struct.pack(">b", value)
    if -32768 <= value < 0:
        return bytes([FMT_INT16]) + struct.pack(">h", value)
    if -2147483648 <= value < 0:
        return bytes([FMT_INT32]) + struct.pack(">i", value)

    raise ValueError(f"Integer out of range: {value}")


def encode_string(value: str) -> bytes:
    """Encode string."""
    encoded = value.encode("utf-8")
    length = len(encoded)

    if length <= 31:
        # Fixstr
        return bytes([0xA0 | length]) + encoded
    if length <= 255:
        return bytes([FMT_STR8, length]) + encoded
    if length <= 65535:
        return bytes([FMT_STR16]) + struct.pack(">H", length) + encoded

    raise ValueError(f"String too long: {length}")


def encode_array(value: list) -> bytes:
    """Encode array."""
    length = len(value)

    if length <= 15:
        # Fixarray
        result = bytes([0x90 | length])
    elif length <= 65535:
        result = bytes([FMT_ARRAY16]) + struct.pack(">H", length)
    else:
        raise ValueError(f"Array too long: {length}")

    for item in value:
        result += msgpack_encode(item)

    return result


def encode_map(value: dict) -> bytes:
    """Encode map/dict."""
    length = len(value)

    if length <= 15:
        # Fixmap
        result = bytes([0x80 | length])
    elif length <= 65535:
        result = bytes([FMT_MAP16]) + struct.pack(">H", length)
    else:
        raise ValueError(f"Map too long: {length}")

    for k, v in value.items():
        result += msgpack_encode(str(k))
        result += msgpack_encode(v)

    return result


def msgpack_encode(value) -> bytes:
    """Encode Python value to msgpack-lite."""
    if value is None:
        return encode_nil()
    if isinstance(value, bool):
        return encode_bool(value)
    if isinstance(value, int):
        return encode_int(value)
    if isinstance(value, str):
        return encode_string(value)
    if isinstance(value, list):
        return encode_array(value)
    if isinstance(value, dict):
        return encode_map(value)

    raise ValueError(f"Cannot encode type: {type(value)}")


class MsgPackDecoder:
    """Stateful decoder."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_bytes(self, n: int) -> bytes:
        """Read n bytes."""
        if self.pos + n > len(self.data):
            raise ValueError("Unexpected end of data")
        result = self.data[self.pos : self.pos + n]
        self.pos += n
        return result

    def decode(self):
        """Decode next value."""
        byte = self.read_bytes(1)[0]

        # Nil
        if byte == FMT_NIL:
            return None

        # Bool
        if byte == FMT_FALSE:
            return False
        if byte == FMT_TRUE:
            return True

        # Positive fixint (0-127)
        if byte <= 0x7F:
            return byte

        # Negative fixint
        if byte >= 0xE0:
            return byte - 256

        # Fixstr
        if 0xA0 <= byte <= 0xBF:
            length = byte & 0x1F
            return self.read_bytes(length).decode("utf-8")

        # Fixarray
        if 0x90 <= byte <= 0x9F:
            length = byte & 0x0F
            return [self.decode() for _ in range(length)]

        # Fixmap
        if 0x80 <= byte <= 0x8F:
            length = byte & 0x0F
            return {self.decode(): self.decode() for _ in range(length)}

        # Extended formats
        if byte == FMT_UINT8:
            return self.read_bytes(1)[0]
        if byte == FMT_UINT16:
            return struct.unpack(">H", self.read_bytes(2))[0]
        if byte == FMT_UINT32:
            return struct.unpack(">I", self.read_bytes(4))[0]
        if byte == FMT_INT8:
            return struct.unpack(">b", self.read_bytes(1))[0]
        if byte == FMT_INT16:
            return struct.unpack(">h", self.read_bytes(2))[0]
        if byte == FMT_INT32:
            return struct.unpack(">i", self.read_bytes(4))[0]
        if byte == FMT_STR8:
            length = self.read_bytes(1)[0]
            return self.read_bytes(length).decode("utf-8")
        if byte == FMT_STR16:
            length = struct.unpack(">H", self.read_bytes(2))[0]
            return self.read_bytes(length).decode("utf-8")
        if byte == FMT_ARRAY16:
            length = struct.unpack(">H", self.read_bytes(2))[0]
            return [self.decode() for _ in range(length)]
        if byte == FMT_MAP16:
            length = struct.unpack(">H", self.read_bytes(2))[0]
            return {self.decode(): self.decode() for _ in range(length)}

        raise ValueError(f"Unknown format: 0x{byte:02X}")


def msgpack_decode(data: bytes):
    """Decode msgpack-lite data."""
    decoder = MsgPackDecoder(data)
    return decoder.decode()


def calculate_size(value) -> int:
    """Calculate encoded size without encoding."""
    return len(msgpack_encode(value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Encode and decode msgpack-lite format")
    parser.add_argument("input", nargs="?", help="Input file (- for stdin)")
    parser.add_argument("-e", "--encode", action="store_true", help="Encode JSON to msgpack")
    parser.add_argument("-d", "--decode", action="store_true", help="Decode msgpack to JSON")
    parser.add_argument("--size", action="store_true", help="Show encoded size")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    # Read input
    if args.input is None or args.input == "-":
        if args.encode or args.size:
            data = sys.stdin.read()
        else:
            data = sys.stdin.buffer.read()
    else:
        if args.encode or args.size:
            with open(args.input) as f:
                data = f.read()
        else:
            with open(args.input, "rb") as f:
                data = f.read()

    # Process
    if args.size:
        try:
            obj = json.loads(data)
            size = calculate_size(obj)
            json_size = len(data.encode("utf-8"))
            print(f"JSON size: {json_size} bytes")
            print(f"MsgPack size: {size} bytes")
            print(f"Ratio: {size / json_size:.2%}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            return 1
        return 0

    if args.encode:
        try:
            obj = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            return 1

        try:
            result = msgpack_encode(obj)
        except ValueError as e:
            print(f"Encode error: {e}", file=sys.stderr)
            return 1

        if args.output:
            with open(args.output, "wb") as f:
                f.write(result)
        else:
            sys.stdout.buffer.write(result)

    elif args.decode:
        try:
            obj = msgpack_decode(data)
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
        # Default: show hex dump of encoded data
        if isinstance(data, str):
            try:
                obj = json.loads(data)
                encoded = msgpack_encode(obj)
                print(f"Size: {len(encoded)} bytes")
                print(f"Hex: {encoded.hex()}")
            except json.JSONDecodeError:
                print("Input is not valid JSON")
                return 1
        else:
            try:
                obj = msgpack_decode(data)
                print(f"Type: {type(obj).__name__}")
                print(json.dumps(obj, indent=2))
            except Exception as e:
                print(f"Invalid msgpack: {e}")
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
