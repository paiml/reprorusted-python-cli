#!/usr/bin/env python3
"""Datetime Calendar CLI.

Calendar module operations.
"""

import argparse
import calendar
import sys
from datetime import date


def is_leap(year: int) -> bool:
    """Check if year is a leap year."""
    return calendar.isleap(year)


def leap_days(y1: int, y2: int) -> int:
    """Count leap years between y1 and y2."""
    return calendar.leapdays(y1, y2)


def weekday(year: int, month: int, day: int) -> int:
    """Get weekday for date (Monday=0)."""
    return calendar.weekday(year, month, day)


def monthrange(year: int, month: int) -> tuple[int, int]:
    """Get first weekday and days in month."""
    return calendar.monthrange(year, month)


def days_in_month(year: int, month: int) -> int:
    """Get number of days in month."""
    _, days = calendar.monthrange(year, month)
    return days


def first_weekday_of_month(year: int, month: int) -> int:
    """Get first weekday of month (Monday=0)."""
    first, _ = calendar.monthrange(year, month)
    return first


def month_calendar(year: int, month: int) -> list[list[int]]:
    """Get calendar grid for month."""
    return calendar.monthcalendar(year, month)


def text_calendar_month(year: int, month: int, w: int = 2, lines: int = 1) -> str:
    """Get text calendar for month."""
    return calendar.month(year, month, w, lines)


def text_calendar_year(year: int, w: int = 2, lines: int = 1, c: int = 6, m: int = 3) -> str:
    """Get text calendar for year."""
    return calendar.calendar(year, w, lines, c, m)


def month_name(month: int) -> str:
    """Get month name (1-12)."""
    return calendar.month_name[month]


def month_abbr(month: int) -> str:
    """Get abbreviated month name."""
    return calendar.month_abbr[month]


def day_name(weekday: int) -> str:
    """Get day name (0=Monday)."""
    return calendar.day_name[weekday]


def day_abbr(weekday: int) -> str:
    """Get abbreviated day name."""
    return calendar.day_abbr[weekday]


def all_month_names() -> list[str]:
    """Get all month names."""
    return list(calendar.month_name)[1:]  # Skip empty first element


def all_day_names() -> list[str]:
    """Get all day names."""
    return list(calendar.day_name)


def iter_month_days(year: int, month: int) -> list[tuple[int, int]]:
    """Iterate over days in month as (weekday, day) tuples."""
    c = calendar.Calendar()
    return [(wd, day) for day, wd in c.itermonthdays2(year, month) if day != 0]


def iter_month_dates(year: int, month: int) -> list[date]:
    """Iterate over dates in month."""
    c = calendar.Calendar()
    return [date(year, month, day) for day, _ in c.itermonthdays2(year, month) if day != 0]


def weeks_in_month(year: int, month: int) -> int:
    """Get number of weeks in month."""
    return len(calendar.monthcalendar(year, month))


def get_week(year: int, month: int, week: int) -> list[int]:
    """Get specific week of month (0-indexed)."""
    cal = calendar.monthcalendar(year, month)
    if 0 <= week < len(cal):
        return cal[week]
    return []


def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date | None:
    """Get nth occurrence of weekday in month (1-indexed)."""
    c = calendar.Calendar()
    days = [day for day, wd in c.itermonthdays2(year, month) if day != 0 and wd == weekday]
    if 1 <= n <= len(days):
        return date(year, month, days[n - 1])
    return None


def last_weekday_of_month(year: int, month: int, weekday: int) -> date | None:
    """Get last occurrence of weekday in month."""
    c = calendar.Calendar()
    days = [day for day, wd in c.itermonthdays2(year, month) if day != 0 and wd == weekday]
    if days:
        return date(year, month, days[-1])
    return None


def timegm(t: tuple) -> int:
    """Convert time tuple to Unix timestamp (UTC)."""
    return calendar.timegm(t)


def set_first_weekday(weekday: int) -> None:
    """Set first day of week (0=Monday, 6=Sunday)."""
    calendar.setfirstweekday(weekday)


def get_first_weekday() -> int:
    """Get first day of week setting."""
    return calendar.firstweekday()


def html_calendar_month(year: int, month: int) -> str:
    """Get HTML calendar for month."""
    hc = calendar.HTMLCalendar()
    return hc.formatmonth(year, month)


def html_calendar_year(year: int) -> str:
    """Get HTML calendar for year."""
    hc = calendar.HTMLCalendar()
    return hc.formatyear(year)


def year_calendar(year: int) -> list[list[list[list[int]]]]:
    """Get calendar data for year."""
    c = calendar.Calendar()
    return [c.monthdayscalendar(year, month) for month in range(1, 13)]


def weekdays_in_month(year: int, month: int, weekday: int) -> list[int]:
    """Get all occurrences of a weekday in month."""
    c = calendar.Calendar()
    return [day for day, wd in c.itermonthdays2(year, month) if day != 0 and wd == weekday]


def count_weekdays_in_month(year: int, month: int, weekday: int) -> int:
    """Count occurrences of weekday in month."""
    return len(weekdays_in_month(year, month, weekday))


def business_days_in_month(year: int, month: int) -> int:
    """Count business days (Mon-Fri) in month."""
    c = calendar.Calendar()
    count = 0
    for day, wd in c.itermonthdays2(year, month):
        if day != 0 and wd < 5:
            count += 1
    return count


def weekend_days_in_month(year: int, month: int) -> int:
    """Count weekend days in month."""
    c = calendar.Calendar()
    count = 0
    for day, wd in c.itermonthdays2(year, month):
        if day != 0 and wd >= 5:
            count += 1
    return count


def is_last_day_of_month(d: date) -> bool:
    """Check if date is last day of month."""
    return d.day == days_in_month(d.year, d.month)


def is_first_day_of_month(d: date) -> bool:
    """Check if date is first day of month."""
    return d.day == 1


def next_month(year: int, month: int) -> tuple[int, int]:
    """Get next month as (year, month)."""
    if month == 12:
        return (year + 1, 1)
    return (year, month + 1)


def prev_month(year: int, month: int) -> tuple[int, int]:
    """Get previous month as (year, month)."""
    if month == 1:
        return (year - 1, 12)
    return (year, month - 1)


def quarter_of_month(month: int) -> int:
    """Get quarter (1-4) for month."""
    return (month - 1) // 3 + 1


def months_in_quarter(quarter: int) -> list[int]:
    """Get months in quarter (1-4)."""
    start = (quarter - 1) * 3 + 1
    return [start, start + 1, start + 2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Datetime calendar CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # month
    month_p = subparsers.add_parser("month", help="Show month calendar")
    month_p.add_argument("year", type=int, help="Year")
    month_p.add_argument("month", type=int, help="Month")

    # year
    year_p = subparsers.add_parser("year", help="Show year calendar")
    year_p.add_argument("year", type=int, help="Year")

    # leap
    leap_p = subparsers.add_parser("leap", help="Check leap year")
    leap_p.add_argument("year", type=int, help="Year")

    # info
    info_p = subparsers.add_parser("info", help="Month info")
    info_p.add_argument("year", type=int, help="Year")
    info_p.add_argument("month", type=int, help="Month")

    # nth
    nth_p = subparsers.add_parser("nth", help="Find nth weekday")
    nth_p.add_argument("year", type=int, help="Year")
    nth_p.add_argument("month", type=int, help="Month")
    nth_p.add_argument("weekday", type=int, help="Weekday (0=Mon)")
    nth_p.add_argument("n", type=int, help="Which occurrence")

    args = parser.parse_args()

    if args.command == "month":
        print(text_calendar_month(args.year, args.month))

    elif args.command == "year":
        print(text_calendar_year(args.year))

    elif args.command == "leap":
        if is_leap(args.year):
            print(f"{args.year} is a leap year")
        else:
            print(f"{args.year} is not a leap year")

    elif args.command == "info":
        name = month_name(args.month)
        days = days_in_month(args.year, args.month)
        weeks = weeks_in_month(args.year, args.month)
        biz = business_days_in_month(args.year, args.month)
        weekend = weekend_days_in_month(args.year, args.month)
        print(f"Month: {name} {args.year}")
        print(f"Days: {days}")
        print(f"Weeks: {weeks}")
        print(f"Business days: {biz}")
        print(f"Weekend days: {weekend}")

    elif args.command == "nth":
        d = nth_weekday_of_month(args.year, args.month, args.weekday, args.n)
        if d:
            day_n = day_name(args.weekday)
            print(
                f"The {args.n}{'st' if args.n == 1 else 'nd' if args.n == 2 else 'rd' if args.n == 3 else 'th'} {day_n} is {d}"
            )
        else:
            print("Not found")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
