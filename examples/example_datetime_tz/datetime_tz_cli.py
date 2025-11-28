#!/usr/bin/env python3
"""Datetime Timezone CLI.

Timezone handling with datetime and zoneinfo.
"""

import argparse
import sys
from datetime import UTC, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, available_timezones


def utc_timezone() -> timezone:
    """Get UTC timezone."""
    return UTC


def create_fixed_offset(hours: int, minutes: int = 0) -> timezone:
    """Create fixed offset timezone."""
    return timezone(timedelta(hours=hours, minutes=minutes))


def get_timezone(name: str) -> ZoneInfo:
    """Get timezone by name."""
    return ZoneInfo(name)


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def now_in_timezone(tz: ZoneInfo | timezone) -> datetime:
    """Get current datetime in specific timezone."""
    return datetime.now(tz)


def make_aware(dt: datetime, tz: ZoneInfo | timezone) -> datetime:
    """Make naive datetime timezone-aware."""
    return dt.replace(tzinfo=tz)


def localize(dt: datetime, tz: ZoneInfo) -> datetime:
    """Localize naive datetime to timezone (handles DST)."""
    # For ZoneInfo, replace is the proper way
    return dt.replace(tzinfo=tz)


def convert_timezone(dt: datetime, tz: ZoneInfo | timezone) -> datetime:
    """Convert datetime to different timezone."""
    return dt.astimezone(tz)


def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC."""
    return dt.astimezone(UTC)


def from_utc(dt: datetime, tz: ZoneInfo | timezone) -> datetime:
    """Convert UTC datetime to timezone."""
    return dt.astimezone(tz)


def get_offset(dt: datetime) -> timedelta | None:
    """Get UTC offset for datetime."""
    return dt.utcoffset()


def get_offset_hours(dt: datetime) -> float | None:
    """Get UTC offset in hours."""
    offset = dt.utcoffset()
    if offset is None:
        return None
    return offset.total_seconds() / 3600


def get_tzname(dt: datetime) -> str | None:
    """Get timezone name."""
    return dt.tzname()


def is_aware(dt: datetime) -> bool:
    """Check if datetime is timezone-aware."""
    return dt.tzinfo is not None and dt.utcoffset() is not None


def is_naive(dt: datetime) -> bool:
    """Check if datetime is timezone-naive."""
    return dt.tzinfo is None or dt.utcoffset() is None


def strip_timezone(dt: datetime) -> datetime:
    """Remove timezone info from datetime."""
    return dt.replace(tzinfo=None)


def list_timezones() -> list[str]:
    """List all available timezones."""
    return sorted(available_timezones())


def list_common_timezones() -> list[str]:
    """List common timezones."""
    common = [
        "UTC",
        "US/Eastern",
        "US/Central",
        "US/Mountain",
        "US/Pacific",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Asia/Singapore",
        "Australia/Sydney",
    ]
    return [tz for tz in common if tz in available_timezones()]


def get_utc_offset_at(tz: ZoneInfo, dt: datetime) -> timedelta:
    """Get UTC offset for timezone at specific datetime."""
    aware = dt.replace(tzinfo=tz)
    offset = aware.utcoffset()
    return offset if offset else timedelta(0)


def is_dst(dt: datetime) -> bool | None:
    """Check if datetime is in DST."""
    if dt.tzinfo is None:
        return None
    dst = dt.dst()
    if dst is None:
        return None
    return dst != timedelta(0)


def get_dst_offset(dt: datetime) -> timedelta | None:
    """Get DST offset for datetime."""
    return dt.dst()


def utc_timestamp(dt: datetime) -> float:
    """Get UTC timestamp from aware datetime."""
    return dt.timestamp()


def from_utc_timestamp(ts: float, tz: ZoneInfo | timezone | None = None) -> datetime:
    """Create datetime from UTC timestamp in timezone."""
    if tz is None:
        tz = UTC
    return datetime.fromtimestamp(ts, tz=tz)


def compare_aware(dt1: datetime, dt2: datetime) -> int:
    """Compare two aware datetimes (-1, 0, 1)."""
    if dt1 < dt2:
        return -1
    elif dt1 > dt2:
        return 1
    return 0


def same_instant(dt1: datetime, dt2: datetime) -> bool:
    """Check if two aware datetimes represent the same instant."""
    return dt1.timestamp() == dt2.timestamp()


def format_with_offset(dt: datetime) -> str:
    """Format datetime with UTC offset."""
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def format_iso_with_tz(dt: datetime) -> str:
    """Format datetime as ISO with timezone."""
    return dt.isoformat()


def parse_iso_with_tz(s: str) -> datetime:
    """Parse ISO datetime with timezone."""
    return datetime.fromisoformat(s)


def time_in_timezone(t: time, tz: ZoneInfo | timezone) -> time:
    """Create time with timezone."""
    return t.replace(tzinfo=tz)


def world_clock(zones: list[str]) -> dict[str, datetime]:
    """Get current time in multiple timezones."""
    now = datetime.now(UTC)
    result = {}
    for zone in zones:
        tz = ZoneInfo(zone)
        result[zone] = now.astimezone(tz)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Datetime timezone CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # now
    now_p = subparsers.add_parser("now", help="Current time in timezone")
    now_p.add_argument("timezone", nargs="?", default="UTC", help="Timezone")

    # convert
    convert_p = subparsers.add_parser("convert", help="Convert between timezones")
    convert_p.add_argument("datetime", help="ISO datetime with timezone")
    convert_p.add_argument("--to", dest="to_tz", required=True, help="Target timezone")

    # world
    subparsers.add_parser("world", help="World clock")

    # list
    list_p = subparsers.add_parser("list", help="List timezones")
    list_p.add_argument("-a", "--all", action="store_true", help="List all")

    # offset
    offset_p = subparsers.add_parser("offset", help="Get timezone offset")
    offset_p.add_argument("timezone", help="Timezone")

    args = parser.parse_args()

    if args.command == "now":
        tz = ZoneInfo(args.timezone) if args.timezone != "UTC" else UTC
        dt = now_in_timezone(tz)
        print(f"Current time: {format_iso_with_tz(dt)}")
        print(f"Timezone: {get_tzname(dt)}")
        offset = get_offset_hours(dt)
        print(f"UTC offset: {'+' if offset and offset >= 0 else ''}{offset}h")

    elif args.command == "convert":
        dt = parse_iso_with_tz(args.datetime)
        target_tz = ZoneInfo(args.to_tz)
        converted = convert_timezone(dt, target_tz)
        print(f"Original: {format_iso_with_tz(dt)}")
        print(f"Converted: {format_iso_with_tz(converted)}")

    elif args.command == "world":
        zones = list_common_timezones()
        clock = world_clock(zones)
        print("World Clock:")
        for zone, dt in clock.items():
            print(f"  {zone}: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

    elif args.command == "list":
        if args.all:
            zones = list_timezones()
        else:
            zones = list_common_timezones()
        for zone in zones:
            print(zone)

    elif args.command == "offset":
        tz = ZoneInfo(args.timezone)
        dt = datetime.now(tz)
        offset = get_offset_hours(dt)
        dst = is_dst(dt)
        print(f"Timezone: {args.timezone}")
        print(f"UTC offset: {'+' if offset and offset >= 0 else ''}{offset}h")
        print(f"DST active: {dst}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
