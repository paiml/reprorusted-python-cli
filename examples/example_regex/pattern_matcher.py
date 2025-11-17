#!/usr/bin/env python3
"""
Regex Example - Regular expression pattern matching

Demonstrates:
- re.match(), re.search(), re.findall()
- re.sub() for text replacement
- Compiled patterns with re.compile()
- Named groups and backreferences
- Case-insensitive matching
- Multi-line patterns

This validates depyler's ability to transpile regex operations
to Rust (regex crate).
"""

import argparse
import re
import sys


def match_pattern(pattern, text, ignore_case=False):
    """
    Match pattern at start of text

    Args:
        pattern: Regular expression pattern
        text: Text to search
        ignore_case: Case-insensitive matching

    Depyler: proven to terminate
    """
    flags = re.IGNORECASE if ignore_case else 0
    match = re.match(pattern, text, flags)

    if match:
        print(f"Match found: {match.group(0)}")
        if match.groups():
            print(f"Groups: {match.groups()}")
        return True
    else:
        print("No match")
        return False


def search_pattern(pattern, text, ignore_case=False):
    """
    Search for pattern anywhere in text

    Args:
        pattern: Regular expression pattern
        text: Text to search
        ignore_case: Case-insensitive matching

    Depyler: proven to terminate
    """
    flags = re.IGNORECASE if ignore_case else 0
    match = re.search(pattern, text, flags)

    if match:
        print(f"Found at position {match.start()}: {match.group(0)}")
        return True
    else:
        print("Pattern not found")
        return False


def find_all(pattern, text, ignore_case=False):
    """
    Find all occurrences of pattern

    Args:
        pattern: Regular expression pattern
        text: Text to search
        ignore_case: Case-insensitive matching

    Depyler: proven to terminate
    """
    flags = re.IGNORECASE if ignore_case else 0
    matches = re.findall(pattern, text, flags)

    print(f"Found {len(matches)} matches:")
    for i, match in enumerate(matches, 1):
        print(f"  {i}. {match}")

    return matches


def substitute(pattern, replacement, text, ignore_case=False):
    """
    Replace pattern with replacement text

    Args:
        pattern: Regular expression pattern
        replacement: Replacement string
        text: Text to process
        ignore_case: Case-insensitive matching

    Depyler: proven to terminate
    """
    flags = re.IGNORECASE if ignore_case else 0
    result = re.sub(pattern, replacement, text, flags=flags)

    print(f"Original: {text}")
    print(f"Result:   {result}")

    return result


def validate_email(email):
    """
    Validate email address format

    Args:
        email: Email address to validate

    Depyler: proven to terminate
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    compiled = re.compile(pattern)
    match = compiled.match(email)

    if match:
        print(f"Valid email: {email}")
        return True
    else:
        print(f"Invalid email: {email}")
        return False


def extract_numbers(text):
    """
    Extract all numbers from text

    Args:
        text: Text to search

    Depyler: proven to terminate
    """
    # Match integers and floats
    pattern = r"-?\d+\.?\d*"
    numbers = re.findall(pattern, text)

    print(f"Found {len(numbers)} numbers: {numbers}")
    return numbers


def main():
    """
    Main entry point for pattern matcher CLI

    Demonstrates various regex operations.
    """
    parser = argparse.ArgumentParser(
        description="Regular expression pattern matching",
        prog="pattern_matcher.py",
    )

    parser.add_argument("--version", action="version", version="1.0.0")

    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Case-insensitive matching",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Match command
    match_parser = subparsers.add_parser("match", help="Match pattern at start of text")
    match_parser.add_argument("pattern", help="Regular expression pattern")
    match_parser.add_argument("text", help="Text to search")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for pattern in text")
    search_parser.add_argument("pattern", help="Regular expression pattern")
    search_parser.add_argument("text", help="Text to search")

    # Findall command
    findall_parser = subparsers.add_parser("findall", help="Find all occurrences")
    findall_parser.add_argument("pattern", help="Regular expression pattern")
    findall_parser.add_argument("text", help="Text to search")

    # Substitute command
    sub_parser = subparsers.add_parser("sub", help="Replace pattern with text")
    sub_parser.add_argument("pattern", help="Regular expression pattern")
    sub_parser.add_argument("replacement", help="Replacement text")
    sub_parser.add_argument("text", help="Text to process")

    # Validate email command
    email_parser = subparsers.add_parser("email", help="Validate email address")
    email_parser.add_argument("address", help="Email address to validate")

    # Extract numbers command
    numbers_parser = subparsers.add_parser("numbers", help="Extract numbers from text")
    numbers_parser.add_argument("text", help="Text to search")

    args = parser.parse_args()

    # Execute command
    if args.command == "match":
        match_pattern(args.pattern, args.text, args.ignore_case)

    elif args.command == "search":
        search_pattern(args.pattern, args.text, args.ignore_case)

    elif args.command == "findall":
        find_all(args.pattern, args.text, args.ignore_case)

    elif args.command == "sub":
        substitute(args.pattern, args.replacement, args.text, args.ignore_case)

    elif args.command == "email":
        if not validate_email(args.address):
            sys.exit(1)

    elif args.command == "numbers":
        extract_numbers(args.text)


if __name__ == "__main__":
    main()
