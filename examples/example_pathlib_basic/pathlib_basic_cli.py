#!/usr/bin/env python3
"""Pathlib Basic CLI.

Basic path operations using Python's pathlib module.
"""

import argparse
import sys
from pathlib import Path


def create_path(path_str: str) -> Path:
    """Create Path object from string."""
    return Path(path_str)


def get_name(path: Path) -> str:
    """Get file name."""
    return path.name


def get_stem(path: Path) -> str:
    """Get file name without suffix."""
    return path.stem


def get_suffix(path: Path) -> str:
    """Get file suffix/extension."""
    return path.suffix


def get_suffixes(path: Path) -> list[str]:
    """Get all suffixes (e.g., .tar.gz)."""
    return path.suffixes


def get_parent(path: Path) -> Path:
    """Get parent directory."""
    return path.parent


def get_parents(path: Path) -> list[Path]:
    """Get all parent directories."""
    return list(path.parents)


def get_parts(path: Path) -> tuple[str, ...]:
    """Get path components."""
    return path.parts


def get_anchor(path: Path) -> str:
    """Get anchor (root + drive)."""
    return path.anchor


def get_root(path: Path) -> str:
    """Get root."""
    return path.root


def is_absolute(path: Path) -> bool:
    """Check if path is absolute."""
    return path.is_absolute()


def is_relative(path: Path) -> bool:
    """Check if path is relative."""
    return not path.is_absolute()


def exists(path: Path) -> bool:
    """Check if path exists."""
    return path.exists()


def is_file(path: Path) -> bool:
    """Check if path is a file."""
    return path.is_file()


def is_dir(path: Path) -> bool:
    """Check if path is a directory."""
    return path.is_dir()


def is_symlink(path: Path) -> bool:
    """Check if path is a symlink."""
    return path.is_symlink()


def resolve(path: Path) -> Path:
    """Resolve path to absolute."""
    return path.resolve()


def expanduser(path: Path) -> Path:
    """Expand ~ to home directory."""
    return path.expanduser()


def absolute(path: Path) -> Path:
    """Get absolute path."""
    return path.absolute()


def join_paths(base: Path, *parts: str) -> Path:
    """Join path components."""
    result = base
    for part in parts:
        result = result / part
    return result


def with_name(path: Path, name: str) -> Path:
    """Return path with different name."""
    return path.with_name(name)


def with_stem(path: Path, stem: str) -> Path:
    """Return path with different stem."""
    return path.with_stem(stem)


def with_suffix(path: Path, suffix: str) -> Path:
    """Return path with different suffix."""
    return path.with_suffix(suffix)


def relative_to(path: Path, other: Path) -> Path:
    """Get path relative to other."""
    return path.relative_to(other)


def is_relative_to(path: Path, other: Path) -> bool:
    """Check if path is relative to other."""
    return path.is_relative_to(other)


def match_pattern(path: Path, pattern: str) -> bool:
    """Check if path matches pattern."""
    return path.match(pattern)


def as_posix(path: Path) -> str:
    """Return path with forward slashes."""
    return path.as_posix()


def as_uri(path: Path) -> str:
    """Return path as file:// URI."""
    return path.as_uri()


def home_dir() -> Path:
    """Get home directory."""
    return Path.home()


def cwd() -> Path:
    """Get current working directory."""
    return Path.cwd()


def parse_path_info(path_str: str) -> dict:
    """Parse path and return all components."""
    path = Path(path_str)
    return {
        "path": str(path),
        "name": path.name,
        "stem": path.stem,
        "suffix": path.suffix,
        "suffixes": path.suffixes,
        "parent": str(path.parent),
        "parts": path.parts,
        "is_absolute": path.is_absolute(),
        "anchor": path.anchor,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pathlib basic CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # info
    info_p = subparsers.add_parser("info", help="Show path info")
    info_p.add_argument("path", help="Path to analyze")

    # exists
    exists_p = subparsers.add_parser("exists", help="Check if exists")
    exists_p.add_argument("path", help="Path to check")

    # type
    type_p = subparsers.add_parser("type", help="Check path type")
    type_p.add_argument("path", help="Path to check")

    # join
    join_p = subparsers.add_parser("join", help="Join paths")
    join_p.add_argument("paths", nargs="+", help="Paths to join")

    # parent
    parent_p = subparsers.add_parser("parent", help="Get parent")
    parent_p.add_argument("path", help="Path")
    parent_p.add_argument("-n", type=int, default=1, help="Levels up")

    # name
    name_p = subparsers.add_parser("name", help="Get name/stem/suffix")
    name_p.add_argument("path", help="Path")

    # resolve
    resolve_p = subparsers.add_parser("resolve", help="Resolve path")
    resolve_p.add_argument("path", help="Path to resolve")

    # home
    subparsers.add_parser("home", help="Show home directory")

    # cwd
    subparsers.add_parser("cwd", help="Show current directory")

    args = parser.parse_args()

    if args.command == "info":
        info = parse_path_info(args.path)
        for key, value in info.items():
            print(f"{key}: {value}")

    elif args.command == "exists":
        path = Path(args.path)
        if path.exists():
            print(f"'{args.path}' exists")
        else:
            print(f"'{args.path}' does not exist")

    elif args.command == "type":
        path = Path(args.path)
        if not path.exists():
            print("Does not exist")
        elif path.is_file():
            print("File")
        elif path.is_dir():
            print("Directory")
        elif path.is_symlink():
            print("Symlink")
        else:
            print("Other")

    elif args.command == "join":
        result = Path(args.paths[0])
        for p in args.paths[1:]:
            result = result / p
        print(result)

    elif args.command == "parent":
        path = Path(args.path)
        for _ in range(args.n):
            path = path.parent
        print(path)

    elif args.command == "name":
        path = Path(args.path)
        print(f"Name: {path.name}")
        print(f"Stem: {path.stem}")
        print(f"Suffix: {path.suffix}")

    elif args.command == "resolve":
        path = Path(args.path)
        print(path.resolve())

    elif args.command == "home":
        print(home_dir())

    elif args.command == "cwd":
        print(cwd())

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
