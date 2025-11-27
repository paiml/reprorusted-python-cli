"""HTTP/1.1 Protocol Parser CLI.

Demonstrates HTTP request/response parsing with headers and body handling.
"""

import sys
from dataclasses import dataclass, field
from enum import Enum, auto


class HttpMethod(Enum):
    """HTTP methods."""

    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    PATCH = auto()
    HEAD = auto()
    OPTIONS = auto()
    TRACE = auto()
    CONNECT = auto()


@dataclass
class HttpRequest:
    """HTTP request."""

    method: HttpMethod
    path: str
    version: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    def header(self, name: str) -> str | None:
        """Get header value (case-insensitive)."""
        name_lower = name.lower()
        for k, v in self.headers.items():
            if k.lower() == name_lower:
                return v
        return None

    def content_length(self) -> int:
        """Get content length."""
        cl = self.header("Content-Length")
        return int(cl) if cl else 0

    def content_type(self) -> str | None:
        """Get content type."""
        return self.header("Content-Type")

    def is_keep_alive(self) -> bool:
        """Check if connection should be kept alive."""
        conn = self.header("Connection")
        if conn:
            return conn.lower() == "keep-alive"
        return self.version == "HTTP/1.1"

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        lines = [f"{self.method.name} {self.path} {self.version}"]
        for k, v in self.headers.items():
            lines.append(f"{k}: {v}")
        lines.append("")
        header_bytes = "\r\n".join(lines).encode() + b"\r\n"
        return header_bytes + self.body


@dataclass
class HttpResponse:
    """HTTP response."""

    version: str
    status_code: int
    reason: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    def header(self, name: str) -> str | None:
        """Get header value (case-insensitive)."""
        name_lower = name.lower()
        for k, v in self.headers.items():
            if k.lower() == name_lower:
                return v
        return None

    def content_length(self) -> int:
        """Get content length."""
        cl = self.header("Content-Length")
        return int(cl) if cl else 0

    def is_success(self) -> bool:
        """Check if response is successful (2xx)."""
        return 200 <= self.status_code < 300

    def is_redirect(self) -> bool:
        """Check if response is redirect (3xx)."""
        return 300 <= self.status_code < 400

    def is_error(self) -> bool:
        """Check if response is error (4xx or 5xx)."""
        return self.status_code >= 400

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        lines = [f"{self.version} {self.status_code} {self.reason}"]
        for k, v in self.headers.items():
            lines.append(f"{k}: {v}")
        lines.append("")
        header_bytes = "\r\n".join(lines).encode() + b"\r\n"
        return header_bytes + self.body


class HttpParseError(Exception):
    """HTTP parsing error."""

    pass


class HttpParser:
    """HTTP protocol parser."""

    METHODS = {
        "GET": HttpMethod.GET,
        "POST": HttpMethod.POST,
        "PUT": HttpMethod.PUT,
        "DELETE": HttpMethod.DELETE,
        "PATCH": HttpMethod.PATCH,
        "HEAD": HttpMethod.HEAD,
        "OPTIONS": HttpMethod.OPTIONS,
        "TRACE": HttpMethod.TRACE,
        "CONNECT": HttpMethod.CONNECT,
    }

    def __init__(self) -> None:
        self.buffer = b""

    def feed(self, data: bytes) -> None:
        """Feed data to parser."""
        self.buffer += data

    def parse_request(self) -> HttpRequest | None:
        """Parse HTTP request from buffer."""
        # Find end of headers
        header_end = self.buffer.find(b"\r\n\r\n")
        if header_end == -1:
            return None

        header_bytes = self.buffer[:header_end]
        lines = header_bytes.decode("utf-8").split("\r\n")

        if not lines:
            raise HttpParseError("Empty request")

        # Parse request line
        request_line = lines[0].split(" ")
        if len(request_line) < 3:
            raise HttpParseError("Invalid request line")

        method_str, path, version = request_line[0], request_line[1], request_line[2]
        if method_str not in self.METHODS:
            raise HttpParseError(f"Unknown method: {method_str}")

        method = self.METHODS[method_str]

        # Parse headers
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        # Create request
        request = HttpRequest(method, path, version, headers)

        # Check for body
        body_start = header_end + 4
        content_length = request.content_length()

        if content_length > 0:
            if len(self.buffer) < body_start + content_length:
                return None  # Need more data
            request.body = self.buffer[body_start : body_start + content_length]
            self.buffer = self.buffer[body_start + content_length :]
        else:
            self.buffer = self.buffer[body_start:]

        return request

    def parse_response(self) -> HttpResponse | None:
        """Parse HTTP response from buffer."""
        # Find end of headers
        header_end = self.buffer.find(b"\r\n\r\n")
        if header_end == -1:
            return None

        header_bytes = self.buffer[:header_end]
        lines = header_bytes.decode("utf-8").split("\r\n")

        if not lines:
            raise HttpParseError("Empty response")

        # Parse status line
        status_line = lines[0].split(" ", 2)
        if len(status_line) < 3:
            raise HttpParseError("Invalid status line")

        version = status_line[0]
        status_code = int(status_line[1])
        reason = status_line[2]

        # Parse headers
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        # Create response
        response = HttpResponse(version, status_code, reason, headers)

        # Check for body
        body_start = header_end + 4
        content_length = response.content_length()

        if content_length > 0:
            if len(self.buffer) < body_start + content_length:
                return None  # Need more data
            response.body = self.buffer[body_start : body_start + content_length]
            self.buffer = self.buffer[body_start + content_length :]
        else:
            self.buffer = self.buffer[body_start:]

        return response


def parse_request(data: bytes) -> HttpRequest:
    """Parse HTTP request."""
    parser = HttpParser()
    parser.feed(data)
    request = parser.parse_request()
    if request is None:
        raise HttpParseError("Incomplete request")
    return request


def parse_response(data: bytes) -> HttpResponse:
    """Parse HTTP response."""
    parser = HttpParser()
    parser.feed(data)
    response = parser.parse_response()
    if response is None:
        raise HttpParseError("Incomplete response")
    return response


def build_request(
    method: str,
    path: str,
    headers: dict[str, str] | None = None,
    body: bytes = b"",
) -> bytes:
    """Build HTTP request."""
    method_enum = HttpParser.METHODS.get(method.upper())
    if method_enum is None:
        raise ValueError(f"Unknown method: {method}")

    hdrs = headers or {}
    if body and "Content-Length" not in hdrs:
        hdrs["Content-Length"] = str(len(body))

    request = HttpRequest(method_enum, path, "HTTP/1.1", hdrs, body)
    return request.to_bytes()


def build_response(
    status_code: int,
    reason: str,
    headers: dict[str, str] | None = None,
    body: bytes = b"",
) -> bytes:
    """Build HTTP response."""
    hdrs = headers or {}
    if body and "Content-Length" not in hdrs:
        hdrs["Content-Length"] = str(len(body))

    response = HttpResponse("HTTP/1.1", status_code, reason, hdrs, body)
    return response.to_bytes()


def simulate_http(operations: list[str]) -> list[str]:
    """Simulate HTTP operations."""
    results: list[str] = []
    parser = HttpParser()

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "parse_request":
            try:
                data = parts[1].encode().replace(b"\\r\\n", b"\r\n")
                parser.feed(data)
                req = parser.parse_request()
                if req:
                    results.append(f"{req.method.name} {req.path}")
                else:
                    results.append("incomplete")
            except HttpParseError as e:
                results.append(f"error:{e}")
        elif cmd == "parse_response":
            try:
                data = parts[1].encode().replace(b"\\r\\n", b"\r\n")
                parser.feed(data)
                resp = parser.parse_response()
                if resp:
                    results.append(f"{resp.status_code} {resp.reason}")
                else:
                    results.append("incomplete")
            except HttpParseError as e:
                results.append(f"error:{e}")
        elif cmd == "build_request":
            method, path = parts[1].split(" ", 1)
            data = build_request(method, path)
            results.append(data.decode().replace("\r\n", "\\r\\n"))
        elif cmd == "build_response":
            code, reason = parts[1].split(" ", 1)
            data = build_response(int(code), reason)
            results.append(data.decode().replace("\r\n", "\\r\\n"))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: proto_http_cli.py <command> [args]")
        print("Commands: parse-request, parse-response, build-request, build-response")
        return 1

    cmd = sys.argv[1]

    if cmd == "parse-request" and len(sys.argv) > 2:
        data = sys.argv[2].encode().replace(b"\\r\\n", b"\r\n")
        try:
            req = parse_request(data)
            print(f"Method: {req.method.name}")
            print(f"Path: {req.path}")
            print(f"Version: {req.version}")
            for k, v in req.headers.items():
                print(f"Header: {k}: {v}")
        except HttpParseError as e:
            print(f"Error: {e}")
            return 1
    elif cmd == "parse-response" and len(sys.argv) > 2:
        data = sys.argv[2].encode().replace(b"\\r\\n", b"\r\n")
        try:
            resp = parse_response(data)
            print(f"Status: {resp.status_code} {resp.reason}")
            for k, v in resp.headers.items():
                print(f"Header: {k}: {v}")
        except HttpParseError as e:
            print(f"Error: {e}")
            return 1
    else:
        print("Unknown command or missing arguments")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
