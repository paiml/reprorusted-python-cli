#!/usr/bin/env python3
"""Groups Example - Argument groups CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Argument groups tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    r = subs.add_parser("run")
    r.add_argument("--verbose", action="store_true")
    r.add_argument("--quiet", action="store_true")

    args = parser.parse_args()
    if args.cmd == "run":
        if args.verbose:
            print("Running in verbose mode")
        elif args.quiet:
            print("Running in quiet mode")
        else:
            print("Running in normal mode")


if __name__ == "__main__":
    main()
