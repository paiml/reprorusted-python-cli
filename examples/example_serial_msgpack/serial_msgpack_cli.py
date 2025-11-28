"""MessagePack-style Binary Encoding CLI.

Demonstrates binary serialization patterns without external dependencies.
Implements a subset of MessagePack format for educational purposes.
"""

import struct
import sys
from dataclasses import dataclass
from typing import Any

# MessagePack format markers
FIXINT_POS_MAX = 0x7F
FIXINT_NEG_MIN = 0xE0
FIXMAP_MAX = 0x8F
FIXARRAY_MAX = 0x9F
FIXSTR_MAX = 0xBF

NIL = 0xC0
FALSE = 0xC2
TRUE = 0xC3
BIN8 = 0xC4
BIN16 = 0xC5
BIN32 = 0xC6
FLOAT32 = 0xCA
FLOAT64 = 0xCB
UINT8 = 0xCC
UINT16 = 0xCD
UINT32 = 0xCE
UINT64 = 0xCF
INT8 = 0xD0
INT16 = 0xD1
INT32 = 0xD2
INT64 = 0xD3
STR8 = 0xD9
STR16 = 0xDA
STR32 = 0xDB
ARRAY16 = 0xDC
ARRAY32 = 0xDD
MAP16 = 0xDE
MAP32 = 0xDF


@dataclass
class EncodeResult:
    """Result of encoding operation."""

    data: bytes
    size: int


@dataclass
class DecodeResult:
    """Result of decoding operation."""

    value: Any
    bytes_consumed: int


class MsgPackEncoder:
    """MessagePack encoder."""

    def __init__(self) -> None:
        self.buffer = bytearray()

    def encode(self, value: Any) -> bytes:
        """Encode a value to MessagePack format."""
        self.buffer.clear()
        self._encode_value(value)
        return bytes(self.buffer)

    def _encode_value(self, value: Any) -> None:
        """Encode any value."""
        if value is None:
            self.buffer.append(NIL)
        elif isinstance(value, bool):
            self.buffer.append(TRUE if value else FALSE)
        elif isinstance(value, int):
            self._encode_int(value)
        elif isinstance(value, float):
            self._encode_float(value)
        elif isinstance(value, str):
            self._encode_str(value)
        elif isinstance(value, bytes):
            self._encode_bin(value)
        elif isinstance(value, list):
            self._encode_array(value)
        elif isinstance(value, dict):
            self._encode_map(value)
        else:
            raise ValueError(f"Cannot encode type: {type(value)}")

    def _encode_int(self, value: int) -> None:
        """Encode an integer."""
        if 0 <= value <= FIXINT_POS_MAX:
            self.buffer.append(value)
        elif -32 <= value < 0:
            self.buffer.append(value & 0xFF)
        elif 0 <= value <= 0xFF:
            self.buffer.append(UINT8)
            self.buffer.append(value)
        elif 0 <= value <= 0xFFFF:
            self.buffer.append(UINT16)
            self.buffer.extend(struct.pack(">H", value))
        elif 0 <= value <= 0xFFFFFFFF:
            self.buffer.append(UINT32)
            self.buffer.extend(struct.pack(">I", value))
        elif 0 <= value <= 0xFFFFFFFFFFFFFFFF:
            self.buffer.append(UINT64)
            self.buffer.extend(struct.pack(">Q", value))
        elif -128 <= value < 0:
            self.buffer.append(INT8)
            self.buffer.extend(struct.pack(">b", value))
        elif -32768 <= value < 0:
            self.buffer.append(INT16)
            self.buffer.extend(struct.pack(">h", value))
        elif -2147483648 <= value < 0:
            self.buffer.append(INT32)
            self.buffer.extend(struct.pack(">i", value))
        else:
            self.buffer.append(INT64)
            self.buffer.extend(struct.pack(">q", value))

    def _encode_float(self, value: float) -> None:
        """Encode a float as 64-bit."""
        self.buffer.append(FLOAT64)
        self.buffer.extend(struct.pack(">d", value))

    def _encode_str(self, value: str) -> None:
        """Encode a string."""
        data = value.encode("utf-8")
        length = len(data)

        if length <= 31:
            self.buffer.append(0xA0 | length)
        elif length <= 0xFF:
            self.buffer.append(STR8)
            self.buffer.append(length)
        elif length <= 0xFFFF:
            self.buffer.append(STR16)
            self.buffer.extend(struct.pack(">H", length))
        else:
            self.buffer.append(STR32)
            self.buffer.extend(struct.pack(">I", length))

        self.buffer.extend(data)

    def _encode_bin(self, value: bytes) -> None:
        """Encode binary data."""
        length = len(value)

        if length <= 0xFF:
            self.buffer.append(BIN8)
            self.buffer.append(length)
        elif length <= 0xFFFF:
            self.buffer.append(BIN16)
            self.buffer.extend(struct.pack(">H", length))
        else:
            self.buffer.append(BIN32)
            self.buffer.extend(struct.pack(">I", length))

        self.buffer.extend(value)

    def _encode_array(self, value: list[Any]) -> None:
        """Encode an array."""
        length = len(value)

        if length <= 15:
            self.buffer.append(0x90 | length)
        elif length <= 0xFFFF:
            self.buffer.append(ARRAY16)
            self.buffer.extend(struct.pack(">H", length))
        else:
            self.buffer.append(ARRAY32)
            self.buffer.extend(struct.pack(">I", length))

        for item in value:
            self._encode_value(item)

    def _encode_map(self, value: dict[str, Any]) -> None:
        """Encode a map."""
        length = len(value)

        if length <= 15:
            self.buffer.append(0x80 | length)
        elif length <= 0xFFFF:
            self.buffer.append(MAP16)
            self.buffer.extend(struct.pack(">H", length))
        else:
            self.buffer.append(MAP32)
            self.buffer.extend(struct.pack(">I", length))

        for key, val in value.items():
            self._encode_value(key)
            self._encode_value(val)


class MsgPackDecoder:
    """MessagePack decoder."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def decode(self) -> Any:
        """Decode a MessagePack value."""
        if self.pos >= len(self.data):
            raise ValueError("Unexpected end of data")

        marker = self.data[self.pos]
        self.pos += 1

        # Positive fixint
        if marker <= FIXINT_POS_MAX:
            return marker

        # Fixmap
        if 0x80 <= marker <= FIXMAP_MAX:
            return self._decode_map(marker & 0x0F)

        # Fixarray
        if 0x90 <= marker <= FIXARRAY_MAX:
            return self._decode_array(marker & 0x0F)

        # Fixstr
        if 0xA0 <= marker <= FIXSTR_MAX:
            return self._decode_str(marker & 0x1F)

        # Negative fixint
        if marker >= FIXINT_NEG_MIN:
            return struct.unpack(">b", bytes([marker]))[0]

        # Other types
        if marker == NIL:
            return None
        if marker == FALSE:
            return False
        if marker == TRUE:
            return True
        if marker == BIN8:
            return self._decode_bin(self._read_uint8())
        if marker == BIN16:
            return self._decode_bin(self._read_uint16())
        if marker == BIN32:
            return self._decode_bin(self._read_uint32())
        if marker == FLOAT32:
            return self._read_float32()
        if marker == FLOAT64:
            return self._read_float64()
        if marker == UINT8:
            return self._read_uint8()
        if marker == UINT16:
            return self._read_uint16()
        if marker == UINT32:
            return self._read_uint32()
        if marker == UINT64:
            return self._read_uint64()
        if marker == INT8:
            return self._read_int8()
        if marker == INT16:
            return self._read_int16()
        if marker == INT32:
            return self._read_int32()
        if marker == INT64:
            return self._read_int64()
        if marker == STR8:
            return self._decode_str(self._read_uint8())
        if marker == STR16:
            return self._decode_str(self._read_uint16())
        if marker == STR32:
            return self._decode_str(self._read_uint32())
        if marker == ARRAY16:
            return self._decode_array(self._read_uint16())
        if marker == ARRAY32:
            return self._decode_array(self._read_uint32())
        if marker == MAP16:
            return self._decode_map(self._read_uint16())
        if marker == MAP32:
            return self._decode_map(self._read_uint32())

        raise ValueError(f"Unknown marker: 0x{marker:02X}")

    def _read_bytes(self, n: int) -> bytes:
        """Read n bytes from buffer."""
        if self.pos + n > len(self.data):
            raise ValueError("Unexpected end of data")
        result = self.data[self.pos : self.pos + n]
        self.pos += n
        return result

    def _read_uint8(self) -> int:
        return self._read_bytes(1)[0]

    def _read_uint16(self) -> int:
        return struct.unpack(">H", self._read_bytes(2))[0]

    def _read_uint32(self) -> int:
        return struct.unpack(">I", self._read_bytes(4))[0]

    def _read_uint64(self) -> int:
        return struct.unpack(">Q", self._read_bytes(8))[0]

    def _read_int8(self) -> int:
        return struct.unpack(">b", self._read_bytes(1))[0]

    def _read_int16(self) -> int:
        return struct.unpack(">h", self._read_bytes(2))[0]

    def _read_int32(self) -> int:
        return struct.unpack(">i", self._read_bytes(4))[0]

    def _read_int64(self) -> int:
        return struct.unpack(">q", self._read_bytes(8))[0]

    def _read_float32(self) -> float:
        return struct.unpack(">f", self._read_bytes(4))[0]

    def _read_float64(self) -> float:
        return struct.unpack(">d", self._read_bytes(8))[0]

    def _decode_str(self, length: int) -> str:
        return self._read_bytes(length).decode("utf-8")

    def _decode_bin(self, length: int) -> bytes:
        return bytes(self._read_bytes(length))

    def _decode_array(self, length: int) -> list[Any]:
        return [self.decode() for _ in range(length)]

    def _decode_map(self, length: int) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for _ in range(length):
            key = self.decode()
            value = self.decode()
            result[key] = value
        return result


def msgpack_encode(value: Any) -> bytes:
    """Encode value to MessagePack."""
    return MsgPackEncoder().encode(value)


def msgpack_decode(data: bytes) -> Any:
    """Decode MessagePack data."""
    return MsgPackDecoder(data).decode()


def msgpack_size(value: Any) -> int:
    """Calculate encoded size."""
    return len(msgpack_encode(value))


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string."""
    return data.hex()


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string to bytes."""
    return bytes.fromhex(hex_str)


def compare_encoded(val1: Any, val2: Any) -> bool:
    """Compare two values by their encoded form."""
    return msgpack_encode(val1) == msgpack_encode(val2)


def encode_batch(values: list[Any]) -> bytes:
    """Encode multiple values as an array."""
    return msgpack_encode(values)


def decode_batch(data: bytes) -> list[Any]:
    """Decode array of values."""
    result = msgpack_decode(data)
    if not isinstance(result, list):
        raise ValueError("Expected array")
    return result


def simulate_msgpack(operations: list[str]) -> list[str]:
    """Simulate MessagePack operations."""
    results = []
    context: dict[str, Any] = {}

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "encode":
            import json

            value = json.loads(parts[1])
            encoded = msgpack_encode(value)
            context["encoded"] = encoded
            results.append(bytes_to_hex(encoded))
        elif cmd == "decode":
            data = hex_to_bytes(parts[1])
            value = msgpack_decode(data)
            import json

            results.append(json.dumps(value))
        elif cmd == "size":
            results.append(str(len(context.get("encoded", b""))))
        elif cmd == "roundtrip":
            import json

            value = json.loads(parts[1])
            encoded = msgpack_encode(value)
            decoded = msgpack_decode(encoded)
            results.append("ok" if value == decoded else "fail")

    return results


def main() -> int:
    """CLI entry point."""
    import json

    if len(sys.argv) < 2:
        print("Usage: serial_msgpack_cli.py <command> [args...]")
        print("Commands: encode, decode, size")
        return 1

    cmd = sys.argv[1]

    if cmd == "encode":
        data = json.loads(sys.stdin.read())
        encoded = msgpack_encode(data)
        sys.stdout.buffer.write(encoded)

    elif cmd == "decode":
        data = sys.stdin.buffer.read()
        decoded = msgpack_decode(data)
        print(json.dumps(decoded, indent=2))

    elif cmd == "size":
        data = json.loads(sys.stdin.read())
        encoded = msgpack_encode(data)
        print(len(encoded))

    elif cmd == "hex":
        data = json.loads(sys.stdin.read())
        encoded = msgpack_encode(data)
        print(bytes_to_hex(encoded))

    return 0


if __name__ == "__main__":
    sys.exit(main())
