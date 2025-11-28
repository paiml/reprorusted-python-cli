#!/usr/bin/env python3
"""File Text CLI.

Text file operations with encoding handling.
"""

import argparse
import sys
from pathlib import Path


def read_text(path: str, encoding: str = "utf-8") -> str:
    """Read entire file as text."""
    return Path(path).read_text(encoding=encoding)


def write_text(path: str, content: str, encoding: str = "utf-8") -> int:
    """Write text to file."""
    return Path(path).write_text(content, encoding=encoding)


def read_lines_text(path: str, encoding: str = "utf-8") -> list[str]:
    """Read file lines as list."""
    return Path(path).read_text(encoding=encoding).splitlines()


def read_lines_keep_ends(path: str, encoding: str = "utf-8") -> list[str]:
    """Read file lines keeping line endings."""
    return Path(path).read_text(encoding=encoding).splitlines(keepends=True)


def count_characters(path: str, encoding: str = "utf-8") -> int:
    """Count characters in file."""
    return len(Path(path).read_text(encoding=encoding))


def count_lines_text(path: str, encoding: str = "utf-8") -> int:
    """Count lines in file."""
    return len(Path(path).read_text(encoding=encoding).splitlines())


def count_words_text(path: str, encoding: str = "utf-8") -> int:
    """Count words in file."""
    return len(Path(path).read_text(encoding=encoding).split())


def head_lines(path: str, n: int = 10, encoding: str = "utf-8") -> list[str]:
    """Get first n lines."""
    lines = Path(path).read_text(encoding=encoding).splitlines()
    return lines[:n]


def tail_lines(path: str, n: int = 10, encoding: str = "utf-8") -> list[str]:
    """Get last n lines."""
    lines = Path(path).read_text(encoding=encoding).splitlines()
    return lines[-n:]


def get_line(path: str, line_num: int, encoding: str = "utf-8") -> str:
    """Get specific line (1-indexed)."""
    lines = Path(path).read_text(encoding=encoding).splitlines()
    if 1 <= line_num <= len(lines):
        return lines[line_num - 1]
    return ""


def search_text(path: str, pattern: str, encoding: str = "utf-8") -> list[tuple[int, str]]:
    """Search for pattern in file, return matching lines with numbers."""
    lines = Path(path).read_text(encoding=encoding).splitlines()
    results = []
    for i, line in enumerate(lines, 1):
        if pattern in line:
            results.append((i, line))
    return results


def replace_text(path: str, old: str, new: str, encoding: str = "utf-8") -> int:
    """Replace text in file, return count of replacements."""
    p = Path(path)
    content = p.read_text(encoding=encoding)
    count = content.count(old)
    new_content = content.replace(old, new)
    p.write_text(new_content, encoding=encoding)
    return count


def append_text(path: str, content: str, encoding: str = "utf-8") -> int:
    """Append text to file."""
    p = Path(path)
    existing = p.read_text(encoding=encoding) if p.exists() else ""
    new_content = existing + content
    return p.write_text(new_content, encoding=encoding)


def prepend_text(path: str, content: str, encoding: str = "utf-8") -> int:
    """Prepend text to file."""
    p = Path(path)
    existing = p.read_text(encoding=encoding) if p.exists() else ""
    new_content = content + existing
    return p.write_text(new_content, encoding=encoding)


def insert_at_line(path: str, line_num: int, content: str, encoding: str = "utf-8") -> int:
    """Insert content at specific line."""
    p = Path(path)
    lines = p.read_text(encoding=encoding).splitlines(keepends=True)
    # Handle line endings
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    if not content.endswith("\n"):
        content += "\n"
    lines.insert(line_num - 1, content)
    return p.write_text("".join(lines), encoding=encoding)


def delete_at_line(path: str, line_num: int, encoding: str = "utf-8") -> str:
    """Delete specific line, return deleted content."""
    p = Path(path)
    lines = p.read_text(encoding=encoding).splitlines(keepends=True)
    if 1 <= line_num <= len(lines):
        deleted = lines.pop(line_num - 1)
        p.write_text("".join(lines), encoding=encoding)
        return deleted.rstrip("\n")
    return ""


def strip_lines(path: str, encoding: str = "utf-8") -> list[str]:
    """Read and strip all lines."""
    return [line.strip() for line in Path(path).read_text(encoding=encoding).splitlines()]


def filter_empty_lines(path: str, encoding: str = "utf-8") -> list[str]:
    """Read non-empty lines."""
    return [line for line in Path(path).read_text(encoding=encoding).splitlines() if line.strip()]


def detect_encoding(path: str) -> str:
    """Simple encoding detection (checks for BOM)."""
    data = Path(path).read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if data.startswith(b"\xff\xfe"):
        return "utf-16-le"
    if data.startswith(b"\xfe\xff"):
        return "utf-16-be"
    return "utf-8"


def convert_encoding(src: str, dst: str, src_enc: str, dst_enc: str) -> int:
    """Convert file between encodings."""
    content = Path(src).read_text(encoding=src_enc)
    return Path(dst).write_text(content, encoding=dst_enc)


def normalize_line_endings(path: str, ending: str = "\n", encoding: str = "utf-8") -> int:
    """Normalize line endings (\\n, \\r\\n, or \\r)."""
    p = Path(path)
    content = p.read_text(encoding=encoding)
    # Replace all variants with target
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    if ending != "\n":
        normalized = normalized.replace("\n", ending)
    return p.write_text(normalized, encoding=encoding)


def ensure_newline_at_end(path: str, encoding: str = "utf-8") -> bool:
    """Ensure file ends with newline."""
    p = Path(path)
    content = p.read_text(encoding=encoding)
    if content and not content.endswith("\n"):
        p.write_text(content + "\n", encoding=encoding)
        return True
    return False


def remove_trailing_whitespace(path: str, encoding: str = "utf-8") -> int:
    """Remove trailing whitespace from each line."""
    p = Path(path)
    lines = p.read_text(encoding=encoding).splitlines()
    stripped = [line.rstrip() for line in lines]
    p.write_text("\n".join(stripped) + "\n" if stripped else "", encoding=encoding)
    count = sum(1 for old, new in zip(lines, stripped, strict=False) if old != new)
    return count


def join_lines(path: str, separator: str = " ", encoding: str = "utf-8") -> str:
    """Join all lines with separator."""
    lines = Path(path).read_text(encoding=encoding).splitlines()
    return separator.join(lines)


def split_into_files(
    path: str, output_dir: str, lines_per_file: int, encoding: str = "utf-8"
) -> int:
    """Split file into multiple files."""
    lines = Path(path).read_text(encoding=encoding).splitlines()
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    file_count = 0
    for i in range(0, len(lines), lines_per_file):
        chunk = lines[i : i + lines_per_file]
        out_file = out_path / f"part_{file_count:04d}.txt"
        out_file.write_text("\n".join(chunk) + "\n", encoding=encoding)
        file_count += 1
    return file_count


def main() -> int:
    parser = argparse.ArgumentParser(description="File text CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # read
    read_p = subparsers.add_parser("read", help="Read file")
    read_p.add_argument("path", help="File path")
    read_p.add_argument("-e", "--encoding", default="utf-8", help="Encoding")

    # write
    write_p = subparsers.add_parser("write", help="Write file")
    write_p.add_argument("path", help="File path")
    write_p.add_argument("content", help="Content")
    write_p.add_argument("-e", "--encoding", default="utf-8", help="Encoding")

    # head
    head_p = subparsers.add_parser("head", help="First n lines")
    head_p.add_argument("path", help="File path")
    head_p.add_argument("-n", type=int, default=10, help="Number of lines")

    # tail
    tail_p = subparsers.add_parser("tail", help="Last n lines")
    tail_p.add_argument("path", help="File path")
    tail_p.add_argument("-n", type=int, default=10, help="Number of lines")

    # count
    count_p = subparsers.add_parser("count", help="Count stats")
    count_p.add_argument("path", help="File path")

    # search
    search_p = subparsers.add_parser("search", help="Search pattern")
    search_p.add_argument("path", help="File path")
    search_p.add_argument("pattern", help="Search pattern")

    # replace
    replace_p = subparsers.add_parser("replace", help="Replace text")
    replace_p.add_argument("path", help="File path")
    replace_p.add_argument("old", help="Old text")
    replace_p.add_argument("new", help="New text")

    # convert
    convert_p = subparsers.add_parser("convert", help="Convert encoding")
    convert_p.add_argument("src", help="Source file")
    convert_p.add_argument("dst", help="Destination file")
    convert_p.add_argument("--from", dest="src_enc", default="utf-8", help="Source encoding")
    convert_p.add_argument("--to", dest="dst_enc", default="utf-8", help="Dest encoding")

    args = parser.parse_args()

    if args.command == "read":
        content = read_text(args.path, args.encoding)
        print(content, end="")

    elif args.command == "write":
        n = write_text(args.path, args.content, args.encoding)
        print(f"Wrote {n} bytes")

    elif args.command == "head":
        lines = head_lines(args.path, args.n)
        for line in lines:
            print(line)

    elif args.command == "tail":
        lines = tail_lines(args.path, args.n)
        for line in lines:
            print(line)

    elif args.command == "count":
        chars = count_characters(args.path)
        lines = count_lines_text(args.path)
        words = count_words_text(args.path)
        print(f"Characters: {chars}")
        print(f"Lines: {lines}")
        print(f"Words: {words}")

    elif args.command == "search":
        results = search_text(args.path, args.pattern)
        for line_num, line in results:
            print(f"{line_num}: {line}")

    elif args.command == "replace":
        count = replace_text(args.path, args.old, args.new)
        print(f"Replaced {count} occurrences")

    elif args.command == "convert":
        n = convert_encoding(args.src, args.dst, args.src_enc, args.dst_enc)
        print(f"Converted {n} bytes")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
