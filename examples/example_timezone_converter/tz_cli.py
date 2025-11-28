#!/usr/bin/env python3
"""Timezone converter CLI.

Convert times between timezones.
"""

import argparse
import sys
from datetime import UTC, datetime, timedelta, timezone

# Common timezone offsets (hours from UTC)
TIMEZONE_OFFSETS: dict[str, int] = {
    "UTC": 0,
    "GMT": 0,
    "EST": -5,
    "EDT": -4,
    "CST": -6,
    "CDT": -5,
    "MST": -7,
    "MDT": -6,
    "PST": -8,
    "PDT": -7,
    "CET": 1,
    "CEST": 2,
    "JST": 9,
    "IST": 5,  # India (5:30 but simplified)
    "AEST": 10,
    "AEDT": 11,
}


def get_timezone(name: str) -> timezone | None:
    """Get timezone from name or offset string."""
    name = name.upper()

    if name in TIMEZONE_OFFSETS:
        hours = TIMEZONE_OFFSETS[name]
        return timezone(timedelta(hours=hours))

    # Parse offset format like +05:30 or -08:00
    if name.startswith("+") or name.startswith("-"):
        try:
            sign = 1 if name[0] == "+" else -1
            parts = name[1:].split(":")
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            total_minutes = sign * (hours * 60 + minutes)
            return timezone(timedelta(minutes=total_minutes))
        except (ValueError, IndexError):
            return None

    return None


def parse_time(time_str: str, tz: timezone | None = None) -> datetime | None:
    """Parse time string into datetime."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%H:%M:%S",
        "%H:%M",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            # If only time provided, use today's date
            if dt.year == 1900:
                now = datetime.now()
                dt = dt.replace(year=now.year, month=now.month, day=now.day)
            if tz:
                dt = dt.replace(tzinfo=tz)
            return dt
        except ValueError:
            continue

    return None


def convert_time(dt: datetime, to_tz: timezone) -> datetime:
    """Convert datetime to different timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(to_tz)


def format_time(dt: datetime, include_tz: bool = True) -> str:
    """Format datetime for display."""
    base = dt.strftime("%Y-%m-%d %H:%M:%S")
    if include_tz and dt.tzinfo:
        offset = dt.strftime("%z")
        return f"{base} {offset}"
    return base


def list_timezones() -> list[str]:
    """List available timezone names."""
    return sorted(TIMEZONE_OFFSETS.keys())


def get_current_time(tz: timezone) -> datetime:
    """Get current time in specified timezone."""
    return datetime.now(tz)


def time_difference(tz1: timezone, tz2: timezone) -> timedelta:
    """Calculate difference between two timezones."""
    now = datetime.now(UTC)
    t1 = now.astimezone(tz1)
    t2 = now.astimezone(tz2)
    # Get offset difference
    offset1 = t1.utcoffset() or timedelta(0)
    offset2 = t2.utcoffset() or timedelta(0)
    return offset2 - offset1


def format_offset(td: timedelta) -> str:
    """Format timedelta as offset string."""
    total_seconds = int(td.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert times between timezones")
    parser.add_argument("time", nargs="?", help="Time to convert (or 'now')")
    parser.add_argument("-f", "--from", dest="from_tz", default="UTC", help="Source timezone")
    parser.add_argument("-t", "--to", dest="to_tz", default="UTC", help="Target timezone")
    parser.add_argument("--list", action="store_true", help="List available timezones")
    parser.add_argument("--diff", action="store_true", help="Show time difference between zones")

    args = parser.parse_args()

    if args.list:
        print("Available timezones:")
        for tz_name in list_timezones():
            offset = TIMEZONE_OFFSETS[tz_name]
            sign = "+" if offset >= 0 else ""
            print(f"  {tz_name:<6} {sign}{offset:>3}:00")
        return 0

    from_tz = get_timezone(args.from_tz)
    to_tz = get_timezone(args.to_tz)

    if not from_tz:
        print(f"Unknown timezone: {args.from_tz}", file=sys.stderr)
        return 1
    if not to_tz:
        print(f"Unknown timezone: {args.to_tz}", file=sys.stderr)
        return 1

    if args.diff:
        diff = time_difference(from_tz, to_tz)
        offset = format_offset(diff)
        print(f"{args.to_tz} is {offset} from {args.from_tz}")
        return 0

    # Get time to convert
    if not args.time or args.time.lower() == "now":
        dt = get_current_time(from_tz)
    else:
        dt = parse_time(args.time, from_tz)
        if not dt:
            print(f"Invalid time format: {args.time}", file=sys.stderr)
            return 1

    # Convert and display
    result = convert_time(dt, to_tz)
    print(f"{args.from_tz}: {format_time(dt)}")
    print(f"{args.to_tz}: {format_time(result)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
