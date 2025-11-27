"""Tests for proto_redis_cli.py"""

import pytest
from proto_redis_cli import (
    RespDecoder,
    RespEncoder,
    RespError,
    RespParseError,
    RespType,
    decode,
    encode,
    encode_command,
    parse_command,
    simulate_resp,
)


class TestRespType:
    def test_types_exist(self):
        assert RespType.SIMPLE_STRING
        assert RespType.ERROR
        assert RespType.INTEGER
        assert RespType.BULK_STRING
        assert RespType.ARRAY
        assert RespType.NULL


class TestRespError:
    def test_create(self):
        err = RespError("something went wrong")
        assert err.message == "something went wrong"

    def test_str(self):
        err = RespError("oops")
        assert str(err) == "ERR oops"


class TestRespEncoder:
    def test_encode_simple_string(self):
        assert RespEncoder.encode("OK") == b"+OK\r\n"
        assert RespEncoder.encode("hello") == b"+hello\r\n"

    def test_encode_error(self):
        err = RespError("ERR unknown command")
        assert RespEncoder.encode(err) == b"-ERR unknown command\r\n"

    def test_encode_integer(self):
        assert RespEncoder.encode(0) == b":0\r\n"
        assert RespEncoder.encode(42) == b":42\r\n"
        assert RespEncoder.encode(-1) == b":-1\r\n"

    def test_encode_bulk_string(self):
        assert RespEncoder.encode(b"hello") == b"$5\r\nhello\r\n"
        assert RespEncoder.encode(b"") == b"$0\r\n\r\n"

    def test_encode_null(self):
        assert RespEncoder.encode(None) == b"$-1\r\n"

    def test_encode_array(self):
        assert RespEncoder.encode([]) == b"*0\r\n"
        assert RespEncoder.encode(["OK"]) == b"*1\r\n+OK\r\n"

    def test_encode_nested_array(self):
        data = RespEncoder.encode([[1, 2], [3, 4]])
        assert data == b"*2\r\n*2\r\n:1\r\n:2\r\n*2\r\n:3\r\n:4\r\n"

    def test_encode_mixed_array(self):
        data = RespEncoder.encode(["OK", 42, b"data"])
        assert b"*3\r\n" in data
        assert b"+OK\r\n" in data
        assert b":42\r\n" in data

    def test_encode_command(self):
        data = RespEncoder.encode_command("GET", "key")
        assert data == b"*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n"

    def test_encode_command_multiple_args(self):
        data = RespEncoder.encode_command("SET", "key", "value")
        assert b"*3\r\n" in data

    def test_encode_invalid_type(self):
        with pytest.raises(ValueError):
            RespEncoder.encode({"dict": "value"})


class TestRespDecoder:
    def test_decode_simple_string(self):
        decoder = RespDecoder()
        decoder.feed(b"+OK\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value == "OK"

    def test_decode_error(self):
        decoder = RespDecoder()
        decoder.feed(b"-ERR unknown\r\n")
        value, ok = decoder.decode()
        assert ok
        assert isinstance(value, RespError)
        assert value.message == "ERR unknown"

    def test_decode_integer(self):
        decoder = RespDecoder()
        decoder.feed(b":42\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value == 42

    def test_decode_negative_integer(self):
        decoder = RespDecoder()
        decoder.feed(b":-1\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value == -1

    def test_decode_bulk_string(self):
        decoder = RespDecoder()
        decoder.feed(b"$5\r\nhello\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value == b"hello"

    def test_decode_empty_bulk_string(self):
        decoder = RespDecoder()
        decoder.feed(b"$0\r\n\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value == b""

    def test_decode_null_bulk_string(self):
        decoder = RespDecoder()
        decoder.feed(b"$-1\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value is None

    def test_decode_array(self):
        decoder = RespDecoder()
        decoder.feed(b"*2\r\n+OK\r\n:1\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value == ["OK", 1]

    def test_decode_empty_array(self):
        decoder = RespDecoder()
        decoder.feed(b"*0\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value == []

    def test_decode_null_array(self):
        decoder = RespDecoder()
        decoder.feed(b"*-1\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value is None

    def test_decode_nested_array(self):
        decoder = RespDecoder()
        decoder.feed(b"*2\r\n*1\r\n:1\r\n*1\r\n:2\r\n")
        value, ok = decoder.decode()
        assert ok
        assert value == [[1], [2]]

    def test_decode_incomplete_simple_string(self):
        decoder = RespDecoder()
        decoder.feed(b"+OK")  # Missing CRLF
        value, ok = decoder.decode()
        assert not ok

    def test_decode_incomplete_bulk_string(self):
        decoder = RespDecoder()
        decoder.feed(b"$5\r\nhel")  # Missing data
        value, ok = decoder.decode()
        assert not ok

    def test_decode_incomplete_array(self):
        decoder = RespDecoder()
        decoder.feed(b"*2\r\n+OK\r\n")  # Missing second element
        value, ok = decoder.decode()
        assert not ok

    def test_decode_unknown_type(self):
        decoder = RespDecoder()
        decoder.feed(b"?unknown\r\n")
        with pytest.raises(RespParseError):
            decoder.decode()

    def test_incremental_feed(self):
        decoder = RespDecoder()
        decoder.feed(b"+")
        value, ok = decoder.decode()
        assert not ok
        decoder.feed(b"OK")
        decoder.pos = 0
        value, ok = decoder.decode()
        assert not ok
        decoder.feed(b"\r\n")
        decoder.pos = 0
        value, ok = decoder.decode()
        assert ok
        assert value == "OK"

    def test_consume(self):
        decoder = RespDecoder()
        decoder.feed(b"+OK\r\n+NEXT\r\n")
        value, ok = decoder.decode()
        assert ok
        decoder.consume()
        value, ok = decoder.decode()
        assert ok
        assert value == "NEXT"


class TestEncode:
    def test_string(self):
        assert encode("hello") == b"+hello\r\n"

    def test_int(self):
        assert encode(123) == b":123\r\n"

    def test_bytes(self):
        assert encode(b"data") == b"$4\r\ndata\r\n"

    def test_none(self):
        assert encode(None) == b"$-1\r\n"

    def test_list(self):
        assert encode([1, 2]) == b"*2\r\n:1\r\n:2\r\n"


class TestDecode:
    def test_string(self):
        assert decode(b"+hello\r\n") == "hello"

    def test_int(self):
        assert decode(b":42\r\n") == 42

    def test_bulk(self):
        assert decode(b"$3\r\nfoo\r\n") == b"foo"

    def test_incomplete_raises(self):
        with pytest.raises(RespParseError):
            decode(b"+incomplete")


class TestEncodeCommand:
    def test_get(self):
        data = encode_command("GET", "mykey")
        assert b"GET" in data
        assert b"mykey" in data

    def test_set(self):
        data = encode_command("SET", "key", "value")
        assert b"*3\r\n" in data

    def test_lpush_multiple(self):
        data = encode_command("LPUSH", "list", "a", "b", "c")
        assert b"*5\r\n" in data


class TestParseCommand:
    def test_get(self):
        data = encode_command("GET", "mykey")
        cmd, args = parse_command(data)
        assert cmd == "GET"
        assert args == [b"mykey"]

    def test_set(self):
        data = encode_command("set", "key", "value")
        cmd, args = parse_command(data)
        assert cmd == "SET"  # Uppercased
        assert args == [b"key", b"value"]

    def test_ping(self):
        data = encode_command("PING")
        cmd, args = parse_command(data)
        assert cmd == "PING"
        assert args == []

    def test_invalid_empty_array(self):
        with pytest.raises(RespParseError):
            parse_command(b"*0\r\n")


class TestSimulateResp:
    def test_encode_string(self):
        result = simulate_resp(["encode_string:OK"])
        assert result == ["+OK\\r\\n"]

    def test_encode_int(self):
        result = simulate_resp(["encode_int:42"])
        assert result == [":42\\r\\n"]

    def test_decode(self):
        result = simulate_resp(["decode:+hello\\r\\n"])
        assert result == ["'hello'"]

    def test_encode_cmd(self):
        result = simulate_resp(["encode_cmd:GET key"])
        assert "GET" in result[0]


class TestRealWorldCommands:
    def test_info(self):
        cmd = encode_command("INFO")
        parsed_cmd, args = parse_command(cmd)
        assert parsed_cmd == "INFO"

    def test_hset(self):
        cmd = encode_command("HSET", "hash", "field", "value")
        parsed_cmd, args = parse_command(cmd)
        assert parsed_cmd == "HSET"
        assert len(args) == 3

    def test_zadd(self):
        cmd = encode_command("ZADD", "zset", "1", "member")
        parsed_cmd, args = parse_command(cmd)
        assert parsed_cmd == "ZADD"

    def test_multi(self):
        # Test MULTI/EXEC transaction commands
        multi = encode_command("MULTI")
        exec_cmd = encode_command("EXEC")
        assert b"MULTI" in multi
        assert b"EXEC" in exec_cmd
