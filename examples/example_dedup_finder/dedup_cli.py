#!/usr/bin/env python3
"""Duplicate file finder CLI.

Find and manage duplicate files based on content.
"""

import argparse
import hashlib
import os
import sys


def get_file_hash(path: str, quick: bool = False) -> str:
    """Calculate hash of file content.

    If quick=True, only hash first 64KB for speed.
    """
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            if quick:
                chunk = f.read(65536)
                hasher.update(chunk)
            else:
                while chunk := f.read(65536):
                    hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return ""


def get_file_size(path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def scan_directory(
    path: str,
    min_size: int = 0,
    extensions: list[str] | None = None,
) -> list[str]:
    """Scan directory for files matching criteria."""
    files = []

    for root, _, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(root, filename)

            # Check extension filter
            if extensions:
                _, ext = os.path.splitext(filename)
                if ext.lower() not in extensions:
                    continue

            # Check size filter
            size = get_file_size(full_path)
            if size < min_size:
                continue

            files.append(full_path)

    return files


def group_by_size(files: list[str]) -> dict[int, list[str]]:
    """Group files by size."""
    groups: dict[int, list[str]] = {}

    for path in files:
        size = get_file_size(path)
        if size < 0:
            continue
        if size not in groups:
            groups[size] = []
        groups[size].append(path)

    return groups


def find_duplicates(
    files: list[str],
    quick: bool = False,
) -> list[list[str]]:
    """Find duplicate files by content.

    Returns list of duplicate groups.
    """
    # First group by size (fast filter)
    size_groups = group_by_size(files)

    # Only check files with matching sizes
    candidates = []
    for size, paths in size_groups.items():
        if len(paths) > 1 and size > 0:
            candidates.extend(paths)

    # Group by hash
    hash_groups: dict[str, list[str]] = {}

    for path in candidates:
        file_hash = get_file_hash(path, quick)
        if not file_hash:
            continue
        if file_hash not in hash_groups:
            hash_groups[file_hash] = []
        hash_groups[file_hash].append(path)

    # Return groups with duplicates
    return [paths for paths in hash_groups.values() if len(paths) > 1]


def calculate_waste(duplicates: list[list[str]]) -> int:
    """Calculate wasted space from duplicates."""
    total = 0
    for group in duplicates:
        if len(group) < 2:
            continue
        size = get_file_size(group[0])
        # All copies except one are "waste"
        total += size * (len(group) - 1)
    return total


def format_size(size: int) -> str:
    """Format size in human-readable format."""
    if size < 1024:
        return f"{size}B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f}MB"
    return f"{size / (1024 * 1024 * 1024):.1f}GB"


def get_keep_candidate(group: list[str]) -> str:
    """Determine which file to keep (shortest path)."""
    return min(group, key=len)


def format_duplicates(
    duplicates: list[list[str]],
    base_path: str = "",
) -> list[str]:
    """Format duplicates for display."""
    lines = []

    for i, group in enumerate(duplicates, 1):
        size = get_file_size(group[0])
        lines.append(f"Group {i} ({format_size(size)}, {len(group)} files):")

        keep = get_keep_candidate(group)
        for path in sorted(group):
            if base_path:
                display = os.path.relpath(path, base_path)
            else:
                display = path

            marker = "  [keep]" if path == keep else "  [dup]"
            lines.append(f"  {marker} {display}")

        lines.append("")

    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Find duplicate files by content")
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("--min-size", type=int, default=1, help="Minimum file size in bytes")
    parser.add_argument("--ext", action="append", help="Filter by extension (can repeat)")
    parser.add_argument("--quick", action="store_true", help="Quick mode (hash only first 64KB)")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: {args.path} is not a directory", file=sys.stderr)
        return 1

    # Normalize extensions
    extensions = None
    if args.ext:
        extensions = [e if e.startswith(".") else f".{e}" for e in args.ext]
        extensions = [e.lower() for e in extensions]

    # Scan and find duplicates
    files = scan_directory(args.path, args.min_size, extensions)
    duplicates = find_duplicates(files, args.quick)

    if args.json:
        import json

        output = {
            "groups": duplicates,
            "total_groups": len(duplicates),
            "total_duplicates": sum(len(g) - 1 for g in duplicates),
            "wasted_bytes": calculate_waste(duplicates),
        }
        print(json.dumps(output, indent=2))
        return 0

    if args.summary:
        total_files = sum(len(g) for g in duplicates)
        waste = calculate_waste(duplicates)
        print(f"Duplicate groups: {len(duplicates)}")
        print(f"Total duplicate files: {total_files}")
        print(f"Wasted space: {format_size(waste)}")
        return 0

    # Full output
    if not duplicates:
        print("No duplicates found")
        return 0

    for line in format_duplicates(duplicates, args.path):
        print(line)

    waste = calculate_waste(duplicates)
    print(f"Total wasted space: {format_size(waste)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
