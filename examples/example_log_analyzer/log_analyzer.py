#!/usr/bin/env python3
"""
Log Analyzer - Parse and aggregate log files using generators

Demonstrates:
- Generator functions with yield
- itertools.groupby for aggregation
- Regular expressions for parsing
- Lazy line-by-line file processing
- Defaultdict for counting

This validates depyler's ability to transpile:
- yield statements in generator functions
- itertools.groupby with key functions
- re module for pattern matching

Depyler: stress test for yield and itertools transpilation
"""

import argparse
import re
import sys
from collections import defaultdict
from itertools import groupby


def parse_log_lines(file_path):
    """
    Generator function to parse log lines.

    Yields:
        Tuple of (timestamp, level, message)

    Depyler: proven to terminate
    """
    # Pattern: [2025-11-17 10:30:45] INFO: Message text
    pattern = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+): (.+)")

    with open(file_path, "r") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                timestamp, level, message = match.groups()
                yield (timestamp, level, message)


def count_by_level(file_path):
    """
    Count log entries by level using generator.

    Args:
        file_path: Path to log file

    Returns:
        Dict of {level: count}

    Depyler: proven to terminate
    """
    counts = defaultdict(int)

    # Generator expression consuming generator function
    for timestamp, level, message in parse_log_lines(file_path):
        counts[level] += 1

    return dict(counts)


def group_by_hour(file_path):
    """
    Group log entries by hour using itertools.groupby.

    Args:
        file_path: Path to log file

    Returns:
        Dict of {hour: count}

    Depyler: proven to terminate
    """

    def extract_hour(entry):
        """Extract hour from timestamp"""
        timestamp, level, message = entry
        # timestamp format: 2025-11-17 10:30:45
        return timestamp[11:13]  # Extract hour (HH)

    # Parse all entries
    entries = list(parse_log_lines(file_path))

    # Sort by hour for groupby
    entries.sort(key=extract_hour)

    # Group and count
    hour_counts = {}
    for hour, group in groupby(entries, key=extract_hour):
        hour_counts[hour] = sum(1 for _ in group)

    return hour_counts


def filter_by_level(file_path, level):
    """
    Generator that yields only entries of specified level.

    Args:
        file_path: Path to log file
        level: Log level to filter (INFO, WARN, ERROR)

    Yields:
        Matching log entries

    Depyler: proven to terminate
    """
    for entry in parse_log_lines(file_path):
        timestamp, entry_level, message = entry
        if entry_level == level:
            yield entry


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze log files with statistics", prog="log_analyzer"
    )

    parser.add_argument("logfile", help="Log file to analyze")
    parser.add_argument(
        "--count-levels", action="store_true", help="Count by log level"
    )
    parser.add_argument(
        "--group-by-hour", action="store_true", help="Group by hour"
    )
    parser.add_argument(
        "--filter-level", help="Filter by level (INFO, WARN, ERROR)"
    )
    parser.add_argument("--version", action="version", version="1.0.0")

    args = parser.parse_args()

    if args.count_levels:
        counts = count_by_level(args.logfile)
        print("Log Level Counts:")
        for level, count in sorted(counts.items()):
            print(f"  {level}: {count}")

    elif args.group_by_hour:
        hour_counts = group_by_hour(args.logfile)
        print("Hourly Distribution:")
        for hour, count in sorted(hour_counts.items()):
            print(f"  {hour}:00 - {count} entries")

    elif args.filter_level:
        for timestamp, level, message in filter_by_level(
            args.logfile, args.filter_level
        ):
            print(f"[{timestamp}] {level}: {message}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
