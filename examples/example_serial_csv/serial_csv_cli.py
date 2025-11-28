"""CSV Parser and Writer CLI with Type Inference.

Demonstrates CSV parsing, writing, type inference, and transformation patterns.
"""

import re
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CsvConfig:
    """CSV configuration options."""

    delimiter: str = ","
    quote_char: str = '"'
    escape_char: str = "\\"
    has_header: bool = True
    skip_empty: bool = True
    trim_whitespace: bool = True


@dataclass
class CsvDocument:
    """CSV document with optional headers."""

    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    config: CsvConfig = field(default_factory=CsvConfig)

    def __len__(self) -> int:
        return len(self.rows)

    def column(self, name_or_index: str | int) -> list[str]:
        """Get column by name or index."""
        if isinstance(name_or_index, str):
            if name_or_index in self.headers:
                idx = self.headers.index(name_or_index)
            else:
                return []
        else:
            idx = name_or_index

        return [row[idx] if idx < len(row) else "" for row in self.rows]

    def row(self, index: int) -> list[str]:
        """Get row by index."""
        if 0 <= index < len(self.rows):
            return self.rows[index]
        return []

    def as_dicts(self) -> list[dict[str, str]]:
        """Convert to list of dicts."""
        if not self.headers:
            return []
        return [
            {h: row[i] if i < len(row) else "" for i, h in enumerate(self.headers)}
            for row in self.rows
        ]

    def filter_rows(self, column: str, value: str) -> list[list[str]]:
        """Filter rows by column value."""
        if column not in self.headers:
            return []
        idx = self.headers.index(column)
        return [row for row in self.rows if idx < len(row) and row[idx] == value]

    def sort_by(self, column: str, reverse: bool = False) -> list[list[str]]:
        """Sort rows by column."""
        if column not in self.headers:
            return self.rows.copy()
        idx = self.headers.index(column)
        return sorted(self.rows, key=lambda r: r[idx] if idx < len(r) else "", reverse=reverse)


class CsvParser:
    """CSV parser."""

    def __init__(self, config: CsvConfig | None = None) -> None:
        self.config = config or CsvConfig()

    def parse(self, text: str) -> CsvDocument:
        """Parse CSV text."""
        doc = CsvDocument(config=self.config)
        lines = text.splitlines()

        for i, line in enumerate(lines):
            if self.config.skip_empty and not line.strip():
                continue

            row = self._parse_line(line)

            if i == 0 and self.config.has_header:
                doc.headers = row
            else:
                doc.rows.append(row)

        return doc

    def _parse_line(self, line: str) -> list[str]:
        """Parse a single CSV line."""
        fields = []
        current = ""
        in_quotes = False
        prev_char = ""

        for char in line:
            if char == self.config.quote_char and prev_char != self.config.escape_char:
                in_quotes = not in_quotes
            elif char == self.config.delimiter and not in_quotes:
                fields.append(self._clean_field(current))
                current = ""
            else:
                current += char
            prev_char = char

        fields.append(self._clean_field(current))
        return fields

    def _clean_field(self, value: str) -> str:
        """Clean a field value."""
        if self.config.trim_whitespace:
            value = value.strip()

        # Remove surrounding quotes
        if len(value) >= 2:
            if value.startswith(self.config.quote_char) and value.endswith(self.config.quote_char):
                value = value[1:-1]

        # Unescape quotes
        value = value.replace(self.config.quote_char * 2, self.config.quote_char)

        return value


class CsvWriter:
    """CSV writer."""

    def __init__(self, config: CsvConfig | None = None) -> None:
        self.config = config or CsvConfig()

    def write(self, doc: CsvDocument) -> str:
        """Write CSV document to string."""
        lines = []

        if self.config.has_header and doc.headers:
            lines.append(self._format_row(doc.headers))

        for row in doc.rows:
            lines.append(self._format_row(row))

        return "\n".join(lines) + "\n"

    def _format_row(self, row: list[str]) -> str:
        """Format a row."""
        return self.config.delimiter.join(self._quote_field(f) for f in row)

    def _quote_field(self, value: str) -> str:
        """Quote a field if necessary."""
        needs_quote = (
            self.config.delimiter in value
            or self.config.quote_char in value
            or "\n" in value
            or "\r" in value
        )

        if needs_quote:
            escaped = value.replace(self.config.quote_char, self.config.quote_char * 2)
            return f"{self.config.quote_char}{escaped}{self.config.quote_char}"

        return value


def csv_parse(text: str, config: CsvConfig | None = None) -> CsvDocument:
    """Parse CSV text."""
    return CsvParser(config).parse(text)


def csv_dump(doc: CsvDocument) -> str:
    """Dump CSV document to string."""
    return CsvWriter(doc.config).write(doc)


def infer_type(value: str) -> Any:
    """Infer type from string value."""
    if not value or value.lower() in ("null", "none", "na", "n/a", ""):
        return None

    # Boolean
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False

    # Integer
    if re.match(r"^-?\d+$", value):
        return int(value)

    # Float
    if re.match(r"^-?\d*\.\d+$", value) or re.match(r"^-?\d+\.\d*$", value):
        return float(value)

    # Scientific notation
    if re.match(r"^-?\d+\.?\d*[eE][+-]?\d+$", value):
        return float(value)

    return value


def infer_column_type(values: list[str]) -> str:
    """Infer column type from values."""
    types: dict[str, int] = {"null": 0, "bool": 0, "int": 0, "float": 0, "str": 0}

    for value in values:
        inferred = infer_type(value)
        if inferred is None:
            types["null"] += 1
        elif isinstance(inferred, bool):
            types["bool"] += 1
        elif isinstance(inferred, int):
            types["int"] += 1
        elif isinstance(inferred, float):
            types["float"] += 1
        else:
            types["str"] += 1

    # Return most common non-null type
    non_null = {k: v for k, v in types.items() if k != "null" and v > 0}
    if not non_null:
        return "str"

    return max(non_null, key=lambda k: non_null[k])


def csv_schema(doc: CsvDocument) -> dict[str, str]:
    """Infer schema for CSV document."""
    schema = {}

    for i, header in enumerate(doc.headers):
        column_values = [row[i] if i < len(row) else "" for row in doc.rows]
        schema[header] = infer_column_type(column_values)

    return schema


def csv_to_typed(doc: CsvDocument) -> list[dict[str, Any]]:
    """Convert CSV to list of typed dicts."""
    if not doc.headers:
        return []

    result = []
    for row in doc.rows:
        record = {}
        for i, header in enumerate(doc.headers):
            value = row[i] if i < len(row) else ""
            record[header] = infer_type(value)
        result.append(record)

    return result


def csv_stats(doc: CsvDocument, column: str) -> dict[str, Any]:
    """Calculate statistics for a numeric column."""
    if column not in doc.headers:
        return {}

    values = []
    for value in doc.column(column):
        typed = infer_type(value)
        if isinstance(typed, (int, float)):
            values.append(float(typed))

    if not values:
        return {}

    sorted_vals = sorted(values)
    n = len(values)

    return {
        "count": n,
        "min": min(values),
        "max": max(values),
        "sum": sum(values),
        "mean": sum(values) / n,
        "median": sorted_vals[n // 2]
        if n % 2
        else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2,
    }


def csv_select(doc: CsvDocument, columns: list[str]) -> CsvDocument:
    """Select specific columns."""
    indices = []
    new_headers = []

    for col in columns:
        if col in doc.headers:
            indices.append(doc.headers.index(col))
            new_headers.append(col)

    new_rows = [[row[i] if i < len(row) else "" for i in indices] for row in doc.rows]

    return CsvDocument(headers=new_headers, rows=new_rows, config=doc.config)


def csv_join(left: CsvDocument, right: CsvDocument, on: str) -> CsvDocument:
    """Join two CSV documents on a column."""
    if on not in left.headers or on not in right.headers:
        return CsvDocument()

    left_idx = left.headers.index(on)
    right_idx = right.headers.index(on)

    # Build lookup from right
    right_lookup: dict[str, list[list[str]]] = {}
    for row in right.rows:
        key = row[right_idx] if right_idx < len(row) else ""
        if key not in right_lookup:
            right_lookup[key] = []
        right_lookup[key].append(row)

    # New headers (exclude duplicate key column from right)
    new_headers = left.headers + [h for i, h in enumerate(right.headers) if i != right_idx]
    new_rows = []

    for left_row in left.rows:
        key = left_row[left_idx] if left_idx < len(left_row) else ""
        if key in right_lookup:
            for right_row in right_lookup[key]:
                new_row = list(left_row) + [v for i, v in enumerate(right_row) if i != right_idx]
                new_rows.append(new_row)

    return CsvDocument(headers=new_headers, rows=new_rows)


def csv_group_by(doc: CsvDocument, column: str) -> dict[str, list[list[str]]]:
    """Group rows by column value."""
    if column not in doc.headers:
        return {}

    idx = doc.headers.index(column)
    groups: dict[str, list[list[str]]] = {}

    for row in doc.rows:
        key = row[idx] if idx < len(row) else ""
        if key not in groups:
            groups[key] = []
        groups[key].append(row)

    return groups


def csv_aggregate(doc: CsvDocument, group_col: str, agg_col: str, func: str) -> dict[str, float]:
    """Aggregate column values by group."""
    groups = csv_group_by(doc, group_col)
    agg_idx = doc.headers.index(agg_col) if agg_col in doc.headers else -1

    if agg_idx < 0:
        return {}

    result = {}
    for key, rows in groups.items():
        values = []
        for row in rows:
            if agg_idx < len(row):
                typed = infer_type(row[agg_idx])
                if isinstance(typed, (int, float)):
                    values.append(float(typed))

        if values:
            if func == "sum":
                result[key] = sum(values)
            elif func == "avg":
                result[key] = sum(values) / len(values)
            elif func == "min":
                result[key] = min(values)
            elif func == "max":
                result[key] = max(values)
            elif func == "count":
                result[key] = float(len(values))

    return result


def simulate_csv(operations: list[str]) -> list[str]:
    """Simulate CSV operations."""
    results = []
    context: CsvDocument | None = None

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "parse":
            context = csv_parse(parts[1])
            results.append("ok")
        elif cmd == "rows" and context:
            results.append(str(len(context)))
        elif cmd == "cols" and context:
            results.append(str(len(context.headers)))
        elif cmd == "headers" and context:
            results.append(",".join(context.headers))
        elif cmd == "schema" and context:
            schema = csv_schema(context)
            results.append(",".join(f"{k}:{v}" for k, v in schema.items()))
        elif cmd == "column" and context:
            col = context.column(parts[1])
            results.append(",".join(col))
        elif cmd == "filter" and context:
            col_val = parts[1].split("=", 1)
            if len(col_val) == 2:
                filtered = context.filter_rows(col_val[0], col_val[1])
                results.append(str(len(filtered)))
        elif cmd == "stats" and context:
            stats = csv_stats(context, parts[1])
            results.append(",".join(f"{k}:{v}" for k, v in stats.items()))

    return results


def main() -> int:
    """CLI entry point."""
    import json

    if len(sys.argv) < 2:
        print("Usage: serial_csv_cli.py <command> [args...]")
        print("Commands: parse, schema, stats, select, filter, join")
        return 1

    cmd = sys.argv[1]

    if cmd == "parse":
        text = sys.stdin.read()
        doc = csv_parse(text)
        data = csv_to_typed(doc)
        print(json.dumps(data, indent=2))

    elif cmd == "schema":
        text = sys.stdin.read()
        doc = csv_parse(text)
        schema = csv_schema(doc)
        print(json.dumps(schema, indent=2))

    elif cmd == "stats":
        if len(sys.argv) < 3:
            print("Usage: stats <column>", file=sys.stderr)
            return 1
        text = sys.stdin.read()
        doc = csv_parse(text)
        stats = csv_stats(doc, sys.argv[2])
        print(json.dumps(stats, indent=2))

    elif cmd == "select":
        if len(sys.argv) < 3:
            print("Usage: select <col1,col2,...>", file=sys.stderr)
            return 1
        text = sys.stdin.read()
        doc = csv_parse(text)
        columns = sys.argv[2].split(",")
        selected = csv_select(doc, columns)
        print(csv_dump(selected))

    elif cmd == "filter":
        if len(sys.argv) < 4:
            print("Usage: filter <column> <value>", file=sys.stderr)
            return 1
        text = sys.stdin.read()
        doc = csv_parse(text)
        filtered_rows = doc.filter_rows(sys.argv[2], sys.argv[3])
        result = CsvDocument(headers=doc.headers, rows=filtered_rows, config=doc.config)
        print(csv_dump(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
