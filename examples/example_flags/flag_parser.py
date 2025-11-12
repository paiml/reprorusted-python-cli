#!/usr/bin/env python3
"""
Flag Parser - Boolean flags example

Demonstrates argparse boolean flags:
- --verbose/-v: Enable verbose output
- --debug/-d: Enable debug mode
- --quiet/-q: Enable quiet mode

These flags are store_true actions, creating boolean values.
They can be combined in any order.
"""

import argparse


def main():
    """
    Main entry point for the flag parser CLI

    Parses boolean flags and displays their status.
    """
    parser = argparse.ArgumentParser(
        description="Boolean flag parsing example for argparse-to-Rust validation",
        prog="flag_parser.py"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Enable quiet mode"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="1.0.0"
    )

    args = parser.parse_args()

    # Display flag status
    print(f"Verbose: {args.verbose}")
    print(f"Debug: {args.debug}")
    print(f"Quiet: {args.quiet}")

    # Show which modes are enabled
    if args.verbose:
        print("VERBOSE MODE ENABLED")

    if args.debug:
        print("DEBUG MODE ENABLED")

    if args.quiet:
        print("QUIET MODE ENABLED")


if __name__ == "__main__":
    main()
