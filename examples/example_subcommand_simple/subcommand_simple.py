#!/usr/bin/env python3
"""
Simple Subcommand CLI - Minimal subcommand example

This example demonstrates the simplest possible argparse subcommand pattern:
- Single subcommand with one positional argument
- Direct field access on args (validates E0609 fix)
- Minimal handler function

Purpose: Validate depyler handles subcommand field access correctly (E0609).
"""

import argparse


def main():
    """Main entry point with single subcommand."""
    parser = argparse.ArgumentParser(
        description="Simple subcommand example",
        prog="subcommand_simple.py",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Single subcommand: greet
    greet_parser = subparsers.add_parser(
        "greet",
        help="Greet a person",
    )
    greet_parser.add_argument(
        "name",
        help="Name to greet",
    )

    args = parser.parse_args()

    # Direct field access - this is what E0609 tests
    if args.command == "greet":
        print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()
