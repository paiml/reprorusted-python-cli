#!/usr/bin/env python3
"""
Choices Validation Example

Demonstrates:
- choices parameter for string validation
- choices with integer types
- Default values with choices
- Help text showing valid choices

This validates depyler's ability to transpile choices
to Rust (clap value_parser with PossibleValues).
"""

import argparse


def main():
    """
    Main entry point demonstrating choices validation.

    Depyler: proven to terminate
    """
    parser = argparse.ArgumentParser(
        description="Demonstrate argument choices validation",
        prog="choice_validator",
    )

    # String choices - log level
    parser.add_argument(
        "--level",
        "-l",
        type=str,
        choices=["debug", "info", "warning", "error"],
        required=True,
        help="Log level (debug, info, warning, error)",
    )

    # Integer choices - priority
    parser.add_argument(
        "--priority",
        "-p",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=3,
        help="Priority level 1-5 (default: 3)",
    )

    # String choices - output format
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["json", "yaml", "xml", "text"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument("--version", action="version", version="1.0.0")

    args = parser.parse_args()

    print(f"Level: {args.level}")
    print(f"Priority: {args.priority}")
    print(f"Format: {args.format}")


if __name__ == "__main__":
    main()
