#!/usr/bin/env python3
"""Pathlib Operations CLI.

Directory and file operations using Python's pathlib module.
"""

import argparse
import sys
from pathlib import Path


def mkdir(path: Path, parents: bool = False, exist_ok: bool = False) -> bool:
    """Create directory."""
    try:
        path.mkdir(parents=parents, exist_ok=exist_ok)
        return True
    except FileExistsError:
        return False
    except FileNotFoundError:
        return False


def rmdir(path: Path) -> bool:
    """Remove empty directory."""
    try:
        path.rmdir()
        return True
    except (FileNotFoundError, OSError):
        return False


def unlink(path: Path, missing_ok: bool = False) -> bool:
    """Remove file."""
    try:
        path.unlink(missing_ok=missing_ok)
        return True
    except FileNotFoundError:
        return False


def rename(src: Path, dst: Path) -> Path:
    """Rename file or directory."""
    return src.rename(dst)


def replace(src: Path, dst: Path) -> Path:
    """Replace file or directory."""
    return src.replace(dst)


def touch(path: Path, exist_ok: bool = True) -> bool:
    """Create file or update timestamp."""
    try:
        path.touch(exist_ok=exist_ok)
        return True
    except FileExistsError:
        return False


def glob_pattern(path: Path, pattern: str) -> list[Path]:
    """Find files matching pattern."""
    return list(path.glob(pattern))


def rglob_pattern(path: Path, pattern: str) -> list[Path]:
    """Recursively find files matching pattern."""
    return list(path.rglob(pattern))


def iterdir(path: Path) -> list[Path]:
    """List directory contents."""
    return list(path.iterdir())


def list_files(path: Path) -> list[Path]:
    """List only files in directory."""
    return [p for p in path.iterdir() if p.is_file()]


def list_dirs(path: Path) -> list[Path]:
    """List only directories in directory."""
    return [p for p in path.iterdir() if p.is_dir()]


def stat_size(path: Path) -> int:
    """Get file size in bytes."""
    return path.stat().st_size


def stat_mtime(path: Path) -> float:
    """Get modification time."""
    return path.stat().st_mtime


def stat_mode(path: Path) -> int:
    """Get file mode/permissions."""
    return path.stat().st_mode


def chmod(path: Path, mode: int) -> None:
    """Change file permissions."""
    path.chmod(mode)


def samefile(path1: Path, path2: Path) -> bool:
    """Check if two paths point to same file."""
    return path1.samefile(path2)


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """Read file as text."""
    return path.read_text(encoding=encoding)


def write_text(path: Path, content: str, encoding: str = "utf-8") -> int:
    """Write text to file."""
    return path.write_text(content, encoding=encoding)


def read_bytes(path: Path) -> bytes:
    """Read file as bytes."""
    return path.read_bytes()


def write_bytes(path: Path, data: bytes) -> int:
    """Write bytes to file."""
    return path.write_bytes(data)


def owner(path: Path) -> str:
    """Get file owner name."""
    return path.owner()


def group(path: Path) -> str:
    """Get file group name."""
    return path.group()


def hardlink_to(src: Path, dst: Path) -> None:
    """Create hard link."""
    dst.hardlink_to(src)


def symlink_to(link: Path, target: Path) -> None:
    """Create symbolic link."""
    link.symlink_to(target)


def readlink(path: Path) -> Path:
    """Read symbolic link target."""
    return path.readlink()


def count_files(path: Path, pattern: str = "*") -> int:
    """Count files matching pattern."""
    return len([p for p in path.glob(pattern) if p.is_file()])


def count_dirs(path: Path) -> int:
    """Count subdirectories."""
    return len([p for p in path.iterdir() if p.is_dir()])


def total_size(path: Path) -> int:
    """Get total size of all files in directory."""
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def find_by_suffix(path: Path, suffix: str) -> list[Path]:
    """Find all files with given suffix."""
    return [p for p in path.rglob("*") if p.suffix == suffix]


def find_by_name(path: Path, name: str) -> list[Path]:
    """Find all files with given name."""
    return [p for p in path.rglob("*") if p.name == name]


def walk_dir(path: Path) -> list[tuple[Path, list[str], list[str]]]:
    """Walk directory tree (similar to os.walk)."""
    result = []
    dirs = [d.name for d in path.iterdir() if d.is_dir()]
    files = [f.name for f in path.iterdir() if f.is_file()]
    result.append((path, dirs, files))
    for d in path.iterdir():
        if d.is_dir():
            result.extend(walk_dir(d))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Pathlib operations CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # mkdir
    mkdir_p = subparsers.add_parser("mkdir", help="Create directory")
    mkdir_p.add_argument("path", help="Directory path")
    mkdir_p.add_argument("-p", "--parents", action="store_true", help="Create parents")
    mkdir_p.add_argument("--exist-ok", action="store_true", help="OK if exists")

    # rmdir
    rmdir_p = subparsers.add_parser("rmdir", help="Remove directory")
    rmdir_p.add_argument("path", help="Directory path")

    # touch
    touch_p = subparsers.add_parser("touch", help="Create file")
    touch_p.add_argument("path", help="File path")

    # rm
    rm_p = subparsers.add_parser("rm", help="Remove file")
    rm_p.add_argument("path", help="File path")
    rm_p.add_argument("-f", "--force", action="store_true", help="Ignore missing")

    # mv
    mv_p = subparsers.add_parser("mv", help="Move/rename")
    mv_p.add_argument("src", help="Source path")
    mv_p.add_argument("dst", help="Destination path")

    # ls
    ls_p = subparsers.add_parser("ls", help="List directory")
    ls_p.add_argument("path", nargs="?", default=".", help="Directory path")
    ls_p.add_argument("-d", "--dirs", action="store_true", help="Only dirs")
    ls_p.add_argument("-f", "--files", action="store_true", help="Only files")

    # glob
    glob_p = subparsers.add_parser("glob", help="Find files")
    glob_p.add_argument("path", help="Base directory")
    glob_p.add_argument("pattern", help="Glob pattern")
    glob_p.add_argument("-r", "--recursive", action="store_true", help="Recursive")

    # stat
    stat_p = subparsers.add_parser("stat", help="File info")
    stat_p.add_argument("path", help="File path")

    # count
    count_p = subparsers.add_parser("count", help="Count files")
    count_p.add_argument("path", help="Directory path")
    count_p.add_argument("-p", "--pattern", default="*", help="Pattern")

    args = parser.parse_args()

    if args.command == "mkdir":
        path = Path(args.path)
        if mkdir(path, parents=args.parents, exist_ok=args.exist_ok):
            print(f"Created: {path}")
        else:
            print(f"Failed to create: {path}")
            return 1

    elif args.command == "rmdir":
        path = Path(args.path)
        if rmdir(path):
            print(f"Removed: {path}")
        else:
            print(f"Failed to remove: {path}")
            return 1

    elif args.command == "touch":
        path = Path(args.path)
        if touch(path):
            print(f"Touched: {path}")
        else:
            print(f"Failed to touch: {path}")
            return 1

    elif args.command == "rm":
        path = Path(args.path)
        if unlink(path, missing_ok=args.force):
            print(f"Removed: {path}")
        else:
            print(f"Failed to remove: {path}")
            return 1

    elif args.command == "mv":
        src = Path(args.src)
        dst = Path(args.dst)
        result = rename(src, dst)
        print(f"Moved: {src} -> {result}")

    elif args.command == "ls":
        path = Path(args.path)
        if args.dirs:
            items = list_dirs(path)
        elif args.files:
            items = list_files(path)
        else:
            items = iterdir(path)
        for item in sorted(items):
            print(item.name)

    elif args.command == "glob":
        path = Path(args.path)
        if args.recursive:
            matches = rglob_pattern(path, args.pattern)
        else:
            matches = glob_pattern(path, args.pattern)
        for m in sorted(matches):
            print(m)

    elif args.command == "stat":
        path = Path(args.path)
        print(f"Size: {stat_size(path)} bytes")
        print(f"Mode: {oct(stat_mode(path))}")
        print(f"Modified: {stat_mtime(path)}")

    elif args.command == "count":
        path = Path(args.path)
        files = count_files(path, args.pattern)
        dirs = count_dirs(path)
        print(f"Files: {files}")
        print(f"Directories: {dirs}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
