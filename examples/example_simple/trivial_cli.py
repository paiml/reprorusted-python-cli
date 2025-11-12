#!/usr/bin/env python3
"""
Trivial CLI - Simplest argparse example

This script demonstrates basic argparse usage:
- Required argument (--name)
- Version flag (--version)
- Help flag (--help)

This is the simplest example in the reprorusted-python-cli suite,
designed to validate basic Python-to-Rust transpilation via depyler.
"""

import argparse


def main():
    """
    Main entry point for the trivial CLI

    Creates argument parser, parses arguments, and greets the user.
    """
    parser = argparse.ArgumentParser(
        description="A trivial CLI example for argparse-to-Rust validation",
        prog="trivial_cli.py"
    )

    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name to greet"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="1.0.0"
    )

    args = parser.parse_args()

    # Output greeting
    print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()
