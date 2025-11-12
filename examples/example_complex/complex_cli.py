#!/usr/bin/env python3
"""
Complex CLI example demonstrating advanced argparse features.

This example showcases:
- Mutually exclusive groups (--json, --xml, --yaml)
- Argument groups (input, output, processing)
- Custom types and validation (port, positive int, email)
- File I/O arguments
- Environment variable fallback
"""

import argparse
import os
import re


def port_number(value):
    """Custom type for port number validation (1-65535)."""
    try:
        port = int(value)
        if port < 1 or port > 65535:
            raise argparse.ArgumentTypeError(f"Port must be between 1 and 65535, got {port}")
        return port
    except ValueError:
        raise argparse.ArgumentTypeError(f"Port must be an integer, got '{value}'") from None


def positive_int(value):
    """Custom type for positive integer validation (>= 1)."""
    try:
        num = int(value)
        if num < 1:
            raise argparse.ArgumentTypeError(f"Value must be positive (>= 1), got {num}")
        return num
    except ValueError:
        raise argparse.ArgumentTypeError(f"Value must be an integer, got '{value}'") from None


def email_address(value):
    """Custom type for email address validation."""
    # Simple email validation pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, value):
        raise argparse.ArgumentTypeError(f"Invalid email address: '{value}'")
    return value


def main():
    """Main entry point for the complex CLI."""
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="Complex CLI example with advanced argparse features",
        prog="complex_cli.py",
        epilog="Example: %(prog)s --input data.txt --json --port 8080",
    )

    # Version
    parser.add_argument(
        "--version",
        action="version",
        version="1.0.0",
    )

    # ===== INPUT GROUP =====
    input_group = parser.add_argument_group("input options", "Options for input file handling")

    input_group.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input file path (required)",
    )

    input_group.add_argument(
        "--encoding",
        default="utf-8",
        help="Input file encoding (default: utf-8)",
    )

    # ===== OUTPUT GROUP =====
    output_group = parser.add_argument_group(
        "output options", "Options for output format and destination"
    )

    output_group.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )

    # Mutually exclusive group for output format
    format_group = output_group.add_mutually_exclusive_group()

    format_group.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    format_group.add_argument(
        "--xml",
        action="store_true",
        help="Output in XML format",
    )

    format_group.add_argument(
        "--yaml",
        action="store_true",
        help="Output in YAML format",
    )

    # ===== PROCESSING GROUP =====
    processing_group = parser.add_argument_group(
        "processing options", "Options for data processing"
    )

    processing_group.add_argument(
        "--port",
        type=port_number,
        help="Port number (1-65535)",
    )

    processing_group.add_argument(
        "--count",
        type=positive_int,
        help="Count (positive integer)",
    )

    processing_group.add_argument(
        "--email",
        type=email_address,
        help="Email address",
    )

    # Parse arguments
    args = parser.parse_args()

    # Determine output format (with environment variable fallback)
    output_format = None
    if args.json:
        output_format = "json"
    elif args.xml:
        output_format = "xml"
    elif args.yaml:
        output_format = "yaml"
    else:
        # Fallback to environment variable
        env_format = os.environ.get("DEFAULT_FORMAT", "text")
        output_format = env_format.lower()

    # Get config file from environment if set
    config_file = os.environ.get("CONFIG_FILE")

    # Build output message
    output_lines = []
    output_lines.append(f"Input: {args.input}")

    if args.output:
        output_lines.append(f"Output: {args.output}")
    else:
        output_lines.append("Output: stdout")

    output_lines.append(f"Format: {output_format}")

    if args.encoding:
        output_lines.append(f"Encoding: {args.encoding}")

    if args.port:
        output_lines.append(f"Port: {args.port}")

    if args.count:
        output_lines.append(f"Count: {args.count}")

    if args.email:
        output_lines.append(f"Email: {args.email}")

    if config_file:
        output_lines.append(f"Config: {config_file}")

    # Print output
    for line in output_lines:
        print(line)


if __name__ == "__main__":
    main()
