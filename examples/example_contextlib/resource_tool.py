#!/usr/bin/env python3
"""
Contextlib Example - Resource management

Demonstrates contextlib patterns for resource handling.
"""

import argparse
import tempfile
from contextlib import redirect_stdout


def cmd_tempfile(args):
    """Create temp file. Depyler: proven to terminate"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(args.content)
        print(f"Created: {f.name}")


def cmd_redirect(args):
    """Redirect stdout to file. Depyler: proven to terminate"""
    with open(args.output, "w") as f:
        with redirect_stdout(f):
            print(args.message)
    print(f"Written to: {args.output}")


def main():
    parser = argparse.ArgumentParser(description="Resource management tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tmp = subparsers.add_parser("tempfile")
    tmp.add_argument("--content", required=True)

    redir = subparsers.add_parser("redirect")
    redir.add_argument("output")
    redir.add_argument("--message", required=True)

    args = parser.parse_args()
    if args.command == "tempfile":
        cmd_tempfile(args)
    elif args.command == "redirect":
        cmd_redirect(args)


if __name__ == "__main__":
    main()
