#!/usr/bin/env python3
"""Byte Buffer CLI.

Growable byte buffer operations with read/write cursor.
"""

import argparse
import struct
import sys


class ByteBuffer:
    """A growable byte buffer with read/write cursor."""

    def __init__(self, capacity: int = 256) -> None:
        self._data: bytearray = bytearray(capacity)
        self._write_pos: int = 0
        self._read_pos: int = 0
        self._capacity: int = capacity
        self._length: int = 0  # High water mark of data

    @classmethod
    def from_bytes(cls, data: bytes) -> "ByteBuffer":
        """Create buffer from existing bytes."""
        buf = cls(len(data))
        buf._data[: len(data)] = data
        buf._write_pos = len(data)
        buf._length = len(data)
        return buf

    def capacity(self) -> int:
        """Get buffer capacity."""
        return self._capacity

    def length(self) -> int:
        """Get number of bytes written."""
        return self._length

    def remaining_read(self) -> int:
        """Get number of bytes available to read."""
        return self._length - self._read_pos

    def remaining_write(self) -> int:
        """Get number of bytes available to write."""
        return self._capacity - self._write_pos

    def write_pos(self) -> int:
        """Get current write position."""
        return self._write_pos

    def read_pos(self) -> int:
        """Get current read position."""
        return self._read_pos

    def seek_read(self, pos: int) -> None:
        """Set read position."""
        self._read_pos = max(0, min(pos, self._length))

    def seek_write(self, pos: int) -> None:
        """Set write position."""
        self._write_pos = max(0, min(pos, self._capacity))

    def rewind(self) -> None:
        """Reset read position to beginning."""
        self._read_pos = 0

    def clear(self) -> None:
        """Clear buffer."""
        self._write_pos = 0
        self._read_pos = 0
        self._length = 0

    def _ensure_capacity(self, additional: int) -> None:
        """Ensure buffer can hold additional bytes."""
        required = self._write_pos + additional
        if required > self._capacity:
            new_capacity = max(self._capacity * 2, required)
            new_data = bytearray(new_capacity)
            new_data[: self._write_pos] = self._data[: self._write_pos]
            self._data = new_data
            self._capacity = new_capacity

    def write_byte(self, value: int) -> None:
        """Write a single byte."""
        self._ensure_capacity(1)
        self._data[self._write_pos] = value & 0xFF
        self._write_pos += 1
        if self._write_pos > self._length:
            self._length = self._write_pos

    def read_byte(self) -> int:
        """Read a single byte."""
        if self._read_pos >= self._length:
            raise BufferError("No more bytes to read")
        value = self._data[self._read_pos]
        self._read_pos += 1
        return value

    def write_bytes(self, data: bytes) -> None:
        """Write multiple bytes."""
        self._ensure_capacity(len(data))
        self._data[self._write_pos : self._write_pos + len(data)] = data
        self._write_pos += len(data)
        if self._write_pos > self._length:
            self._length = self._write_pos

    def read_bytes(self, count: int) -> bytes:
        """Read multiple bytes."""
        available = self._length - self._read_pos
        count = min(count, available)
        data = bytes(self._data[self._read_pos : self._read_pos + count])
        self._read_pos += count
        return data

    def write_short(self, value: int, big_endian: bool = False) -> None:
        """Write a 16-bit integer."""
        fmt = ">h" if big_endian else "<h"
        self.write_bytes(struct.pack(fmt, value))

    def read_short(self, big_endian: bool = False) -> int:
        """Read a 16-bit integer."""
        fmt = ">h" if big_endian else "<h"
        data = self.read_bytes(2)
        return struct.unpack(fmt, data)[0]

    def write_int(self, value: int, big_endian: bool = False) -> None:
        """Write a 32-bit integer."""
        fmt = ">i" if big_endian else "<i"
        self.write_bytes(struct.pack(fmt, value))

    def read_int(self, big_endian: bool = False) -> int:
        """Read a 32-bit integer."""
        fmt = ">i" if big_endian else "<i"
        data = self.read_bytes(4)
        return struct.unpack(fmt, data)[0]

    def write_long(self, value: int, big_endian: bool = False) -> None:
        """Write a 64-bit integer."""
        fmt = ">q" if big_endian else "<q"
        self.write_bytes(struct.pack(fmt, value))

    def read_long(self, big_endian: bool = False) -> int:
        """Read a 64-bit integer."""
        fmt = ">q" if big_endian else "<q"
        data = self.read_bytes(8)
        return struct.unpack(fmt, data)[0]

    def write_float(self, value: float, big_endian: bool = False) -> None:
        """Write a 32-bit float."""
        fmt = ">f" if big_endian else "<f"
        self.write_bytes(struct.pack(fmt, value))

    def read_float(self, big_endian: bool = False) -> float:
        """Read a 32-bit float."""
        fmt = ">f" if big_endian else "<f"
        data = self.read_bytes(4)
        return struct.unpack(fmt, data)[0]

    def write_double(self, value: float, big_endian: bool = False) -> None:
        """Write a 64-bit double."""
        fmt = ">d" if big_endian else "<d"
        self.write_bytes(struct.pack(fmt, value))

    def read_double(self, big_endian: bool = False) -> float:
        """Read a 64-bit double."""
        fmt = ">d" if big_endian else "<d"
        data = self.read_bytes(8)
        return struct.unpack(fmt, data)[0]

    def write_string(self, value: str, encoding: str = "utf-8") -> None:
        """Write a length-prefixed string."""
        encoded = value.encode(encoding)
        self.write_int(len(encoded))
        self.write_bytes(encoded)

    def read_string(self, encoding: str = "utf-8") -> str:
        """Read a length-prefixed string."""
        length = self.read_int()
        data = self.read_bytes(length)
        return data.decode(encoding)

    def write_fixed_string(self, value: str, length: int) -> None:
        """Write a fixed-length string (null-padded)."""
        encoded = value.encode("utf-8")[:length]
        padded = encoded.ljust(length, b"\x00")
        self.write_bytes(padded)

    def read_fixed_string(self, length: int) -> str:
        """Read a fixed-length string (null-terminated)."""
        data = self.read_bytes(length)
        return data.rstrip(b"\x00").decode("utf-8")

    def to_bytes(self) -> bytes:
        """Get buffer contents as bytes."""
        return bytes(self._data[: self._length])

    def peek_byte(self) -> int:
        """Peek at next byte without advancing read position."""
        if self._read_pos >= self._length:
            raise BufferError("No more bytes to peek")
        return self._data[self._read_pos]

    def skip(self, count: int) -> None:
        """Skip bytes in read stream."""
        self._read_pos = min(self._read_pos + count, self._length)


def create_buffer(capacity: int) -> ByteBuffer:
    """Create a new buffer with given capacity."""
    return ByteBuffer(capacity)


def buffer_from_hex(hex_str: str) -> ByteBuffer:
    """Create buffer from hex string."""
    return ByteBuffer.from_bytes(bytes.fromhex(hex_str))


def write_message(buf: ByteBuffer, msg_type: int, payload: bytes) -> None:
    """Write a typed message (type + length + payload)."""
    buf.write_byte(msg_type)
    buf.write_int(len(payload))
    buf.write_bytes(payload)


def read_message(buf: ByteBuffer) -> tuple[int, bytes]:
    """Read a typed message."""
    msg_type = buf.read_byte()
    length = buf.read_int()
    payload = buf.read_bytes(length)
    return (msg_type, payload)


def write_varints(buf: ByteBuffer, values: list[int]) -> None:
    """Write variable-length encoded integers."""
    buf.write_int(len(values))
    for v in values:
        write_varint(buf, v)


def write_varint(buf: ByteBuffer, value: int) -> None:
    """Write a variable-length encoded integer."""
    while value >= 0x80:
        buf.write_byte((value & 0x7F) | 0x80)
        value >>= 7
    buf.write_byte(value & 0x7F)


def read_varint(buf: ByteBuffer) -> int:
    """Read a variable-length encoded integer."""
    result = 0
    shift = 0
    while True:
        b = buf.read_byte()
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return result


def read_varints(buf: ByteBuffer) -> list[int]:
    """Read variable-length encoded integers."""
    count = buf.read_int()
    return [read_varint(buf) for _ in range(count)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Byte buffer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # create
    create_p = subparsers.add_parser("create", help="Create and populate buffer")
    create_p.add_argument("values", type=int, nargs="+")

    # message
    msg_p = subparsers.add_parser("message", help="Create typed message")
    msg_p.add_argument("type", type=int)
    msg_p.add_argument("hex_payload")

    # varint
    var_p = subparsers.add_parser("varint", help="Encode integers as varints")
    var_p.add_argument("values", type=int, nargs="+")

    args = parser.parse_args()

    if args.command == "create":
        buf = ByteBuffer()
        for v in args.values:
            buf.write_byte(v)
        print(f"Buffer: {buf.to_bytes().hex()}")

    elif args.command == "message":
        buf = ByteBuffer()
        payload = bytes.fromhex(args.hex_payload)
        write_message(buf, args.type, payload)
        print(f"Message: {buf.to_bytes().hex()}")

    elif args.command == "varint":
        buf = ByteBuffer()
        write_varints(buf, args.values)
        print(f"Varints: {buf.to_bytes().hex()}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
