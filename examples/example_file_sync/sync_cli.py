#!/usr/bin/env python3
"""File synchronization CLI.

Sync files between directories with comparison modes.
"""

import argparse
import hashlib
import os
import shutil
import sys


def get_file_hash(path: str) -> str:
    """Calculate MD5 hash of file."""
    hasher = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return ""


def get_file_mtime(path: str) -> float:
    """Get file modification time."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def list_files(directory: str) -> list[str]:
    """List all files in directory recursively."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, directory)
            files.append(rel_path)
    return sorted(files)


def compare_files(src: str, dst: str, use_hash: bool = False) -> bool:
    """Compare two files. Returns True if different."""
    if not os.path.exists(dst):
        return True

    src_size = os.path.getsize(src)
    dst_size = os.path.getsize(dst)

    if src_size != dst_size:
        return True

    if use_hash:
        return get_file_hash(src) != get_file_hash(dst)

    # Compare by mtime
    return get_file_mtime(src) > get_file_mtime(dst)


def find_changes(
    src_dir: str,
    dst_dir: str,
    use_hash: bool = False,
) -> tuple[list[str], list[str], list[str]]:
    """Find files to add, update, and delete.

    Returns (to_add, to_update, to_delete).
    """
    src_files = set(list_files(src_dir))
    dst_files = set(list_files(dst_dir))

    to_add = list(src_files - dst_files)
    to_delete = list(dst_files - src_files)
    to_update = []

    for f in src_files & dst_files:
        src_path = os.path.join(src_dir, f)
        dst_path = os.path.join(dst_dir, f)
        if compare_files(src_path, dst_path, use_hash):
            to_update.append(f)

    return sorted(to_add), sorted(to_update), sorted(to_delete)


def sync_file(src: str, dst: str, dry_run: bool = False) -> bool:
    """Copy file from src to dst."""
    if dry_run:
        return True

    try:
        dst_dir = os.path.dirname(dst)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        shutil.copy2(src, dst)
        return True
    except OSError:
        return False


def delete_file(path: str, dry_run: bool = False) -> bool:
    """Delete a file."""
    if dry_run:
        return True
    try:
        os.remove(path)
        return True
    except OSError:
        return False


def sync_directories(
    src_dir: str,
    dst_dir: str,
    delete: bool = False,
    use_hash: bool = False,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Sync src_dir to dst_dir.

    Returns (added, updated, deleted).
    """
    to_add, to_update, to_delete = find_changes(src_dir, dst_dir, use_hash)

    added = 0
    updated = 0
    deleted = 0

    for f in to_add:
        src = os.path.join(src_dir, f)
        dst = os.path.join(dst_dir, f)
        if sync_file(src, dst, dry_run):
            added += 1

    for f in to_update:
        src = os.path.join(src_dir, f)
        dst = os.path.join(dst_dir, f)
        if sync_file(src, dst, dry_run):
            updated += 1

    if delete:
        for f in to_delete:
            dst = os.path.join(dst_dir, f)
            if delete_file(dst, dry_run):
                deleted += 1

    return added, updated, deleted


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize files between directories")
    parser.add_argument("source", help="Source directory")
    parser.add_argument("dest", help="Destination directory")
    parser.add_argument("--delete", action="store_true", help="Delete files in dest not in source")
    parser.add_argument("--hash", action="store_true", help="Use hash comparison instead of mtime")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--status", action="store_true", help="Show status without syncing")

    args = parser.parse_args()

    if not os.path.isdir(args.source):
        print(f"Error: {args.source} is not a directory", file=sys.stderr)
        return 1

    if args.status:
        if not os.path.isdir(args.dest):
            print(f"Destination does not exist: {args.dest}")
            return 0

        to_add, to_update, to_delete = find_changes(args.source, args.dest, args.hash)
        print(f"To add: {len(to_add)} files")
        for f in to_add:
            print(f"  + {f}")
        print(f"To update: {len(to_update)} files")
        for f in to_update:
            print(f"  ~ {f}")
        print(f"Would delete: {len(to_delete)} files")
        for f in to_delete:
            print(f"  - {f}")
        return 0

    # Create dest if it doesn't exist
    if not os.path.exists(args.dest):
        if not args.dry_run:
            os.makedirs(args.dest)

    added, updated, deleted = sync_directories(
        args.source,
        args.dest,
        delete=args.delete,
        use_hash=args.hash,
        dry_run=args.dry_run,
    )

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"{prefix}Added: {added}, Updated: {updated}, Deleted: {deleted}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
