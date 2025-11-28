#!/usr/bin/env python3
"""JSONPath CLI.

Simple JSONPath query implementation.
"""

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum, auto


class PathType(Enum):
    """JSONPath segment types."""

    ROOT = auto()
    CHILD = auto()
    RECURSIVE = auto()
    INDEX = auto()
    SLICE = auto()
    WILDCARD = auto()
    FILTER = auto()


@dataclass
class PathSegment:
    """JSONPath segment."""

    type: PathType
    value: str | int | tuple | None = None


def parse_path(path: str) -> list[PathSegment]:
    """Parse JSONPath string into segments."""
    segments = []
    i = 0

    while i < len(path):
        char = path[i]

        if char == "$":
            segments.append(PathSegment(PathType.ROOT))
            i += 1

        elif char == ".":
            if i + 1 < len(path) and path[i + 1] == ".":
                segments.append(PathSegment(PathType.RECURSIVE))
                i += 2
            else:
                i += 1
                # Read key name
                start = i
                while i < len(path) and path[i] not in ".[]":
                    i += 1
                if i > start:
                    key = path[start:i]
                    if key == "*":
                        segments.append(PathSegment(PathType.WILDCARD))
                    else:
                        segments.append(PathSegment(PathType.CHILD, key))

        elif char == "[":
            i += 1
            start = i
            bracket_depth = 1

            while i < len(path) and bracket_depth > 0:
                if path[i] == "[":
                    bracket_depth += 1
                elif path[i] == "]":
                    bracket_depth -= 1
                i += 1

            content = path[start : i - 1].strip()

            if content == "*":
                segments.append(PathSegment(PathType.WILDCARD))
            elif content.startswith("?"):
                segments.append(PathSegment(PathType.FILTER, content[1:].strip()))
            elif ":" in content:
                parts = content.split(":")
                start_idx = int(parts[0]) if parts[0] else None
                end_idx = int(parts[1]) if len(parts) > 1 and parts[1] else None
                step = int(parts[2]) if len(parts) > 2 and parts[2] else None
                segments.append(PathSegment(PathType.SLICE, (start_idx, end_idx, step)))
            elif content.isdigit() or (content.startswith("-") and content[1:].isdigit()):
                segments.append(PathSegment(PathType.INDEX, int(content)))
            else:
                # Quoted key
                key = content.strip("'\"")
                segments.append(PathSegment(PathType.CHILD, key))

        else:
            i += 1

    return segments


def query(data: any, path: str) -> list[any]:
    """Execute JSONPath query on data."""
    segments = parse_path(path)
    results = [data]

    for segment in segments:
        new_results = []

        for item in results:
            new_results.extend(apply_segment(item, segment))

        results = new_results

    return results


def apply_segment(data: any, segment: PathSegment) -> list[any]:
    """Apply a single path segment to data."""
    if segment.type == PathType.ROOT:
        return [data]

    if segment.type == PathType.CHILD:
        if isinstance(data, dict) and segment.value in data:
            return [data[segment.value]]
        return []

    if segment.type == PathType.INDEX:
        if isinstance(data, list):
            idx = segment.value
            if isinstance(idx, int) and -len(data) <= idx < len(data):
                return [data[idx]]
        return []

    if segment.type == PathType.SLICE:
        if isinstance(data, list):
            start, end, step = segment.value
            return [data[start:end:step]]
        return []

    if segment.type == PathType.WILDCARD:
        if isinstance(data, dict):
            return list(data.values())
        if isinstance(data, list):
            return data
        return []

    if segment.type == PathType.RECURSIVE:
        return recursive_descent(data)

    if segment.type == PathType.FILTER:
        return apply_filter(data, str(segment.value))

    return []


def recursive_descent(data: any) -> list[any]:
    """Get all descendants of data."""
    results = [data]

    if isinstance(data, dict):
        for value in data.values():
            results.extend(recursive_descent(value))
    elif isinstance(data, list):
        for item in data:
            results.extend(recursive_descent(item))

    return results


def apply_filter(data: any, expr: str) -> list[any]:
    """Apply filter expression to array."""
    if not isinstance(data, list):
        return []

    results = []
    expr = expr.strip("()")

    for item in data:
        if evaluate_filter(item, expr):
            results.append(item)

    return results


def evaluate_filter(item: any, expr: str) -> bool:
    """Evaluate filter expression on item."""
    # Simple filter evaluation
    expr = expr.strip()

    # Handle @.key op value
    if "@." in expr:
        expr = expr.replace("@.", "")

        # Parse comparison
        for op in [">=", "<=", "!=", "==", ">", "<"]:
            if op in expr:
                left, right = expr.split(op, 1)
                left = left.strip()
                right = right.strip().strip("'\"")

                if isinstance(item, dict) and left in item:
                    left_val = item[left]

                    # Try numeric comparison
                    try:
                        right_val = float(right) if "." in right else int(right)
                        left_val = float(left_val)
                    except (ValueError, TypeError):
                        right_val = right

                    if op == "==":
                        return left_val == right_val
                    if op == "!=":
                        return left_val != right_val
                    if op == ">":
                        return left_val > right_val
                    if op == "<":
                        return left_val < right_val
                    if op == ">=":
                        return left_val >= right_val
                    if op == "<=":
                        return left_val <= right_val

                return False

        # Just key existence check
        return isinstance(item, dict) and expr in item

    return False


def get_value(data: any, path: str) -> any:
    """Get single value from path (returns first result or None)."""
    results = query(data, path)
    return results[0] if results else None


def get_all(data: any, path: str) -> list[any]:
    """Get all values matching path."""
    return query(data, path)


def exists(data: any, path: str) -> bool:
    """Check if path exists in data."""
    return len(query(data, path)) > 0


def count(data: any, path: str) -> int:
    """Count matches for path."""
    return len(query(data, path))


def keys(data: any) -> list[str]:
    """Get keys of object."""
    if isinstance(data, dict):
        return list(data.keys())
    return []


def values(data: any) -> list[any]:
    """Get values of object or array."""
    if isinstance(data, dict):
        return list(data.values())
    if isinstance(data, list):
        return data
    return []


def flatten(data: any) -> list[any]:
    """Flatten nested structure."""
    results = []

    if isinstance(data, dict):
        for value in data.values():
            results.extend(flatten(value))
    elif isinstance(data, list):
        for item in data:
            results.extend(flatten(item))
    else:
        results.append(data)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="JSONPath query tool")
    parser.add_argument("path", nargs="?", help="JSONPath expression")
    parser.add_argument("--file", "-f", help="JSON file to query")
    parser.add_argument("--data", "-d", help="JSON data string")
    parser.add_argument(
        "--mode",
        choices=["query", "exists", "count", "keys", "values", "flatten"],
        default="query",
        help="Operation mode",
    )

    args = parser.parse_args()

    # Load data
    if args.file:
        with open(args.file) as f:
            data = json.load(f)
    elif args.data:
        data = json.loads(args.data)
    else:
        data = json.load(sys.stdin)

    if args.mode == "keys":
        result = keys(data)
        print(json.dumps(result, indent=2))
        return 0

    if args.mode == "values":
        result = values(data)
        print(json.dumps(result, indent=2))
        return 0

    if args.mode == "flatten":
        result = flatten(data)
        print(json.dumps(result, indent=2))
        return 0

    if not args.path:
        print("Error: path required for query mode")
        return 1

    if args.mode == "query":
        results = query(data, args.path)
        if len(results) == 1:
            print(json.dumps(results[0], indent=2))
        else:
            print(json.dumps(results, indent=2))

    elif args.mode == "exists":
        print("true" if exists(data, args.path) else "false")

    elif args.mode == "count":
        print(count(data, args.path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
