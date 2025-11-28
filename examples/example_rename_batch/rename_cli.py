#!/usr/bin/env python3
"""Batch file rename CLI.

Rename files using patterns and transformations.
"""

import argparse
import os
import re
import sys


def apply_pattern(
    filename: str,
    find: str,
    replace: str,
    use_regex: bool = False,
) -> str:
    """Apply find/replace pattern to filename."""
    if use_regex:
        return re.sub(find, replace, filename)
    return filename.replace(find, replace)


def apply_case(filename: str, case: str) -> str:
    """Apply case transformation to filename."""
    name, ext = os.path.splitext(filename)

    if case == "lower":
        return name.lower() + ext.lower()
    elif case == "upper":
        return name.upper() + ext.upper()
    elif case == "title":
        return name.title() + ext.lower()
    elif case == "snake":
        # Convert CamelCase or spaces to snake_case
        s = re.sub(r"([A-Z])", r"_\1", name)
        s = re.sub(r"[\s-]+", "_", s)
        s = re.sub(r"_+", "_", s)
        return s.strip("_").lower() + ext.lower()
    elif case == "kebab":
        # Convert to kebab-case
        s = re.sub(r"([A-Z])", r"-\1", name)
        s = re.sub(r"[\s_]+", "-", s)
        s = re.sub(r"-+", "-", s)
        return s.strip("-").lower() + ext.lower()

    return filename


def apply_numbering(
    filename: str,
    index: int,
    start: int = 1,
    width: int = 3,
    position: str = "prefix",
) -> str:
    """Add number to filename."""
    name, ext = os.path.splitext(filename)
    num = str(index + start).zfill(width)

    if position == "prefix":
        return f"{num}_{name}{ext}"
    elif position == "suffix":
        return f"{name}_{num}{ext}"

    return filename


def apply_trim(filename: str, chars: int, position: str = "start") -> str:
    """Trim characters from filename."""
    name, ext = os.path.splitext(filename)

    if position == "start":
        name = name[chars:]
    elif position == "end":
        name = name[:-chars] if chars > 0 else name

    return name + ext


def apply_extension(filename: str, new_ext: str) -> str:
    """Change file extension."""
    name, _ = os.path.splitext(filename)
    if not new_ext.startswith("."):
        new_ext = "." + new_ext
    return name + new_ext


def preview_rename(
    files: list[str],
    transform_fn,
) -> list[tuple[str, str]]:
    """Preview renames without applying.

    Returns list of (old_name, new_name) tuples.
    """
    result = []
    for i, filepath in enumerate(files):
        dirname = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        new_filename = transform_fn(filename, i)

        if new_filename != filename:
            new_path = os.path.join(dirname, new_filename)
            result.append((filepath, new_path))

    return result


def check_conflicts(renames: list[tuple[str, str]]) -> list[str]:
    """Check for naming conflicts."""
    conflicts = []
    new_names = {}

    for old, new in renames:
        if new in new_names:
            conflicts.append(f"Conflict: {old} and {new_names[new]} -> {new}")
        new_names[new] = old

        if os.path.exists(new) and new not in [old for old, _ in renames]:
            conflicts.append(f"Target exists: {new}")

    return conflicts


def execute_renames(
    renames: list[tuple[str, str]],
    dry_run: bool = False,
) -> tuple[int, int]:
    """Execute renames.

    Returns (success_count, error_count).
    """
    success = 0
    errors = 0

    for old, new in renames:
        if dry_run:
            success += 1
            continue

        try:
            # Create target directory if needed
            new_dir = os.path.dirname(new)
            if new_dir and not os.path.exists(new_dir):
                os.makedirs(new_dir)

            os.rename(old, new)
            success += 1
        except OSError:
            errors += 1

    return success, errors


def list_files(
    directory: str,
    pattern: str = "",
    recursive: bool = False,
) -> list[str]:
    """List files in directory."""
    files = []

    if recursive:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if pattern and not re.search(pattern, filename):
                    continue
                files.append(os.path.join(root, filename))
    else:
        for entry in os.listdir(directory):
            path = os.path.join(directory, entry)
            if not os.path.isfile(path):
                continue
            if pattern and not re.search(pattern, entry):
                continue
            files.append(path)

    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch rename files")
    parser.add_argument("path", nargs="?", default=".", help="Directory or file")
    parser.add_argument("--find", metavar="PATTERN", help="Find pattern")
    parser.add_argument("--replace", metavar="STRING", default="", help="Replace with")
    parser.add_argument("-E", "--regex", action="store_true", help="Use regex for find/replace")
    parser.add_argument(
        "--case", choices=["lower", "upper", "title", "snake", "kebab"], help="Change case"
    )
    parser.add_argument("--number", action="store_true", help="Add sequential numbers")
    parser.add_argument("--number-start", type=int, default=1, help="Starting number")
    parser.add_argument("--number-width", type=int, default=3, help="Number padding width")
    parser.add_argument(
        "--number-pos", choices=["prefix", "suffix"], default="prefix", help="Number position"
    )
    parser.add_argument("--trim-start", type=int, help="Trim N chars from start")
    parser.add_argument("--trim-end", type=int, help="Trim N chars from end")
    parser.add_argument("--ext", metavar="EXT", help="Change extension")
    parser.add_argument("--filter", metavar="PATTERN", help="Filter files by regex")
    parser.add_argument("-r", "--recursive", action="store_true", help="Process subdirectories")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Preview without renaming")

    args = parser.parse_args()

    # Get files
    if os.path.isfile(args.path):
        files = [args.path]
    elif os.path.isdir(args.path):
        files = list_files(args.path, args.filter, args.recursive)
    else:
        print(f"Error: {args.path} not found", file=sys.stderr)
        return 1

    if not files:
        print("No files found")
        return 0

    # Build transform function
    def transform(filename: str, index: int) -> str:
        result = filename

        if args.find:
            result = apply_pattern(result, args.find, args.replace, args.regex)

        if args.case:
            result = apply_case(result, args.case)

        if args.trim_start:
            result = apply_trim(result, args.trim_start, "start")

        if args.trim_end:
            result = apply_trim(result, args.trim_end, "end")

        if args.ext:
            result = apply_extension(result, args.ext)

        if args.number:
            result = apply_numbering(
                result, index, args.number_start, args.number_width, args.number_pos
            )

        return result

    # Preview and execute
    renames = preview_rename(files, transform)

    if not renames:
        print("No files to rename")
        return 0

    conflicts = check_conflicts(renames)
    if conflicts:
        print("Conflicts detected:", file=sys.stderr)
        for c in conflicts:
            print(f"  {c}", file=sys.stderr)
        return 1

    # Show preview
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Renaming {len(renames)} files:")
    for old, new in renames:
        old_name = os.path.basename(old)
        new_name = os.path.basename(new)
        print(f"  {old_name} -> {new_name}")

    success, errors = execute_renames(renames, args.dry_run)
    print(f"\nRenamed: {success}, Errors: {errors}")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
