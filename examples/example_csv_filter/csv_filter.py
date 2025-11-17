#!/usr/bin/env python3
"""
CSV Filter - Memory-efficient CSV filtering using generators

Demonstrates:
- Generator expressions for lazy evaluation
- csv.DictReader iteration
- Predicate filtering with lambda/functions
- Streaming write to stdout or file
- argparse for CLI options

This validates depyler's ability to transpile:
- Generator expressions: (row for row in reader if predicate(row))
- File iteration patterns: for line in f
- csv module usage

Depyler: stress test for generator transpilation
"""

import argparse
import csv
import sys


def filter_csv(input_file, column, value, output_file=None):
    """
    Filter CSV rows where column equals value.

    Uses generator to process one row at a time.

    Args:
        input_file: Path to input CSV
        column: Column name to filter on
        value: Value to match
        output_file: Path to output CSV (stdout if None)

    Depyler: proven to terminate
    """
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)

        # Store fieldnames before consuming reader
        fieldnames = reader.fieldnames

        # Generator expression - lazy evaluation
        filtered_rows = (row for row in reader if row[column] == value)

        # Setup output
        output = open(output_file, "w") if output_file else sys.stdout

        try:
            # Write header
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            # Process and write one row at a time
            for row in filtered_rows:
                writer.writerow(row)
        finally:
            if output_file:
                output.close()


def filter_csv_advanced(input_file, filters, output_file=None):
    """
    Filter CSV with multiple column criteria.

    Args:
        input_file: Path to input CSV
        filters: Dict of {column: value} filters (AND logic)
        output_file: Path to output CSV

    Depyler: proven to terminate
    """

    def matches_all_filters(row):
        """Check if row matches all filter criteria"""
        return all(row.get(col) == val for col, val in filters.items())

    with open(input_file, "r") as f:
        reader = csv.DictReader(f)

        # Store fieldnames
        fieldnames = reader.fieldnames

        # Generator with complex predicate
        filtered_rows = (row for row in reader if matches_all_filters(row))

        output = open(output_file, "w") if output_file else sys.stdout

        try:
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            count = 0
            for row in filtered_rows:
                writer.writerow(row)
                count += 1

            print(f"Filtered {count} rows", file=sys.stderr)
        finally:
            if output_file:
                output.close()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Filter CSV files by column values", prog="csv_filter"
    )

    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--column", "-c", required=True, help="Column to filter")
    parser.add_argument("--value", "-v", required=True, help="Value to match")
    parser.add_argument(
        "--output", "-o", help="Output CSV file (default: stdout)"
    )
    parser.add_argument("--version", action="version", version="1.0.0")

    args = parser.parse_args()

    filter_csv(args.input, args.column, args.value, args.output)


if __name__ == "__main__":
    main()
