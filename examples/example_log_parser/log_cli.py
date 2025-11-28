#!/usr/bin/env python3
"""Apache/nginx combined log format parser CLI.

Parses log lines in Combined Log Format:
IP - - [timestamp] "METHOD /path HTTP/x.x" status size "referer" "user-agent"
"""

import argparse
import re
import sys

# Combined Log Format regex
LOG_PATTERN = re.compile(
    r"(\S+)\s+"  # IP address
    r"(\S+)\s+"  # ident
    r"(\S+)\s+"  # user
    r"\[([^\]]+)\]\s+"  # timestamp
    r'"(\S+)\s+(\S+)\s+(\S+)"\s+'  # method, path, protocol
    r"(\d+)\s+"  # status code
    r"(\S+)\s*"  # response size
    r'(?:"([^"]*)"\s*)?'  # referer (optional)
    r'(?:"([^"]*)")?'  # user-agent (optional)
)


def parse_log_line(line: str) -> dict | None:
    """Parse a single log line into components."""
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    groups = match.groups()
    return {
        "ip": groups[0],
        "ident": groups[1],
        "user": groups[2],
        "timestamp": groups[3],
        "method": groups[4],
        "path": groups[5],
        "protocol": groups[6],
        "status": int(groups[7]),
        "size": 0 if groups[8] == "-" else int(groups[8]),
        "referer": groups[9] if groups[9] else "-",
        "user_agent": groups[10] if groups[10] else "-",
    }


def filter_by_status(entries: list, status_code: int) -> list:
    """Filter log entries by status code."""
    return [e for e in entries if e["status"] == status_code]


def filter_by_method(entries: list, method: str) -> list:
    """Filter log entries by HTTP method."""
    return [e for e in entries if e["method"].upper() == method.upper()]


def count_by_ip(entries: list) -> dict:
    """Count requests per IP address."""
    counts: dict = {}
    for entry in entries:
        ip = entry["ip"]
        counts[ip] = counts.get(ip, 0) + 1
    return counts


def count_by_status(entries: list) -> dict:
    """Count requests per status code."""
    counts: dict = {}
    for entry in entries:
        status = entry["status"]
        counts[status] = counts.get(status, 0) + 1
    return counts


def format_entry(entry: dict, output_format: str) -> str:
    """Format a log entry for output."""
    if output_format == "json":
        import json

        return json.dumps(entry)
    elif output_format == "csv":
        return f"{entry['ip']},{entry['method']},{entry['path']},{entry['status']},{entry['size']}"
    else:  # table
        return f"{entry['ip']:15} {entry['method']:6} {entry['status']:3} {entry['path']}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse and analyze Apache/nginx log files")
    parser.add_argument("logfile", nargs="?", help="Log file to parse (- for stdin)")
    parser.add_argument(
        "-f", "--format", choices=["table", "json", "csv"], default="table", help="Output format"
    )
    parser.add_argument("--status", type=int, help="Filter by status code")
    parser.add_argument("--method", help="Filter by HTTP method")
    parser.add_argument("--stats", action="store_true", help="Show statistics instead of entries")
    parser.add_argument("--top-ips", type=int, metavar="N", help="Show top N IPs by request count")

    args = parser.parse_args()

    # Read input
    if args.logfile is None or args.logfile == "-":
        lines = sys.stdin.readlines()
    else:
        with open(args.logfile) as f:
            lines = f.readlines()

    # Parse all lines
    entries = []
    parse_errors = 0
    for line in lines:
        entry = parse_log_line(line)
        if entry:
            entries.append(entry)
        else:
            parse_errors += 1

    # Apply filters
    if args.status:
        entries = filter_by_status(entries, args.status)

    if args.method:
        entries = filter_by_method(entries, args.method)

    # Output
    if args.stats:
        print(f"Total entries: {len(entries)}")
        print(f"Parse errors: {parse_errors}")
        status_counts = count_by_status(entries)
        print("Status codes:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")
    elif args.top_ips:
        ip_counts = count_by_ip(entries)
        sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
        for ip, count in sorted_ips[: args.top_ips]:
            print(f"{ip}: {count}")
    else:
        for entry in entries:
            print(format_entry(entry, args.format))

    return 0


if __name__ == "__main__":
    sys.exit(main())
