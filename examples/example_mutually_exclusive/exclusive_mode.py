#!/usr/bin/env python3
"""
Mutually Exclusive Groups Example

Demonstrates:
- add_mutually_exclusive_group()
- Required mutually exclusive groups
- Multiple exclusive groups in one parser

This validates depyler's ability to transpile mutually exclusive
argument groups to Rust (clap conflicts_with).
"""

import argparse


def main():
    """
    Main entry point demonstrating mutually exclusive groups.

    Depyler: proven to terminate
    """
    parser = argparse.ArgumentParser(
        description="Demonstrate mutually exclusive argument groups",
        prog="exclusive_mode",
    )

    # Optional mutually exclusive: --verbose vs --quiet
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    output_group.add_argument("--quiet", "-q", action="store_true", help="Suppress all output")

    # Required mutually exclusive: must specify input source
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", "-i", type=str, help="Read from file")
    input_group.add_argument("--stdin", action="store_true", help="Read from stdin")
    input_group.add_argument("--url", "-u", type=str, help="Read from URL")

    parser.add_argument("--version", action="version", version="1.0.0")

    args = parser.parse_args()

    # Determine output mode
    if args.verbose:
        mode = "verbose"
    elif args.quiet:
        mode = "quiet"
    else:
        mode = "normal"

    # Determine input source
    if args.input:
        source = f"file({args.input})"
    elif args.stdin:
        source = "stdin"
    elif args.url:
        source = f"url({args.url})"
    else:
        source = "none"

    print(f"Mode: {mode}")
    print(f"Source: {source}")


if __name__ == "__main__":
    main()
