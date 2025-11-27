"""Memcached Binary Protocol Parser CLI.

Demonstrates Memcached binary protocol encoding/decoding.
"""

import sys
from dataclasses import dataclass
from enum import IntEnum


class Opcode(IntEnum):
    """Memcached opcodes."""

    GET = 0x00
    SET = 0x01
    ADD = 0x02
    REPLACE = 0x03
    DELETE = 0x04
    INCREMENT = 0x05
    DECREMENT = 0x06
    QUIT = 0x07
    FLUSH = 0x08
    GETQ = 0x09
    NOOP = 0x0A
    VERSION = 0x0B
    GETK = 0x0C
    GETKQ = 0x0D
    APPEND = 0x0E
    PREPEND = 0x0F


class Status(IntEnum):
    """Response status codes."""

    NO_ERROR = 0x0000
    KEY_NOT_FOUND = 0x0001
    KEY_EXISTS = 0x0002
    VALUE_TOO_LARGE = 0x0003
    INVALID_ARGUMENTS = 0x0004
    ITEM_NOT_STORED = 0x0005
    NON_NUMERIC_VALUE = 0x0006
    UNKNOWN_COMMAND = 0x0081
    OUT_OF_MEMORY = 0x0082


class Magic(IntEnum):
    """Magic bytes."""

    REQUEST = 0x80
    RESPONSE = 0x81


HEADER_SIZE = 24


@dataclass
class RequestHeader:
    """Binary protocol request header."""

    opcode: Opcode
    key_length: int = 0
    extras_length: int = 0
    data_type: int = 0
    vbucket_id: int = 0
    total_body_length: int = 0
    opaque: int = 0
    cas: int = 0

    def to_bytes(self) -> bytes:
        """Serialize header to bytes."""
        return bytes(
            [
                Magic.REQUEST,
                self.opcode,
                (self.key_length >> 8) & 0xFF,
                self.key_length & 0xFF,
                self.extras_length,
                self.data_type,
                (self.vbucket_id >> 8) & 0xFF,
                self.vbucket_id & 0xFF,
                (self.total_body_length >> 24) & 0xFF,
                (self.total_body_length >> 16) & 0xFF,
                (self.total_body_length >> 8) & 0xFF,
                self.total_body_length & 0xFF,
                (self.opaque >> 24) & 0xFF,
                (self.opaque >> 16) & 0xFF,
                (self.opaque >> 8) & 0xFF,
                self.opaque & 0xFF,
                (self.cas >> 56) & 0xFF,
                (self.cas >> 48) & 0xFF,
                (self.cas >> 40) & 0xFF,
                (self.cas >> 32) & 0xFF,
                (self.cas >> 24) & 0xFF,
                (self.cas >> 16) & 0xFF,
                (self.cas >> 8) & 0xFF,
                self.cas & 0xFF,
            ]
        )


@dataclass
class ResponseHeader:
    """Binary protocol response header."""

    opcode: Opcode
    key_length: int
    extras_length: int
    data_type: int
    status: Status
    total_body_length: int
    opaque: int
    cas: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "ResponseHeader":
        """Parse header from bytes."""
        if len(data) < HEADER_SIZE:
            raise ValueError("Insufficient data for header")
        if data[0] != Magic.RESPONSE:
            raise ValueError(f"Invalid magic byte: {data[0]:#x}")

        return cls(
            opcode=Opcode(data[1]),
            key_length=(data[2] << 8) | data[3],
            extras_length=data[4],
            data_type=data[5],
            status=Status((data[6] << 8) | data[7]),
            total_body_length=((data[8] << 24) | (data[9] << 16) | (data[10] << 8) | data[11]),
            opaque=(data[12] << 24) | (data[13] << 16) | (data[14] << 8) | data[15],
            cas=int.from_bytes(data[16:24], "big"),
        )


@dataclass
class GetRequest:
    """GET request."""

    key: str
    opaque: int = 0

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        key_bytes = self.key.encode("utf-8")
        header = RequestHeader(
            opcode=Opcode.GET,
            key_length=len(key_bytes),
            total_body_length=len(key_bytes),
            opaque=self.opaque,
        )
        return header.to_bytes() + key_bytes


@dataclass
class SetRequest:
    """SET request."""

    key: str
    value: bytes
    flags: int = 0
    expiration: int = 0
    opaque: int = 0
    cas: int = 0

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        key_bytes = self.key.encode("utf-8")
        extras = bytes(
            [
                (self.flags >> 24) & 0xFF,
                (self.flags >> 16) & 0xFF,
                (self.flags >> 8) & 0xFF,
                self.flags & 0xFF,
                (self.expiration >> 24) & 0xFF,
                (self.expiration >> 16) & 0xFF,
                (self.expiration >> 8) & 0xFF,
                self.expiration & 0xFF,
            ]
        )
        header = RequestHeader(
            opcode=Opcode.SET,
            key_length=len(key_bytes),
            extras_length=8,
            total_body_length=8 + len(key_bytes) + len(self.value),
            opaque=self.opaque,
            cas=self.cas,
        )
        return header.to_bytes() + extras + key_bytes + self.value


@dataclass
class DeleteRequest:
    """DELETE request."""

    key: str
    opaque: int = 0

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        key_bytes = self.key.encode("utf-8")
        header = RequestHeader(
            opcode=Opcode.DELETE,
            key_length=len(key_bytes),
            total_body_length=len(key_bytes),
            opaque=self.opaque,
        )
        return header.to_bytes() + key_bytes


@dataclass
class IncrDecrRequest:
    """INCREMENT/DECREMENT request."""

    key: str
    delta: int
    initial: int = 0
    expiration: int = 0
    opaque: int = 0
    is_increment: bool = True

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        key_bytes = self.key.encode("utf-8")
        extras = (
            self.delta.to_bytes(8, "big")
            + self.initial.to_bytes(8, "big")
            + self.expiration.to_bytes(4, "big")
        )
        opcode = Opcode.INCREMENT if self.is_increment else Opcode.DECREMENT
        header = RequestHeader(
            opcode=opcode,
            key_length=len(key_bytes),
            extras_length=20,
            total_body_length=20 + len(key_bytes),
            opaque=self.opaque,
        )
        return header.to_bytes() + extras + key_bytes


@dataclass
class Response:
    """Generic response."""

    header: ResponseHeader
    extras: bytes
    key: bytes
    value: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "Response":
        """Parse response from bytes."""
        header = ResponseHeader.from_bytes(data)
        pos = HEADER_SIZE
        extras = data[pos : pos + header.extras_length]
        pos += header.extras_length
        key = data[pos : pos + header.key_length]
        pos += header.key_length
        value_length = header.total_body_length - header.extras_length - header.key_length
        value = data[pos : pos + value_length]
        return cls(header, extras, key, value)

    def is_success(self) -> bool:
        """Check if response indicates success."""
        return self.header.status == Status.NO_ERROR


class MemcachedClient:
    """Simple memcached protocol client (encoder/decoder)."""

    @staticmethod
    def encode_get(key: str) -> bytes:
        """Encode GET request."""
        return GetRequest(key).to_bytes()

    @staticmethod
    def encode_set(key: str, value: bytes, flags: int = 0, expiry: int = 0) -> bytes:
        """Encode SET request."""
        return SetRequest(key, value, flags, expiry).to_bytes()

    @staticmethod
    def encode_delete(key: str) -> bytes:
        """Encode DELETE request."""
        return DeleteRequest(key).to_bytes()

    @staticmethod
    def encode_incr(key: str, delta: int = 1) -> bytes:
        """Encode INCREMENT request."""
        return IncrDecrRequest(key, delta, is_increment=True).to_bytes()

    @staticmethod
    def encode_decr(key: str, delta: int = 1) -> bytes:
        """Encode DECREMENT request."""
        return IncrDecrRequest(key, delta, is_increment=False).to_bytes()

    @staticmethod
    def encode_flush() -> bytes:
        """Encode FLUSH request."""
        header = RequestHeader(opcode=Opcode.FLUSH)
        return header.to_bytes()

    @staticmethod
    def encode_noop() -> bytes:
        """Encode NOOP request."""
        header = RequestHeader(opcode=Opcode.NOOP)
        return header.to_bytes()

    @staticmethod
    def encode_version() -> bytes:
        """Encode VERSION request."""
        header = RequestHeader(opcode=Opcode.VERSION)
        return header.to_bytes()

    @staticmethod
    def encode_quit() -> bytes:
        """Encode QUIT request."""
        header = RequestHeader(opcode=Opcode.QUIT)
        return header.to_bytes()

    @staticmethod
    def decode_response(data: bytes) -> Response:
        """Decode response."""
        return Response.from_bytes(data)


def simulate_memcached(operations: list[str]) -> list[str]:
    """Simulate memcached operations."""
    results: list[str] = []
    client = MemcachedClient()

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "get":
            data = client.encode_get(parts[1])
            results.append(f"GET key={parts[1]} len={len(data)}")
        elif cmd == "set":
            key, value = parts[1].split(",", 1)
            data = client.encode_set(key, value.encode())
            results.append(f"SET key={key} len={len(data)}")
        elif cmd == "delete":
            data = client.encode_delete(parts[1])
            results.append(f"DELETE key={parts[1]} len={len(data)}")
        elif cmd == "incr":
            key = parts[1] if len(parts) > 1 else "counter"
            data = client.encode_incr(key)
            results.append(f"INCR key={key} len={len(data)}")
        elif cmd == "decr":
            key = parts[1] if len(parts) > 1 else "counter"
            data = client.encode_decr(key)
            results.append(f"DECR key={key} len={len(data)}")
        elif cmd == "flush":
            data = client.encode_flush()
            results.append(f"FLUSH len={len(data)}")
        elif cmd == "noop":
            data = client.encode_noop()
            results.append(f"NOOP len={len(data)}")
        elif cmd == "version":
            data = client.encode_version()
            results.append(f"VERSION len={len(data)}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: proto_memcached_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]
    client = MemcachedClient()

    if cmd == "get" and len(sys.argv) > 2:
        data = client.encode_get(sys.argv[2])
        print(f"GET request: {len(data)} bytes")
        print(f"Hex: {data.hex()}")
    elif cmd == "set" and len(sys.argv) > 3:
        data = client.encode_set(sys.argv[2], sys.argv[3].encode())
        print(f"SET request: {len(data)} bytes")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
