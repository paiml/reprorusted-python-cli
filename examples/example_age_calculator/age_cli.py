#!/usr/bin/env python3
"""Age calculator CLI.

Calculate age and related date information.
"""

import argparse
import sys
from datetime import date, datetime


def parse_date(date_str: str) -> date | None:
    """Parse date string into date object."""
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def calculate_age(birth_date: date, as_of: date | None = None) -> dict:
    """Calculate age in years, months, days."""
    if as_of is None:
        as_of = date.today()

    # Calculate years
    years = as_of.year - birth_date.year

    # Adjust if birthday hasn't occurred this year
    if (as_of.month, as_of.day) < (birth_date.month, birth_date.day):
        years -= 1

    # Calculate months
    months = as_of.month - birth_date.month
    if as_of.day < birth_date.day:
        months -= 1
    if months < 0:
        months += 12

    # Calculate days
    days = as_of.day - birth_date.day
    if days < 0:
        # Get days in previous month
        prev_month = as_of.month - 1 if as_of.month > 1 else 12
        prev_year = as_of.year if as_of.month > 1 else as_of.year - 1
        days_in_prev = days_in_month(prev_year, prev_month)
        days += days_in_prev

    return {
        "years": years,
        "months": months,
        "days": days,
    }


def days_in_month(year: int, month: int) -> int:
    """Get number of days in a month."""
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    if month in [4, 6, 9, 11]:
        return 30
    # February
    if is_leap_year(year):
        return 29
    return 28


def is_leap_year(year: int) -> bool:
    """Check if year is a leap year."""
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False


def total_days(birth_date: date, as_of: date | None = None) -> int:
    """Calculate total days lived."""
    if as_of is None:
        as_of = date.today()
    return (as_of - birth_date).days


def next_birthday(birth_date: date, as_of: date | None = None) -> date:
    """Calculate next birthday."""
    if as_of is None:
        as_of = date.today()

    # Try this year
    try:
        this_year = date(as_of.year, birth_date.month, birth_date.day)
    except ValueError:
        # Feb 29 in non-leap year
        this_year = date(as_of.year, 3, 1)

    if this_year > as_of:
        return this_year

    # Next year
    try:
        return date(as_of.year + 1, birth_date.month, birth_date.day)
    except ValueError:
        return date(as_of.year + 1, 3, 1)


def days_until_birthday(birth_date: date, as_of: date | None = None) -> int:
    """Days until next birthday."""
    if as_of is None:
        as_of = date.today()
    return (next_birthday(birth_date, as_of) - as_of).days


def zodiac_sign(birth_date: date) -> str:
    """Get zodiac sign for birth date."""
    month = birth_date.month
    day = birth_date.day

    signs = [
        (1, 20, "Capricorn"),
        (2, 19, "Aquarius"),
        (3, 20, "Pisces"),
        (4, 20, "Aries"),
        (5, 21, "Taurus"),
        (6, 21, "Gemini"),
        (7, 22, "Cancer"),
        (8, 23, "Leo"),
        (9, 23, "Virgo"),
        (10, 23, "Libra"),
        (11, 22, "Scorpio"),
        (12, 22, "Sagittarius"),
    ]

    for end_month, end_day, sign in signs:
        if month == end_month and day <= end_day:
            return sign
        if month < end_month:
            # Return previous sign
            idx = signs.index((end_month, end_day, sign))
            return signs[idx - 1][2]

    return "Capricorn"


def day_of_week(d: date) -> str:
    """Get day of week name."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[d.weekday()]


def format_age(age: dict) -> str:
    """Format age dict for display."""
    parts = []
    if age["years"] > 0:
        parts.append(f"{age['years']} year{'s' if age['years'] != 1 else ''}")
    if age["months"] > 0:
        parts.append(f"{age['months']} month{'s' if age['months'] != 1 else ''}")
    if age["days"] > 0 or not parts:
        parts.append(f"{age['days']} day{'s' if age['days'] != 1 else ''}")
    return ", ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate age and date information")
    parser.add_argument("birthdate", help="Birth date (YYYY-MM-DD)")
    parser.add_argument("--as-of", metavar="DATE", help="Calculate as of date (default: today)")
    parser.add_argument("--days", action="store_true", help="Show total days")
    parser.add_argument("--next", action="store_true", help="Show next birthday")
    parser.add_argument("--zodiac", action="store_true", help="Show zodiac sign")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    birth = parse_date(args.birthdate)
    if not birth:
        print(f"Invalid date format: {args.birthdate}", file=sys.stderr)
        return 1

    as_of = None
    if args.as_of:
        as_of = parse_date(args.as_of)
        if not as_of:
            print(f"Invalid date format: {args.as_of}", file=sys.stderr)
            return 1

    age = calculate_age(birth, as_of)

    if args.json:
        import json

        result = {
            "birth_date": str(birth),
            "age": age,
            "total_days": total_days(birth, as_of),
            "next_birthday": str(next_birthday(birth, as_of)),
            "days_until_birthday": days_until_birthday(birth, as_of),
            "zodiac": zodiac_sign(birth),
            "birth_day": day_of_week(birth),
        }
        print(json.dumps(result, indent=2))
        return 0

    if args.days:
        print(total_days(birth, as_of))
        return 0

    if args.next:
        nb = next_birthday(birth, as_of)
        days = days_until_birthday(birth, as_of)
        print(f"Next birthday: {nb} ({days} days)")
        return 0

    if args.zodiac:
        print(zodiac_sign(birth))
        return 0

    # Default: show full info
    print(f"Birth date: {birth} ({day_of_week(birth)})")
    print(f"Age: {format_age(age)}")
    print(f"Total days: {total_days(birth, as_of):,}")
    print(f"Zodiac: {zodiac_sign(birth)}")
    nb = next_birthday(birth, as_of)
    days = days_until_birthday(birth, as_of)
    print(f"Next birthday: {nb} ({days} days away)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
