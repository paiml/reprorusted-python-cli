#!/usr/bin/env python3
"""File Read CLI.

File reading operations using Python's built-in file handling.
"""

import argparse
import sys


def read_file(path: str) -> str:
    """Read entire file as string."""
    with open(path) as f:
        return f.read()


def read_lines(path: str) -> list[str]:
    """Read file as list of lines."""
    with open(path) as f:
        return f.readlines()


def read_lines_stripped(path: str) -> list[str]:
    """Read file as list of stripped lines."""
    with open(path) as f:
        return [line.strip() for line in f]


def read_line(path: str, line_num: int) -> str:
    """Read specific line from file (1-indexed)."""
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if i == line_num:
                return line.rstrip()
    return ""


def read_first_n_lines(path: str, n: int) -> list[str]:
    """Read first n lines from file."""
    lines = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            lines.append(line.rstrip())
    return lines


def read_last_n_lines(path: str, n: int) -> list[str]:
    """Read last n lines from file."""
    with open(path) as f:
        lines = f.readlines()
    return [line.rstrip() for line in lines[-n:]]


def count_lines(path: str) -> int:
    """Count number of lines in file."""
    count = 0
    with open(path) as f:
        for _ in f:
            count += 1
    return count


def count_words(path: str) -> int:
    """Count number of words in file."""
    count = 0
    with open(path) as f:
        for line in f:
            count += len(line.split())
    return count


def count_chars(path: str) -> int:
    """Count number of characters in file."""
    with open(path) as f:
        return len(f.read())


def read_binary(path: str) -> bytes:
    """Read file as binary."""
    with open(path, "rb") as f:
        return f.read()


def read_chunks(path: str, chunk_size: int) -> list[str]:
    """Read file in chunks."""
    chunks = []
    with open(path) as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    return chunks


def search_in_file(path: str, pattern: str) -> list[tuple[int, str]]:
    """Search for pattern in file, return matching lines with numbers."""
    matches = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if pattern in line:
                matches.append((i, line.rstrip()))
    return matches


def read_csv_simple(path: str, delimiter: str = ",") -> list[list[str]]:
    """Read simple CSV file without csv module."""
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(line.split(delimiter))
    return rows


def read_key_value(path: str, delimiter: str = "=") -> dict[str, str]:
    """Read key=value file."""
    result = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if delimiter in line:
                    key, value = line.split(delimiter, 1)
                    result[key.strip()] = value.strip()
    return result


def file_exists(path: str) -> bool:
    """Check if file exists by trying to open it."""
    try:
        with open(path):
            return True
    except FileNotFoundError:
        return False


def get_file_size(path: str) -> int:
    """Get file size in bytes."""
    with open(path, "rb") as f:
        f.seek(0, 2)  # Seek to end
        return f.tell()


def main() -> int:
    parser = argparse.ArgumentParser(description="File read CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # read
    read_p = subparsers.add_parser("read", help="Read entire file")
    read_p.add_argument("file", help="File path")

    # lines
    lines_p = subparsers.add_parser("lines", help="Read lines")
    lines_p.add_argument("file", help="File path")
    lines_p.add_argument("-n", type=int, help="Number of lines")
    lines_p.add_argument("--tail", action="store_true", help="Read from end")

    # line
    line_p = subparsers.add_parser("line", help="Read specific line")
    line_p.add_argument("file", help="File path")
    line_p.add_argument("num", type=int, help="Line number")

    # count
    count_p = subparsers.add_parser("count", help="Count lines/words/chars")
    count_p.add_argument("file", help="File path")
    count_p.add_argument("--lines", "-l", action="store_true")
    count_p.add_argument("--words", "-w", action="store_true")
    count_p.add_argument("--chars", "-c", action="store_true")

    # search
    search_p = subparsers.add_parser("search", help="Search in file")
    search_p.add_argument("file", help="File path")
    search_p.add_argument("pattern", help="Search pattern")

    # size
    size_p = subparsers.add_parser("size", help="Get file size")
    size_p.add_argument("file", help="File path")

    # exists
    exists_p = subparsers.add_parser("exists", help="Check if file exists")
    exists_p.add_argument("file", help="File path")

    args = parser.parse_args()

    try:
        if args.command == "read":
            print(read_file(args.file))
        elif args.command == "lines":
            if args.n:
                if args.tail:
                    lines = read_last_n_lines(args.file, args.n)
                else:
                    lines = read_first_n_lines(args.file, args.n)
            else:
                lines = read_lines_stripped(args.file)
            for line in lines:
                print(line)
        elif args.command == "line":
            print(read_line(args.file, args.num))
        elif args.command == "count":
            if args.lines:
                print(f"Lines: {count_lines(args.file)}")
            if args.words:
                print(f"Words: {count_words(args.file)}")
            if args.chars:
                print(f"Chars: {count_chars(args.file)}")
            if not (args.lines or args.words or args.chars):
                print(f"Lines: {count_lines(args.file)}")
                print(f"Words: {count_words(args.file)}")
                print(f"Chars: {count_chars(args.file)}")
        elif args.command == "search":
            matches = search_in_file(args.file, args.pattern)
            for line_num, line in matches:
                print(f"{line_num}: {line}")
            print(f"Found {len(matches)} matches")
        elif args.command == "size":
            size = get_file_size(args.file)
            print(f"{size} bytes")
        elif args.command == "exists":
            if file_exists(args.file):
                print(f"'{args.file}' exists")
            else:
                print(f"'{args.file}' does not exist")
        else:
            parser.print_help()

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
