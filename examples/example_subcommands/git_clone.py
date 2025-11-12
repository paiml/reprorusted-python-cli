#!/usr/bin/env python3
"""
Git-like CLI with subcommands (example_subcommands).

This example demonstrates argparse subparsers for creating
git-like command structures with multiple subcommands.

Features:
- Three subcommands: clone, push, pull
- Global --verbose flag
- Subcommand-specific arguments
"""

import argparse


def main():
    """Main entry point for the git-like CLI."""
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="Git-like CLI example with subcommands",
        prog="git_clone.py",
    )

    # Add global arguments (before subparsers)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="1.0.0",
    )

    # Create subparsers
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,  # Make subcommand required
    )

    # Subcommand: clone
    parser_clone = subparsers.add_parser(
        "clone",
        help="Clone a repository",
    )
    parser_clone.add_argument(
        "url",
        help="Repository URL to clone",
    )

    # Subcommand: push
    parser_push = subparsers.add_parser(
        "push",
        help="Push to a remote repository",
    )
    parser_push.add_argument(
        "remote",
        help="Remote name to push to",
    )

    # Subcommand: pull
    parser_pull = subparsers.add_parser(
        "pull",
        help="Pull from a remote repository",
    )
    parser_pull.add_argument(
        "remote",
        help="Remote name to pull from",
    )

    # Parse arguments
    args = parser.parse_args()

    # Execute the appropriate subcommand
    if args.command == "clone":
        handle_clone(args)
    elif args.command == "push":
        handle_push(args)
    elif args.command == "pull":
        handle_pull(args)


def handle_clone(args):
    """Handle the 'clone' subcommand."""
    if args.verbose:
        print("Verbose mode: ON")
        print(f"Clone: {args.url}")
        print("This is a demo - no actual cloning performed")
    else:
        print(f"Clone: {args.url}")


def handle_push(args):
    """Handle the 'push' subcommand."""
    if args.verbose:
        print("Verbose mode: ON")
        print(f"Push to: {args.remote}")
        print("This is a demo - no actual pushing performed")
    else:
        print(f"Push to: {args.remote}")


def handle_pull(args):
    """Handle the 'pull' subcommand."""
    if args.verbose:
        print("Verbose mode: ON")
        print(f"Pull from: {args.remote}")
        print("This is a demo - no actual pulling performed")
    else:
        print(f"Pull from: {args.remote}")


if __name__ == "__main__":
    main()
