#!/usr/bin/env python3
"""CSV Basic CLI.

CSV reading and writing operations.
"""

import argparse
import csv
import io
import sys


def parse_csv(content: str, delimiter: str = ",") -> list[list[str]]:
    """Parse CSV string to list of rows."""
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    return list(reader)


def parse_csv_dict(content: str, delimiter: str = ",") -> list[dict[str, str]]:
    """Parse CSV to list of dicts (first row as headers)."""
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    return list(reader)


def to_csv(rows: list[list[str]], delimiter: str = ",") -> str:
    """Convert list of rows to CSV string."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter)
    writer.writerows(rows)
    return output.getvalue()


def to_csv_dict(
    data: list[dict[str, str]], headers: list[str] | None = None, delimiter: str = ","
) -> str:
    """Convert list of dicts to CSV string."""
    if not data:
        return ""
    output = io.StringIO()
    fieldnames = headers or list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def read_csv_file(path: str, delimiter: str = ",") -> list[list[str]]:
    """Read CSV file to list of rows."""
    with open(path, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        return list(reader)


def read_csv_dict_file(path: str, delimiter: str = ",") -> list[dict[str, str]]:
    """Read CSV file to list of dicts."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return list(reader)


def write_csv_file(path: str, rows: list[list[str]], delimiter: str = ",") -> None:
    """Write list of rows to CSV file."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(rows)


def write_csv_dict_file(
    path: str, data: list[dict[str, str]], headers: list[str] | None = None, delimiter: str = ","
) -> None:
    """Write list of dicts to CSV file."""
    if not data:
        return
    with open(path, "w", newline="") as f:
        fieldnames = headers or list(data[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)


def get_headers(content: str, delimiter: str = ",") -> list[str]:
    """Get CSV headers (first row)."""
    rows = parse_csv(content, delimiter)
    return rows[0] if rows else []


def get_column(rows: list[list[str]], index: int) -> list[str]:
    """Get column by index."""
    return [row[index] for row in rows if index < len(row)]


def get_column_by_name(data: list[dict[str, str]], name: str) -> list[str]:
    """Get column by name from dict data."""
    return [row.get(name, "") for row in data]


def row_count(rows: list[list[str]]) -> int:
    """Count rows (including header)."""
    return len(rows)


def column_count(rows: list[list[str]]) -> int:
    """Count columns (based on first row)."""
    return len(rows[0]) if rows else 0


def filter_rows(rows: list[list[str]], column: int, value: str) -> list[list[str]]:
    """Filter rows where column equals value."""
    return [row for row in rows if len(row) > column and row[column] == value]


def filter_dict_rows(data: list[dict[str, str]], key: str, value: str) -> list[dict[str, str]]:
    """Filter dict rows where key equals value."""
    return [row for row in data if row.get(key) == value]


def sort_by_column(rows: list[list[str]], column: int, reverse: bool = False) -> list[list[str]]:
    """Sort rows by column (keeps header first if present)."""
    if not rows:
        return rows
    header = rows[0]
    data = rows[1:]
    sorted_data = sorted(data, key=lambda r: r[column] if column < len(r) else "", reverse=reverse)
    return [header] + sorted_data


def sort_dict_by_key(
    data: list[dict[str, str]], key: str, reverse: bool = False
) -> list[dict[str, str]]:
    """Sort dict rows by key."""
    return sorted(data, key=lambda r: r.get(key, ""), reverse=reverse)


def select_columns(rows: list[list[str]], columns: list[int]) -> list[list[str]]:
    """Select specific columns by index."""
    return [[row[i] for i in columns if i < len(row)] for row in rows]


def select_dict_columns(data: list[dict[str, str]], columns: list[str]) -> list[dict[str, str]]:
    """Select specific columns by name."""
    return [{k: row.get(k, "") for k in columns} for row in data]


def add_column(rows: list[list[str]], values: list[str], header: str = "") -> list[list[str]]:
    """Add column to rows."""
    result = []
    for i, row in enumerate(rows):
        if i == 0:
            result.append(row + [header])
        elif i - 1 < len(values):
            result.append(row + [values[i - 1]])
        else:
            result.append(row + [""])
    return result


def remove_column(rows: list[list[str]], column: int) -> list[list[str]]:
    """Remove column by index."""
    return [[cell for j, cell in enumerate(row) if j != column] for row in rows]


def rename_header(rows: list[list[str]], old: str, new: str) -> list[list[str]]:
    """Rename header."""
    if not rows:
        return rows
    header = [new if h == old else h for h in rows[0]]
    return [header] + rows[1:]


def merge_csv(rows1: list[list[str]], rows2: list[list[str]]) -> list[list[str]]:
    """Merge two CSVs (append rows, assuming same headers)."""
    if not rows1:
        return rows2
    if not rows2:
        return rows1
    return rows1 + rows2[1:]


def unique_values(rows: list[list[str]], column: int) -> list[str]:
    """Get unique values in column."""
    seen: set[str] = set()
    result: list[str] = []
    for row in rows:
        if column < len(row):
            val = row[column]
            if val not in seen:
                seen.add(val)
                result.append(val)
    return result


def count_by_column(rows: list[list[str]], column: int) -> dict[str, int]:
    """Count occurrences of each value in column."""
    counts: dict[str, int] = {}
    for row in rows:
        if column < len(row):
            val = row[column]
            counts[val] = counts.get(val, 0) + 1
    return counts


def transpose(rows: list[list[str]]) -> list[list[str]]:
    """Transpose CSV (rows become columns)."""
    if not rows:
        return []
    max_cols = max(len(row) for row in rows)
    return [
        [rows[j][i] if i < len(rows[j]) else "" for j in range(len(rows))] for i in range(max_cols)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="CSV basic CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # parse
    parse_p = subparsers.add_parser("parse", help="Parse CSV string")
    parse_p.add_argument("csv", help="CSV string")
    parse_p.add_argument("-d", "--delimiter", default=",", help="Delimiter")

    # read
    read_p = subparsers.add_parser("read", help="Read CSV file")
    read_p.add_argument("file", help="CSV file path")
    read_p.add_argument("-d", "--delimiter", default=",", help="Delimiter")

    # headers
    headers_p = subparsers.add_parser("headers", help="Get headers")
    headers_p.add_argument("file", help="CSV file path")

    # count
    count_p = subparsers.add_parser("count", help="Count rows")
    count_p.add_argument("file", help="CSV file path")

    # column
    column_p = subparsers.add_parser("column", help="Get column")
    column_p.add_argument("file", help="CSV file path")
    column_p.add_argument("index", type=int, help="Column index")

    args = parser.parse_args()

    if args.command == "parse":
        rows = parse_csv(args.csv, args.delimiter)
        for row in rows:
            print(row)

    elif args.command == "read":
        rows = read_csv_file(args.file, args.delimiter)
        for row in rows:
            print(row)

    elif args.command == "headers":
        rows = read_csv_file(args.file)
        if rows:
            print(rows[0])

    elif args.command == "count":
        rows = read_csv_file(args.file)
        print(f"Rows: {len(rows)}")
        if rows:
            print(f"Columns: {len(rows[0])}")

    elif args.command == "column":
        rows = read_csv_file(args.file)
        column = get_column(rows, args.index)
        for val in column:
            print(val)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
