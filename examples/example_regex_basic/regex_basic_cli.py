#!/usr/bin/env python3
"""Regex Basic CLI.

Regular expression operations.
"""

import argparse
import re
import sys


def match(pattern: str, text: str) -> bool:
    """Check if pattern matches at start of text."""
    return re.match(pattern, text) is not None


def search(pattern: str, text: str) -> str | None:
    """Find first match of pattern in text."""
    m = re.search(pattern, text)
    return m.group(0) if m else None


def findall(pattern: str, text: str) -> list[str]:
    """Find all matches of pattern in text."""
    return re.findall(pattern, text)


def findall_groups(pattern: str, text: str) -> list[tuple[str, ...]]:
    """Find all matches with groups."""
    return re.findall(pattern, text)


def finditer_positions(pattern: str, text: str) -> list[tuple[int, int, str]]:
    """Find all matches with positions (start, end, match)."""
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(pattern, text)]


def sub(pattern: str, replacement: str, text: str) -> str:
    """Replace pattern matches with replacement."""
    return re.sub(pattern, replacement, text)


def sub_count(pattern: str, replacement: str, text: str, count: int) -> str:
    """Replace first n matches."""
    return re.sub(pattern, replacement, text, count=count)


def subn(pattern: str, replacement: str, text: str) -> tuple[str, int]:
    """Replace and return (new_text, replacement_count)."""
    return re.subn(pattern, replacement, text)


def split(pattern: str, text: str) -> list[str]:
    """Split text by pattern."""
    return re.split(pattern, text)


def split_maxsplit(pattern: str, text: str, maxsplit: int) -> list[str]:
    """Split text by pattern with max splits."""
    return re.split(pattern, text, maxsplit=maxsplit)


def escape(text: str) -> str:
    """Escape special regex characters."""
    return re.escape(text)


def is_valid_pattern(pattern: str) -> bool:
    """Check if pattern is valid regex."""
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def match_groups(pattern: str, text: str) -> tuple[str, ...] | None:
    """Match and return groups."""
    m = re.match(pattern, text)
    return m.groups() if m else None


def match_groupdict(pattern: str, text: str) -> dict[str, str] | None:
    """Match and return named groups as dict."""
    m = re.match(pattern, text)
    return m.groupdict() if m else None


def fullmatch(pattern: str, text: str) -> bool:
    """Check if pattern matches entire text."""
    return re.fullmatch(pattern, text) is not None


def extract_numbers(text: str) -> list[int]:
    """Extract all integers from text."""
    return [int(n) for n in re.findall(r"-?\d+", text)]


def extract_floats(text: str) -> list[float]:
    """Extract all floats from text."""
    return [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]


def extract_words(text: str) -> list[str]:
    """Extract all words from text."""
    return re.findall(r"\b\w+\b", text)


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    return re.findall(r"https?://[^\s<>\"]+", text)


def extract_ipv4(text: str) -> list[str]:
    """Extract IPv4 addresses from text."""
    return re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text."""
    return re.findall(r"#\w+", text)


def extract_mentions(text: str) -> list[str]:
    """Extract @mentions from text."""
    return re.findall(r"@\w+", text)


def is_email(text: str) -> bool:
    """Check if text is a valid email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, text))


def is_url(text: str) -> bool:
    """Check if text is a URL."""
    pattern = r"^https?://[^\s<>\"]+$"
    return bool(re.match(pattern, text))


def is_ipv4(text: str) -> bool:
    """Check if text is IPv4 address."""
    pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, text):
        return False
    parts = text.split(".")
    return all(0 <= int(p) <= 255 for p in parts)


def is_phone(text: str) -> bool:
    """Check if text looks like a phone number."""
    pattern = r"^[\d\s\-\(\)\+]+$"
    digits = re.sub(r"\D", "", text)
    return bool(re.match(pattern, text)) and 7 <= len(digits) <= 15


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text)


def remove_punctuation(text: str) -> str:
    """Remove punctuation from text."""
    return re.sub(r"[^\w\s]", "", text)


def remove_extra_spaces(text: str) -> str:
    """Remove extra whitespace from text."""
    return re.sub(r"\s+", " ", text).strip()


def camel_to_snake(text: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    return re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(text: str) -> str:
    """Convert snake_case to camelCase."""
    components = text.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def count_matches(pattern: str, text: str) -> int:
    """Count pattern matches in text."""
    return len(re.findall(pattern, text))


def replace_func(pattern: str, text: str, func: callable) -> str:
    """Replace using function on each match."""
    return re.sub(pattern, func, text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Regex basic CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # match
    match_p = subparsers.add_parser("match", help="Check pattern match")
    match_p.add_argument("pattern", help="Regex pattern")
    match_p.add_argument("text", help="Text to match")

    # find
    find_p = subparsers.add_parser("find", help="Find all matches")
    find_p.add_argument("pattern", help="Regex pattern")
    find_p.add_argument("text", help="Text to search")

    # replace
    replace_p = subparsers.add_parser("replace", help="Replace matches")
    replace_p.add_argument("pattern", help="Regex pattern")
    replace_p.add_argument("replacement", help="Replacement")
    replace_p.add_argument("text", help="Text to modify")

    # split
    split_p = subparsers.add_parser("split", help="Split by pattern")
    split_p.add_argument("pattern", help="Regex pattern")
    split_p.add_argument("text", help="Text to split")

    # extract
    extract_p = subparsers.add_parser("extract", help="Extract patterns")
    extract_p.add_argument("type", choices=["numbers", "emails", "urls", "words"])
    extract_p.add_argument("text", help="Text to extract from")

    args = parser.parse_args()

    if args.command == "match":
        result = match(args.pattern, args.text)
        print(f"Match: {result}")

    elif args.command == "find":
        matches = findall(args.pattern, args.text)
        print(f"Matches: {matches}")

    elif args.command == "replace":
        result = sub(args.pattern, args.replacement, args.text)
        print(f"Result: {result}")

    elif args.command == "split":
        parts = split(args.pattern, args.text)
        print(f"Parts: {parts}")

    elif args.command == "extract":
        if args.type == "numbers":
            result = extract_numbers(args.text)
        elif args.type == "emails":
            result = extract_emails(args.text)
        elif args.type == "urls":
            result = extract_urls(args.text)
        else:
            result = extract_words(args.text)
        print(f"Extracted: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
