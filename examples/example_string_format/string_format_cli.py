#!/usr/bin/env python3
"""String Format CLI.

String formatting operations.
"""

import argparse
import sys


def format_basic(template: str, *args: str) -> str:
    """Format string with positional arguments."""
    return template.format(*args)


def format_named(template: str, **kwargs: str) -> str:
    """Format string with named arguments."""
    return template.format(**kwargs)


def format_dict(template: str, data: dict[str, str]) -> str:
    """Format string with dictionary."""
    return template.format(**data)


def f_string_style(name: str, value: int) -> str:
    """Demonstrate f-string style formatting."""
    return f"Name: {name}, Value: {value}"


def percent_format(template: str, *args: str) -> str:
    """Old-style % formatting."""
    return template % args


def format_number(n: float, decimals: int = 2) -> str:
    """Format number with decimal places."""
    return f"{n:.{decimals}f}"


def format_currency(amount: float, symbol: str = "$") -> str:
    """Format number as currency."""
    return f"{symbol}{amount:,.2f}"


def format_percent(value: float) -> str:
    """Format number as percentage."""
    return f"{value:.1%}"


def format_scientific(n: float) -> str:
    """Format number in scientific notation."""
    return f"{n:.2e}"


def format_binary(n: int) -> str:
    """Format integer as binary."""
    return f"{n:b}"


def format_hex(n: int) -> str:
    """Format integer as hexadecimal."""
    return f"{n:x}"


def format_octal(n: int) -> str:
    """Format integer as octal."""
    return f"{n:o}"


def pad_left(s: str, width: int, char: str = " ") -> str:
    """Pad string on left to width."""
    return s.rjust(width, char)


def pad_right(s: str, width: int, char: str = " ") -> str:
    """Pad string on right to width."""
    return s.ljust(width, char)


def pad_center(s: str, width: int, char: str = " ") -> str:
    """Center string to width."""
    return s.center(width, char)


def zfill(s: str, width: int) -> str:
    """Pad string with zeros on left."""
    return s.zfill(width)


def truncate(s: str, max_len: int, suffix: str = "...") -> str:
    """Truncate string to max length with suffix."""
    if len(s) <= max_len:
        return s
    return s[: max_len - len(suffix)] + suffix


def wrap_text(s: str, width: int) -> str:
    """Wrap text to width."""
    words = s.split()
    lines: list[str] = []
    current_line: list[str] = []
    current_len = 0

    for word in words:
        if current_len + len(word) + len(current_line) <= width:
            current_line.append(word)
            current_len += len(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)

    if current_line:
        lines.append(" ".join(current_line))
    return "\n".join(lines)


def format_list(items: list[str], separator: str = ", ", last_separator: str = " and ") -> str:
    """Format list with separators."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return separator.join(items[:-1]) + last_separator + items[-1]


def format_table(rows: list[list[str]], headers: list[str] | None = None) -> str:
    """Format data as ASCII table."""
    if not rows:
        return ""

    all_rows = [headers] + rows if headers else rows
    col_widths = [
        max(len(str(row[i])) for row in all_rows if i < len(row)) for i in range(len(all_rows[0]))
    ]

    def format_row(row: list[str]) -> str:
        return "| " + " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))) + " |"

    def separator() -> str:
        return "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

    lines = [separator()]
    if headers:
        lines.append(format_row(headers))
        lines.append(separator())
    for row in rows:
        lines.append(format_row(row))
    lines.append(separator())
    return "\n".join(lines)


def format_key_value(data: dict[str, str], separator: str = ": ") -> str:
    """Format dictionary as key-value pairs."""
    max_key_len = max(len(k) for k in data.keys()) if data else 0
    lines = [f"{k.ljust(max_key_len)}{separator}{v}" for k, v in data.items()]
    return "\n".join(lines)


def format_bytes(n: int) -> str:
    """Format byte count as human-readable."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n //= 1024
    return f"{n:.1f} PB"


def format_duration(seconds: int) -> str:
    """Format seconds as duration string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s" if secs else f"{mins}m"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m" if mins else f"{hours}h"


def format_ordinal(n: int) -> str:
    """Format number with ordinal suffix."""
    if 11 <= n % 100 <= 13:
        suffix = "th"
    elif n % 10 == 1:
        suffix = "st"
    elif n % 10 == 2:
        suffix = "nd"
    elif n % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"
    return f"{n}{suffix}"


def format_plural(n: int, singular: str, plural: str | None = None) -> str:
    """Format count with appropriate plural form."""
    if plural is None:
        plural = singular + "s"
    return f"{n} {singular if n == 1 else plural}"


def template_replace(
    template: str, replacements: dict[str, str], prefix: str = "{{", suffix: str = "}}"
) -> str:
    """Replace template placeholders."""
    result = template
    for key, value in replacements.items():
        result = result.replace(f"{prefix}{key}{suffix}", value)
    return result


def quote(s: str, char: str = '"') -> str:
    """Quote string."""
    return f"{char}{s}{char}"


def unquote(s: str) -> str:
    """Remove surrounding quotes."""
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description="String format CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # format
    format_p = subparsers.add_parser("format", help="Format string")
    format_p.add_argument("template", help="Template string")
    format_p.add_argument("args", nargs="*", help="Arguments")

    # number
    number_p = subparsers.add_parser("number", help="Format number")
    number_p.add_argument("value", type=float, help="Number")
    number_p.add_argument("--decimals", type=int, default=2, help="Decimal places")
    number_p.add_argument("--currency", action="store_true", help="Format as currency")
    number_p.add_argument("--percent", action="store_true", help="Format as percent")

    # pad
    pad_p = subparsers.add_parser("pad", help="Pad string")
    pad_p.add_argument("text", help="Text to pad")
    pad_p.add_argument("width", type=int, help="Target width")
    pad_p.add_argument("--side", choices=["left", "right", "center"], default="left")
    pad_p.add_argument("--char", default=" ", help="Padding character")

    # bytes
    bytes_p = subparsers.add_parser("bytes", help="Format bytes")
    bytes_p.add_argument("value", type=int, help="Byte count")

    # duration
    duration_p = subparsers.add_parser("duration", help="Format duration")
    duration_p.add_argument("seconds", type=int, help="Seconds")

    args = parser.parse_args()

    if args.command == "format":
        result = format_basic(args.template, *args.args)
        print(result)

    elif args.command == "number":
        if args.currency:
            print(format_currency(args.value))
        elif args.percent:
            print(format_percent(args.value))
        else:
            print(format_number(args.value, args.decimals))

    elif args.command == "pad":
        if args.side == "left":
            print(pad_left(args.text, args.width, args.char))
        elif args.side == "right":
            print(pad_right(args.text, args.width, args.char))
        else:
            print(pad_center(args.text, args.width, args.char))

    elif args.command == "bytes":
        print(format_bytes(args.value))

    elif args.command == "duration":
        print(format_duration(args.seconds))

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
