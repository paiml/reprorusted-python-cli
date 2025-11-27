#!/usr/bin/env python3
"""
Datetime Example - Time manipulation CLI

Demonstrates:
- datetime.now(), datetime.fromtimestamp()
- strftime/strptime formatting
- timedelta calculations
- ISO format handling

This validates depyler's ability to transpile datetime
to Rust (chrono crate).
"""

import argparse
from datetime import datetime, timedelta


def cmd_now(args):
    """Display current time. Depyler: proven to terminate"""
    now = datetime.now()
    if args.format == "iso":
        print(now.isoformat())
    elif args.format == "date":
        print(now.strftime("%Y-%m-%d"))
    else:
        print(now.strftime("%Y-%m-%d %H:%M:%S"))


def cmd_timestamp(args):
    """Convert Unix timestamp. Depyler: proven to terminate"""
    dt = datetime.fromtimestamp(int(args.timestamp))
    print(dt.strftime("%Y-%m-%d %H:%M:%S"))


def cmd_parse(args):
    """Parse date string. Depyler: proven to terminate"""
    if "T" in args.date:
        dt = datetime.fromisoformat(args.date)
    else:
        dt = datetime.strptime(args.date, "%Y-%m-%d")
    print(f"Parsed: {dt.strftime('%Y-%m-%d %H:%M:%S')}")


def cmd_duration(args):
    """Calculate duration. Depyler: proven to terminate"""
    if args.days:
        delta = timedelta(days=args.days)
        print(f"{args.days} days = {int(delta.total_seconds() // 3600)} hours")
    elif args.hours:
        delta = timedelta(hours=args.hours)
        print(f"{args.hours} hours = {int(delta.total_seconds() // 86400)} days")


def main():
    """Main entry point. Depyler: proven to terminate"""
    parser = argparse.ArgumentParser(description="Time manipulation tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # now subcommand
    now_parser = subparsers.add_parser("now", help="Show current time")
    now_parser.add_argument("--format", choices=["default", "iso", "date"], default="default")

    # timestamp subcommand
    ts_parser = subparsers.add_parser("timestamp", help="Convert Unix timestamp")
    ts_parser.add_argument("timestamp", help="Unix timestamp")

    # parse subcommand
    parse_parser = subparsers.add_parser("parse", help="Parse date string")
    parse_parser.add_argument("date", help="Date string (YYYY-MM-DD or ISO)")

    # duration subcommand
    dur_parser = subparsers.add_parser("duration", help="Calculate duration")
    dur_parser.add_argument("--days", type=int, help="Number of days")
    dur_parser.add_argument("--hours", type=int, help="Number of hours")

    args = parser.parse_args()

    if args.command == "now":
        cmd_now(args)
    elif args.command == "timestamp":
        cmd_timestamp(args)
    elif args.command == "parse":
        cmd_parse(args)
    elif args.command == "duration":
        cmd_duration(args)


if __name__ == "__main__":
    main()
