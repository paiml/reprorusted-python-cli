#!/usr/bin/env python3
"""Directory tree walker CLI.

Display and analyze directory structures.
"""

import argparse
import os
import sys


def get_file_size(path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def format_size(size: int) -> str:
    """Format size in human-readable format."""
    if size < 1024:
        return f"{size}B"
    if size < 1024 * 1024:
        return f"{size // 1024}K"
    if size < 1024 * 1024 * 1024:
        return f"{size // (1024 * 1024)}M"
    return f"{size // (1024 * 1024 * 1024)}G"


def walk_directory(
    path: str,
    max_depth: int = -1,
    show_hidden: bool = False,
    dirs_only: bool = False,
) -> list[tuple[str, int, bool]]:
    """Walk directory and return list of (path, depth, is_dir)."""
    result = []

    def walk(current_path: str, depth: int) -> None:
        if max_depth >= 0 and depth > max_depth:
            return

        try:
            entries = os.listdir(current_path)
        except PermissionError:
            return

        entries.sort()

        for entry in entries:
            if not show_hidden and entry.startswith("."):
                continue

            full_path = os.path.join(current_path, entry)
            is_dir = os.path.isdir(full_path)

            if dirs_only and not is_dir:
                continue

            result.append((full_path, depth, is_dir))

            if is_dir:
                walk(full_path, depth + 1)

    walk(path, 0)
    return result


def format_tree(
    entries: list[tuple[str, int, bool]],
    base_path: str,
    show_size: bool = False,
) -> list[str]:
    """Format entries as tree with box-drawing characters."""
    lines = []
    base_len = len(base_path.rstrip("/")) + 1

    for i, (path, depth, is_dir) in enumerate(entries):
        name = path[base_len:]
        parts = name.split("/")
        display_name = parts[-1]

        # Determine prefix
        prefix = ""
        for _d in range(depth):
            prefix += "│   "

        # Check if last at this depth
        is_last = True
        for j in range(i + 1, len(entries)):
            if entries[j][1] == depth:
                is_last = False
                break
            if entries[j][1] < depth:
                break

        if is_last:
            prefix += "└── "
        else:
            prefix += "├── "

        # Format line
        if show_size and not is_dir:
            size = get_file_size(path)
            line = f"{prefix}{display_name} ({format_size(size)})"
        else:
            line = f"{prefix}{display_name}"
            if is_dir:
                line += "/"

        lines.append(line)

    return lines


def count_entries(entries: list[tuple[str, int, bool]]) -> tuple[int, int]:
    """Count directories and files."""
    dirs = sum(1 for _, _, is_dir in entries if is_dir)
    files = sum(1 for _, _, is_dir in entries if not is_dir)
    return dirs, files


def total_size(entries: list[tuple[str, int, bool]]) -> int:
    """Calculate total size of all files."""
    total = 0
    for path, _, is_dir in entries:
        if not is_dir:
            total += get_file_size(path)
    return total


def filter_by_extension(
    entries: list[tuple[str, int, bool]], ext: str
) -> list[tuple[str, int, bool]]:
    """Filter entries by file extension."""
    if not ext.startswith("."):
        ext = "." + ext
    return [
        (path, depth, is_dir) for path, depth, is_dir in entries if is_dir or path.endswith(ext)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Display directory tree structure")
    parser.add_argument("path", nargs="?", default=".", help="Directory to display")
    parser.add_argument(
        "-d", "--depth", type=int, default=-1, help="Maximum depth (-1 for unlimited)"
    )
    parser.add_argument("-a", "--all", action="store_true", help="Show hidden files")
    parser.add_argument("--dirs", action="store_true", help="Show directories only")
    parser.add_argument("-s", "--size", action="store_true", help="Show file sizes")
    parser.add_argument("--ext", metavar="EXT", help="Filter by extension")
    parser.add_argument("--count", action="store_true", help="Show count summary only")
    parser.add_argument("--total-size", action="store_true", help="Show total size only")

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: {args.path} is not a directory", file=sys.stderr)
        return 1

    entries = walk_directory(
        args.path,
        max_depth=args.depth,
        show_hidden=args.all,
        dirs_only=args.dirs,
    )

    if args.ext:
        entries = filter_by_extension(entries, args.ext)

    # Output
    if args.count:
        dirs, files = count_entries(entries)
        print(f"{dirs} directories, {files} files")
    elif args.total_size:
        size = total_size(entries)
        print(format_size(size))
    else:
        print(args.path)
        for line in format_tree(entries, args.path, show_size=args.size):
            print(line)
        dirs, files = count_entries(entries)
        print(f"\n{dirs} directories, {files} files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
