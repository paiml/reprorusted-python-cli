"""Tests for proto_http_cli.py"""

import pytest
from proto_http_cli import (
    HttpMethod,
    HttpParseError,
    HttpParser,
    HttpRequest,
    HttpResponse,
    build_request,
    build_response,
    parse_request,
    parse_response,
    simulate_http,
)


class TestHttpMethod:
    def test_methods_exist(self):
        assert HttpMethod.GET
        assert HttpMethod.POST
        assert HttpMethod.PUT
        assert HttpMethod.DELETE
        assert HttpMethod.PATCH


class TestHttpRequest:
    def test_create(self):
        req = HttpRequest(HttpMethod.GET, "/", "HTTP/1.1")
        assert req.method == HttpMethod.GET
        assert req.path == "/"
        assert req.version == "HTTP/1.1"

    def test_headers(self):
        req = HttpRequest(
            HttpMethod.GET, "/", "HTTP/1.1", {"Content-Type": "text/html"}
        )
        assert req.header("Content-Type") == "text/html"

    def test_header_case_insensitive(self):
        req = HttpRequest(
            HttpMethod.GET, "/", "HTTP/1.1", {"Content-Type": "text/html"}
        )
        assert req.header("content-type") == "text/html"

    def test_header_missing(self):
        req = HttpRequest(HttpMethod.GET, "/", "HTTP/1.1")
        assert req.header("X-Missing") is None

    def test_content_length(self):
        req = HttpRequest(
            HttpMethod.POST, "/", "HTTP/1.1", {"Content-Length": "42"}
        )
        assert req.content_length() == 42

    def test_content_length_missing(self):
        req = HttpRequest(HttpMethod.GET, "/", "HTTP/1.1")
        assert req.content_length() == 0

    def test_content_type(self):
        req = HttpRequest(
            HttpMethod.POST, "/", "HTTP/1.1", {"Content-Type": "application/json"}
        )
        assert req.content_type() == "application/json"

    def test_keep_alive_http11(self):
        req = HttpRequest(HttpMethod.GET, "/", "HTTP/1.1")
        assert req.is_keep_alive()

    def test_keep_alive_http10(self):
        req = HttpRequest(HttpMethod.GET, "/", "HTTP/1.0")
        assert not req.is_keep_alive()

    def test_keep_alive_header(self):
        req = HttpRequest(
            HttpMethod.GET, "/", "HTTP/1.0", {"Connection": "keep-alive"}
        )
        assert req.is_keep_alive()

    def test_to_bytes(self):
        req = HttpRequest(HttpMethod.GET, "/test", "HTTP/1.1")
        data = req.to_bytes()
        assert b"GET /test HTTP/1.1" in data

    def test_to_bytes_with_body(self):
        req = HttpRequest(
            HttpMethod.POST, "/", "HTTP/1.1", {}, b"hello"
        )
        data = req.to_bytes()
        assert data.endswith(b"hello")


class TestHttpResponse:
    def test_create(self):
        resp = HttpResponse("HTTP/1.1", 200, "OK")
        assert resp.status_code == 200
        assert resp.reason == "OK"

    def test_is_success(self):
        assert HttpResponse("HTTP/1.1", 200, "OK").is_success()
        assert HttpResponse("HTTP/1.1", 201, "Created").is_success()
        assert not HttpResponse("HTTP/1.1", 404, "Not Found").is_success()

    def test_is_redirect(self):
        assert HttpResponse("HTTP/1.1", 301, "Moved").is_redirect()
        assert HttpResponse("HTTP/1.1", 302, "Found").is_redirect()
        assert not HttpResponse("HTTP/1.1", 200, "OK").is_redirect()

    def test_is_error(self):
        assert HttpResponse("HTTP/1.1", 404, "Not Found").is_error()
        assert HttpResponse("HTTP/1.1", 500, "Server Error").is_error()
        assert not HttpResponse("HTTP/1.1", 200, "OK").is_error()

    def test_to_bytes(self):
        resp = HttpResponse("HTTP/1.1", 200, "OK")
        data = resp.to_bytes()
        assert b"HTTP/1.1 200 OK" in data


class TestHttpParser:
    def test_parse_simple_request(self):
        parser = HttpParser()
        parser.feed(b"GET / HTTP/1.1\r\n\r\n")
        req = parser.parse_request()
        assert req is not None
        assert req.method == HttpMethod.GET
        assert req.path == "/"

    def test_parse_request_with_headers(self):
        parser = HttpParser()
        parser.feed(b"GET /test HTTP/1.1\r\nHost: example.com\r\n\r\n")
        req = parser.parse_request()
        assert req is not None
        assert req.header("Host") == "example.com"

    def test_parse_request_with_body(self):
        parser = HttpParser()
        data = b"POST / HTTP/1.1\r\nContent-Length: 5\r\n\r\nhello"
        parser.feed(data)
        req = parser.parse_request()
        assert req is not None
        assert req.body == b"hello"

    def test_parse_incomplete_request(self):
        parser = HttpParser()
        parser.feed(b"GET / HTTP/1.1\r\n")  # Missing final \r\n
        req = parser.parse_request()
        assert req is None

    def test_parse_simple_response(self):
        parser = HttpParser()
        parser.feed(b"HTTP/1.1 200 OK\r\n\r\n")
        resp = parser.parse_response()
        assert resp is not None
        assert resp.status_code == 200
        assert resp.reason == "OK"

    def test_parse_response_with_body(self):
        parser = HttpParser()
        data = b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello"
        parser.feed(data)
        resp = parser.parse_response()
        assert resp is not None
        assert resp.body == b"hello"

    def test_parse_all_methods(self):
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        for method in methods:
            parser = HttpParser()
            parser.feed(f"{method} / HTTP/1.1\r\n\r\n".encode())
            req = parser.parse_request()
            assert req is not None
            assert req.method.name == method

    def test_parse_invalid_method(self):
        parser = HttpParser()
        parser.feed(b"INVALID / HTTP/1.1\r\n\r\n")
        with pytest.raises(HttpParseError):
            parser.parse_request()

    def test_incremental_parsing(self):
        parser = HttpParser()
        parser.feed(b"GET / ")
        assert parser.parse_request() is None
        parser.feed(b"HTTP/1.1\r\n")
        assert parser.parse_request() is None
        parser.feed(b"\r\n")
        req = parser.parse_request()
        assert req is not None


class TestParseRequest:
    def test_simple(self):
        req = parse_request(b"GET / HTTP/1.1\r\n\r\n")
        assert req.method == HttpMethod.GET

    def test_with_headers(self):
        data = b"GET / HTTP/1.1\r\nHost: test.com\r\nAccept: */*\r\n\r\n"
        req = parse_request(data)
        assert req.header("Host") == "test.com"
        assert req.header("Accept") == "*/*"

    def test_incomplete_raises(self):
        with pytest.raises(HttpParseError):
            parse_request(b"GET / HTTP/1.1\r\n")


class TestParseResponse:
    def test_simple(self):
        resp = parse_response(b"HTTP/1.1 200 OK\r\n\r\n")
        assert resp.status_code == 200

    def test_with_body(self):
        data = b"HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\ntest"
        resp = parse_response(data)
        assert resp.body == b"test"


class TestBuildRequest:
    def test_simple(self):
        data = build_request("GET", "/")
        assert b"GET / HTTP/1.1" in data

    def test_with_body(self):
        data = build_request("POST", "/", body=b"data")
        assert b"Content-Length: 4" in data
        assert data.endswith(b"data")

    def test_with_headers(self):
        data = build_request("GET", "/", {"X-Custom": "value"})
        assert b"X-Custom: value" in data

    def test_unknown_method(self):
        with pytest.raises(ValueError):
            build_request("UNKNOWN", "/")


class TestBuildResponse:
    def test_simple(self):
        data = build_response(200, "OK")
        assert b"HTTP/1.1 200 OK" in data

    def test_with_body(self):
        data = build_response(200, "OK", body=b"hello")
        assert b"Content-Length: 5" in data
        assert data.endswith(b"hello")


class TestSimulateHttp:
    def test_parse_request(self):
        result = simulate_http(["parse_request:GET / HTTP/1.1\\r\\n\\r\\n"])
        assert result == ["GET /"]

    def test_parse_response(self):
        result = simulate_http(["parse_response:HTTP/1.1 200 OK\\r\\n\\r\\n"])
        assert result == ["200 OK"]

    def test_build_request(self):
        result = simulate_http(["build_request:GET /test"])
        assert "GET /test HTTP/1.1" in result[0]

    def test_build_response(self):
        result = simulate_http(["build_response:404 Not Found"])
        assert "404 Not Found" in result[0]


class TestStatusCodes:
    def test_informational(self):
        resp = HttpResponse("HTTP/1.1", 100, "Continue")
        assert not resp.is_success()
        assert not resp.is_redirect()
        assert not resp.is_error()

    def test_success_range(self):
        for code in [200, 201, 204, 299]:
            resp = HttpResponse("HTTP/1.1", code, "OK")
            assert resp.is_success()

    def test_redirect_range(self):
        for code in [301, 302, 303, 307, 308]:
            resp = HttpResponse("HTTP/1.1", code, "Redirect")
            assert resp.is_redirect()

    def test_client_error_range(self):
        for code in [400, 401, 403, 404, 429]:
            resp = HttpResponse("HTTP/1.1", code, "Error")
            assert resp.is_error()

    def test_server_error_range(self):
        for code in [500, 502, 503, 504]:
            resp = HttpResponse("HTTP/1.1", code, "Error")
            assert resp.is_error()
