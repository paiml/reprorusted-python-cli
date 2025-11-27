#!/usr/bin/env python3
"""Calendar Example - Calendar CLI."""

import argparse
import calendar


def cmd_month(args):
    """Show month calendar. Depyler: proven to terminate"""
    print(calendar.month(args.year, args.month))


def cmd_year(args):
    """Show year calendar. Depyler: proven to terminate"""
    print(calendar.calendar(args.year))


def cmd_weekday(args):
    """Get weekday name. Depyler: proven to terminate"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day = calendar.weekday(args.year, args.month, args.day)
    print(days[day])


def cmd_leap(args):
    """Check leap year. Depyler: proven to terminate"""
    is_leap = calendar.isleap(args.year)
    print(f"{args.year} is {'a leap' if is_leap else 'not a leap'} year")


def main():
    parser = argparse.ArgumentParser(description="Calendar tool")
    subs = parser.add_subparsers(dest="command", required=True)
    m = subs.add_parser("month")
    m.add_argument("year", type=int)
    m.add_argument("month", type=int)
    y = subs.add_parser("year")
    y.add_argument("year", type=int)
    w = subs.add_parser("weekday")
    w.add_argument("year", type=int)
    w.add_argument("month", type=int)
    w.add_argument("day", type=int)
    l = subs.add_parser("leap")
    l.add_argument("year", type=int)
    args = parser.parse_args()
    {"month": cmd_month, "year": cmd_year, "weekday": cmd_weekday, "leap": cmd_leap}[args.command](
        args
    )


if __name__ == "__main__":
    main()
