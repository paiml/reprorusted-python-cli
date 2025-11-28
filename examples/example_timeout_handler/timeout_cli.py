#!/usr/bin/env python3
"""Timeout handler CLI.

Timeout management and deadline tracking.
"""

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Timeout:
    """Represents a timeout."""

    duration: float  # seconds
    started_at: float

    def __init__(self, duration: float):
        self.duration = duration
        self.started_at = time.time()

    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.started_at

    def remaining(self) -> float:
        """Get remaining time in seconds."""
        return max(0, self.duration - self.elapsed())

    def is_expired(self) -> bool:
        """Check if timeout has expired."""
        return self.elapsed() >= self.duration

    def deadline(self) -> datetime:
        """Get deadline as datetime."""
        return datetime.fromtimestamp(self.started_at + self.duration)

    def extend(self, seconds: float) -> None:
        """Extend the timeout."""
        self.duration += seconds

    def reset(self) -> None:
        """Reset the timeout."""
        self.started_at = time.time()


@dataclass
class Deadline:
    """Represents an absolute deadline."""

    deadline_time: datetime

    def __init__(self, deadline_time: datetime | str):
        if isinstance(deadline_time, str):
            self.deadline_time = datetime.fromisoformat(deadline_time)
        else:
            self.deadline_time = deadline_time

    def remaining(self) -> float:
        """Get remaining time in seconds."""
        delta = self.deadline_time - datetime.now()
        return max(0, delta.total_seconds())

    def is_expired(self) -> bool:
        """Check if deadline has passed."""
        return datetime.now() >= self.deadline_time

    def to_timeout(self) -> Timeout:
        """Convert to a Timeout."""
        remaining = self.remaining()
        return Timeout(remaining)


def parse_duration(duration_str: str) -> float:
    """Parse duration string to seconds.

    Formats: 30s, 5m, 2h, 1d, or combinations like 1h30m
    """
    total_seconds = 0.0

    # Simple number = seconds
    try:
        return float(duration_str)
    except ValueError:
        pass

    # Parse units
    import re

    pattern = r"(\d+(?:\.\d+)?)\s*([smhd])"
    matches = re.findall(pattern, duration_str.lower())

    if not matches:
        raise ValueError(f"Invalid duration: {duration_str}")

    for value, unit in matches:
        value = float(value)
        if unit == "s":
            total_seconds += value
        elif unit == "m":
            total_seconds += value * 60
        elif unit == "h":
            total_seconds += value * 3600
        elif unit == "d":
            total_seconds += value * 86400

    return total_seconds


def format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 0:
        return "expired"

    if seconds < 60:
        return f"{seconds:.1f}s"

    if seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"

    if seconds < 86400:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    return f"{days}d {hours}h"


def calculate_progress(elapsed: float, total: float) -> float:
    """Calculate progress percentage."""
    if total <= 0:
        return 100.0
    return min(100.0, (elapsed / total) * 100)


def format_progress_bar(progress: float, width: int = 30) -> str:
    """Format progress as a bar."""
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress:.1f}%"


class TimeoutGroup:
    """Manage multiple named timeouts."""

    def __init__(self):
        self.timeouts: dict[str, Timeout] = {}

    def add(self, name: str, duration: float) -> Timeout:
        """Add a new timeout."""
        timeout = Timeout(duration)
        self.timeouts[name] = timeout
        return timeout

    def get(self, name: str) -> Timeout | None:
        """Get a timeout by name."""
        return self.timeouts.get(name)

    def check(self, name: str) -> bool:
        """Check if a timeout is expired."""
        timeout = self.get(name)
        if timeout is None:
            return True  # Non-existent = expired
        return timeout.is_expired()

    def remove(self, name: str) -> bool:
        """Remove a timeout."""
        if name in self.timeouts:
            del self.timeouts[name]
            return True
        return False

    def cleanup_expired(self) -> list[str]:
        """Remove expired timeouts."""
        expired = [name for name, t in self.timeouts.items() if t.is_expired()]
        for name in expired:
            del self.timeouts[name]
        return expired

    def first_to_expire(self) -> tuple[str, Timeout] | None:
        """Get the timeout that will expire first."""
        active = [(name, t) for name, t in self.timeouts.items() if not t.is_expired()]
        if not active:
            return None
        return min(active, key=lambda x: x[1].remaining())


def main() -> int:
    parser = argparse.ArgumentParser(description="Timeout and deadline management")
    parser.add_argument("duration", nargs="?", help="Timeout duration (e.g., 30s, 5m, 1h)")
    parser.add_argument("--deadline", metavar="TIME", help="Absolute deadline (ISO format)")
    parser.add_argument("--check", action="store_true", help="Check remaining time")
    parser.add_argument("--progress", action="store_true", help="Show progress bar")
    parser.add_argument("--wait", action="store_true", help="Wait until timeout expires")
    parser.add_argument("--countdown", action="store_true", help="Show countdown")
    parser.add_argument("--parse", action="store_true", help="Just parse and show duration")

    args = parser.parse_args()

    # Parse duration or deadline
    if args.deadline:
        try:
            deadline = Deadline(args.deadline)
            timeout = deadline.to_timeout()
        except ValueError as e:
            print(f"Invalid deadline: {e}", file=sys.stderr)
            return 1
    elif args.duration:
        try:
            duration = parse_duration(args.duration)
            timeout = Timeout(duration)
        except ValueError as e:
            print(f"Invalid duration: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1

    if args.parse:
        print(f"Duration: {timeout.duration:.2f} seconds")
        print(f"Formatted: {format_duration(timeout.duration)}")
        return 0

    if args.wait:
        print(f"Waiting {format_duration(timeout.duration)}...")
        while not timeout.is_expired():
            time.sleep(0.1)
        print("Timeout expired")
        return 0

    if args.countdown:
        try:
            while not timeout.is_expired():
                remaining = timeout.remaining()
                progress = calculate_progress(timeout.elapsed(), timeout.duration)
                bar = format_progress_bar(progress)
                print(f"\r{bar} {format_duration(remaining)} remaining", end="")
                time.sleep(0.1)
            print(f"\r{format_progress_bar(100.0)} Timeout expired!        ")
        except KeyboardInterrupt:
            print("\nCancelled")
            return 1
        return 0

    if args.progress:
        progress = calculate_progress(timeout.elapsed(), timeout.duration)
        print(format_progress_bar(progress))
        return 0

    # Default: show status
    print(f"Duration: {format_duration(timeout.duration)}")
    print(f"Elapsed: {format_duration(timeout.elapsed())}")
    print(f"Remaining: {format_duration(timeout.remaining())}")
    print(f"Deadline: {timeout.deadline().isoformat()}")
    print(f"Expired: {timeout.is_expired()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
