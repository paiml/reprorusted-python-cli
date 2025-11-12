#!/usr/bin/env python3
"""
Standard Library Integration Example (stdlib_integration.py)

This CLI tool demonstrates integration of multiple Python standard library modules:
- argparse: Command-line argument parsing
- json: JSON serialization/deserialization
- pathlib: Path operations and file metadata
- datetime: Timestamp formatting
- hashlib: File hashing (MD5, SHA256)

The tool provides detailed file information including size, timestamps,
hashes, and outputs in various formats (text, JSON, compact).
"""

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path


def calculate_hash(file_path, algorithm):
    """Calculate file hash using specified algorithm."""
    if algorithm not in ["md5", "sha256"]:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hasher = hashlib.md5() if algorithm == "md5" else hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            # Read file in chunks for efficiency
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except PermissionError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to calculate hash: {e}") from e


def format_timestamp(timestamp, time_format):
    """Format timestamp according to specified format."""
    dt = datetime.datetime.fromtimestamp(timestamp)

    if time_format == "iso":
        return dt.isoformat()
    elif time_format == "human":
        return dt.strftime("%b %d, %Y %I:%M:%S %p")
    else:
        return dt.isoformat()


def get_file_info(file_path, hash_algorithm=None, time_format="iso"):
    """Gather comprehensive file information using pathlib, datetime, hashlib."""
    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    # Get file stats
    stats = path.stat()

    # Build file info dictionary
    info = {
        "path": str(path.absolute()),
        "filename": path.name,
        "extension": path.suffix,
        "size": stats.st_size,
        "modified": format_timestamp(stats.st_mtime, time_format),
    }

    # Add hash if requested
    if hash_algorithm:
        try:
            info["hash"] = calculate_hash(path, hash_algorithm)
            info["hash_algorithm"] = hash_algorithm
        except PermissionError:
            # Let permission errors propagate
            raise
        except Exception as e:
            info["hash_error"] = str(e)

    return info


def format_output_text(info, include_hash):
    """Format file info as human-readable text."""
    lines = []
    lines.append(f"Path: {info['path']}")
    lines.append(f"Filename: {info['filename']}")
    if info["extension"]:
        lines.append(f"Extension: {info['extension']}")
    lines.append(f"Size: {info['size']} bytes")
    lines.append(f"Modified: {info['modified']}")

    if include_hash and "hash" in info:
        lines.append(f"Hash ({info['hash_algorithm'].upper()}): {info['hash']}")

    return "\n".join(lines)


def format_output_json(info):
    """Format file info as JSON."""
    return json.dumps(info, indent=2)


def format_output_compact(info, include_hash):
    """Format file info as compact single-line output."""
    parts = [
        info["filename"],
        f"{info['size']}B",
        info["modified"],
    ]

    if include_hash and "hash" in info:
        parts.append(f"{info['hash_algorithm']}:{info['hash'][:16]}...")

    return " | ".join(parts)


def main():
    """Main entry point for the stdlib integration CLI."""
    parser = argparse.ArgumentParser(
        description="File information tool demonstrating Python stdlib integration",
        prog="stdlib_integration.py",
        epilog="Example: %(prog)s --file data.txt --format json --hash sha256",
    )

    # Version
    parser.add_argument(
        "--version",
        action="version",
        version="1.0.0",
    )

    # Required file argument
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="File path to analyze (required)",
    )

    # Output format
    parser.add_argument(
        "--format",
        choices=["text", "json", "compact"],
        default="text",
        help="Output format (default: text)",
    )

    # Hash algorithm
    parser.add_argument(
        "--hash",
        choices=["md5", "sha256"],
        help="Hash algorithm (optional)",
    )

    # Output destination
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )

    # Time format
    parser.add_argument(
        "--time-format",
        choices=["iso", "human"],
        default="iso",
        help="Timestamp format (default: iso)",
    )

    # Parse arguments
    args = parser.parse_args()

    try:
        # Get file information
        info = get_file_info(args.file, args.hash, args.time_format)

        # Format output
        if args.format == "json":
            output = format_output_json(info)
        elif args.format == "compact":
            output = format_output_compact(info, args.hash is not None)
        else:  # text
            output = format_output_text(info, args.hash is not None)

        # Write output
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w") as f:
                f.write(output)
                if args.format != "compact":
                    f.write("\n")
        else:
            print(output)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print("Error: Permission denied", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
