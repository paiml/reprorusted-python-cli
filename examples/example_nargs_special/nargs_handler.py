#!/usr/bin/env python3
"""
Nargs Special Values Example

Demonstrates:
- nargs='?' - zero or one argument
- nargs='*' - zero or more arguments
- nargs='+' - one or more arguments
- const and default with nargs='?'

This validates depyler's ability to transpile nargs
to Rust (clap num_args, default_value, requires).
"""

import argparse


def main():
    """
    Main entry point demonstrating nargs special values.

    Depyler: proven to terminate
    """
    parser = argparse.ArgumentParser(
        description="Demonstrate nargs special values",
        prog="nargs_handler",
    )

    # Required positional
    parser.add_argument(
        "input",
        type=str,
        help="Input file (required)",
    )

    # nargs='?' - zero or one, with const when flag present but no value
    parser.add_argument(
        "--output",
        "-o",
        nargs="?",
        const="output.txt",
        default="stdout",
        help="Output file (default: stdout, flag only: output.txt)",
    )

    # nargs='*' - zero or more
    parser.add_argument(
        "--tags",
        "-t",
        nargs="*",
        default=[],
        help="Tags to apply (zero or more)",
    )

    # nargs='+' - one or more
    parser.add_argument(
        "--files",
        "-f",
        nargs="+",
        help="Additional files (one or more when specified)",
    )

    parser.add_argument("--version", action="version", version="1.0.0")

    args = parser.parse_args()

    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Tags: {args.tags}")
    if args.files:
        print(f"Files: {args.files}")


if __name__ == "__main__":
    main()
