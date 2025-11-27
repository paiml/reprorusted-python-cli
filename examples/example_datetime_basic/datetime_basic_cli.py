#!/usr/bin/env python3
"""Datetime Basic CLI.

Basic date and time operations.
"""

import argparse
import sys
from datetime import UTC, date, datetime, time


def today() -> date:
    """Get today's date."""
    return date.today()


def now() -> datetime:
    """Get current datetime."""
    return datetime.now()


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def create_date(year: int, month: int, day: int) -> date:
    """Create date from components."""
    return date(year, month, day)


def create_time(hour: int, minute: int, second: int = 0, microsecond: int = 0) -> time:
    """Create time from components."""
    return time(hour, minute, second, microsecond)


def create_datetime(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0
) -> datetime:
    """Create datetime from components."""
    return datetime(year, month, day, hour, minute, second)


def get_year(d: date) -> int:
    """Get year from date."""
    return d.year


def get_month(d: date) -> int:
    """Get month from date."""
    return d.month


def get_day(d: date) -> int:
    """Get day from date."""
    return d.day


def get_hour(t: time) -> int:
    """Get hour from time."""
    return t.hour


def get_minute(t: time) -> int:
    """Get minute from time."""
    return t.minute


def get_second(t: time) -> int:
    """Get second from time."""
    return t.second


def get_microsecond(t: time) -> int:
    """Get microsecond from time."""
    return t.microsecond


def weekday(d: date) -> int:
    """Get weekday (Monday=0, Sunday=6)."""
    return d.weekday()


def isoweekday(d: date) -> int:
    """Get ISO weekday (Monday=1, Sunday=7)."""
    return d.isoweekday()


def isocalendar(d: date) -> tuple[int, int, int]:
    """Get ISO calendar (year, week, weekday)."""
    iso = d.isocalendar()
    return (iso.year, iso.week, iso.weekday)


def isoformat_date(d: date) -> str:
    """Get ISO format string for date."""
    return d.isoformat()


def isoformat_time(t: time) -> str:
    """Get ISO format string for time."""
    return t.isoformat()


def isoformat_datetime(dt: datetime) -> str:
    """Get ISO format string for datetime."""
    return dt.isoformat()


def from_isoformat_date(s: str) -> date:
    """Parse date from ISO format."""
    return date.fromisoformat(s)


def from_isoformat_time(s: str) -> time:
    """Parse time from ISO format."""
    return time.fromisoformat(s)


def from_isoformat_datetime(s: str) -> datetime:
    """Parse datetime from ISO format."""
    return datetime.fromisoformat(s)


def from_timestamp(ts: float) -> datetime:
    """Create datetime from Unix timestamp."""
    return datetime.fromtimestamp(ts)


def from_utc_timestamp(ts: float) -> datetime:
    """Create datetime from UTC Unix timestamp."""
    return datetime.fromtimestamp(ts, UTC)


def to_timestamp(dt: datetime) -> float:
    """Get Unix timestamp from datetime."""
    return dt.timestamp()


def from_ordinal(n: int) -> date:
    """Create date from ordinal (days since year 1)."""
    return date.fromordinal(n)


def to_ordinal(d: date) -> int:
    """Get ordinal (days since year 1) from date."""
    return d.toordinal()


def replace_date(
    d: date, year: int | None = None, month: int | None = None, day: int | None = None
) -> date:
    """Replace date components."""
    return d.replace(
        year=year if year is not None else d.year,
        month=month if month is not None else d.month,
        day=day if day is not None else d.day,
    )


def replace_time(
    t: time,
    hour: int | None = None,
    minute: int | None = None,
    second: int | None = None,
) -> time:
    """Replace time components."""
    return t.replace(
        hour=hour if hour is not None else t.hour,
        minute=minute if minute is not None else t.minute,
        second=second if second is not None else t.second,
    )


def date_to_datetime(d: date) -> datetime:
    """Convert date to datetime at midnight."""
    return datetime.combine(d, time())


def datetime_date(dt: datetime) -> date:
    """Extract date from datetime."""
    return dt.date()


def datetime_time(dt: datetime) -> time:
    """Extract time from datetime."""
    return dt.time()


def combine(d: date, t: time) -> datetime:
    """Combine date and time into datetime."""
    return datetime.combine(d, t)


def min_date() -> date:
    """Get minimum representable date."""
    return date.min


def max_date() -> date:
    """Get maximum representable date."""
    return date.max


def min_time() -> time:
    """Get minimum representable time."""
    return time.min


def max_time() -> time:
    """Get maximum representable time."""
    return time.max


def min_datetime() -> datetime:
    """Get minimum representable datetime."""
    return datetime.min


def max_datetime() -> datetime:
    """Get maximum representable datetime."""
    return datetime.max


def ctime(dt: datetime) -> str:
    """Get ctime format string."""
    return dt.ctime()


def timetuple(dt: datetime) -> tuple:
    """Get time tuple."""
    return dt.timetuple()


def is_leap_year(year: int) -> bool:
    """Check if year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    """Get number of days in a month."""
    if month == 2:
        return 29 if is_leap_year(year) else 28
    elif month in (4, 6, 9, 11):
        return 30
    else:
        return 31


def days_in_year(year: int) -> int:
    """Get number of days in a year."""
    return 366 if is_leap_year(year) else 365


def compare_dates(d1: date, d2: date) -> int:
    """Compare two dates (-1, 0, 1)."""
    if d1 < d2:
        return -1
    elif d1 > d2:
        return 1
    return 0


def weekday_name(d: date) -> str:
    """Get weekday name."""
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return names[d.weekday()]


def month_name(month: int) -> str:
    """Get month name."""
    names = [
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    return names[month]


def main() -> int:
    parser = argparse.ArgumentParser(description="Datetime basic CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # now
    subparsers.add_parser("now", help="Show current datetime")

    # today
    subparsers.add_parser("today", help="Show today's date")

    # date
    date_p = subparsers.add_parser("date", help="Create date")
    date_p.add_argument("year", type=int, help="Year")
    date_p.add_argument("month", type=int, help="Month")
    date_p.add_argument("day", type=int, help="Day")

    # parse
    parse_p = subparsers.add_parser("parse", help="Parse ISO date/datetime")
    parse_p.add_argument("value", help="ISO format string")

    # timestamp
    ts_p = subparsers.add_parser("timestamp", help="Convert timestamp")
    ts_p.add_argument("value", type=float, help="Unix timestamp")

    # weekday
    wd_p = subparsers.add_parser("weekday", help="Get weekday")
    wd_p.add_argument("date", help="Date (YYYY-MM-DD)")

    # leap
    leap_p = subparsers.add_parser("leap", help="Check leap year")
    leap_p.add_argument("year", type=int, help="Year")

    # days
    days_p = subparsers.add_parser("days", help="Days in month/year")
    days_p.add_argument("year", type=int, help="Year")
    days_p.add_argument("month", type=int, nargs="?", help="Month")

    args = parser.parse_args()

    if args.command == "now":
        print(f"Local: {now()}")
        print(f"UTC: {utc_now()}")
        print(f"Timestamp: {now().timestamp()}")

    elif args.command == "today":
        d = today()
        print(f"Date: {d}")
        print(f"Weekday: {weekday_name(d)}")
        print(f"Day of year: {d.timetuple().tm_yday}")

    elif args.command == "date":
        d = create_date(args.year, args.month, args.day)
        print(f"Date: {d}")
        print(f"ISO: {d.isoformat()}")
        print(f"Weekday: {weekday_name(d)}")

    elif args.command == "parse":
        if "T" in args.value or " " in args.value:
            dt = from_isoformat_datetime(args.value)
            print(f"Datetime: {dt}")
            print(f"Date: {dt.date()}")
            print(f"Time: {dt.time()}")
        else:
            d = from_isoformat_date(args.value)
            print(f"Date: {d}")
            print(f"Weekday: {weekday_name(d)}")

    elif args.command == "timestamp":
        dt = from_timestamp(args.value)
        print(f"Local: {dt}")
        print(f"UTC: {from_utc_timestamp(args.value)}")

    elif args.command == "weekday":
        d = from_isoformat_date(args.date)
        print(f"Weekday: {weekday(d)} ({weekday_name(d)})")
        print(f"ISO weekday: {isoweekday(d)}")

    elif args.command == "leap":
        if is_leap_year(args.year):
            print(f"{args.year} is a leap year")
        else:
            print(f"{args.year} is not a leap year")

    elif args.command == "days":
        if args.month:
            d = days_in_month(args.year, args.month)
            print(f"Days in {month_name(args.month)} {args.year}: {d}")
        else:
            d = days_in_year(args.year)
            print(f"Days in {args.year}: {d}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
