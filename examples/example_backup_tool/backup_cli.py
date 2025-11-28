#!/usr/bin/env python3
"""Simple backup tool CLI.

Create and restore file backups with timestamps.
"""

import argparse
import hashlib
import os
import shutil
import sys
from datetime import datetime


def get_timestamp() -> str:
    """Get current timestamp for backup naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def parse_timestamp(name: str) -> datetime | None:
    """Parse timestamp from backup name."""
    # Extract timestamp pattern YYYYMMDD_HHMMSS_ffffff
    parts = name.split("_")
    if len(parts) < 3:
        return None
    try:
        date_part = parts[-3]
        time_part = parts[-2]
        micro_part = parts[-1].split(".")[0]  # Remove extension
        return datetime.strptime(f"{date_part}_{time_part}_{micro_part}", "%Y%m%d_%H%M%S_%f")
    except (ValueError, IndexError):
        return None


def get_file_checksum(path: str) -> str:
    """Calculate SHA256 checksum of file."""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]  # Short checksum
    except OSError:
        return ""


def create_backup_name(source: str, backup_dir: str) -> str:
    """Create backup filename with timestamp."""
    basename = os.path.basename(source)
    name, ext = os.path.splitext(basename)
    timestamp = get_timestamp()
    backup_name = f"{name}_{timestamp}{ext}"
    return os.path.join(backup_dir, backup_name)


def backup_file(source: str, backup_dir: str, verify: bool = False) -> str:
    """Create a backup of a file.

    Returns backup path on success, empty string on failure.
    """
    if not os.path.isfile(source):
        return ""

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    backup_path = create_backup_name(source, backup_dir)

    try:
        shutil.copy2(source, backup_path)

        if verify:
            src_checksum = get_file_checksum(source)
            bak_checksum = get_file_checksum(backup_path)
            if src_checksum != bak_checksum:
                os.remove(backup_path)
                return ""

        return backup_path
    except OSError:
        return ""


def list_backups(backup_dir: str, pattern: str = "") -> list[tuple[str, datetime]]:
    """List backups in directory, optionally filtered by pattern.

    Returns list of (path, timestamp) tuples sorted by date.
    """
    if not os.path.isdir(backup_dir):
        return []

    backups = []
    for entry in os.listdir(backup_dir):
        if pattern and pattern not in entry:
            continue

        path = os.path.join(backup_dir, entry)
        if not os.path.isfile(path):
            continue

        timestamp = parse_timestamp(entry)
        if timestamp:
            backups.append((path, timestamp))

    return sorted(backups, key=lambda x: x[1], reverse=True)


def get_latest_backup(backup_dir: str, pattern: str = "") -> str:
    """Get the most recent backup matching pattern."""
    backups = list_backups(backup_dir, pattern)
    if not backups:
        return ""
    return backups[0][0]


def restore_backup(backup_path: str, dest: str, verify: bool = False) -> bool:
    """Restore a backup to destination."""
    if not os.path.isfile(backup_path):
        return False

    try:
        shutil.copy2(backup_path, dest)

        if verify:
            src_checksum = get_file_checksum(backup_path)
            dst_checksum = get_file_checksum(dest)
            if src_checksum != dst_checksum:
                return False

        return True
    except OSError:
        return False


def prune_backups(backup_dir: str, pattern: str, keep: int) -> int:
    """Remove old backups, keeping only the most recent N.

    Returns number of backups removed.
    """
    backups = list_backups(backup_dir, pattern)

    if len(backups) <= keep:
        return 0

    removed = 0
    for path, _ in backups[keep:]:
        try:
            os.remove(path)
            removed += 1
        except OSError:
            pass

    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple file backup tool")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create a backup")
    backup_parser.add_argument("source", help="File to backup")
    backup_parser.add_argument("-d", "--dest", default="./backups", help="Backup directory")
    backup_parser.add_argument("--verify", action="store_true", help="Verify backup checksum")

    # List command
    list_parser = subparsers.add_parser("list", help="List backups")
    list_parser.add_argument("-d", "--dir", default="./backups", help="Backup directory")
    list_parser.add_argument("-p", "--pattern", default="", help="Filter by pattern")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore a backup")
    restore_parser.add_argument("backup", help="Backup file or 'latest'")
    restore_parser.add_argument("dest", help="Destination path")
    restore_parser.add_argument("-d", "--dir", default="./backups", help="Backup directory")
    restore_parser.add_argument("-p", "--pattern", default="", help="Pattern for latest lookup")
    restore_parser.add_argument("--verify", action="store_true", help="Verify restore checksum")

    # Prune command
    prune_parser = subparsers.add_parser("prune", help="Remove old backups")
    prune_parser.add_argument("-d", "--dir", default="./backups", help="Backup directory")
    prune_parser.add_argument("-p", "--pattern", default="", help="Filter by pattern")
    prune_parser.add_argument("-k", "--keep", type=int, default=5, help="Number of backups to keep")

    args = parser.parse_args()

    if args.command == "backup":
        result = backup_file(args.source, args.dest, args.verify)
        if result:
            print(f"Created backup: {result}")
            return 0
        print("Backup failed", file=sys.stderr)
        return 1

    elif args.command == "list":
        backups = list_backups(args.dir, args.pattern)
        if not backups:
            print("No backups found")
            return 0
        for path, timestamp in backups:
            name = os.path.basename(path)
            size = os.path.getsize(path)
            print(f"{timestamp.isoformat()} {size:>10} {name}")
        return 0

    elif args.command == "restore":
        if args.backup == "latest":
            backup_path = get_latest_backup(args.dir, args.pattern)
            if not backup_path:
                print("No backups found", file=sys.stderr)
                return 1
        else:
            backup_path = args.backup

        if restore_backup(backup_path, args.dest, args.verify):
            print(f"Restored {backup_path} to {args.dest}")
            return 0
        print("Restore failed", file=sys.stderr)
        return 1

    elif args.command == "prune":
        removed = prune_backups(args.dir, args.pattern, args.keep)
        print(f"Removed {removed} old backups")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
