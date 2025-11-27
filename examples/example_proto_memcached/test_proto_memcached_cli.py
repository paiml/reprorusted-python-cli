"""Tests for proto_memcached_cli.py"""

import pytest
from proto_memcached_cli import (
    HEADER_SIZE,
    DeleteRequest,
    GetRequest,
    IncrDecrRequest,
    Magic,
    MemcachedClient,
    Opcode,
    RequestHeader,
    Response,
    ResponseHeader,
    SetRequest,
    Status,
    simulate_memcached,
)


class TestOpcode:
    def test_values(self):
        assert Opcode.GET == 0x00
        assert Opcode.SET == 0x01
        assert Opcode.DELETE == 0x04
        assert Opcode.INCREMENT == 0x05
        assert Opcode.DECREMENT == 0x06


class TestStatus:
    def test_values(self):
        assert Status.NO_ERROR == 0x0000
        assert Status.KEY_NOT_FOUND == 0x0001
        assert Status.KEY_EXISTS == 0x0002


class TestMagic:
    def test_values(self):
        assert Magic.REQUEST == 0x80
        assert Magic.RESPONSE == 0x81


class TestRequestHeader:
    def test_create(self):
        header = RequestHeader(opcode=Opcode.GET)
        assert header.opcode == Opcode.GET
        assert header.key_length == 0

    def test_to_bytes_length(self):
        header = RequestHeader(opcode=Opcode.GET)
        data = header.to_bytes()
        assert len(data) == HEADER_SIZE

    def test_to_bytes_magic(self):
        header = RequestHeader(opcode=Opcode.GET)
        data = header.to_bytes()
        assert data[0] == Magic.REQUEST

    def test_to_bytes_opcode(self):
        header = RequestHeader(opcode=Opcode.SET)
        data = header.to_bytes()
        assert data[1] == Opcode.SET

    def test_to_bytes_key_length(self):
        header = RequestHeader(opcode=Opcode.GET, key_length=256)
        data = header.to_bytes()
        assert data[2] == 1  # High byte
        assert data[3] == 0  # Low byte

    def test_to_bytes_extras_length(self):
        header = RequestHeader(opcode=Opcode.SET, extras_length=8)
        data = header.to_bytes()
        assert data[4] == 8

    def test_to_bytes_body_length(self):
        header = RequestHeader(opcode=Opcode.SET, total_body_length=100)
        data = header.to_bytes()
        assert data[11] == 100


class TestResponseHeader:
    def test_from_bytes(self):
        data = bytes([
            Magic.RESPONSE,  # Magic
            Opcode.GET,  # Opcode
            0, 0,  # Key length
            0,  # Extras length
            0,  # Data type
            0, 0,  # Status
            0, 0, 0, 5,  # Body length
            0, 0, 0, 1,  # Opaque
            0, 0, 0, 0, 0, 0, 0, 0,  # CAS
        ])
        header = ResponseHeader.from_bytes(data)
        assert header.opcode == Opcode.GET
        assert header.status == Status.NO_ERROR
        assert header.total_body_length == 5
        assert header.opaque == 1

    def test_from_bytes_with_status(self):
        data = bytes([
            Magic.RESPONSE,
            Opcode.GET,
            0, 0,
            0,
            0,
            0, 1,  # KEY_NOT_FOUND
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ])
        header = ResponseHeader.from_bytes(data)
        assert header.status == Status.KEY_NOT_FOUND

    def test_from_bytes_invalid_magic(self):
        data = bytes([0x00] + [0] * 23)
        with pytest.raises(ValueError):
            ResponseHeader.from_bytes(data)

    def test_from_bytes_too_short(self):
        with pytest.raises(ValueError):
            ResponseHeader.from_bytes(b"\x81\x00")


class TestGetRequest:
    def test_create(self):
        req = GetRequest("mykey")
        assert req.key == "mykey"

    def test_to_bytes(self):
        req = GetRequest("test")
        data = req.to_bytes()
        assert len(data) == HEADER_SIZE + 4
        assert data[0] == Magic.REQUEST
        assert data[1] == Opcode.GET
        assert b"test" in data

    def test_key_length_in_header(self):
        req = GetRequest("hello")
        data = req.to_bytes()
        # Key length is bytes 2-3 (big endian)
        assert data[2] == 0
        assert data[3] == 5


class TestSetRequest:
    def test_create(self):
        req = SetRequest("key", b"value")
        assert req.key == "key"
        assert req.value == b"value"

    def test_to_bytes(self):
        req = SetRequest("k", b"v")
        data = req.to_bytes()
        assert data[0] == Magic.REQUEST
        assert data[1] == Opcode.SET
        assert data[4] == 8  # Extras length

    def test_flags_and_expiry(self):
        req = SetRequest("k", b"v", flags=0x0001, expiration=3600)
        data = req.to_bytes()
        # Flags are in extras at offset 24
        assert data[27] == 1  # Low byte of flags

    def test_body_contains_key_and_value(self):
        req = SetRequest("mykey", b"myvalue")
        data = req.to_bytes()
        assert b"mykey" in data
        assert b"myvalue" in data


class TestDeleteRequest:
    def test_create(self):
        req = DeleteRequest("key")
        assert req.key == "key"

    def test_to_bytes(self):
        req = DeleteRequest("delme")
        data = req.to_bytes()
        assert data[1] == Opcode.DELETE
        assert b"delme" in data


class TestIncrDecrRequest:
    def test_increment(self):
        req = IncrDecrRequest("counter", delta=5, is_increment=True)
        data = req.to_bytes()
        assert data[1] == Opcode.INCREMENT

    def test_decrement(self):
        req = IncrDecrRequest("counter", delta=1, is_increment=False)
        data = req.to_bytes()
        assert data[1] == Opcode.DECREMENT

    def test_extras_length(self):
        req = IncrDecrRequest("c", delta=1)
        data = req.to_bytes()
        assert data[4] == 20  # Extras length


class TestResponse:
    def test_from_bytes(self):
        # Build a simple response
        header_bytes = bytes([
            Magic.RESPONSE,
            Opcode.GET,
            0, 0,  # Key length
            0,  # Extras length
            0,  # Data type
            0, 0,  # Status OK
            0, 0, 0, 5,  # Body length = 5
            0, 0, 0, 0,  # Opaque
            0, 0, 0, 0, 0, 0, 0, 0,  # CAS
        ])
        data = header_bytes + b"hello"
        resp = Response.from_bytes(data)
        assert resp.value == b"hello"
        assert resp.is_success()

    def test_is_success_true(self):
        header = ResponseHeader(
            Opcode.GET, 0, 0, 0, Status.NO_ERROR, 0, 0, 0
        )
        resp = Response(header, b"", b"", b"")
        assert resp.is_success()

    def test_is_success_false(self):
        header = ResponseHeader(
            Opcode.GET, 0, 0, 0, Status.KEY_NOT_FOUND, 0, 0, 0
        )
        resp = Response(header, b"", b"", b"")
        assert not resp.is_success()


class TestMemcachedClient:
    def test_encode_get(self):
        data = MemcachedClient.encode_get("key")
        assert data[1] == Opcode.GET
        assert b"key" in data

    def test_encode_set(self):
        data = MemcachedClient.encode_set("key", b"value")
        assert data[1] == Opcode.SET
        assert b"key" in data
        assert b"value" in data

    def test_encode_set_with_flags(self):
        data = MemcachedClient.encode_set("k", b"v", flags=1)
        assert data[1] == Opcode.SET

    def test_encode_delete(self):
        data = MemcachedClient.encode_delete("key")
        assert data[1] == Opcode.DELETE

    def test_encode_incr(self):
        data = MemcachedClient.encode_incr("counter", 10)
        assert data[1] == Opcode.INCREMENT

    def test_encode_decr(self):
        data = MemcachedClient.encode_decr("counter", 5)
        assert data[1] == Opcode.DECREMENT

    def test_encode_flush(self):
        data = MemcachedClient.encode_flush()
        assert data[1] == Opcode.FLUSH

    def test_encode_noop(self):
        data = MemcachedClient.encode_noop()
        assert data[1] == Opcode.NOOP

    def test_encode_version(self):
        data = MemcachedClient.encode_version()
        assert data[1] == Opcode.VERSION

    def test_encode_quit(self):
        data = MemcachedClient.encode_quit()
        assert data[1] == Opcode.QUIT


class TestSimulateMemcached:
    def test_get(self):
        result = simulate_memcached(["get:mykey"])
        assert "GET" in result[0]
        assert "mykey" in result[0]

    def test_set(self):
        result = simulate_memcached(["set:key,value"])
        assert "SET" in result[0]

    def test_delete(self):
        result = simulate_memcached(["delete:key"])
        assert "DELETE" in result[0]

    def test_incr(self):
        result = simulate_memcached(["incr:counter"])
        assert "INCR" in result[0]

    def test_decr(self):
        result = simulate_memcached(["decr:counter"])
        assert "DECR" in result[0]

    def test_flush(self):
        result = simulate_memcached(["flush:"])
        assert "FLUSH" in result[0]

    def test_noop(self):
        result = simulate_memcached(["noop:"])
        assert "NOOP" in result[0]

    def test_version(self):
        result = simulate_memcached(["version:"])
        assert "VERSION" in result[0]


class TestHeaderSize:
    def test_constant(self):
        assert HEADER_SIZE == 24

    def test_request_header_size(self):
        header = RequestHeader(Opcode.GET)
        assert len(header.to_bytes()) == HEADER_SIZE
