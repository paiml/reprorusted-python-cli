#!/usr/bin/env python3
"""
I/O Streams Example - File I/O and stream processing

Demonstrates:
- Reading from stdin line-by-line
- Writing to stdout/stderr
- File operations (read, write, append)
- Temporary files and cleanup
- Binary vs text mode
- Context managers (with statement)

This validates depyler's ability to transpile I/O operations
to Rust (std::io::{BufReader, BufRead}, std::fs).
"""

import argparse
import os
import sys
import tempfile


def read_stdin_lines():
    """
    Read and process lines from stdin

    Depyler: proven to terminate
    """
    print("Reading from stdin (Ctrl+D to end):", file=sys.stderr)
    line_count = 0
    word_count = 0
    char_count = 0

    for line in sys.stdin:
        line_count += 1
        words = line.split()
        word_count += len(words)
        char_count += len(line)
        print(f"{line_count}: {line.rstrip()}")

    print(f"\nStats: {line_count} lines, {word_count} words, {char_count} chars", file=sys.stderr)


def read_file(filepath, binary=False):
    """
    Read and display file contents

    Args:
        filepath: Path to file
        binary: Read in binary mode

    Depyler: proven to terminate
    """
    mode = "rb" if binary else "r"

    try:
        with open(filepath, mode) as f:
            content = f.read()
            if binary:
                print(f"Read {len(content)} bytes")
                # Show first 100 bytes as hex
                hex_str = content[:100].hex()
                print(f"First bytes (hex): {hex_str}")
            else:
                print(content)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: {filepath}", file=sys.stderr)
        sys.exit(1)


def write_file(filepath, content, append=False):
    """
    Write content to file

    Args:
        filepath: Path to file
        content: Content to write
        append: Append instead of overwrite

    Depyler: proven to terminate
    """
    mode = "a" if append else "w"

    with open(filepath, mode) as f:
        f.write(content)
        if not content.endswith("\n"):
            f.write("\n")

    action = "Appended to" if append else "Wrote to"
    print(f"{action} {filepath}")


def count_lines(filepath):
    """
    Count lines in file efficiently

    Args:
        filepath: Path to file

    Depyler: proven to terminate
    """
    try:
        with open(filepath) as f:
            lines = sum(1 for line in f)
        print(f"{filepath}: {lines} lines")
        return lines
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)


def create_temp_file(content=None):
    """
    Create temporary file

    Args:
        content: Optional content to write

    Depyler: proven to terminate
    """
    # Create named temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        temp_path = f.name
        if content:
            f.write(content)

    print(f"Created temporary file: {temp_path}")

    # Verify it exists
    if os.path.exists(temp_path):
        print(f"File exists: {os.path.getsize(temp_path)} bytes")

    return temp_path


def filter_lines(filepath, pattern):
    """
    Filter lines containing pattern

    Args:
        filepath: Path to input file
        pattern: String to search for

    Depyler: proven to terminate
    """
    try:
        with open(filepath) as f:
            matching_lines = [line.rstrip() for line in f if pattern in line]

        print(f"Found {len(matching_lines)} matching lines:")
        for line in matching_lines:
            print(f"  {line}")

        return matching_lines
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main entry point for stream processor CLI

    Demonstrates various I/O operations.
    """
    parser = argparse.ArgumentParser(
        description="File I/O and stream processing",
        prog="stream_processor.py",
    )

    parser.add_argument("--version", action="version", version="1.0.0")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Stdin command
    subparsers.add_parser("stdin", help="Read from stdin")

    # Read file command
    read_parser = subparsers.add_parser("read", help="Read file contents")
    read_parser.add_argument("file", help="File to read")
    read_parser.add_argument("--binary", action="store_true", help="Read in binary mode")

    # Write file command
    write_parser = subparsers.add_parser("write", help="Write to file")
    write_parser.add_argument("file", help="File to write")
    write_parser.add_argument("content", help="Content to write")
    write_parser.add_argument("--append", action="store_true", help="Append instead of overwrite")

    # Count lines command
    count_parser = subparsers.add_parser("count", help="Count lines in file")
    count_parser.add_argument("file", help="File to count")

    # Temp file command
    temp_parser = subparsers.add_parser("temp", help="Create temporary file")
    temp_parser.add_argument("--content", help="Content for temp file")

    # Filter command
    filter_parser = subparsers.add_parser("filter", help="Filter lines by pattern")
    filter_parser.add_argument("file", help="File to filter")
    filter_parser.add_argument("pattern", help="Pattern to search for")

    args = parser.parse_args()

    # Execute command
    if args.command == "stdin":
        read_stdin_lines()

    elif args.command == "read":
        read_file(args.file, args.binary)

    elif args.command == "write":
        write_file(args.file, args.content, args.append)

    elif args.command == "count":
        count_lines(args.file)

    elif args.command == "temp":
        create_temp_file(args.content)

    elif args.command == "filter":
        filter_lines(args.file, args.pattern)


if __name__ == "__main__":
    main()
