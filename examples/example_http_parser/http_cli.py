#!/usr/bin/env python3
"""HTTP Parser CLI.

Parse and encode HTTP/1.1 protocol messages.
"""

import argparse
import sys
from dataclasses import dataclass, field

HTTP_STATUS_CODES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
}

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]


@dataclass
class HTTPRequest:
    """HTTP request message."""

    method: str
    path: str
    version: str = "HTTP/1.1"
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""


@dataclass
class HTTPResponse:
    """HTTP response message."""

    version: str
    status_code: int
    reason: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""


def parse_request_line(line: str) -> tuple[str, str, str]:
    """Parse HTTP request line."""
    parts = line.split(" ", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid request line: {line}")

    method, path, version = parts
    if method not in HTTP_METHODS:
        raise ValueError(f"Unknown HTTP method: {method}")

    return method, path, version


def parse_status_line(line: str) -> tuple[str, int, str]:
    """Parse HTTP status line."""
    parts = line.split(" ", 2)
    if len(parts) < 2:
        raise ValueError(f"Invalid status line: {line}")

    version = parts[0]
    status_code = int(parts[1])
    reason = parts[2] if len(parts) > 2 else HTTP_STATUS_CODES.get(status_code, "")

    return version, status_code, reason


def parse_headers(lines: list[str]) -> dict[str, str]:
    """Parse HTTP headers."""
    headers = {}

    for line in lines:
        if not line:
            break

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    return headers


def parse_request(data: bytes) -> HTTPRequest:
    """Parse HTTP request from bytes."""
    # Split headers and body
    parts = data.split(b"\r\n\r\n", 1)
    header_section = parts[0].decode("utf-8")
    body = parts[1] if len(parts) > 1 else b""

    lines = header_section.split("\r\n")
    if not lines:
        raise ValueError("Empty request")

    method, path, version = parse_request_line(lines[0])
    headers = parse_headers(lines[1:])

    return HTTPRequest(method=method, path=path, version=version, headers=headers, body=body)


def parse_response(data: bytes) -> HTTPResponse:
    """Parse HTTP response from bytes."""
    # Split headers and body
    parts = data.split(b"\r\n\r\n", 1)
    header_section = parts[0].decode("utf-8")
    body = parts[1] if len(parts) > 1 else b""

    lines = header_section.split("\r\n")
    if not lines:
        raise ValueError("Empty response")

    version, status_code, reason = parse_status_line(lines[0])
    headers = parse_headers(lines[1:])

    return HTTPResponse(
        version=version, status_code=status_code, reason=reason, headers=headers, body=body
    )


def encode_request(request: HTTPRequest) -> bytes:
    """Encode HTTP request to bytes."""
    lines = [f"{request.method} {request.path} {request.version}"]

    for key, value in request.headers.items():
        lines.append(f"{key}: {value}")

    # Add Content-Length if body present and not already set
    if request.body and "content-length" not in {k.lower() for k in request.headers}:
        lines.append(f"Content-Length: {len(request.body)}")

    header = "\r\n".join(lines) + "\r\n\r\n"
    return header.encode("utf-8") + request.body


def encode_response(response: HTTPResponse) -> bytes:
    """Encode HTTP response to bytes."""
    lines = [f"{response.version} {response.status_code} {response.reason}"]

    for key, value in response.headers.items():
        lines.append(f"{key}: {value}")

    # Add Content-Length if body present and not already set
    if response.body and "content-length" not in {k.lower() for k in response.headers}:
        lines.append(f"Content-Length: {len(response.body)}")

    header = "\r\n".join(lines) + "\r\n\r\n"
    return header.encode("utf-8") + response.body


def parse_url(url: str) -> dict[str, str]:
    """Parse URL into components."""
    result = {"scheme": "", "host": "", "port": "", "path": "/", "query": "", "fragment": ""}

    # Remove fragment
    if "#" in url:
        url, result["fragment"] = url.rsplit("#", 1)

    # Remove query string
    if "?" in url:
        url, result["query"] = url.split("?", 1)

    # Extract scheme
    if "://" in url:
        result["scheme"], url = url.split("://", 1)

    # Extract host and path
    if "/" in url:
        host_part, result["path"] = url.split("/", 1)
        result["path"] = "/" + result["path"]
    else:
        host_part = url

    # Extract port
    if ":" in host_part:
        result["host"], result["port"] = host_part.rsplit(":", 1)
    else:
        result["host"] = host_part

    return result


def parse_query_string(query: str) -> dict[str, str]:
    """Parse query string into key-value pairs."""
    if not query:
        return {}

    params = {}
    for pair in query.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[url_decode(key)] = url_decode(value)
        else:
            params[url_decode(pair)] = ""

    return params


def url_decode(s: str) -> str:
    """Decode URL-encoded string."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == "%":
            if i + 2 < len(s):
                try:
                    result.append(chr(int(s[i + 1 : i + 3], 16)))
                    i += 3
                    continue
                except ValueError:
                    pass
        elif s[i] == "+":
            result.append(" ")
            i += 1
            continue
        result.append(s[i])
        i += 1

    return "".join(result)


def url_encode(s: str) -> str:
    """URL-encode a string."""
    safe = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~"
    result = []

    for char in s:
        if char in safe:
            result.append(char)
        elif char == " ":
            result.append("+")
        else:
            for byte in char.encode("utf-8"):
                result.append(f"%{byte:02X}")

    return "".join(result)


def build_query_string(params: dict[str, str]) -> str:
    """Build query string from parameters."""
    parts = []
    for key, value in params.items():
        parts.append(f"{url_encode(key)}={url_encode(value)}")
    return "&".join(parts)


def parse_content_type(content_type: str) -> tuple[str, dict[str, str]]:
    """Parse Content-Type header into media type and parameters."""
    parts = content_type.split(";")
    media_type = parts[0].strip()

    params = {}
    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            params[key.strip()] = value.strip().strip('"')

    return media_type, params


def is_chunked(headers: dict[str, str]) -> bool:
    """Check if response uses chunked transfer encoding."""
    encoding = headers.get("transfer-encoding", "").lower()
    return "chunked" in encoding


def parse_chunked_body(data: bytes) -> bytes:
    """Parse chunked transfer encoding."""
    result = []
    pos = 0

    while pos < len(data):
        # Find chunk size line
        end_of_line = data.find(b"\r\n", pos)
        if end_of_line == -1:
            break

        size_line = data[pos:end_of_line].decode("utf-8")
        chunk_size = int(size_line.split(";")[0], 16)

        if chunk_size == 0:
            break

        pos = end_of_line + 2
        chunk_data = data[pos : pos + chunk_size]
        result.append(chunk_data)

        pos += chunk_size + 2  # Skip chunk data and trailing CRLF

    return b"".join(result)


def get_content_length(headers: dict[str, str]) -> int:
    """Get content length from headers."""
    length = headers.get("content-length", "0")
    return int(length)


def main() -> int:
    parser = argparse.ArgumentParser(description="HTTP protocol parser")
    parser.add_argument(
        "--mode",
        choices=["request", "response", "url", "query", "build"],
        default="request",
        help="Operation mode",
    )
    parser.add_argument("--method", default="GET", help="HTTP method")
    parser.add_argument("--path", default="/", help="Request path")
    parser.add_argument("--url", help="URL to parse")
    parser.add_argument("--data", help="Raw HTTP data (hex or text)")
    parser.add_argument("--headers", nargs="*", help="Headers: Key:Value")

    args = parser.parse_args()

    if args.mode == "request":
        headers = {}
        if args.headers:
            for h in args.headers:
                if ":" in h:
                    k, v = h.split(":", 1)
                    headers[k.strip()] = v.strip()

        request = HTTPRequest(
            method=args.method, path=args.path, headers=headers or {"Host": "example.com"}
        )

        encoded = encode_request(request)
        print("Encoded HTTP Request:")
        print(encoded.decode("utf-8"))

    elif args.mode == "response":
        response = HTTPResponse(
            version="HTTP/1.1",
            status_code=200,
            reason="OK",
            headers={"Content-Type": "text/html"},
            body=b"<html><body>Hello</body></html>",
        )

        encoded = encode_response(response)
        print("Encoded HTTP Response:")
        print(encoded.decode("utf-8"))

    elif args.mode == "url" and args.url:
        components = parse_url(args.url)
        print(f"URL: {args.url}")
        for key, value in components.items():
            if value:
                print(f"  {key}: {value}")

        if components["query"]:
            params = parse_query_string(components["query"])
            print("  Query Parameters:")
            for k, v in params.items():
                print(f"    {k} = {v}")

    elif args.mode == "query":
        params = {"name": "John Doe", "age": "30", "city": "New York"}
        query = build_query_string(params)
        print(f"Query string: {query}")

        parsed = parse_query_string(query)
        print("Parsed back:")
        for k, v in parsed.items():
            print(f"  {k} = {v}")

    elif args.mode == "build":
        headers = {}
        if args.headers:
            for h in args.headers:
                if ":" in h:
                    k, v = h.split(":", 1)
                    headers[k.strip()] = v.strip()

        request = HTTPRequest(method=args.method, path=args.path, headers=headers)
        encoded = encode_request(request)
        print(f"Hex: {encoded.hex()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
