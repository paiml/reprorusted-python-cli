#!/usr/bin/env python3
"""Redis Protocol CLI.

Parse and encode RESP (Redis Serialization Protocol) messages.
"""

import argparse
import sys
from dataclasses import dataclass
from enum import Enum


class RESPType(Enum):
    """RESP data types."""

    SIMPLE_STRING = "+"
    ERROR = "-"
    INTEGER = ":"
    BULK_STRING = "$"
    ARRAY = "*"
    NULL = "_"
    BOOLEAN = "#"
    DOUBLE = ","
    BIG_NUMBER = "("
    BULK_ERROR = "!"
    VERBATIM_STRING = "="
    MAP = "%"
    SET = "~"
    PUSH = ">"


@dataclass
class RESPValue:
    """RESP value container."""

    type: RESPType
    value: any


def encode_simple_string(s: str) -> bytes:
    """Encode simple string (+OK\r\n)."""
    return f"+{s}\r\n".encode()


def encode_error(s: str) -> bytes:
    """Encode error message (-ERR message\r\n)."""
    return f"-{s}\r\n".encode()


def encode_integer(n: int) -> bytes:
    """Encode integer (:<number>\r\n)."""
    return f":{n}\r\n".encode()


def encode_bulk_string(s: str | None) -> bytes:
    """Encode bulk string ($<len>\r\n<data>\r\n or $-1\r\n for null)."""
    if s is None:
        return b"$-1\r\n"

    data = s.encode("utf-8")
    return f"${len(data)}\r\n".encode() + data + b"\r\n"


def encode_array(items: list | None) -> bytes:
    """Encode array (*<count>\r\n<items> or *-1\r\n for null)."""
    if items is None:
        return b"*-1\r\n"

    result = f"*{len(items)}\r\n".encode()
    for item in items:
        result += encode_value(item)

    return result


def encode_value(value: any) -> bytes:
    """Encode any value to RESP format."""
    if value is None:
        return encode_bulk_string(None)

    if isinstance(value, bool):
        return f"#{('t' if value else 'f')}\r\n".encode()

    if isinstance(value, int):
        return encode_integer(value)

    if isinstance(value, float):
        return f",{value}\r\n".encode()

    if isinstance(value, str):
        # Use bulk string for strings with special chars
        if "\r" in value or "\n" in value:
            return encode_bulk_string(value)
        return encode_bulk_string(value)

    if isinstance(value, (list, tuple)):
        return encode_array(list(value))

    if isinstance(value, dict):
        # Encode as RESP3 map
        result = f"%{len(value)}\r\n".encode()
        for k, v in value.items():
            result += encode_value(k)
            result += encode_value(v)
        return result

    if isinstance(value, set):
        # Encode as RESP3 set
        result = f"~{len(value)}\r\n".encode()
        for item in value:
            result += encode_value(item)
        return result

    return encode_bulk_string(str(value))


def parse_simple_string(data: bytes, pos: int) -> tuple[str, int]:
    """Parse simple string."""
    end = data.find(b"\r\n", pos)
    if end == -1:
        raise ValueError("Incomplete simple string")
    return data[pos:end].decode("utf-8"), end + 2


def parse_error(data: bytes, pos: int) -> tuple[str, int]:
    """Parse error message."""
    end = data.find(b"\r\n", pos)
    if end == -1:
        raise ValueError("Incomplete error")
    return data[pos:end].decode("utf-8"), end + 2


def parse_integer(data: bytes, pos: int) -> tuple[int, int]:
    """Parse integer."""
    end = data.find(b"\r\n", pos)
    if end == -1:
        raise ValueError("Incomplete integer")
    return int(data[pos:end].decode("utf-8")), end + 2


def parse_bulk_string(data: bytes, pos: int) -> tuple[str | None, int]:
    """Parse bulk string."""
    end = data.find(b"\r\n", pos)
    if end == -1:
        raise ValueError("Incomplete bulk string length")

    length = int(data[pos:end].decode("utf-8"))

    if length == -1:
        return None, end + 2

    start = end + 2
    string_end = start + length

    if len(data) < string_end + 2:
        raise ValueError("Incomplete bulk string data")

    return data[start:string_end].decode("utf-8"), string_end + 2


def parse_array(data: bytes, pos: int) -> tuple[list | None, int]:
    """Parse array."""
    end = data.find(b"\r\n", pos)
    if end == -1:
        raise ValueError("Incomplete array length")

    count = int(data[pos:end].decode("utf-8"))

    if count == -1:
        return None, end + 2

    items = []
    current_pos = end + 2

    for _ in range(count):
        value, current_pos = parse_value(data, current_pos)
        items.append(value)

    return items, current_pos


def parse_value(data: bytes, pos: int = 0) -> tuple[any, int]:
    """Parse any RESP value."""
    if pos >= len(data):
        raise ValueError("Unexpected end of data")

    type_byte = chr(data[pos])
    pos += 1

    if type_byte == "+":
        return parse_simple_string(data, pos)

    if type_byte == "-":
        error, new_pos = parse_error(data, pos)
        return RESPValue(RESPType.ERROR, error), new_pos

    if type_byte == ":":
        return parse_integer(data, pos)

    if type_byte == "$":
        return parse_bulk_string(data, pos)

    if type_byte == "*":
        return parse_array(data, pos)

    if type_byte == "#":
        # Boolean
        end = data.find(b"\r\n", pos)
        value = data[pos:end].decode("utf-8") == "t"
        return value, end + 2

    if type_byte == ",":
        # Double
        end = data.find(b"\r\n", pos)
        value = float(data[pos:end].decode("utf-8"))
        return value, end + 2

    if type_byte == "_":
        # Null
        end = data.find(b"\r\n", pos)
        return None, end + 2

    raise ValueError(f"Unknown RESP type: {type_byte}")


def encode_command(name: str, *args: str) -> bytes:
    """Encode Redis command to RESP array format."""
    items = [name] + list(args)
    return encode_array(items)


def parse_command(data: bytes) -> tuple[str, list[str]]:
    """Parse Redis command from RESP format."""
    value, _ = parse_value(data)

    if not isinstance(value, list) or not value:
        raise ValueError("Invalid command format")

    command = value[0].upper()
    args = value[1:]

    return command, args


class RedisCommandBuilder:
    """Builder for common Redis commands."""

    @staticmethod
    def get(key: str) -> bytes:
        """GET key."""
        return encode_command("GET", key)

    @staticmethod
    def set(key: str, value: str, ex: int | None = None, px: int | None = None) -> bytes:
        """SET key value [EX seconds] [PX milliseconds]."""
        args = [key, value]
        if ex is not None:
            args.extend(["EX", str(ex)])
        elif px is not None:
            args.extend(["PX", str(px)])
        return encode_command("SET", *args)

    @staticmethod
    def del_key(*keys: str) -> bytes:
        """DEL key [key ...]."""
        return encode_command("DEL", *keys)

    @staticmethod
    def mget(*keys: str) -> bytes:
        """MGET key [key ...]."""
        return encode_command("MGET", *keys)

    @staticmethod
    def mset(**kwargs: str) -> bytes:
        """MSET key value [key value ...]."""
        args = []
        for k, v in kwargs.items():
            args.extend([k, v])
        return encode_command("MSET", *args)

    @staticmethod
    def incr(key: str) -> bytes:
        """INCR key."""
        return encode_command("INCR", key)

    @staticmethod
    def decr(key: str) -> bytes:
        """DECR key."""
        return encode_command("DECR", key)

    @staticmethod
    def lpush(key: str, *values: str) -> bytes:
        """LPUSH key value [value ...]."""
        return encode_command("LPUSH", key, *values)

    @staticmethod
    def rpush(key: str, *values: str) -> bytes:
        """RPUSH key value [value ...]."""
        return encode_command("RPUSH", key, *values)

    @staticmethod
    def lrange(key: str, start: int, stop: int) -> bytes:
        """LRANGE key start stop."""
        return encode_command("LRANGE", key, str(start), str(stop))

    @staticmethod
    def hset(key: str, field: str, value: str) -> bytes:
        """HSET key field value."""
        return encode_command("HSET", key, field, value)

    @staticmethod
    def hget(key: str, field: str) -> bytes:
        """HGET key field."""
        return encode_command("HGET", key, field)

    @staticmethod
    def hgetall(key: str) -> bytes:
        """HGETALL key."""
        return encode_command("HGETALL", key)

    @staticmethod
    def sadd(key: str, *members: str) -> bytes:
        """SADD key member [member ...]."""
        return encode_command("SADD", key, *members)

    @staticmethod
    def smembers(key: str) -> bytes:
        """SMEMBERS key."""
        return encode_command("SMEMBERS", key)

    @staticmethod
    def zadd(key: str, score: float, member: str) -> bytes:
        """ZADD key score member."""
        return encode_command("ZADD", key, str(score), member)

    @staticmethod
    def zrange(key: str, start: int, stop: int, withscores: bool = False) -> bytes:
        """ZRANGE key start stop [WITHSCORES]."""
        args = [key, str(start), str(stop)]
        if withscores:
            args.append("WITHSCORES")
        return encode_command("ZRANGE", *args)

    @staticmethod
    def ping(message: str | None = None) -> bytes:
        """PING [message]."""
        if message:
            return encode_command("PING", message)
        return encode_command("PING")

    @staticmethod
    def info(section: str | None = None) -> bytes:
        """INFO [section]."""
        if section:
            return encode_command("INFO", section)
        return encode_command("INFO")


def format_value(value: any, indent: int = 0) -> str:
    """Format RESP value for display."""
    prefix = "  " * indent

    if value is None:
        return f"{prefix}(nil)"

    if isinstance(value, RESPValue):
        if value.type == RESPType.ERROR:
            return f"{prefix}(error) {value.value}"
        return f"{prefix}{value.value}"

    if isinstance(value, bool):
        return f"{prefix}(boolean) {'true' if value else 'false'}"

    if isinstance(value, int):
        return f"{prefix}(integer) {value}"

    if isinstance(value, float):
        return f"{prefix}(double) {value}"

    if isinstance(value, str):
        return f'{prefix}"{value}"'

    if isinstance(value, list):
        if not value:
            return f"{prefix}(empty array)"
        lines = [f"{prefix}(array)"]
        for i, item in enumerate(value):
            lines.append(f"{prefix}{i + 1}) {format_value(item, indent + 1).strip()}")
        return "\n".join(lines)

    return f"{prefix}{value}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Redis protocol parser")
    parser.add_argument(
        "--mode",
        choices=["encode", "parse", "command", "builder"],
        default="command",
        help="Operation mode",
    )
    parser.add_argument("--cmd", default="PING", help="Redis command")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--hex", help="Hex-encoded RESP data to parse")

    args = parser.parse_args()

    if args.mode == "encode":
        value = args.args[0] if args.args else "OK"
        encoded = encode_simple_string(value)
        print(f"Encoded: {encoded}")
        print(f"Hex: {encoded.hex()}")

    elif args.mode == "parse":
        if args.hex:
            data = bytes.fromhex(args.hex.replace(" ", ""))
            value, _ = parse_value(data)
            print(format_value(value))

    elif args.mode == "command":
        encoded = encode_command(args.cmd, *args.args)
        print(f"Command: {args.cmd} {' '.join(args.args)}")
        print(f"RESP: {encoded}")
        print(f"Hex: {encoded.hex()}")

    elif args.mode == "builder":
        builder = RedisCommandBuilder()
        examples = [
            ("GET", builder.get("mykey")),
            ("SET", builder.set("mykey", "myvalue", ex=60)),
            ("PING", builder.ping()),
            ("LPUSH", builder.lpush("mylist", "a", "b", "c")),
            ("HSET", builder.hset("myhash", "field1", "value1")),
        ]

        for name, encoded in examples:
            print(f"\n{name}:")
            print(f"  RESP: {encoded}")
            print(f"  Hex: {encoded.hex()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
