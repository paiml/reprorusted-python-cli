#!/usr/bin/env python3
"""
Positional Arguments Example

Demonstrates argparse positional arguments:
- command: Required positional with choices (start, stop, restart)
- targets: Optional positional with nargs='*' (multiple values)

This shows how to handle positional arguments with validation.
"""

import argparse


def main():
    """
    Main entry point for the positional args CLI

    Parses command and optional targets, displays them.
    """
    parser = argparse.ArgumentParser(
        description="Positional arguments example with command and targets",
        prog="positional_args.py",
    )

    # Required positional argument with choices
    parser.add_argument(
        "command",
        choices=["start", "stop", "restart"],
        help="Command to execute (start, stop, or restart)",
    )

    # Optional positional argument with nargs
    parser.add_argument(
        "targets",
        nargs="*",  # Zero or more arguments
        default=["all"],
        help="Targets to apply command to (default: all)",
    )

    parser.add_argument("--version", action="version", version="1.0.0")

    args = parser.parse_args()

    # Display parsed arguments
    print(f"Command: {args.command}")
    print(f"Targets: {args.targets}")


if __name__ == "__main__":
    main()
