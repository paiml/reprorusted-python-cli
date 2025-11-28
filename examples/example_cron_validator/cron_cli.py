#!/usr/bin/env python3
"""Cron expression validator CLI.

Validate and explain cron expressions.
"""

import argparse
import re
import sys
from datetime import datetime, timedelta

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}

MONTH_NAMES = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

DAY_NAMES = {
    "sun": 0,
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
}


def parse_field(field: str, field_name: str) -> list[int] | None:
    """Parse a single cron field.

    Returns list of values or None if invalid.
    """
    min_val, max_val = FIELD_RANGES[field_name]
    field = field.lower()

    # Replace month/day names
    if field_name == "month":
        for name, num in MONTH_NAMES.items():
            field = field.replace(name, str(num))
    elif field_name == "day_of_week":
        for name, num in DAY_NAMES.items():
            field = field.replace(name, str(num))

    values = set()

    # Handle wildcards
    if field == "*":
        return list(range(min_val, max_val + 1))

    # Handle comma-separated parts
    for part in field.split(","):
        part = part.strip()

        # Handle step values */n or range/n
        step = 1
        if "/" in part:
            part, step_str = part.split("/", 1)
            try:
                step = int(step_str)
            except ValueError:
                return None

        # Handle ranges
        if "-" in part and part != "*":
            range_match = re.match(r"(\d+)-(\d+)", part)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                if start > end or start < min_val or end > max_val:
                    return None
                values.update(range(start, end + 1, step))
            else:
                return None
        elif part == "*":
            values.update(range(min_val, max_val + 1, step))
        else:
            try:
                val = int(part)
                if val < min_val or val > max_val:
                    return None
                values.add(val)
            except ValueError:
                return None

    return sorted(values)


def parse_cron(expression: str) -> dict | None:
    """Parse cron expression into field values.

    Returns dict with parsed values or None if invalid.
    """
    parts = expression.strip().split()

    if len(parts) != 5:
        return None

    result = {}
    for i, field_name in enumerate(FIELD_NAMES):
        values = parse_field(parts[i], field_name)
        if values is None:
            return None
        result[field_name] = values

    return result


def validate_cron(expression: str) -> tuple[bool, str]:
    """Validate cron expression.

    Returns (is_valid, error_message).
    """
    parsed = parse_cron(expression)
    if parsed is None:
        return False, "Invalid cron expression format"
    return True, ""


def explain_field(values: list[int], field_name: str) -> str:
    """Generate human-readable explanation of field values."""
    min_val, max_val = FIELD_RANGES[field_name]

    if values == list(range(min_val, max_val + 1)):
        return "every " + field_name.replace("_", " ")

    if len(values) == 1:
        if field_name == "day_of_week":
            days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            return f"on {days[values[0]]}"
        if field_name == "month":
            months = [
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
            return f"in {months[values[0]]}"
        return f"at {field_name.replace('_', ' ')} {values[0]}"

    # Check for step pattern
    if len(values) > 2:
        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        if len(set(diffs)) == 1:
            step = diffs[0]
            return f"every {step} {field_name.replace('_', ' ')}s"

    return f"{field_name.replace('_', ' ')}s {', '.join(map(str, values))}"


def explain_cron(expression: str) -> str:
    """Generate human-readable explanation of cron expression."""
    parsed = parse_cron(expression)
    if not parsed:
        return "Invalid expression"

    parts = []

    # Minute
    if parsed["minute"] != list(range(0, 60)):
        parts.append(f"at minute {', '.join(map(str, parsed['minute']))}")

    # Hour
    if parsed["hour"] != list(range(0, 24)):
        parts.append(f"at hour {', '.join(map(str, parsed['hour']))}")

    # Day of month
    if parsed["day_of_month"] != list(range(1, 32)):
        parts.append(f"on day {', '.join(map(str, parsed['day_of_month']))}")

    # Month
    if parsed["month"] != list(range(1, 13)):
        months = [
            "",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        month_names = [months[m] for m in parsed["month"]]
        parts.append(f"in {', '.join(month_names)}")

    # Day of week
    if parsed["day_of_week"] != list(range(0, 7)):
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        day_names = [days[d] for d in parsed["day_of_week"]]
        parts.append(f"on {', '.join(day_names)}")

    if not parts:
        return "Every minute"

    return ", ".join(parts)


def matches_cron(parsed: dict, dt: datetime) -> bool:
    """Check if datetime matches parsed cron expression."""
    if dt.minute not in parsed["minute"]:
        return False
    if dt.hour not in parsed["hour"]:
        return False
    if dt.day not in parsed["day_of_month"]:
        return False
    if dt.month not in parsed["month"]:
        return False
    if dt.weekday() not in [(d - 1) % 7 for d in parsed["day_of_week"]]:
        # Cron: 0=Sunday, Python: 0=Monday
        dow = (dt.weekday() + 1) % 7
        if dow not in parsed["day_of_week"]:
            return False
    return True


def next_run(expression: str, after: datetime | None = None) -> datetime | None:
    """Calculate next run time for cron expression."""
    parsed = parse_cron(expression)
    if not parsed:
        return None

    if after is None:
        after = datetime.now()

    current = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

    # Check up to 1 year ahead
    for _ in range(365 * 24 * 60):
        if matches_cron(parsed, current):
            return current
        current += timedelta(minutes=1)

    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and explain cron expressions")
    parser.add_argument("expression", nargs="?", help="Cron expression (5 fields)")
    parser.add_argument("--validate", action="store_true", help="Only validate, don't explain")
    parser.add_argument("--next", action="store_true", help="Show next run time")
    parser.add_argument("--next-n", type=int, metavar="N", help="Show next N run times")

    args = parser.parse_args()

    if not args.expression:
        print("Usage: cron_cli.py '* * * * *'")
        print("\nCommon examples:")
        print("  '0 * * * *'     - Every hour")
        print("  '0 0 * * *'     - Every day at midnight")
        print("  '0 0 * * 0'     - Every Sunday at midnight")
        print("  '*/15 * * * *'  - Every 15 minutes")
        return 0

    valid, error = validate_cron(args.expression)

    if not valid:
        print(f"Invalid: {error}", file=sys.stderr)
        return 1

    if args.validate:
        print("Valid")
        return 0

    if args.next:
        next_time = next_run(args.expression)
        if next_time:
            print(f"Next run: {next_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("No upcoming run found")
        return 0

    if args.next_n:
        current = datetime.now()
        print(f"Next {args.next_n} runs:")
        for _ in range(args.next_n):
            next_time = next_run(args.expression, current)
            if next_time:
                print(f"  {next_time.strftime('%Y-%m-%d %H:%M')}")
                current = next_time
            else:
                break
        return 0

    # Default: explain
    print(f"Expression: {args.expression}")
    print(f"Explanation: {explain_cron(args.expression)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
