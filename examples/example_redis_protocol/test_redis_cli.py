"""Tests for redis_cli.py"""

import pytest
from redis_cli import (
    RedisCommandBuilder,
    RESPType,
    RESPValue,
    encode_array,
    encode_bulk_string,
    encode_command,
    encode_error,
    encode_integer,
    encode_simple_string,
    encode_value,
    format_value,
    parse_array,
    parse_bulk_string,
    parse_command,
    parse_error,
    parse_integer,
    parse_simple_string,
    parse_value,
)


class TestEncodeSimpleString:
    def test_ok(self):
        assert encode_simple_string("OK") == b"+OK\r\n"

    def test_pong(self):
        assert encode_simple_string("PONG") == b"+PONG\r\n"

    def test_empty(self):
        assert encode_simple_string("") == b"+\r\n"


class TestEncodeError:
    def test_basic(self):
        assert encode_error("ERR unknown command") == b"-ERR unknown command\r\n"

    def test_wrong_type(self):
        assert encode_error("WRONGTYPE Operation") == b"-WRONGTYPE Operation\r\n"


class TestEncodeInteger:
    def test_positive(self):
        assert encode_integer(42) == b":42\r\n"

    def test_zero(self):
        assert encode_integer(0) == b":0\r\n"

    def test_negative(self):
        assert encode_integer(-1) == b":-1\r\n"


class TestEncodeBulkString:
    def test_simple(self):
        assert encode_bulk_string("hello") == b"$5\r\nhello\r\n"

    def test_empty(self):
        assert encode_bulk_string("") == b"$0\r\n\r\n"

    def test_null(self):
        assert encode_bulk_string(None) == b"$-1\r\n"

    def test_binary_safe(self):
        # Bulk strings can contain newlines
        result = encode_bulk_string("hello\r\nworld")
        assert b"$12\r\n" in result


class TestEncodeArray:
    def test_simple(self):
        result = encode_array(["foo", "bar"])
        assert result.startswith(b"*2\r\n")

    def test_empty(self):
        assert encode_array([]) == b"*0\r\n"

    def test_null(self):
        assert encode_array(None) == b"*-1\r\n"

    def test_mixed(self):
        result = encode_array(["hello", 42])
        assert b"*2\r\n" in result
        assert b":42\r\n" in result


class TestEncodeValue:
    def test_string(self):
        result = encode_value("hello")
        assert b"$5\r\nhello\r\n" == result

    def test_integer(self):
        assert encode_value(42) == b":42\r\n"

    def test_list(self):
        result = encode_value(["a", "b"])
        assert result.startswith(b"*2\r\n")

    def test_bool_true(self):
        assert encode_value(True) == b"#t\r\n"

    def test_bool_false(self):
        assert encode_value(False) == b"#f\r\n"

    def test_float(self):
        result = encode_value(3.14)
        assert b",3.14\r\n" == result

    def test_none(self):
        assert encode_value(None) == b"$-1\r\n"


class TestParseSimpleString:
    def test_basic(self):
        value, pos = parse_simple_string(b"OK\r\n", 0)
        assert value == "OK"
        assert pos == 4

    def test_with_offset(self):
        value, pos = parse_simple_string(b"+OK\r\n", 1)
        assert value == "OK"


class TestParseError:
    def test_basic(self):
        value, pos = parse_error(b"ERR unknown command\r\n", 0)
        assert value == "ERR unknown command"


class TestParseInteger:
    def test_positive(self):
        value, pos = parse_integer(b"42\r\n", 0)
        assert value == 42

    def test_negative(self):
        value, pos = parse_integer(b"-1\r\n", 0)
        assert value == -1


class TestParseBulkString:
    def test_simple(self):
        value, pos = parse_bulk_string(b"5\r\nhello\r\n", 0)
        assert value == "hello"
        assert pos == 10  # Position after parsing

    def test_null(self):
        value, pos = parse_bulk_string(b"-1\r\n", 0)
        assert value is None

    def test_empty(self):
        value, pos = parse_bulk_string(b"0\r\n\r\n", 0)
        assert value == ""


class TestParseArray:
    def test_simple(self):
        data = b"2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
        value, pos = parse_array(data, 0)

        assert value == ["foo", "bar"]

    def test_null(self):
        value, pos = parse_array(b"-1\r\n", 0)
        assert value is None

    def test_empty(self):
        value, pos = parse_array(b"0\r\n", 0)
        assert value == []


class TestParseValue:
    def test_simple_string(self):
        value, _ = parse_value(b"+OK\r\n")
        assert value == "OK"

    def test_error(self):
        value, _ = parse_value(b"-ERR error\r\n")
        assert isinstance(value, RESPValue)
        assert value.type == RESPType.ERROR
        assert value.value == "ERR error"

    def test_integer(self):
        value, _ = parse_value(b":42\r\n")
        assert value == 42

    def test_bulk_string(self):
        value, _ = parse_value(b"$5\r\nhello\r\n")
        assert value == "hello"

    def test_array(self):
        data = b"*2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
        value, _ = parse_value(data)
        assert value == ["foo", "bar"]

    def test_boolean_true(self):
        value, _ = parse_value(b"#t\r\n")
        assert value is True

    def test_boolean_false(self):
        value, _ = parse_value(b"#f\r\n")
        assert value is False

    def test_double(self):
        value, _ = parse_value(b",3.14\r\n")
        assert value == pytest.approx(3.14)


class TestEncodeCommand:
    def test_simple(self):
        result = encode_command("PING")
        assert result == b"*1\r\n$4\r\nPING\r\n"

    def test_with_args(self):
        result = encode_command("GET", "mykey")
        assert b"*2\r\n" in result
        assert b"$3\r\nGET\r\n" in result
        assert b"$5\r\nmykey\r\n" in result

    def test_set(self):
        result = encode_command("SET", "key", "value")
        assert b"*3\r\n" in result


class TestParseCommand:
    def test_simple(self):
        data = b"*1\r\n$4\r\nPING\r\n"
        cmd, args = parse_command(data)

        assert cmd == "PING"
        assert args == []

    def test_with_args(self):
        data = b"*2\r\n$3\r\nGET\r\n$5\r\nmykey\r\n"
        cmd, args = parse_command(data)

        assert cmd == "GET"
        assert args == ["mykey"]


class TestRedisCommandBuilder:
    def test_get(self):
        result = RedisCommandBuilder.get("mykey")
        cmd, args = parse_command(result)

        assert cmd == "GET"
        assert args == ["mykey"]

    def test_set(self):
        result = RedisCommandBuilder.set("mykey", "myvalue")
        cmd, args = parse_command(result)

        assert cmd == "SET"
        assert args == ["mykey", "myvalue"]

    def test_set_with_ex(self):
        result = RedisCommandBuilder.set("mykey", "myvalue", ex=60)
        cmd, args = parse_command(result)

        assert cmd == "SET"
        assert "EX" in args
        assert "60" in args

    def test_ping(self):
        result = RedisCommandBuilder.ping()
        cmd, args = parse_command(result)

        assert cmd == "PING"
        assert args == []

    def test_ping_with_message(self):
        result = RedisCommandBuilder.ping("hello")
        cmd, args = parse_command(result)

        assert cmd == "PING"
        assert args == ["hello"]

    def test_lpush(self):
        result = RedisCommandBuilder.lpush("mylist", "a", "b", "c")
        cmd, args = parse_command(result)

        assert cmd == "LPUSH"
        assert args[0] == "mylist"
        assert "a" in args
        assert "b" in args
        assert "c" in args

    def test_hset(self):
        result = RedisCommandBuilder.hset("myhash", "field1", "value1")
        cmd, args = parse_command(result)

        assert cmd == "HSET"
        assert args == ["myhash", "field1", "value1"]


class TestFormatValue:
    def test_nil(self):
        assert "(nil)" in format_value(None)

    def test_integer(self):
        assert "(integer) 42" in format_value(42)

    def test_string(self):
        assert '"hello"' in format_value("hello")

    def test_boolean(self):
        assert "(boolean) true" in format_value(True)
        assert "(boolean) false" in format_value(False)

    def test_array(self):
        result = format_value(["a", "b"])
        assert "(array)" in result
        assert "1)" in result
        assert "2)" in result
