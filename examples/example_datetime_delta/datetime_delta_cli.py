#!/usr/bin/env python3
"""Datetime Delta CLI.

Timedelta operations for date/time arithmetic.
"""

import argparse
import sys
from datetime import date, datetime, time, timedelta


def create_timedelta(
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    milliseconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0,
) -> timedelta:
    """Create timedelta from components."""
    return timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )


def days_delta(days: int) -> timedelta:
    """Create timedelta for days."""
    return timedelta(days=days)


def hours_delta(hours: int) -> timedelta:
    """Create timedelta for hours."""
    return timedelta(hours=hours)


def minutes_delta(minutes: int) -> timedelta:
    """Create timedelta for minutes."""
    return timedelta(minutes=minutes)


def seconds_delta(seconds: int) -> timedelta:
    """Create timedelta for seconds."""
    return timedelta(seconds=seconds)


def weeks_delta(weeks: int) -> timedelta:
    """Create timedelta for weeks."""
    return timedelta(weeks=weeks)


def get_days(td: timedelta) -> int:
    """Get days component."""
    return td.days


def get_seconds(td: timedelta) -> int:
    """Get seconds component."""
    return td.seconds


def get_microseconds(td: timedelta) -> int:
    """Get microseconds component."""
    return td.microseconds


def total_seconds(td: timedelta) -> float:
    """Get total seconds."""
    return td.total_seconds()


def add_days(d: date, days: int) -> date:
    """Add days to date."""
    return d + timedelta(days=days)


def subtract_days(d: date, days: int) -> date:
    """Subtract days from date."""
    return d - timedelta(days=days)


def add_to_datetime(dt: datetime, td: timedelta) -> datetime:
    """Add timedelta to datetime."""
    return dt + td


def subtract_from_datetime(dt: datetime, td: timedelta) -> datetime:
    """Subtract timedelta from datetime."""
    return dt - td


def diff_dates(d1: date, d2: date) -> timedelta:
    """Get difference between dates."""
    return d1 - d2


def diff_datetimes(dt1: datetime, dt2: datetime) -> timedelta:
    """Get difference between datetimes."""
    return dt1 - dt2


def days_between(d1: date, d2: date) -> int:
    """Get days between dates."""
    return abs((d1 - d2).days)


def hours_between(dt1: datetime, dt2: datetime) -> float:
    """Get hours between datetimes."""
    return abs((dt1 - dt2).total_seconds()) / 3600


def minutes_between(dt1: datetime, dt2: datetime) -> float:
    """Get minutes between datetimes."""
    return abs((dt1 - dt2).total_seconds()) / 60


def seconds_between(dt1: datetime, dt2: datetime) -> float:
    """Get seconds between datetimes."""
    return abs((dt1 - dt2).total_seconds())


def add_business_days(d: date, days: int) -> date:
    """Add business days (skip weekends)."""
    result = d
    added = 0
    direction = 1 if days >= 0 else -1
    days = abs(days)
    while added < days:
        result += timedelta(days=direction)
        if result.weekday() < 5:  # Monday=0, Friday=4
            added += 1
    return result


def next_weekday(d: date, weekday: int) -> date:
    """Get next occurrence of weekday (0=Monday, 6=Sunday)."""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days=days_ahead)


def previous_weekday(d: date, weekday: int) -> date:
    """Get previous occurrence of weekday."""
    days_behind = d.weekday() - weekday
    if days_behind <= 0:
        days_behind += 7
    return d - timedelta(days=days_behind)


def start_of_day(dt: datetime) -> datetime:
    """Get start of day (midnight)."""
    return datetime.combine(dt.date(), time())


def end_of_day(dt: datetime) -> datetime:
    """Get end of day (23:59:59.999999)."""
    return datetime.combine(dt.date(), time(23, 59, 59, 999999))


def start_of_week(d: date) -> date:
    """Get Monday of the week."""
    return d - timedelta(days=d.weekday())


def end_of_week(d: date) -> date:
    """Get Sunday of the week."""
    return d + timedelta(days=6 - d.weekday())


def start_of_month(d: date) -> date:
    """Get first day of month."""
    return d.replace(day=1)


def end_of_month(d: date) -> date:
    """Get last day of month."""
    if d.month == 12:
        next_month = d.replace(year=d.year + 1, month=1, day=1)
    else:
        next_month = d.replace(month=d.month + 1, day=1)
    return next_month - timedelta(days=1)


def start_of_year(d: date) -> date:
    """Get first day of year."""
    return date(d.year, 1, 1)


def end_of_year(d: date) -> date:
    """Get last day of year."""
    return date(d.year, 12, 31)


def is_weekend(d: date) -> bool:
    """Check if date is weekend."""
    return d.weekday() >= 5


def is_weekday(d: date) -> bool:
    """Check if date is weekday."""
    return d.weekday() < 5


def multiply_delta(td: timedelta, factor: int) -> timedelta:
    """Multiply timedelta by factor."""
    return td * factor


def divide_delta(td: timedelta, divisor: int) -> timedelta:
    """Divide timedelta by divisor."""
    return td // divisor


def negate_delta(td: timedelta) -> timedelta:
    """Negate timedelta."""
    return -td


def abs_delta(td: timedelta) -> timedelta:
    """Get absolute value of timedelta."""
    return abs(td)


def min_delta() -> timedelta:
    """Get minimum timedelta."""
    return timedelta.min


def max_delta() -> timedelta:
    """Get maximum timedelta."""
    return timedelta.max


def resolution() -> timedelta:
    """Get timedelta resolution."""
    return timedelta.resolution


def format_delta(td: timedelta) -> str:
    """Format timedelta as string."""
    total = int(td.total_seconds())
    sign = "-" if total < 0 else ""
    total = abs(total)
    days = total // 86400
    hours = (total % 86400) // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return sign + " ".join(parts)


def format_delta_verbose(td: timedelta) -> str:
    """Format timedelta verbosely."""
    total = int(td.total_seconds())
    if total < 0:
        return f"-{format_delta_verbose(abs(td))}"

    days = total // 86400
    hours = (total % 86400) // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return ", ".join(parts)


def age_in_years(birth_date: date) -> int:
    """Calculate age in years."""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def main() -> int:
    parser = argparse.ArgumentParser(description="Datetime delta CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # add
    add_p = subparsers.add_parser("add", help="Add duration to date")
    add_p.add_argument("date", help="Date (YYYY-MM-DD)")
    add_p.add_argument("--days", type=int, default=0, help="Days")
    add_p.add_argument("--weeks", type=int, default=0, help="Weeks")
    add_p.add_argument("--hours", type=int, default=0, help="Hours")

    # diff
    diff_p = subparsers.add_parser("diff", help="Difference between dates")
    diff_p.add_argument("date1", help="First date")
    diff_p.add_argument("date2", help="Second date")

    # business
    biz_p = subparsers.add_parser("business", help="Business day operations")
    biz_p.add_argument("date", help="Start date")
    biz_p.add_argument("days", type=int, help="Business days to add")

    # range
    range_p = subparsers.add_parser("range", help="Date range info")
    range_p.add_argument("date", nargs="?", help="Date (default: today)")

    # age
    age_p = subparsers.add_parser("age", help="Calculate age")
    age_p.add_argument("birth_date", help="Birth date (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.command == "add":
        d = date.fromisoformat(args.date)
        td = create_timedelta(days=args.days, weeks=args.weeks, hours=args.hours)
        if args.hours:
            dt = datetime.combine(d, time())
            result = add_to_datetime(dt, td)
            print(f"Result: {result}")
        else:
            result = d + td
            print(f"Result: {result}")

    elif args.command == "diff":
        d1 = date.fromisoformat(args.date1)
        d2 = date.fromisoformat(args.date2)
        delta = diff_dates(d1, d2)
        print(f"Difference: {delta}")
        print(f"Days: {delta.days}")
        print(f"Formatted: {format_delta_verbose(delta)}")

    elif args.command == "business":
        d = date.fromisoformat(args.date)
        result = add_business_days(d, args.days)
        print(f"Result: {result}")

    elif args.command == "range":
        if args.date:
            d = date.fromisoformat(args.date)
        else:
            d = date.today()
        print(f"Date: {d}")
        print(f"Start of week: {start_of_week(d)}")
        print(f"End of week: {end_of_week(d)}")
        print(f"Start of month: {start_of_month(d)}")
        print(f"End of month: {end_of_month(d)}")
        print(f"Start of year: {start_of_year(d)}")
        print(f"End of year: {end_of_year(d)}")

    elif args.command == "age":
        birth = date.fromisoformat(args.birth_date)
        age = age_in_years(birth)
        print(f"Age: {age} years")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
