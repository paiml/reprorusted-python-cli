#!/usr/bin/env python3
"""Datetime Format CLI.

Date/time formatting with strftime and strptime.
"""

import argparse
import sys
from datetime import date, datetime, time


def strftime_date(d: date, fmt: str) -> str:
    """Format date with strftime."""
    return d.strftime(fmt)


def strftime_datetime(dt: datetime, fmt: str) -> str:
    """Format datetime with strftime."""
    return dt.strftime(fmt)


def strptime(s: str, fmt: str) -> datetime:
    """Parse datetime from string with format."""
    return datetime.strptime(s, fmt)


def format_iso_date(d: date) -> str:
    """Format as ISO date (YYYY-MM-DD)."""
    return d.strftime("%Y-%m-%d")


def format_iso_datetime(dt: datetime) -> str:
    """Format as ISO datetime."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def format_us_date(d: date) -> str:
    """Format as US date (MM/DD/YYYY)."""
    return d.strftime("%m/%d/%Y")


def format_eu_date(d: date) -> str:
    """Format as European date (DD/MM/YYYY)."""
    return d.strftime("%d/%m/%Y")


def format_long_date(d: date) -> str:
    """Format as long date (Month Day, Year)."""
    return d.strftime("%B %d, %Y")


def format_short_date(d: date) -> str:
    """Format as short date (Mon DD, YYYY)."""
    return d.strftime("%b %d, %Y")


def format_weekday_date(d: date) -> str:
    """Format with weekday (Day, Month DD, YYYY)."""
    return d.strftime("%A, %B %d, %Y")


def format_time_12h(t: time) -> str:
    """Format time in 12-hour format."""
    dt = datetime.combine(date.today(), t)
    return dt.strftime("%I:%M:%S %p")


def format_time_24h(t: time) -> str:
    """Format time in 24-hour format."""
    dt = datetime.combine(date.today(), t)
    return dt.strftime("%H:%M:%S")


def format_time_short(t: time) -> str:
    """Format time without seconds."""
    dt = datetime.combine(date.today(), t)
    return dt.strftime("%H:%M")


def format_datetime_full(dt: datetime) -> str:
    """Format full datetime."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_datetime_human(dt: datetime) -> str:
    """Format human-readable datetime."""
    return dt.strftime("%B %d, %Y at %I:%M %p")


def format_datetime_compact(dt: datetime) -> str:
    """Format compact datetime (YYYYMMDDHHMMSS)."""
    return dt.strftime("%Y%m%d%H%M%S")


def format_datetime_rfc2822(dt: datetime) -> str:
    """Format datetime in RFC 2822 style."""
    return dt.strftime("%a, %d %b %Y %H:%M:%S")


def format_datetime_log(dt: datetime) -> str:
    """Format datetime for log files."""
    return dt.strftime("[%Y-%m-%d %H:%M:%S]")


def format_year(d: date) -> str:
    """Get year as string."""
    return d.strftime("%Y")


def format_month(d: date) -> str:
    """Get month name."""
    return d.strftime("%B")


def format_month_short(d: date) -> str:
    """Get abbreviated month name."""
    return d.strftime("%b")


def format_weekday(d: date) -> str:
    """Get weekday name."""
    return d.strftime("%A")


def format_weekday_short(d: date) -> str:
    """Get abbreviated weekday name."""
    return d.strftime("%a")


def format_week_number(d: date) -> int:
    """Get week number (Sunday start)."""
    return int(d.strftime("%U"))


def format_week_number_iso(d: date) -> int:
    """Get ISO week number (Monday start)."""
    return int(d.strftime("%W"))


def format_day_of_year(d: date) -> int:
    """Get day of year (1-366)."""
    return int(d.strftime("%j"))


def format_century(d: date) -> str:
    """Get century (first two digits of year)."""
    return d.strftime("%C")


def parse_iso_date(s: str) -> date:
    """Parse ISO date string."""
    return datetime.strptime(s, "%Y-%m-%d").date()


def parse_us_date(s: str) -> date:
    """Parse US date string (MM/DD/YYYY)."""
    return datetime.strptime(s, "%m/%d/%Y").date()


def parse_eu_date(s: str) -> date:
    """Parse European date string (DD/MM/YYYY)."""
    return datetime.strptime(s, "%d/%m/%Y").date()


def parse_datetime_full(s: str) -> datetime:
    """Parse full datetime string."""
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def parse_datetime_compact(s: str) -> datetime:
    """Parse compact datetime string."""
    return datetime.strptime(s, "%Y%m%d%H%M%S")


def parse_time_24h(s: str) -> time:
    """Parse 24-hour time string."""
    return datetime.strptime(s, "%H:%M:%S").time()


def parse_time_12h(s: str) -> time:
    """Parse 12-hour time string."""
    return datetime.strptime(s, "%I:%M:%S %p").time()


def try_parse_date(s: str, formats: list[str]) -> date | None:
    """Try parsing date with multiple formats."""
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def auto_parse_date(s: str) -> date | None:
    """Automatically parse common date formats."""
    formats = [
        "%Y-%m-%d",  # ISO
        "%m/%d/%Y",  # US
        "%d/%m/%Y",  # EU
        "%Y/%m/%d",  # Alternative ISO
        "%d-%m-%Y",  # EU with dashes
        "%B %d, %Y",  # Long
        "%b %d, %Y",  # Short
    ]
    return try_parse_date(s, formats)


def format_relative_day(d: date) -> str:
    """Format date as relative day if applicable."""
    today = date.today()
    delta = (d - today).days
    if delta == 0:
        return "Today"
    elif delta == 1:
        return "Tomorrow"
    elif delta == -1:
        return "Yesterday"
    elif 1 < delta <= 7:
        return f"In {delta} days"
    elif -7 <= delta < -1:
        return f"{-delta} days ago"
    else:
        return d.strftime("%B %d, %Y")


def format_ordinal_day(day: int) -> str:
    """Format day with ordinal suffix (1st, 2nd, 3rd, etc.)."""
    if 11 <= day <= 13:
        suffix = "th"
    elif day % 10 == 1:
        suffix = "st"
    elif day % 10 == 2:
        suffix = "nd"
    elif day % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"
    return f"{day}{suffix}"


def format_date_ordinal(d: date) -> str:
    """Format date with ordinal day."""
    day_str = format_ordinal_day(d.day)
    return d.strftime(f"%B {day_str}, %Y")


def format_duration_hms(seconds: int) -> str:
    """Format duration as HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_file_timestamp(dt: datetime) -> str:
    """Format timestamp suitable for filenames."""
    return dt.strftime("%Y%m%d_%H%M%S")


def main() -> int:
    parser = argparse.ArgumentParser(description="Datetime format CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # format
    format_p = subparsers.add_parser("format", help="Format datetime")
    format_p.add_argument("datetime", nargs="?", help="Datetime (default: now)")
    format_p.add_argument("-f", "--format", default="%Y-%m-%d %H:%M:%S", help="Format string")

    # parse
    parse_p = subparsers.add_parser("parse", help="Parse datetime")
    parse_p.add_argument("value", help="String to parse")
    parse_p.add_argument("-f", "--format", help="Format string (auto-detect if not given)")

    # convert
    convert_p = subparsers.add_parser("convert", help="Convert between formats")
    convert_p.add_argument("value", help="Input value")
    convert_p.add_argument("--from", dest="from_fmt", required=True, help="Input format")
    convert_p.add_argument("--to", dest="to_fmt", required=True, help="Output format")

    # examples
    subparsers.add_parser("examples", help="Show format examples")

    args = parser.parse_args()

    if args.command == "format":
        if args.datetime:
            dt = datetime.fromisoformat(args.datetime)
        else:
            dt = datetime.now()
        print(strftime_datetime(dt, args.format))

    elif args.command == "parse":
        if args.format:
            dt = strptime(args.value, args.format)
            print(f"Parsed: {dt}")
        else:
            d = auto_parse_date(args.value)
            if d:
                print(f"Parsed: {d}")
            else:
                print("Could not parse date")
                return 1

    elif args.command == "convert":
        dt = strptime(args.value, args.from_fmt)
        print(strftime_datetime(dt, args.to_fmt))

    elif args.command == "examples":
        now = datetime.now()
        today = date.today()
        print("Format Examples:")
        print(f"  ISO date:     {format_iso_date(today)}")
        print(f"  US date:      {format_us_date(today)}")
        print(f"  EU date:      {format_eu_date(today)}")
        print(f"  Long date:    {format_long_date(today)}")
        print(f"  Full datetime:{format_datetime_full(now)}")
        print(f"  Human:        {format_datetime_human(now)}")
        print(f"  Log:          {format_datetime_log(now)}")
        print(f"  File:         {format_file_timestamp(now)}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
