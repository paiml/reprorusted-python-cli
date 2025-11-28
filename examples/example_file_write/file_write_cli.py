#!/usr/bin/env python3
"""File Write CLI.

File writing operations using Python's built-in file handling.
"""

import argparse
import sys


def write_file(path: str, content: str) -> int:
    """Write string to file, return bytes written."""
    with open(path, "w") as f:
        return f.write(content)


def write_lines(path: str, lines: list[str]) -> None:
    """Write lines to file."""
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")


def writelines(path: str, lines: list[str]) -> None:
    """Write lines using writelines method."""
    with open(path, "w") as f:
        f.writelines(line + "\n" for line in lines)


def append_file(path: str, content: str) -> int:
    """Append string to file."""
    with open(path, "a") as f:
        return f.write(content)


def append_line(path: str, line: str) -> None:
    """Append single line to file."""
    with open(path, "a") as f:
        f.write(line + "\n")


def append_lines(path: str, lines: list[str]) -> None:
    """Append multiple lines to file."""
    with open(path, "a") as f:
        for line in lines:
            f.write(line + "\n")


def write_binary(path: str, data: bytes) -> int:
    """Write binary data to file."""
    with open(path, "wb") as f:
        return f.write(data)


def append_binary(path: str, data: bytes) -> int:
    """Append binary data to file."""
    with open(path, "ab") as f:
        return f.write(data)


def write_csv_simple(path: str, rows: list[list[str]], delimiter: str = ",") -> None:
    """Write simple CSV file."""
    with open(path, "w") as f:
        for row in rows:
            f.write(delimiter.join(row) + "\n")


def write_key_value(path: str, data: dict[str, str], delimiter: str = "=") -> None:
    """Write key-value file."""
    with open(path, "w") as f:
        for key, value in data.items():
            f.write(f"{key}{delimiter}{value}\n")


def copy_file(src: str, dst: str) -> int:
    """Copy file from src to dst."""
    with open(src, "rb") as f_src:
        content = f_src.read()
    with open(dst, "wb") as f_dst:
        return f_dst.write(content)


def truncate_file(path: str, size: int) -> None:
    """Truncate file to size bytes."""
    with open(path, "r+") as f:
        f.truncate(size)


def clear_file(path: str) -> None:
    """Clear file contents."""
    with open(path, "w"):
        pass


def overwrite_line(path: str, line_num: int, new_content: str) -> None:
    """Overwrite specific line in file."""
    with open(path) as f:
        lines = f.readlines()

    if 1 <= line_num <= len(lines):
        lines[line_num - 1] = new_content + "\n"

    with open(path, "w") as f:
        f.writelines(lines)


def insert_line(path: str, line_num: int, content: str) -> None:
    """Insert line at position."""
    with open(path) as f:
        lines = f.readlines()

    lines.insert(line_num - 1, content + "\n")

    with open(path, "w") as f:
        f.writelines(lines)


def delete_line(path: str, line_num: int) -> None:
    """Delete line at position."""
    with open(path) as f:
        lines = f.readlines()

    if 1 <= line_num <= len(lines):
        del lines[line_num - 1]

    with open(path, "w") as f:
        f.writelines(lines)


def replace_in_file(path: str, old: str, new: str) -> int:
    """Replace all occurrences in file, return count."""
    with open(path) as f:
        content = f.read()

    count = content.count(old)
    new_content = content.replace(old, new)

    with open(path, "w") as f:
        f.write(new_content)

    return count


def atomic_write(path: str, content: str) -> None:
    """Atomic write using temp file."""
    temp_path = path + ".tmp"
    with open(temp_path, "w") as f:
        f.write(content)
    # In real code, would use os.rename for atomicity
    with open(temp_path) as f_tmp:
        data = f_tmp.read()
    with open(path, "w") as f:
        f.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="File write CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # write
    write_p = subparsers.add_parser("write", help="Write to file")
    write_p.add_argument("file", help="File path")
    write_p.add_argument("content", help="Content to write")

    # append
    append_p = subparsers.add_parser("append", help="Append to file")
    append_p.add_argument("file", help="File path")
    append_p.add_argument("content", help="Content to append")

    # copy
    copy_p = subparsers.add_parser("copy", help="Copy file")
    copy_p.add_argument("src", help="Source file")
    copy_p.add_argument("dst", help="Destination file")

    # clear
    clear_p = subparsers.add_parser("clear", help="Clear file")
    clear_p.add_argument("file", help="File path")

    # replace
    replace_p = subparsers.add_parser("replace", help="Replace in file")
    replace_p.add_argument("file", help="File path")
    replace_p.add_argument("old", help="Text to replace")
    replace_p.add_argument("new", help="Replacement text")

    # insert
    insert_p = subparsers.add_parser("insert", help="Insert line")
    insert_p.add_argument("file", help="File path")
    insert_p.add_argument("line_num", type=int, help="Line number")
    insert_p.add_argument("content", help="Content to insert")

    # delete
    delete_p = subparsers.add_parser("delete", help="Delete line")
    delete_p.add_argument("file", help="File path")
    delete_p.add_argument("line_num", type=int, help="Line number")

    args = parser.parse_args()

    try:
        if args.command == "write":
            n = write_file(args.file, args.content)
            print(f"Wrote {n} bytes to {args.file}")
        elif args.command == "append":
            n = append_file(args.file, args.content)
            print(f"Appended {n} bytes to {args.file}")
        elif args.command == "copy":
            n = copy_file(args.src, args.dst)
            print(f"Copied {n} bytes from {args.src} to {args.dst}")
        elif args.command == "clear":
            clear_file(args.file)
            print(f"Cleared {args.file}")
        elif args.command == "replace":
            count = replace_in_file(args.file, args.old, args.new)
            print(f"Replaced {count} occurrences")
        elif args.command == "insert":
            insert_line(args.file, args.line_num, args.content)
            print(f"Inserted line at {args.line_num}")
        elif args.command == "delete":
            delete_line(args.file, args.line_num)
            print(f"Deleted line {args.line_num}")
        else:
            parser.print_help()

    except (FileNotFoundError, PermissionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
