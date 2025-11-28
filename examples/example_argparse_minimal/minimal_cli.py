#!/usr/bin/env python3
"""
Minimal Argparse CLI - Baseline example that must compile

This is the absolute minimum argparse example:
- Single positional argument
- Single optional argument
- No subcommands
- Minimal handler

Purpose: Baseline CLI that depyler must handle correctly.
"""

import argparse


def main():
    """Main entry point with minimal argparse."""
    parser = argparse.ArgumentParser(
        description="Minimal CLI example",
        prog="minimal_cli.py",
    )

    # Single positional argument
    parser.add_argument(
        "input",
        help="Input value",
    )

    # Single optional argument
    parser.add_argument(
        "-u",
        "--upper",
        action="store_true",
        help="Convert to uppercase",
    )

    args = parser.parse_args()

    # Minimal handler
    if args.upper:
        print(args.input.upper())
    else:
        print(args.input)


if __name__ == "__main__":
    main()
