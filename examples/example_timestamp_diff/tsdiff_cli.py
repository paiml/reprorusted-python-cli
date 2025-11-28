#!/usr/bin/env python3
"""Timestamp difference calculator CLI.

Calculate differences between timestamps in various formats.
"""

import argparse
import re
import sys
from datetime import datetime, timedelta


def parse_timestamp(ts: str) -> datetime | None:
    """Parse various timestamp formats."""
    ts = ts.strip()

    # Unix timestamp (seconds since epoch)
    if ts.isdigit() and len(ts) >= 10:
        try:
            if len(ts) == 10:
                return datetime.fromtimestamp(int(ts))
            elif len(ts) == 13:  # Milliseconds
                return datetime.fromtimestamp(int(ts) / 1000)
            elif len(ts) == 16:  # Microseconds
                return datetime.fromtimestamp(int(ts) / 1000000)
        except (ValueError, OSError):
            pass

    # Try various formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue

    # Try ISO format with timezone
    iso_match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+-]\d{2}:?\d{2})?", ts)
    if iso_match:
        try:
            return datetime.fromisoformat(iso_match.group(1))
        except ValueError:
            pass

    return None


def format_duration(td: timedelta, precision: str = "seconds") -> str:
    """Format timedelta as human-readable duration."""
    total_seconds = abs(td.total_seconds())

    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds * 1000) % 1000)

    parts = []

    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")

    if precision == "milliseconds":
        parts.append(f"{seconds}.{milliseconds:03d}s")
    elif precision == "seconds":
        parts.append(f"{seconds}s")
    elif precision == "minutes" and not parts:
        # Show at least minutes
        parts.append(f"{minutes}m")

    return " ".join(parts) if parts else "0s"


def duration_breakdown(td: timedelta) -> dict:
    """Break down timedelta into components."""
    total_seconds = abs(td.total_seconds())

    return {
        "total_seconds": total_seconds,
        "total_minutes": total_seconds / 60,
        "total_hours": total_seconds / 3600,
        "total_days": total_seconds / 86400,
        "days": int(total_seconds // 86400),
        "hours": int((total_seconds % 86400) // 3600),
        "minutes": int((total_seconds % 3600) // 60),
        "seconds": int(total_seconds % 60),
        "milliseconds": int((total_seconds * 1000) % 1000),
    }


def to_unix_timestamp(dt: datetime) -> int:
    """Convert datetime to Unix timestamp."""
    return int(dt.timestamp())


def from_unix_timestamp(ts: int) -> datetime:
    """Convert Unix timestamp to datetime."""
    return datetime.fromtimestamp(ts)


def add_duration(dt: datetime, duration_str: str) -> datetime | None:
    """Add duration string to datetime.

    Format: 1d2h3m4s
    """
    total_seconds = 0

    # Parse duration parts
    pattern = r"(\d+)([dhms])"
    matches = re.findall(pattern, duration_str.lower())

    if not matches:
        return None

    for value, unit in matches:
        value = int(value)
        if unit == "d":
            total_seconds += value * 86400
        elif unit == "h":
            total_seconds += value * 3600
        elif unit == "m":
            total_seconds += value * 60
        elif unit == "s":
            total_seconds += value

    return dt + timedelta(seconds=total_seconds)


def subtract_duration(dt: datetime, duration_str: str) -> datetime | None:
    """Subtract duration string from datetime."""
    total_seconds = 0

    pattern = r"(\d+)([dhms])"
    matches = re.findall(pattern, duration_str.lower())

    if not matches:
        return None

    for value, unit in matches:
        value = int(value)
        if unit == "d":
            total_seconds += value * 86400
        elif unit == "h":
            total_seconds += value * 3600
        elif unit == "m":
            total_seconds += value * 60
        elif unit == "s":
            total_seconds += value

    return dt - timedelta(seconds=total_seconds)


def compare_timestamps(ts1: datetime, ts2: datetime) -> dict:
    """Compare two timestamps."""
    diff = ts2 - ts1
    is_after = ts2 > ts1
    is_same = ts1 == ts2

    return {
        "difference": diff,
        "is_after": is_after,
        "is_same": is_same,
        "breakdown": duration_breakdown(diff),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate timestamp differences")
    parser.add_argument("timestamp1", help="First timestamp")
    parser.add_argument("timestamp2", nargs="?", help="Second timestamp (default: now)")
    parser.add_argument(
        "--add", metavar="DURATION", help="Add duration to timestamp (e.g., 1d2h30m)"
    )
    parser.add_argument("--sub", metavar="DURATION", help="Subtract duration from timestamp")
    parser.add_argument("--unix", action="store_true", help="Output as Unix timestamp")
    parser.add_argument("--breakdown", action="store_true", help="Show detailed breakdown")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Parse first timestamp
    ts1 = parse_timestamp(args.timestamp1)
    if not ts1:
        print(f"Invalid timestamp: {args.timestamp1}", file=sys.stderr)
        return 1

    # Handle add/subtract
    if args.add:
        result = add_duration(ts1, args.add)
        if not result:
            print(f"Invalid duration: {args.add}", file=sys.stderr)
            return 1
        if args.unix:
            print(to_unix_timestamp(result))
        else:
            print(result.strftime("%Y-%m-%d %H:%M:%S"))
        return 0

    if args.sub:
        result = subtract_duration(ts1, args.sub)
        if not result:
            print(f"Invalid duration: {args.sub}", file=sys.stderr)
            return 1
        if args.unix:
            print(to_unix_timestamp(result))
        else:
            print(result.strftime("%Y-%m-%d %H:%M:%S"))
        return 0

    # Get second timestamp
    if args.timestamp2:
        ts2 = parse_timestamp(args.timestamp2)
        if not ts2:
            print(f"Invalid timestamp: {args.timestamp2}", file=sys.stderr)
            return 1
    else:
        ts2 = datetime.now()

    # Compare
    comparison = compare_timestamps(ts1, ts2)
    diff = comparison["difference"]
    breakdown = comparison["breakdown"]

    if args.json:
        import json

        output = {
            "timestamp1": ts1.isoformat(),
            "timestamp2": ts2.isoformat(),
            "difference": {
                "formatted": format_duration(diff),
                "total_seconds": breakdown["total_seconds"],
                "total_minutes": breakdown["total_minutes"],
                "total_hours": breakdown["total_hours"],
                "total_days": breakdown["total_days"],
            },
            "is_ts2_after_ts1": comparison["is_after"],
        }
        print(json.dumps(output, indent=2))
        return 0

    # Default output
    sign = "" if diff.total_seconds() >= 0 else "-"
    print(f"From: {ts1.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"To:   {ts2.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Diff: {sign}{format_duration(diff)}")

    if args.breakdown:
        print("\nBreakdown:")
        print(f"  Days: {breakdown['days']}")
        print(f"  Hours: {breakdown['hours']}")
        print(f"  Minutes: {breakdown['minutes']}")
        print(f"  Seconds: {breakdown['seconds']}")
        print("\nTotals:")
        print(f"  {breakdown['total_seconds']:.2f} seconds")
        print(f"  {breakdown['total_minutes']:.2f} minutes")
        print(f"  {breakdown['total_hours']:.2f} hours")
        print(f"  {breakdown['total_days']:.2f} days")

    return 0


if __name__ == "__main__":
    sys.exit(main())
