#!/usr/bin/env python3
"""Simple markdown to HTML converter CLI.

Supports basic markdown syntax:
- Headers (# to ######)
- Bold (**text**)
- Italic (*text*)
- Code (`text`)
- Links ([text](url))
- Unordered lists (- item)
"""

import argparse
import re
import sys


def parse_headers(text: str) -> str:
    """Convert markdown headers to HTML."""
    for i in range(6, 0, -1):
        pattern = r"^" + "#" * i + r" (.+)$"
        text = re.sub(pattern, rf"<h{i}>\1</h{i}>", text, flags=re.MULTILINE)
    return text


def parse_bold(text: str) -> str:
    """Convert **bold** to <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def parse_italic(text: str) -> str:
    """Convert *italic* to <em>."""
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)


def parse_code(text: str) -> str:
    """Convert `code` to <code>."""
    return re.sub(r"`(.+?)`", r"<code>\1</code>", text)


def parse_links(text: str) -> str:
    """Convert [text](url) to <a href>."""
    return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)


def parse_lists(text: str) -> str:
    """Convert unordered lists to HTML."""
    lines = text.split("\n")
    result = []
    in_list = False

    for line in lines:
        if line.startswith("- "):
            if not in_list:
                result.append("<ul>")
                in_list = True
            result.append(f"<li>{line[2:]}</li>")
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(line)

    if in_list:
        result.append("</ul>")

    return "\n".join(result)


def parse_paragraphs(text: str) -> str:
    """Wrap standalone text in <p> tags."""
    lines = text.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("<"):
            result.append(f"<p>{stripped}</p>")
        else:
            result.append(line)

    return "\n".join(result)


def markdown_to_html(markdown: str) -> str:
    """Convert markdown text to HTML."""
    html = markdown
    html = parse_headers(html)
    html = parse_bold(html)
    html = parse_italic(html)
    html = parse_code(html)
    html = parse_links(html)
    html = parse_lists(html)
    html = parse_paragraphs(html)
    return html


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert markdown to HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", nargs="?", help="Input markdown file (- for stdin)")
    parser.add_argument("-o", "--output", help="Output HTML file (default: stdout)")
    parser.add_argument("--wrap", action="store_true", help="Wrap output in HTML document")

    args = parser.parse_args()

    # Read input
    if args.input is None or args.input == "-":
        markdown = sys.stdin.read()
    else:
        with open(args.input) as f:
            markdown = f.read()

    # Convert
    html = markdown_to_html(markdown)

    # Optionally wrap in document
    if args.wrap:
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Document</title></head>
<body>
{html}
</body>
</html>"""

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(html)
    else:
        print(html)

    return 0


if __name__ == "__main__":
    sys.exit(main())
