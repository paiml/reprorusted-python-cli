#!/usr/bin/env python3
"""Schedule parser CLI.

Parse and evaluate time-based schedules.
"""

import argparse
import re
import sys
from datetime import datetime, timedelta


def parse_time_range(spec: str) -> tuple[int, int] | None:
    """Parse time range like '09:00-17:00'.

    Returns (start_minutes, end_minutes) from midnight.
    """
    match = re.match(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})", spec)
    if not match:
        return None

    start_h, start_m, end_h, end_m = map(int, match.groups())
    start = start_h * 60 + start_m
    end = end_h * 60 + end_m

    return start, end


def parse_days(spec: str) -> list[int]:
    """Parse day specification.

    Examples: 'Mon-Fri', 'Mon,Wed,Fri', '1-5', 'weekdays'
    Returns list of weekday numbers (0=Monday).
    """
    spec = spec.lower().strip()

    # Named shortcuts
    if spec == "weekdays":
        return [0, 1, 2, 3, 4]
    if spec == "weekends":
        return [5, 6]
    if spec == "daily" or spec == "*":
        return [0, 1, 2, 3, 4, 5, 6]

    day_names = {
        "mon": 0,
        "monday": 0,
        "tue": 1,
        "tuesday": 1,
        "wed": 2,
        "wednesday": 2,
        "thu": 3,
        "thursday": 3,
        "fri": 4,
        "friday": 4,
        "sat": 5,
        "saturday": 5,
        "sun": 6,
        "sunday": 6,
    }

    result = []

    # Handle comma-separated
    for part in spec.split(","):
        part = part.strip()

        # Handle range
        if "-" in part:
            start, end = part.split("-", 1)
            start = start.strip()
            end = end.strip()

            if start.isdigit() and end.isdigit():
                # Numeric range
                for d in range(int(start), int(end) + 1):
                    if 0 <= d <= 6:
                        result.append(d)
            else:
                # Named range
                start_d = day_names.get(start)
                end_d = day_names.get(end)
                if start_d is not None and end_d is not None:
                    if start_d <= end_d:
                        result.extend(range(start_d, end_d + 1))
                    else:
                        # Wrap around (Fri-Mon)
                        result.extend(range(start_d, 7))
                        result.extend(range(0, end_d + 1))
        else:
            # Single day
            if part.isdigit():
                d = int(part)
                if 0 <= d <= 6:
                    result.append(d)
            else:
                d = day_names.get(part)
                if d is not None:
                    result.append(d)

    return sorted(set(result))


def parse_schedule(spec: str) -> dict:
    """Parse full schedule specification.

    Format: 'days time_range' (e.g., 'Mon-Fri 09:00-17:00')
    """
    parts = spec.strip().split()

    if len(parts) == 0:
        return {"days": [], "start": 0, "end": 1440}

    if len(parts) == 1:
        # Could be just days or just time
        time_range = parse_time_range(parts[0])
        if time_range:
            return {"days": list(range(7)), "start": time_range[0], "end": time_range[1]}
        return {"days": parse_days(parts[0]), "start": 0, "end": 1440}

    days = parse_days(parts[0])
    time_range = parse_time_range(parts[1])

    return {
        "days": days,
        "start": time_range[0] if time_range else 0,
        "end": time_range[1] if time_range else 1440,
    }


def is_in_schedule(schedule: dict, dt: datetime) -> bool:
    """Check if datetime falls within schedule."""
    weekday = dt.weekday()
    minutes = dt.hour * 60 + dt.minute

    if weekday not in schedule["days"]:
        return False

    start = schedule["start"]
    end = schedule["end"]

    # Handle overnight ranges
    if start <= end:
        return start <= minutes < end
    else:
        return minutes >= start or minutes < end


def next_occurrence(schedule: dict, after: datetime) -> datetime | None:
    """Find next datetime that matches schedule."""
    current = after.replace(second=0, microsecond=0)

    # Check up to 7 days
    for _ in range(7 * 24 * 60):  # Max iterations
        current += timedelta(minutes=1)
        if is_in_schedule(schedule, current):
            return current

    return None


def time_until_schedule(schedule: dict, dt: datetime) -> timedelta | None:
    """Calculate time until schedule starts."""
    if is_in_schedule(schedule, dt):
        return timedelta(0)

    next_start = next_occurrence(schedule, dt)
    if next_start:
        return next_start - dt

    return None


def format_schedule(schedule: dict) -> str:
    """Format schedule for display."""
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    days = schedule["days"]
    if days == list(range(7)):
        days_str = "Daily"
    elif days == [0, 1, 2, 3, 4]:
        days_str = "Weekdays"
    elif days == [5, 6]:
        days_str = "Weekends"
    else:
        days_str = ", ".join(day_names[d] for d in days)

    start_h, start_m = divmod(schedule["start"], 60)
    end_h, end_m = divmod(schedule["end"], 60)
    time_str = f"{start_h:02d}:{start_m:02d}-{end_h:02d}:{end_m:02d}"

    return f"{days_str} {time_str}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse and evaluate schedules")
    parser.add_argument("schedule", nargs="?", help="Schedule specification")
    parser.add_argument("--check", metavar="TIME", help="Check if time matches schedule")
    parser.add_argument("--next", action="store_true", help="Show next occurrence")
    parser.add_argument("--until", action="store_true", help="Show time until schedule")
    parser.add_argument("--format", action="store_true", help="Show formatted schedule")

    args = parser.parse_args()

    if not args.schedule:
        print("Usage: schedule_cli.py 'Mon-Fri 09:00-17:00'")
        return 1

    schedule = parse_schedule(args.schedule)

    if not schedule["days"]:
        print("Invalid schedule specification", file=sys.stderr)
        return 1

    if args.format:
        print(format_schedule(schedule))
        return 0

    # Get check time
    if args.check:
        # Parse time to check
        try:
            if "T" in args.check:
                check_dt = datetime.fromisoformat(args.check)
            else:
                check_dt = datetime.strptime(args.check, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Invalid time format: {args.check}", file=sys.stderr)
            return 1
    else:
        check_dt = datetime.now()

    # Check/display
    in_schedule = is_in_schedule(schedule, check_dt)

    if args.next:
        next_dt = next_occurrence(schedule, check_dt)
        if next_dt:
            print(f"Next: {next_dt.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("No upcoming occurrence")
        return 0

    if args.until:
        remaining = time_until_schedule(schedule, check_dt)
        if remaining:
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            if hours > 0:
                print(f"Time until schedule: {hours}h {minutes}m")
            else:
                print(f"Time until schedule: {minutes}m")
        else:
            print("Schedule not found")
        return 0

    # Default: check current status
    status = "IN SCHEDULE" if in_schedule else "NOT IN SCHEDULE"
    print(f"Schedule: {format_schedule(schedule)}")
    print(f"Status: {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
