#!/usr/bin/env python3
"""URL percent-encoding CLI.

Encode and decode URL-safe strings.
"""

import argparse
import sys

# Characters that are safe (unreserved) in URLs
SAFE_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")

# Additional characters safe in path component
PATH_SAFE = SAFE_CHARS | set("!$&'()*+,;=:@/")

# Characters safe in query string
QUERY_SAFE = SAFE_CHARS | set("!$&'()*+,;=:@/?")


def percent_encode_byte(byte: int) -> str:
    """Encode a single byte as percent-encoded."""
    return f"%{byte:02X}"


def percent_encode(
    text: str,
    safe: set[str] | None = None,
    space_as_plus: bool = False,
) -> str:
    """Percent-encode a string.

    Args:
        text: String to encode
        safe: Set of safe characters (default: unreserved chars)
        space_as_plus: Encode spaces as + (for form data)
    """
    if safe is None:
        safe = SAFE_CHARS

    result = []
    for char in text:
        if char == " " and space_as_plus:
            result.append("+")
        elif char in safe:
            result.append(char)
        else:
            for byte in char.encode("utf-8"):
                result.append(percent_encode_byte(byte))

    return "".join(result)


def percent_decode(text: str, plus_as_space: bool = False) -> str:
    """Decode percent-encoded string."""
    result = []
    i = 0

    while i < len(text):
        char = text[i]

        if char == "+" and plus_as_space:
            result.append(" ")
            i += 1
        elif char == "%" and i + 2 < len(text):
            try:
                byte = int(text[i + 1 : i + 3], 16)
                result.append(chr(byte))
                i += 3
            except ValueError:
                result.append(char)
                i += 1
        else:
            result.append(char)
            i += 1

    # Handle UTF-8 decoding
    try:
        return "".join(result).encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return "".join(result)


def encode_query_param(key: str, value: str) -> str:
    """Encode a single query parameter."""
    encoded_key = percent_encode(key, space_as_plus=True)
    encoded_value = percent_encode(value, space_as_plus=True)
    return f"{encoded_key}={encoded_value}"


def encode_query_string(params: list[tuple[str, str]]) -> str:
    """Encode query parameters into query string."""
    return "&".join(encode_query_param(k, v) for k, v in params)


def parse_query_string(query: str) -> list[tuple[str, str]]:
    """Parse query string into list of (key, value) pairs."""
    result = []

    for part in query.split("&"):
        if not part:
            continue
        if "=" in part:
            key, value = part.split("=", 1)
        else:
            key, value = part, ""

        decoded_key = percent_decode(key, plus_as_space=True)
        decoded_value = percent_decode(value, plus_as_space=True)
        result.append((decoded_key, decoded_value))

    return result


def encode_path(path: str) -> str:
    """Encode URL path, preserving structure."""
    parts = path.split("/")
    return "/".join(percent_encode(p, safe=SAFE_CHARS) for p in parts)


def decode_path(path: str) -> str:
    """Decode URL path."""
    return percent_decode(path)


def is_encoded(text: str) -> bool:
    """Check if text contains percent-encoding."""
    i = 0
    while i < len(text):
        if text[i] == "%":
            if i + 2 < len(text):
                try:
                    int(text[i + 1 : i + 3], 16)
                    return True
                except ValueError:
                    pass
        i += 1
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="URL percent-encoding tool")
    parser.add_argument("text", nargs="?", help="Text to encode/decode")
    parser.add_argument("-d", "--decode", action="store_true", help="Decode instead of encode")
    parser.add_argument("--path", action="store_true", help="Encode/decode as URL path")
    parser.add_argument("--query", action="store_true", help="Encode/decode as query string")
    parser.add_argument(
        "--param", metavar="KEY=VALUE", action="append", help="Encode query parameter (can repeat)"
    )
    parser.add_argument("--plus", action="store_true", help="Use + for spaces (form encoding)")
    parser.add_argument("--auto", action="store_true", help="Auto-detect encode/decode")

    args = parser.parse_args()

    # Build query from params
    if args.param:
        params = []
        for p in args.param:
            if "=" in p:
                key, value = p.split("=", 1)
            else:
                key, value = p, ""
            params.append((key, value))
        print(encode_query_string(params))
        return 0

    # Read text
    if args.text is None:
        text = sys.stdin.read().rstrip("\n")
    else:
        text = args.text

    # Auto-detect
    if args.auto:
        args.decode = is_encoded(text)

    # Process
    if args.decode:
        if args.query:
            params = parse_query_string(text)
            for key, value in params:
                print(f"{key}={value}")
        elif args.path:
            print(decode_path(text))
        else:
            print(percent_decode(text, plus_as_space=args.plus))
    else:
        if args.query:
            # Encode as query value
            print(percent_encode(text, space_as_plus=True))
        elif args.path:
            print(encode_path(text))
        else:
            print(percent_encode(text, space_as_plus=args.plus))

    return 0


if __name__ == "__main__":
    sys.exit(main())
