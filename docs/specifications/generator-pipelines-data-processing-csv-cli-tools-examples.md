# Generator Pipelines & Data Processing CLI Tools Specification

**Version:** 1.0.0
**Status:** Draft
**Last Updated:** 2025-11-17
**Related Spec:** [argparse-depyler-compile-examples-spec.md](argparse-depyler-compile-examples-spec.md)

## Executive Summary

This specification defines a **stress-test validation framework** for depyler focused on **data engineering CLI tools** that heavily use Python's generator expressions, lazy evaluation, and streaming data processing patterns. The goal is to find rough edges in depyler's transpilation by testing real-world data processing scenarios with memory-efficient iterator patterns.

**Key Focus Areas:**
- Generator expressions and comprehensions
- `yield` statements and generator functions
- `itertools` module usage (groupby, chain, islice, etc.)
- Streaming file I/O with line-by-line processing
- Memory-efficient data pipelines
- CSV/JSON/log file processing at scale

---

## 1. Project Overview

### 1.1 Purpose

Create a systematic validation framework that:
- **Stress-tests** depyler with generator expressions and lazy evaluation patterns
- **Identifies rough edges** in Python→Rust transpilation for iterators
- **Validates** that Rust implementations maintain semantic equivalence
- **Benchmarks** memory efficiency (Python generators vs Rust iterators)
- **Demonstrates** real-world data engineering CLI tool patterns

### 1.2 Why Generators Matter for Depyler Validation

| Python Feature | Challenge for Transpilation | Rust Equivalent |
|----------------|----------------------------|-----------------|
| Generator expressions `(x for x in data)` | Lazy evaluation, single-pass iteration | Iterator chains `.iter().map()` |
| Generator functions `yield` | Stateful iteration with suspension | Custom iterator struct or closure |
| List comprehensions `[x for x in data]` | Eager vs lazy distinction | `.collect::<Vec<_>>()` vs iterator |
| `itertools.groupby()` | Complex iterator protocol | `itertools::GroupBy` crate |
| `itertools.chain()` | Multi-source iteration | `.chain()` method |
| File iteration `for line in f:` | Implicit buffering | `BufRead::lines()` |
| Memory efficiency | Process GB files with MB memory | Iterator fusion optimization |

**Success means:**
- Generators transpile to efficient Rust iterators
- Memory usage comparable between Python (streaming) and Rust
- Performance improvements from Rust iterator fusion
- Functional equivalence for all data transformations

### 1.3 Core Dependencies

| Dependency | Purpose | Notes |
|------------|---------|-------|
| **depyler** v3.20.0+ | Python-to-Rust transpiler | Must handle generators, yield, itertools |
| **itertools** (Rust) | Iterator utilities | Rust equivalent of Python itertools |
| **csv** (Rust) | CSV parsing | For CSV processing examples |
| **serde_json** (Rust) | JSON processing | For JSON conversion examples |
| **rayon** (optional) | Parallel iterators | For parallel data processing comparison |

### 1.4 Success Criteria

- ✅ 100% transpilation success for generator-based tools
- ✅ 100% functional equivalence (identical output for same input)
- ✅ Memory efficiency: Process 1GB+ files with <100MB RSS
- ✅ Performance: Rust ≥2x faster than Python for large datasets
- ✅ Extreme TDD: 100% test coverage with property-based tests
- ✅ Scientific benchmarking: Reproducible performance measurements

---

## 2. Example Tools Specification

### 2.1 Example Portfolio (6 Tools)

| Tool | Python Features Tested | Data Engineering Pattern |
|------|----------------------|--------------------------|
| **csv_filter** | Generator expressions, file iteration | Filter large CSV by column criteria |
| **log_analyzer** | `yield`, groupby, comprehensions | Parse logs, aggregate by timestamp |
| **data_dedup** | Generator functions, sets, iteration | Find duplicates in streaming data |
| **json_to_csv** | Nested generators, JSON streaming | Convert JSONL to CSV line-by-line |
| **data_aggregator** | itertools.groupby, reduce patterns | Group by key, aggregate values |
| **stream_merger** | itertools.chain, heapq, multiple files | Merge sorted CSV files |

### 2.2 Tool 1: CSV Filter

**Purpose**: Filter large CSV files by column criteria without loading into memory.

**File**: `examples/example_csv_filter/csv_filter.py`

```python
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
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)

        # Generator expression - lazy evaluation
        filtered_rows = (row for row in reader if row[column] == value)

        # Setup output
        output = open(output_file, 'w') if output_file else sys.stdout

        try:
            # Write header
            fieldnames = reader.fieldnames
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

    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)

        # Generator with complex predicate
        filtered_rows = (row for row in reader if matches_all_filters(row))

        output = open(output_file, 'w') if output_file else sys.stdout

        try:
            writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
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
        description="Filter CSV files by column values",
        prog="csv_filter"
    )

    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('--column', '-c', required=True, help='Column to filter')
    parser.add_argument('--value', '-v', required=True, help='Value to match')
    parser.add_argument('--output', '-o', help='Output CSV file (default: stdout)')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    filter_csv(args.input, args.column, args.value, args.output)


if __name__ == "__main__":
    main()
```

**Test Cases** (`test_csv_filter.py`):
- Small CSV (100 rows) - verify correctness
- Large CSV (1M rows) - verify memory efficiency
- Multiple filters - verify AND logic
- Empty result set - verify handles no matches
- Invalid column - verify error handling
- Property test: len(filtered) ≤ len(input)

**Benchmark Focus**:
- Memory: Peak RSS should be O(1) not O(n)
- Speed: Rust vs Python for 1M row CSV
- I/O efficiency: Verify streaming behavior

---

### 2.3 Tool 2: Log Analyzer

**Purpose**: Parse log files and aggregate statistics using generators and groupby.

**File**: `examples/example_log_analyzer/log_analyzer.py`

```python
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
    pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+): (.+)')

    with open(file_path, 'r') as f:
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
        description="Analyze log files with statistics",
        prog="log_analyzer"
    )

    parser.add_argument('logfile', help='Log file to analyze')
    parser.add_argument('--count-levels', action='store_true', help='Count by log level')
    parser.add_argument('--group-by-hour', action='store_true', help='Group by hour')
    parser.add_argument('--filter-level', help='Filter by level (INFO, WARN, ERROR)')
    parser.add_argument('--version', action='version', version='1.0.0')

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
        for timestamp, level, message in filter_by_level(args.logfile, args.filter_level):
            print(f"[{timestamp}] {level}: {message}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Test Cases** (`test_log_analyzer.py`):
- Parse valid log format - verify regex matching
- Count by level - verify aggregation
- Group by hour - verify groupby behavior
- Filter by level - verify generator filtering
- Large log file (1M lines) - verify memory efficiency
- Malformed lines - verify error handling
- Property test: sum(level_counts) == total_lines

**Benchmark Focus**:
- Memory: O(1) for streaming, O(unique_keys) for groupby
- Speed: Rust regex vs Python re module
- Iterator fusion: Rust should optimize chained generators

---

### 2.4 Tool 3: Data Deduplicator

**Purpose**: Find duplicate records in streaming data using generators and sets.

**File**: `examples/example_data_dedup/data_dedup.py`

```python
#!/usr/bin/env python3
"""
Data Deduplicator - Find duplicates in streaming data

Demonstrates:
- Generator functions for memory-efficient processing
- Set operations for duplicate detection
- Multiple file iteration
- Composite key generation
- Streaming output

This validates depyler's ability to transpile:
- yield expressions with stateful iteration
- Set add/contains operations
- Generator composition
"""

import argparse
import csv
import sys


def find_duplicates(file_path, key_columns):
    """
    Generator that yields duplicate rows based on key columns.

    Args:
        file_path: Path to CSV file
        key_columns: List of column names to use as composite key

    Yields:
        Duplicate rows (second+ occurrence)

    Depyler: proven to terminate
    """
    seen_keys = set()

    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Create composite key from specified columns
            key = tuple(row[col] for col in key_columns)

            if key in seen_keys:
                # Duplicate found - yield it
                yield row
            else:
                # First occurrence - add to set
                seen_keys.add(key)


def deduplicate_stream(file_path, key_columns, output_path=None):
    """
    Remove duplicates from CSV, keeping first occurrence.

    Args:
        file_path: Input CSV
        key_columns: Columns for duplicate detection
        output_path: Output CSV (stdout if None)

    Depyler: proven to terminate
    """
    seen_keys = set()

    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)

        # Generator for unique rows only
        unique_rows = (
            row for row in reader
            if (key := tuple(row[col] for col in key_columns)) not in seen_keys
            and not seen_keys.add(key)  # Add to set, returns None (falsy)
        )

        output = open(output_path, 'w') if output_path else sys.stdout

        try:
            writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
            writer.writeheader()

            count = 0
            for row in unique_rows:
                writer.writerow(row)
                count += 1

            print(f"Kept {count} unique rows", file=sys.stderr)
        finally:
            if output_path:
                output.close()


def count_duplicates(file_path, key_columns):
    """
    Count total duplicates without outputting them.

    Args:
        file_path: Input CSV
        key_columns: Columns for duplicate detection

    Returns:
        Tuple of (unique_count, duplicate_count)

    Depyler: proven to terminate
    """
    seen_keys = set()
    unique_count = 0
    duplicate_count = 0

    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            key = tuple(row[col] for col in key_columns)

            if key in seen_keys:
                duplicate_count += 1
            else:
                seen_keys.add(key)
                unique_count += 1

    return unique_count, duplicate_count


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Find and remove duplicate records in CSV files",
        prog="data_dedup"
    )

    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('--keys', '-k', nargs='+', required=True,
                        help='Columns to use as duplicate key')
    parser.add_argument('--output', '-o', help='Output CSV file (deduplicated)')
    parser.add_argument('--show-duplicates', action='store_true',
                        help='Show duplicate rows instead of deduplicating')
    parser.add_argument('--count-only', action='store_true',
                        help='Only count duplicates')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    if args.count_only:
        unique, dupes = count_duplicates(args.input, args.keys)
        print(f"Unique rows: {unique}")
        print(f"Duplicate rows: {dupes}")
        print(f"Total rows: {unique + dupes}")

    elif args.show_duplicates:
        # Show duplicate rows
        with open(args.input, 'r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()

        for row in find_duplicates(args.input, args.keys):
            writer.writerow(row)

    else:
        # Deduplicate
        deduplicate_stream(args.input, args.keys, args.output)


if __name__ == "__main__":
    main()
```

**Test Cases** (`test_data_dedup.py`):
- No duplicates - verify all rows pass through
- All duplicates - verify only first kept
- Partial duplicates - verify correct filtering
- Multi-column keys - verify composite key logic
- Large dataset (1M rows, 10% dupes) - verify memory efficiency
- Property test: unique_count + duplicate_count == total_count

**Benchmark Focus**:
- Memory: O(unique_keys) for set storage
- Speed: Set lookup performance Rust vs Python
- Hash function performance for composite keys

---

### 2.5 Tool 4: JSON to CSV Converter

**Purpose**: Convert JSONL (JSON Lines) to CSV using streaming.

**File**: `examples/example_json_to_csv/json_to_csv.py`

```python
#!/usr/bin/env python3
"""
JSON to CSV Converter - Stream conversion of JSONL files

Demonstrates:
- Nested generators for multi-stage processing
- JSON streaming (line-by-line)
- Dynamic CSV field detection
- Flattening nested JSON objects
- Generator expressions for transformation

This validates depyler's ability to transpile:
- json.loads() for each line
- Nested generator expressions
- Dict flattening algorithms
"""

import argparse
import csv
import json
import sys


def parse_jsonl(file_path):
    """
    Generator to parse JSONL file line by line.

    Yields:
        Parsed JSON objects (dicts)

    Depyler: proven to terminate
    """
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Key prefix for nested items
        sep: Separator for nested keys

    Returns:
        Flattened dict

    Depyler: proven to terminate
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            # Recursively flatten nested dict
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def convert_jsonl_to_csv(input_file, output_file=None, flatten=False):
    """
    Convert JSONL to CSV using generators.

    Args:
        input_file: Path to JSONL file
        output_file: Path to output CSV (stdout if None)
        flatten: Whether to flatten nested objects

    Depyler: proven to terminate
    """
    # Generator for parsed JSON
    json_stream = parse_jsonl(input_file)

    # Optional flattening
    if flatten:
        record_stream = (flatten_dict(obj) for obj in json_stream)
    else:
        record_stream = json_stream

    # Collect first record to determine fieldnames
    record_stream = list(record_stream)  # Must materialize for fieldnames

    if not record_stream:
        print("Empty input file", file=sys.stderr)
        return

    fieldnames = list(record_stream[0].keys())

    # Write CSV
    output = open(output_file, 'w') if output_file else sys.stdout

    try:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for record in record_stream:
            writer.writerow(record)

        print(f"Converted {len(record_stream)} records", file=sys.stderr)
    finally:
        if output_file:
            output.close()


def extract_fields(input_file, fields):
    """
    Extract specific fields from JSONL.

    Args:
        input_file: Path to JSONL file
        fields: List of field names to extract

    Yields:
        Dicts with only specified fields

    Depyler: proven to terminate
    """
    for obj in parse_jsonl(input_file):
        # Generator expression for field extraction
        extracted = {field: obj.get(field, '') for field in fields}
        yield extracted


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Convert JSONL (JSON Lines) to CSV",
        prog="json_to_csv"
    )

    parser.add_argument('input', help='Input JSONL file')
    parser.add_argument('--output', '-o', help='Output CSV file (default: stdout)')
    parser.add_argument('--flatten', action='store_true',
                        help='Flatten nested JSON objects')
    parser.add_argument('--fields', '-f', nargs='+',
                        help='Extract only specified fields')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    if args.fields:
        # Extract specific fields
        output = open(args.output, 'w') if args.output else sys.stdout

        try:
            writer = csv.DictWriter(output, fieldnames=args.fields)
            writer.writeheader()

            for record in extract_fields(args.input, args.fields):
                writer.writerow(record)
        finally:
            if args.output:
                output.close()
    else:
        # Full conversion
        convert_jsonl_to_csv(args.input, args.output, args.flatten)


if __name__ == "__main__":
    main()
```

**Test Cases** (`test_json_to_csv.py`):
- Simple flat JSON - verify basic conversion
- Nested JSON - verify flattening
- Field extraction - verify subset selection
- Large JSONL (100K records) - verify streaming
- Malformed JSON - verify error handling
- Property test: CSV row count == JSONL line count

**Benchmark Focus**:
- JSON parsing speed: Rust serde_json vs Python json
- Memory: Verify streaming vs loading all into memory
- Flattening performance: Recursive dict operations

---

### 2.6 Tool 5: Data Aggregator

**Purpose**: Group data and compute aggregates using itertools.groupby.

**File**: `examples/example_data_aggregator/data_aggregator.py`

```python
#!/usr/bin/env python3
"""
Data Aggregator - Group and aggregate CSV data

Demonstrates:
- itertools.groupby for SQL-like GROUP BY
- Generator-based aggregation functions
- Multiple aggregation strategies (sum, count, avg, min, max)
- Sorted iteration requirement for groupby
- Complex key functions

This validates depyler's ability to transpile:
- itertools.groupby with custom key functions
- Generator-based reduce operations
- Multiple simultaneous aggregations
"""

import argparse
import csv
import sys
from itertools import groupby


def read_csv_sorted(file_path, sort_key):
    """
    Read CSV and sort by key columns.

    Args:
        file_path: Path to CSV file
        sort_key: Column name(s) to sort by

    Returns:
        Sorted list of row dicts

    Depyler: proven to terminate
    """
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Sort by key column(s)
    if isinstance(sort_key, list):
        rows.sort(key=lambda row: tuple(row[k] for k in sort_key))
    else:
        rows.sort(key=lambda row: row[sort_key])

    return rows


def group_and_count(file_path, group_by):
    """
    Count records by group.

    Args:
        file_path: Path to CSV
        group_by: Column to group by

    Returns:
        List of (group_value, count) tuples

    Depyler: proven to terminate
    """
    rows = read_csv_sorted(file_path, group_by)

    results = []
    for key, group in groupby(rows, key=lambda row: row[group_by]):
        count = sum(1 for _ in group)
        results.append((key, count))

    return results


def group_and_sum(file_path, group_by, sum_column):
    """
    Sum numeric column by group.

    Args:
        file_path: Path to CSV
        group_by: Column to group by
        sum_column: Numeric column to sum

    Returns:
        List of (group_value, sum) tuples

    Depyler: proven to terminate
    """
    rows = read_csv_sorted(file_path, group_by)

    results = []
    for key, group in groupby(rows, key=lambda row: row[group_by]):
        total = sum(float(row[sum_column]) for row in group)
        results.append((key, total))

    return results


def group_and_aggregate_multi(file_path, group_by, agg_column, operations):
    """
    Perform multiple aggregations on same group.

    Args:
        file_path: Path to CSV
        group_by: Column to group by
        agg_column: Column to aggregate
        operations: List of operations ('sum', 'count', 'avg', 'min', 'max')

    Returns:
        List of dicts with group key and aggregations

    Depyler: proven to terminate
    """
    rows = read_csv_sorted(file_path, group_by)

    results = []
    for key, group in groupby(rows, key=lambda row: row[group_by]):
        # Materialize group (groupby can only be iterated once)
        group_list = list(group)
        values = [float(row[agg_column]) for row in group_list]

        agg_result = {group_by: key}

        if 'count' in operations:
            agg_result['count'] = len(values)
        if 'sum' in operations:
            agg_result['sum'] = sum(values)
        if 'avg' in operations:
            agg_result['avg'] = sum(values) / len(values) if values else 0
        if 'min' in operations:
            agg_result['min'] = min(values) if values else None
        if 'max' in operations:
            agg_result['max'] = max(values) if values else None

        results.append(agg_result)

    return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Group and aggregate CSV data",
        prog="data_aggregator"
    )

    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('--group-by', '-g', required=True,
                        help='Column to group by')
    parser.add_argument('--column', '-c', help='Column to aggregate')
    parser.add_argument('--operation', '-op',
                        choices=['count', 'sum', 'avg', 'min', 'max'],
                        default='count',
                        help='Aggregation operation')
    parser.add_argument('--output', '-o', help='Output CSV file')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    # Perform aggregation
    if args.operation == 'count':
        results = group_and_count(args.input, args.group_by)
        header = [args.group_by, 'count']
    elif args.operation == 'sum':
        if not args.column:
            print("--column required for sum operation", file=sys.stderr)
            sys.exit(1)
        results = group_and_sum(args.input, args.group_by, args.column)
        header = [args.group_by, 'sum']
    else:
        if not args.column:
            print("--column required for aggregation", file=sys.stderr)
            sys.exit(1)
        results = group_and_aggregate_multi(
            args.input, args.group_by, args.column, [args.operation]
        )
        header = [args.group_by, args.operation]

    # Write results
    output = open(args.output, 'w') if args.output else sys.stdout

    try:
        writer = csv.writer(output)
        writer.writerow(header)

        for result in results:
            if isinstance(result, tuple):
                writer.writerow(result)
            else:
                writer.writerow([result[header[0]], result[header[1]]])
    finally:
        if args.output:
            output.close()


if __name__ == "__main__":
    main()
```

**Test Cases** (`test_data_aggregator.py`):
- Group and count - verify counts
- Group and sum - verify numeric aggregation
- Multiple aggregations - verify all operations
- Empty groups - verify handling
- Large dataset (100K rows) - verify performance
- Property test: sum(group_counts) == total_rows

**Benchmark Focus**:
- Sort performance: Rust vs Python
- groupby performance: Iterator protocol efficiency
- Multiple aggregations: Single-pass vs multi-pass

---

### 2.7 Tool 6: Stream Merger

**Purpose**: Merge multiple sorted CSV files maintaining sort order.

**File**: `examples/example_stream_merger/stream_merger.py`

```python
#!/usr/bin/env python3
"""
Stream Merger - Merge multiple sorted CSV files

Demonstrates:
- heapq for efficient k-way merge
- Multiple file iteration simultaneously
- Generator-based merge algorithm
- Maintaining sort order
- Resource management with multiple files

This validates depyler's ability to transpile:
- heapq module usage
- Multiple concurrent iterators
- Complex generator patterns
"""

import argparse
import csv
import heapq
import sys


def merge_sorted_csvs(file_paths, key_column, output_path=None):
    """
    Merge multiple sorted CSV files maintaining sort order.

    Uses heapq for efficient k-way merge.

    Args:
        file_paths: List of CSV file paths (must be sorted by key_column)
        key_column: Column to use for sorting
        output_path: Output CSV path (stdout if None)

    Depyler: proven to terminate
    """
    # Open all input files
    files = [open(path, 'r') for path in file_paths]
    readers = [csv.DictReader(f) for f in files]

    try:
        # Get fieldnames from first file
        fieldnames = readers[0].fieldnames

        # Initialize heap with first row from each file
        heap = []
        for i, reader in enumerate(readers):
            try:
                row = next(reader)
                # Heap entry: (sort_key, file_index, row)
                heapq.heappush(heap, (row[key_column], i, row))
            except StopIteration:
                # File is empty
                pass

        # Setup output
        output = open(output_path, 'w') if output_path else sys.stdout

        try:
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            count = 0

            # Merge loop
            while heap:
                # Get smallest item
                key, file_idx, row = heapq.heappop(heap)

                # Write to output
                writer.writerow(row)
                count += 1

                # Try to get next row from same file
                try:
                    next_row = next(readers[file_idx])
                    heapq.heappush(heap, (next_row[key_column], file_idx, next_row))
                except StopIteration:
                    # This file is exhausted
                    pass

            print(f"Merged {count} rows from {len(file_paths)} files", file=sys.stderr)

        finally:
            if output_path:
                output.close()

    finally:
        # Close all input files
        for f in files:
            f.close()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Merge multiple sorted CSV files",
        prog="stream_merger"
    )

    parser.add_argument('files', nargs='+', help='CSV files to merge (must be sorted)')
    parser.add_argument('--key', '-k', required=True,
                        help='Column to use for sort order')
    parser.add_argument('--output', '-o', help='Output CSV file (default: stdout)')
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    merge_sorted_csvs(args.files, args.key, args.output)


if __name__ == "__main__":
    main()
```

**Test Cases** (`test_stream_merger.py`):
- Merge 2 sorted files - verify order maintained
- Merge 10 files - verify k-way merge
- Files with different lengths - verify handles exhausted files
- Large files (100K rows each) - verify memory efficiency
- Property test: output is sorted
- Property test: len(output) == sum(len(input_i))

**Benchmark Focus**:
- Heap operations: Rust BinaryHeap vs Python heapq
- Multiple file I/O: Concurrent reading efficiency
- Memory: O(k) for k files, not O(n)

---

## 3. Testing Methodology

### 3.1 Extreme TDD Workflow

**Test-First Development**:
1. Write specification (this document)
2. Write pytest tests with expected behaviors
3. Generate test data (CSV, JSONL, logs)
4. Write Python implementation to pass tests
5. Transpile with depyler
6. Verify Rust binary passes same tests
7. Run property-based tests for edge cases

**Test Structure** (per example):
```python
# test_<tool>.py structure

import pytest
from <tool> import *

class TestBasicFunctionality:
    """Test core functionality"""
    def test_simple_case(self):
        """Verify basic operation"""
        pass

    def test_edge_case_empty(self):
        """Verify handles empty input"""
        pass

    def test_edge_case_large(self):
        """Verify handles large input"""
        pass

class TestMemoryEfficiency:
    """Test memory usage"""
    def test_streaming_behavior(self, tmpdir):
        """Verify O(1) memory for streaming operations"""
        # Generate large input file
        # Monitor RSS during processing
        # Assert peak memory < threshold
        pass

class TestOutputCorrectness:
    """Test output equivalence"""
    def test_deterministic_output(self):
        """Verify same input produces same output"""
        pass

    def test_idempotent(self):
        """Verify running twice produces same result"""
        pass

class TestPropertyBased:
    """Property-based tests using hypothesis"""
    @given(st.lists(st.integers()))
    def test_property_length_preservation(self, data):
        """Property: filter output ≤ input length"""
        pass
```

### 3.2 Test Data Generation

**Synthetic Data Strategy**:

```python
# scripts/generate_test_data.py

def generate_csv(rows, columns, output_path):
    """Generate test CSV with specified rows/columns"""
    pass

def generate_jsonl(records, output_path):
    """Generate test JSONL file"""
    pass

def generate_log_file(lines, output_path):
    """Generate test log file"""
    pass

# Sizes for testing:
# - Small: 100 rows (correctness)
# - Medium: 10K rows (integration)
# - Large: 1M rows (performance, memory)
# - XL: 10M rows (stress test)
```

### 3.3 Property-Based Testing

**Key Properties to Test**:

| Tool | Property | Assertion |
|------|----------|-----------|
| csv_filter | Length preservation | `len(output) ≤ len(input)` |
| csv_filter | Filter correctness | `all(predicate(row) for row in output)` |
| log_analyzer | Count preservation | `sum(level_counts) == total_lines` |
| data_dedup | Count preservation | `unique + dupes == total` |
| json_to_csv | Row preservation | `csv_rows == jsonl_lines` |
| data_aggregator | Group coverage | `all groups in input appear in output` |
| stream_merger | Sort preservation | `output is sorted` |
| stream_merger | Row preservation | `len(output) == sum(len(input_i))` |

---

## 4. Benchmarking Methodology

### 4.1 Scientific Benchmarking Requirements

**Criteria for Valid Benchmarks**:
- ✅ Reproducible: Same input produces same measurements (±2%)
- ✅ Isolated: Single process, no background load
- ✅ Representative: Realistic data sizes and patterns
- ✅ Statistical: Multiple runs with mean/median/stddev
- ✅ Memory: Track RSS, heap allocations
- ✅ I/O: Measure disk read/write operations

**Benchmark Framework**:
```bash
# scripts/benchmark_generators.sh

# For each tool:
# 1. Generate test data (1M rows)
# 2. Warmup run (Python + Rust)
# 3. 10 measurement runs each
# 4. Collect metrics:
#    - Execution time (real, user, sys)
#    - Peak RSS memory
#    - I/O operations (via renacer)
# 5. Statistical analysis
# 6. Generate comparison report
```

### 4.2 Memory Efficiency Metrics

**Key Question**: Does generator transpilation maintain O(1) memory?

**Measurement Strategy**:
```python
# tests/test_memory_efficiency.py

import resource
import os

def measure_peak_rss(func, *args):
    """Measure peak RSS memory usage"""
    # Linux: /proc/self/status VmHWM (Peak RSS)
    # Use renacer for detailed syscall-level tracking
    pass

def test_csv_filter_memory():
    """Verify CSV filter uses O(1) memory"""
    # Generate 1GB CSV file
    # Run filter operation
    # Assert peak RSS < 100MB
    assert peak_rss < 100 * 1024 * 1024  # 100MB
```

**Renacer Integration**:
```bash
# Trace memory allocations during execution
renacer -e trace=memory -- ./csv_filter large.csv --column age --value 25

# Expected: No large mmap/brk calls
# Python generators: Many small allocations
# Rust iterators: Even smaller allocations (stack-based)
```

### 4.3 Performance Comparison Matrix

**Benchmark Scenarios**:

| Tool | Dataset | Python (sec) | Rust (sec) | Speedup | Python RSS | Rust RSS |
|------|---------|--------------|------------|---------|------------|----------|
| csv_filter | 1M rows | TBD | TBD | TBD | <100MB | <50MB |
| log_analyzer | 1M lines | TBD | TBD | TBD | <100MB | <50MB |
| data_dedup | 1M rows (10% dupes) | TBD | TBD | TBD | ~100MB | ~50MB |
| json_to_csv | 100K records | TBD | TBD | TBD | <50MB | <30MB |
| data_aggregator | 1M rows, 1K groups | TBD | TBD | TBD | ~150MB | ~75MB |
| stream_merger | 10 x 100K rows | TBD | TBD | TBD | <100MB | <50MB |

**Expected Results**:
- Rust ≥2x faster (iterator fusion, no GIL, compiled)
- Rust ≤0.5x memory (stack allocations, no interpreter overhead)
- Both maintain streaming behavior (O(1) or O(unique_keys) memory)

---

## 5. Depyler Rough Edges Discovery

### 5.1 Expected Challenges

**Generator-Related Challenges**:

| Python Pattern | Transpilation Challenge | Rust Equivalent |
|----------------|------------------------|-----------------|
| `yield` statement | Stateful suspension | Iterator trait impl or generator feature |
| `(x for x in data)` | Lazy evaluation | `.iter().map()` chain |
| `[x for x in data]` | Eager collect | `.collect::<Vec<_>>()` |
| `itertools.groupby()` | Iterator protocol | `itertools::group_by()` crate |
| `heapq.heappush()` | Min-heap semantics | `BinaryHeap` with Reverse wrapper |
| `for line in f:` | Implicit buffering | `BufRead::lines()` |
| Nested generators | Complex iterator types | Type inference challenges |

### 5.2 Tracking Rough Edges

**GitHub Issue Template**:
```markdown
## Rough Edge: [Brief Description]

**Example**: example_csv_filter

**Python Code**:
```python
filtered = (row for row in reader if row['age'] == '25')
```

**Transpilation Error**:
```
error: generator expression not yet supported
```

**Expected Rust**:
```rust
let filtered = reader.filter(|row| row.get("age") == Some("25"));
```

**Workaround**:
Manual implementation or feature request.

**Severity**: P0-CRITICAL / P1-HIGH / P2-MEDIUM / P3-LOW

**Impact**: Blocks {X} tools, affects {Y}% of real-world use cases
```

### 5.3 Success Metrics for Rough Edge Discovery

- ✅ Document ≥10 generator-specific transpilation challenges
- ✅ Prioritize by impact (% of tools blocked)
- ✅ Create reproducible test cases for each
- ✅ Track fixes in depyler with validation

---

## 6. Implementation Roadmap

### 6.1 Sprint Planning (Toyota Way - Jidoka)

**Sprint 1: Foundation (1 week)**
- Tool 1: csv_filter (simplest generator pattern)
- Tool 2: log_analyzer (yield statements)
- Test data generation scripts
- Basic benchmarking framework

**Sprint 2: Advanced Patterns (1 week)**
- Tool 3: data_dedup (stateful generators)
- Tool 4: json_to_csv (nested generators)
- Property-based test suite
- Memory efficiency validation

**Sprint 3: Complex Operations (1 week)**
- Tool 5: data_aggregator (itertools.groupby)
- Tool 6: stream_merger (heapq, multiple files)
- Complete benchmark suite
- Scientific performance analysis

**Sprint 4: Depyler Integration (1 week)**
- Transpile all 6 tools
- Document rough edges found
- Create GitHub issues for blockers
- Validate Rust binaries
- Performance comparison report

### 6.2 Definition of Done (per tool)

- ✅ Python implementation complete
- ✅ Test suite with 100% coverage
- ✅ Property-based tests passing
- ✅ Transpiles with depyler (or rough edge documented)
- ✅ Rust binary functionally equivalent
- ✅ Benchmarks collected (Python vs Rust)
- ✅ Memory efficiency validated
- ✅ Documentation complete (README.md)

---

## 7. Documentation Requirements

### 7.1 Per-Tool Documentation

**README.md Template** (per example):
```markdown
# [Tool Name]

## Purpose
Brief description of data engineering task.

## Generator Patterns Used
- Generator expressions: (x for x in data)
- Generator functions: yield
- itertools: groupby, chain, etc.

## Usage
```bash
./tool --help
./tool input.csv --options
```

## Test Data Generation
```bash
./generate_test_data.sh
```

## Benchmarks
| Dataset | Python | Rust | Speedup |
|---------|--------|------|---------|
| 1M rows | X.Xs   | Y.Ys | Z.Zx    |

## Depyler Status
✅ Transpiles successfully
❌ Blocked by: [rough edge description]

## Memory Profile
- Python: XX MB (peak RSS)
- Rust: YY MB (peak RSS)
- Streaming verified: ✅ O(1) memory
```

### 7.2 Overall Project Documentation

**Files to Create**:
- `docs/specifications/generator-pipelines-data-processing-csv-cli-tools-examples.md` (this file)
- `docs/GENERATOR_BENCHMARKS.md` - Consolidated performance results
- `docs/GENERATOR_ROUGH_EDGES.md` - Comprehensive list of transpilation challenges
- `examples/GENERATOR_INDEX.md` - Quick reference for all 6 tools

---

## 8. Quality Gates

### 8.1 Pre-Commit Checks

**Required Passing**:
- ✅ `make format` - ruff format
- ✅ `make lint` - ruff check
- ✅ `make test` - pytest with 100% coverage
- ✅ `make test-property` - hypothesis property tests
- ✅ `bashrs lint` - shell script validation

### 8.2 CI/CD Pipeline

**GitHub Actions Workflow**:
```yaml
name: Generator Tools CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: make install-deps
      - name: Run tests
        run: make test
      - name: Run property tests
        run: make test-property
      - name: Check coverage
        run: make coverage
        # Assert: coverage ≥ 100%

  benchmark:
    runs-on: ubuntu-latest
    steps:
      - name: Generate test data
        run: make generate-test-data
      - name: Benchmark Python
        run: make bench-python
      - name: Transpile with depyler
        run: make transpile
      - name: Benchmark Rust
        run: make bench-rust
      - name: Compare results
        run: make bench-compare
```

---

## 9. Success Criteria Summary

**Project Success Defined As**:

1. **Transpilation Coverage**: ≥4/6 tools transpile successfully (67%)
2. **Rough Edges Documented**: ≥10 generator-specific challenges identified
3. **Performance Validation**: Rust ≥2x faster on all working tools
4. **Memory Efficiency**: Both Python and Rust maintain O(1) streaming
5. **Test Coverage**: 100% line coverage with property tests
6. **Scientific Rigor**: Reproducible benchmarks with statistical analysis

**Deliverables**:
- ✅ 6 data engineering CLI tools
- ✅ Comprehensive test suites
- ✅ Benchmark reports with performance comparison
- ✅ Rough edges documentation for depyler improvements
- ✅ Example portfolio demonstrating generator patterns

---

## 10. References

### 10.1 Related Specifications
- [argparse-depyler-compile-examples-spec.md](argparse-depyler-compile-examples-spec.md) - Base validation framework
- [DEBUGGING.md](../../DEBUGGING.md) - Debugging with depyler --trace and renacer

### 10.2 External Resources
- Python itertools: https://docs.python.org/3/library/itertools.html
- Rust Iterator trait: https://doc.rust-lang.org/std/iter/trait.Iterator.html
- Rust itertools crate: https://docs.rs/itertools/
- Generator expressions PEP 289: https://www.python.org/dev/peps/pep-0289/
- Yield expressions PEP 255: https://www.python.org/dev/peps/pep-0255/

### 10.3 Tools
- **depyler**: Python-to-Rust transpiler
- **renacer**: Syscall tracer for memory/performance profiling
- **pmat**: Quality gates and TDD workflow
- **bashrs**: Makefile generation
- **hypothesis**: Property-based testing framework

---

**Built with Toyota Way Jidoka principles - Find Rough Edges, Document, Improve** 🔧
