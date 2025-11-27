"""Redis RESP Protocol Parser CLI.

Demonstrates RESP (Redis Serialization Protocol) encoding/decoding.
"""

import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union


class RespType(Enum):
    """RESP data types."""

    SIMPLE_STRING = auto()  # +
    ERROR = auto()  # -
    INTEGER = auto()  # :
    BULK_STRING = auto()  # $
    ARRAY = auto()  # *
    NULL = auto()


RespValue = Union[str, int, bytes, list, None, "RespError"]


@dataclass
class RespError:
    """RESP error type."""

    message: str

    def __str__(self) -> str:
        return f"ERR {self.message}"


class RespParseError(Exception):
    """RESP parsing error."""

    pass


class RespEncoder:
    """RESP protocol encoder."""

    @staticmethod
    def encode(value: RespValue) -> bytes:
        """Encode value to RESP format."""
        if value is None:
            return b"$-1\r\n"
        elif isinstance(value, RespError):
            return f"-{value.message}\r\n".encode()
        elif isinstance(value, str):
            return f"+{value}\r\n".encode()
        elif isinstance(value, int):
            return f":{value}\r\n".encode()
        elif isinstance(value, bytes):
            return f"${len(value)}\r\n".encode() + value + b"\r\n"
        elif isinstance(value, list):
            parts = [f"*{len(value)}\r\n".encode()]
            for item in value:
                parts.append(RespEncoder.encode(item))
            return b"".join(parts)
        else:
            raise ValueError(f"Cannot encode type: {type(value)}")

    @staticmethod
    def encode_command(cmd: str, *args: str) -> bytes:
        """Encode Redis command as RESP array."""
        parts: list[RespValue] = [cmd.encode()]
        for arg in args:
            parts.append(arg.encode())
        return RespEncoder.encode(parts)


class RespDecoder:
    """RESP protocol decoder."""

    def __init__(self) -> None:
        self.buffer = b""
        self.pos = 0

    def feed(self, data: bytes) -> None:
        """Feed data to decoder."""
        self.buffer += data

    def decode(self) -> tuple[RespValue, bool]:
        """Decode next value from buffer.

        Returns (value, success) where success is False if more data needed.
        """
        if self.pos >= len(self.buffer):
            return None, False

        type_byte = chr(self.buffer[self.pos])

        if type_byte == "+":
            return self._decode_simple_string()
        elif type_byte == "-":
            return self._decode_error()
        elif type_byte == ":":
            return self._decode_integer()
        elif type_byte == "$":
            return self._decode_bulk_string()
        elif type_byte == "*":
            return self._decode_array()
        else:
            raise RespParseError(f"Unknown type byte: {type_byte}")

    def _read_line(self) -> tuple[str, bool]:
        """Read until CRLF."""
        crlf_pos = self.buffer.find(b"\r\n", self.pos)
        if crlf_pos == -1:
            return "", False
        line = self.buffer[self.pos : crlf_pos].decode("utf-8")
        self.pos = crlf_pos + 2
        return line, True

    def _decode_simple_string(self) -> tuple[str | None, bool]:
        """Decode simple string (+)."""
        self.pos += 1  # Skip +
        line, ok = self._read_line()
        if not ok:
            self.pos -= 1
            return None, False
        return line, True

    def _decode_error(self) -> tuple[RespError | None, bool]:
        """Decode error (-)."""
        self.pos += 1  # Skip -
        line, ok = self._read_line()
        if not ok:
            self.pos -= 1
            return None, False
        return RespError(line), True

    def _decode_integer(self) -> tuple[int | None, bool]:
        """Decode integer (:)."""
        self.pos += 1  # Skip :
        line, ok = self._read_line()
        if not ok:
            self.pos -= 1
            return None, False
        return int(line), True

    def _decode_bulk_string(self) -> tuple[bytes | None, bool]:
        """Decode bulk string ($)."""
        start_pos = self.pos
        self.pos += 1  # Skip $
        line, ok = self._read_line()
        if not ok:
            self.pos = start_pos
            return None, False

        length = int(line)
        if length == -1:
            return None, True  # Null bulk string

        if self.pos + length + 2 > len(self.buffer):
            self.pos = start_pos
            return None, False

        data = self.buffer[self.pos : self.pos + length]
        self.pos += length + 2  # Skip data and CRLF
        return data, True

    def _decode_array(self) -> tuple[list | None, bool]:
        """Decode array (*)."""
        start_pos = self.pos
        self.pos += 1  # Skip *
        line, ok = self._read_line()
        if not ok:
            self.pos = start_pos
            return None, False

        count = int(line)
        if count == -1:
            return None, True  # Null array

        items: list[RespValue] = []
        for _ in range(count):
            item, ok = self.decode()
            if not ok:
                self.pos = start_pos
                return None, False
            items.append(item)

        return items, True

    def consume(self) -> None:
        """Remove decoded data from buffer."""
        self.buffer = self.buffer[self.pos :]
        self.pos = 0


def encode(value: RespValue) -> bytes:
    """Encode value to RESP."""
    return RespEncoder.encode(value)


def decode(data: bytes) -> RespValue:
    """Decode RESP data."""
    decoder = RespDecoder()
    decoder.feed(data)
    value, ok = decoder.decode()
    if not ok:
        raise RespParseError("Incomplete data")
    return value


def encode_command(cmd: str, *args: str) -> bytes:
    """Encode Redis command."""
    return RespEncoder.encode_command(cmd, *args)


def parse_command(data: bytes) -> tuple[str, list[bytes]]:
    """Parse Redis command from RESP array."""
    value = decode(data)
    if not isinstance(value, list) or len(value) == 0:
        raise RespParseError("Expected non-empty array")

    cmd = value[0]
    if isinstance(cmd, bytes):
        cmd = cmd.decode("utf-8")
    elif not isinstance(cmd, str):
        raise RespParseError("Command must be string or bytes")

    args: list[bytes] = []
    for arg in value[1:]:
        if isinstance(arg, bytes):
            args.append(arg)
        elif isinstance(arg, str):
            args.append(arg.encode())
        else:
            args.append(str(arg).encode())

    return cmd.upper(), args


def simulate_resp(operations: list[str]) -> list[str]:
    """Simulate RESP operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "encode_string":
            data = encode(parts[1])
            results.append(data.decode().replace("\r\n", "\\r\\n"))
        elif cmd == "encode_int":
            data = encode(int(parts[1]))
            results.append(data.decode().replace("\r\n", "\\r\\n"))
        elif cmd == "encode_bulk":
            data = encode(parts[1].encode())
            results.append(repr(data))
        elif cmd == "encode_array":
            items = parts[1].split(",")
            data = encode(items)
            results.append(data.decode().replace("\r\n", "\\r\\n"))
        elif cmd == "encode_cmd":
            cmd_parts = parts[1].split(" ")
            data = encode_command(cmd_parts[0], *cmd_parts[1:])
            results.append(repr(data))
        elif cmd == "decode":
            data = parts[1].encode().replace(b"\\r\\n", b"\r\n")
            value = decode(data)
            results.append(repr(value))
        elif cmd == "parse_cmd":
            data = parts[1].encode().replace(b"\\r\\n", b"\r\n")
            cmd_name, args = parse_command(data)
            results.append(f"{cmd_name} {args}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: proto_redis_cli.py <command> [args]")
        print("Commands: encode, decode, command")
        return 1

    cmd = sys.argv[1]

    if cmd == "encode" and len(sys.argv) > 2:
        value = sys.argv[2]
        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            data = encode(int(value))
        else:
            data = encode(value)
        print(repr(data))
    elif cmd == "decode" and len(sys.argv) > 2:
        data = sys.argv[2].encode().replace(b"\\r\\n", b"\r\n")
        value = decode(data)
        print(repr(value))
    elif cmd == "command" and len(sys.argv) > 2:
        parts = sys.argv[2:]
        data = encode_command(parts[0], *parts[1:])
        print(repr(data))
    else:
        print("Unknown command or missing arguments")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
