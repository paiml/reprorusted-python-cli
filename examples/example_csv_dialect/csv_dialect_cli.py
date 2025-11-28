#!/usr/bin/env python3
"""CSV parser with custom dialect support.

Supports custom delimiters, quote characters, and escape handling.
"""

import argparse
import sys


def parse_csv_line(line: str, delimiter: str, quote: str, escape: str) -> list:
    """Parse a single CSV line with custom dialect."""
    fields = []
    current = ""
    in_quotes = False
    i = 0

    while i < len(line):
        char = line[i]

        if escape and char == escape and i + 1 < len(line):
            # Escape sequence
            current += line[i + 1]
            i += 2
            continue

        if char == quote:
            in_quotes = not in_quotes
            i += 1
            continue

        if char == delimiter and not in_quotes:
            fields.append(current)
            current = ""
            i += 1
            continue

        current += char
        i += 1

    fields.append(current)
    return fields


def format_csv_line(fields: list, delimiter: str, quote: str, always_quote: bool) -> str:
    """Format fields as a CSV line."""
    result = []
    for field in fields:
        needs_quote = always_quote or delimiter in field or quote in field or "\n" in field
        if needs_quote:
            escaped = field.replace(quote, quote + quote)
            result.append(f"{quote}{escaped}{quote}")
        else:
            result.append(field)
    return delimiter.join(result)


def convert_delimiter(lines: list, from_delim: str, to_delim: str, quote: str, escape: str) -> list:
    """Convert CSV from one delimiter to another."""
    result = []
    for line in lines:
        if line.strip():
            fields = parse_csv_line(line.strip(), from_delim, quote, escape)
            result.append(format_csv_line(fields, to_delim, quote, False))
    return result


def get_column(lines: list, col_index: int, delimiter: str, quote: str, escape: str) -> list:
    """Extract a single column from CSV."""
    result = []
    for line in lines:
        if line.strip():
            fields = parse_csv_line(line.strip(), delimiter, quote, escape)
            if col_index < len(fields):
                result.append(fields[col_index])
    return result


def count_columns(lines: list, delimiter: str, quote: str, escape: str) -> dict:
    """Count rows by number of columns."""
    counts: dict = {}
    for line in lines:
        if line.strip():
            fields = parse_csv_line(line.strip(), delimiter, quote, escape)
            n = len(fields)
            counts[n] = counts.get(n, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="CSV parser with custom dialect support")
    parser.add_argument("input", nargs="?", help="Input CSV file (- for stdin)")
    parser.add_argument("-d", "--delimiter", default=",", help="Field delimiter (default: ,)")
    parser.add_argument("-q", "--quote", default='"', help='Quote character (default: ")')
    parser.add_argument("-e", "--escape", default="", help="Escape character (default: none)")
    parser.add_argument("--to-delimiter", metavar="DELIM", help="Convert to this delimiter")
    parser.add_argument("--column", type=int, metavar="N", help="Extract column N (0-indexed)")
    parser.add_argument("--count-columns", action="store_true", help="Count rows by column count")
    parser.add_argument("--skip-header", action="store_true", help="Skip first line")

    args = parser.parse_args()

    # Read input
    if args.input is None or args.input == "-":
        lines = sys.stdin.readlines()
    else:
        with open(args.input) as f:
            lines = f.readlines()

    # Skip header if requested
    if args.skip_header and lines:
        lines = lines[1:]

    # Perform operation
    if args.to_delimiter:
        result = convert_delimiter(
            lines, args.delimiter, args.to_delimiter, args.quote, args.escape
        )
        for line in result:
            print(line)
    elif args.column is not None:
        values = get_column(lines, args.column, args.delimiter, args.quote, args.escape)
        for value in values:
            print(value)
    elif args.count_columns:
        counts = count_columns(lines, args.delimiter, args.quote, args.escape)
        for n, count in sorted(counts.items()):
            print(f"{n} columns: {count} rows")
    else:
        # Default: parse and re-output
        for line in lines:
            if line.strip():
                fields = parse_csv_line(line.strip(), args.delimiter, args.quote, args.escape)
                print(format_csv_line(fields, args.delimiter, args.quote, False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
