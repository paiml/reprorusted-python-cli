#!/usr/bin/env python3
"""Text Parse CLI.

Text parsing and manipulation operations.
"""

import argparse
import sys


def split_lines(text: str) -> list[str]:
    """Split text into lines."""
    return text.splitlines()


def split_words(text: str) -> list[str]:
    """Split text into words."""
    return text.split()


def split_by(text: str, delimiter: str) -> list[str]:
    """Split text by delimiter."""
    return text.split(delimiter)


def split_chars(text: str) -> list[str]:
    """Split text into characters."""
    return list(text)


def join_lines(lines: list[str]) -> str:
    """Join lines with newline."""
    return "\n".join(lines)


def join_words(words: list[str]) -> str:
    """Join words with space."""
    return " ".join(words)


def join_by(items: list[str], delimiter: str) -> str:
    """Join items with delimiter."""
    return delimiter.join(items)


def strip(text: str) -> str:
    """Strip leading/trailing whitespace."""
    return text.strip()


def strip_left(text: str) -> str:
    """Strip leading whitespace."""
    return text.lstrip()


def strip_right(text: str) -> str:
    """Strip trailing whitespace."""
    return text.rstrip()


def strip_chars(text: str, chars: str) -> str:
    """Strip specific characters."""
    return text.strip(chars)


def upper(text: str) -> str:
    """Convert to uppercase."""
    return text.upper()


def lower(text: str) -> str:
    """Convert to lowercase."""
    return text.lower()


def title(text: str) -> str:
    """Convert to title case."""
    return text.title()


def capitalize(text: str) -> str:
    """Capitalize first character."""
    return text.capitalize()


def swapcase(text: str) -> str:
    """Swap case of characters."""
    return text.swapcase()


def casefold(text: str) -> str:
    """Aggressive lowercase for comparison."""
    return text.casefold()


def replace(text: str, old: str, new: str) -> str:
    """Replace all occurrences."""
    return text.replace(old, new)


def replace_first(text: str, old: str, new: str) -> str:
    """Replace first occurrence."""
    return text.replace(old, new, 1)


def startswith(text: str, prefix: str) -> bool:
    """Check if starts with prefix."""
    return text.startswith(prefix)


def endswith(text: str, suffix: str) -> bool:
    """Check if ends with suffix."""
    return text.endswith(suffix)


def contains(text: str, substring: str) -> bool:
    """Check if contains substring."""
    return substring in text


def count(text: str, substring: str) -> int:
    """Count occurrences of substring."""
    return text.count(substring)


def find(text: str, substring: str) -> int:
    """Find first occurrence, -1 if not found."""
    return text.find(substring)


def rfind(text: str, substring: str) -> int:
    """Find last occurrence, -1 if not found."""
    return text.rfind(substring)


def index(text: str, substring: str) -> int:
    """Find first occurrence, raise if not found."""
    return text.index(substring)


def is_alpha(text: str) -> bool:
    """Check if all alphabetic."""
    return text.isalpha()


def is_digit(text: str) -> bool:
    """Check if all digits."""
    return text.isdigit()


def is_alnum(text: str) -> bool:
    """Check if all alphanumeric."""
    return text.isalnum()


def is_space(text: str) -> bool:
    """Check if all whitespace."""
    return text.isspace()


def is_upper(text: str) -> bool:
    """Check if all uppercase."""
    return text.isupper()


def is_lower(text: str) -> bool:
    """Check if all lowercase."""
    return text.islower()


def is_title(text: str) -> bool:
    """Check if title case."""
    return text.istitle()


def is_numeric(text: str) -> bool:
    """Check if numeric."""
    return text.isnumeric()


def is_decimal(text: str) -> bool:
    """Check if decimal."""
    return text.isdecimal()


def is_identifier(text: str) -> bool:
    """Check if valid identifier."""
    return text.isidentifier()


def is_printable(text: str) -> bool:
    """Check if printable."""
    return text.isprintable()


def length(text: str) -> int:
    """Get string length."""
    return len(text)


def reverse(text: str) -> str:
    """Reverse string."""
    return text[::-1]


def char_at(text: str, index: int) -> str:
    """Get character at index."""
    if 0 <= index < len(text):
        return text[index]
    return ""


def substring(text: str, start: int, end: int) -> str:
    """Get substring."""
    return text[start:end]


def remove_prefix(text: str, prefix: str) -> str:
    """Remove prefix if present."""
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def remove_suffix(text: str, suffix: str) -> str:
    """Remove suffix if present."""
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text


def center(text: str, width: int) -> str:
    """Center string."""
    return text.center(width)


def ljust(text: str, width: int) -> str:
    """Left justify string."""
    return text.ljust(width)


def rjust(text: str, width: int) -> str:
    """Right justify string."""
    return text.rjust(width)


def partition(text: str, sep: str) -> tuple[str, str, str]:
    """Partition on first separator."""
    return text.partition(sep)


def rpartition(text: str, sep: str) -> tuple[str, str, str]:
    """Partition on last separator."""
    return text.rpartition(sep)


def expandtabs(text: str, tabsize: int = 8) -> str:
    """Expand tabs to spaces."""
    return text.expandtabs(tabsize)


def encode_utf8(text: str) -> bytes:
    """Encode as UTF-8."""
    return text.encode("utf-8")


def decode_utf8(data: bytes) -> str:
    """Decode from UTF-8."""
    return data.decode("utf-8")


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def line_count(text: str) -> int:
    """Count lines in text."""
    return len(text.splitlines())


def char_count(text: str, include_spaces: bool = True) -> int:
    """Count characters in text."""
    if include_spaces:
        return len(text)
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))


def char_frequency(text: str) -> dict[str, int]:
    """Get character frequency."""
    freq: dict[str, int] = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    return freq


def word_frequency(text: str) -> dict[str, int]:
    """Get word frequency."""
    freq: dict[str, int] = {}
    for word in text.lower().split():
        freq[word] = freq.get(word, 0) + 1
    return freq


def main() -> int:
    parser = argparse.ArgumentParser(description="Text parse CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # split
    split_p = subparsers.add_parser("split", help="Split text")
    split_p.add_argument("text", help="Text to split")
    split_p.add_argument("-d", "--delimiter", help="Delimiter")
    split_p.add_argument("--lines", action="store_true", help="Split by lines")
    split_p.add_argument("--words", action="store_true", help="Split by words")

    # join
    join_p = subparsers.add_parser("join", help="Join items")
    join_p.add_argument("items", nargs="+", help="Items to join")
    join_p.add_argument("-d", "--delimiter", default=" ", help="Delimiter")

    # case
    case_p = subparsers.add_parser("case", help="Change case")
    case_p.add_argument("text", help="Text")
    case_p.add_argument("--upper", action="store_true")
    case_p.add_argument("--lower", action="store_true")
    case_p.add_argument("--title", action="store_true")

    # count
    count_p = subparsers.add_parser("count", help="Count in text")
    count_p.add_argument("text", help="Text")
    count_p.add_argument("--words", action="store_true")
    count_p.add_argument("--lines", action="store_true")
    count_p.add_argument("--chars", action="store_true")

    # replace
    replace_p = subparsers.add_parser("replace", help="Replace in text")
    replace_p.add_argument("text", help="Text")
    replace_p.add_argument("old", help="Old string")
    replace_p.add_argument("new", help="New string")

    args = parser.parse_args()

    if args.command == "split":
        if args.lines:
            result = split_lines(args.text)
        elif args.words:
            result = split_words(args.text)
        elif args.delimiter:
            result = split_by(args.text, args.delimiter)
        else:
            result = split_words(args.text)
        for item in result:
            print(item)

    elif args.command == "join":
        result = join_by(args.items, args.delimiter)
        print(result)

    elif args.command == "case":
        if args.upper:
            print(upper(args.text))
        elif args.lower:
            print(lower(args.text))
        elif args.title:
            print(title(args.text))
        else:
            print(args.text)

    elif args.command == "count":
        if args.words:
            print(f"Words: {word_count(args.text)}")
        elif args.lines:
            print(f"Lines: {line_count(args.text)}")
        elif args.chars:
            print(f"Characters: {char_count(args.text)}")
        else:
            print(f"Words: {word_count(args.text)}")
            print(f"Lines: {line_count(args.text)}")
            print(f"Characters: {char_count(args.text)}")

    elif args.command == "replace":
        result = replace(args.text, args.old, args.new)
        print(result)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
