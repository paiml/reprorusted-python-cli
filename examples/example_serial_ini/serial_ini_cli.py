"""INI File Parser and Writer CLI.

Demonstrates INI parsing, writing, and manipulation patterns.
"""

import re
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IniSection:
    """INI file section."""

    name: str
    values: dict[str, str] = field(default_factory=dict)
    comments: list[str] = field(default_factory=list)


@dataclass
class IniDocument:
    """INI document."""

    sections: dict[str, IniSection] = field(default_factory=dict)
    global_values: dict[str, str] = field(default_factory=dict)
    header_comments: list[str] = field(default_factory=list)

    def get(self, section: str, key: str, default: str = "") -> str:
        """Get value from section."""
        if section in self.sections:
            return self.sections[section].values.get(key, default)
        return default

    def set(self, section: str, key: str, value: str) -> None:
        """Set value in section."""
        if section not in self.sections:
            self.sections[section] = IniSection(name=section)
        self.sections[section].values[key] = value

    def has_section(self, name: str) -> bool:
        """Check if section exists."""
        return name in self.sections

    def has_key(self, section: str, key: str) -> bool:
        """Check if key exists in section."""
        return section in self.sections and key in self.sections[section].values

    def remove_key(self, section: str, key: str) -> bool:
        """Remove key from section."""
        if section in self.sections and key in self.sections[section].values:
            del self.sections[section].values[key]
            return True
        return False

    def remove_section(self, section: str) -> bool:
        """Remove section."""
        if section in self.sections:
            del self.sections[section]
            return True
        return False

    def section_names(self) -> list[str]:
        """List section names."""
        return list(self.sections.keys())

    def keys(self, section: str) -> list[str]:
        """List keys in section."""
        if section in self.sections:
            return list(self.sections[section].values.keys())
        return []


class IniParser:
    """INI file parser."""

    SECTION_PATTERN = re.compile(r"^\s*\[([^\]]+)\]\s*$")
    KEY_VALUE_PATTERN = re.compile(r"^\s*([^=]+?)\s*=\s*(.*)$")
    COMMENT_PATTERN = re.compile(r"^\s*[;#](.*)$")

    def __init__(self, text: str) -> None:
        self.text = text
        self.lines = text.splitlines()
        self.pos = 0

    def parse(self) -> IniDocument:
        """Parse INI text."""
        doc = IniDocument()
        current_section: IniSection | None = None
        pending_comments: list[str] = []

        for line in self.lines:
            # Comment
            comment_match = self.COMMENT_PATTERN.match(line)
            if comment_match:
                pending_comments.append(comment_match.group(1).strip())
                continue

            # Empty line
            if not line.strip():
                pending_comments.clear()
                continue

            # Section header
            section_match = self.SECTION_PATTERN.match(line)
            if section_match:
                section_name = section_match.group(1).strip()
                current_section = IniSection(name=section_name, comments=pending_comments.copy())
                doc.sections[section_name] = current_section
                pending_comments.clear()
                continue

            # Key-value pair
            kv_match = self.KEY_VALUE_PATTERN.match(line)
            if kv_match:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()

                # Remove quotes if present
                if len(value) >= 2:
                    if (value.startswith('"') and value.endswith('"')) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        value = value[1:-1]

                if current_section:
                    current_section.values[key] = value
                else:
                    doc.global_values[key] = value

                pending_comments.clear()

        return doc


class IniWriter:
    """INI file writer."""

    def __init__(self, doc: IniDocument) -> None:
        self.doc = doc

    def write(self) -> str:
        """Write INI document to string."""
        lines = []

        # Header comments
        for comment in self.doc.header_comments:
            lines.append(f"; {comment}")

        # Global values
        for key, value in self.doc.global_values.items():
            lines.append(self._format_value(key, value))

        if self.doc.global_values:
            lines.append("")

        # Sections
        for section_name, section in self.doc.sections.items():
            # Section comments
            for comment in section.comments:
                lines.append(f"; {comment}")

            lines.append(f"[{section_name}]")

            for key, value in section.values.items():
                lines.append(self._format_value(key, value))

            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _format_value(self, key: str, value: str) -> str:
        """Format a key-value pair."""
        # Quote values with special characters
        if " " in value or ";" in value or "#" in value or "=" in value:
            value = f'"{value}"'
        return f"{key} = {value}"


def ini_parse(text: str) -> IniDocument:
    """Parse INI text."""
    return IniParser(text).parse()


def ini_dump(doc: IniDocument) -> str:
    """Dump INI document to string."""
    return IniWriter(doc).write()


def ini_get(doc: IniDocument, section: str, key: str, default: str = "") -> str:
    """Get value from INI document."""
    return doc.get(section, key, default)


def ini_set(doc: IniDocument, section: str, key: str, value: str) -> None:
    """Set value in INI document."""
    doc.set(section, key, value)


def ini_to_dict(doc: IniDocument) -> dict[str, dict[str, str]]:
    """Convert INI document to nested dict."""
    result: dict[str, dict[str, str]] = {}

    for section_name, section in doc.sections.items():
        result[section_name] = dict(section.values)

    return result


def dict_to_ini(data: dict[str, dict[str, str]]) -> IniDocument:
    """Convert nested dict to INI document."""
    doc = IniDocument()

    for section_name, values in data.items():
        section = IniSection(name=section_name, values=dict(values))
        doc.sections[section_name] = section

    return doc


def ini_merge(base: IniDocument, overlay: IniDocument) -> IniDocument:
    """Merge two INI documents."""
    result = IniDocument()

    # Copy base
    for name, section in base.sections.items():
        result.sections[name] = IniSection(
            name=name, values=dict(section.values), comments=list(section.comments)
        )

    # Merge overlay
    for name, section in overlay.sections.items():
        if name not in result.sections:
            result.sections[name] = IniSection(name=name)
        result.sections[name].values.update(section.values)

    return result


def ini_diff(doc1: IniDocument, doc2: IniDocument) -> list[str]:
    """Find differences between two INI documents."""
    diffs = []

    all_sections = set(doc1.sections.keys()) | set(doc2.sections.keys())

    for section in sorted(all_sections):
        if section not in doc1.sections:
            diffs.append(f"+ [{section}]")
            continue
        if section not in doc2.sections:
            diffs.append(f"- [{section}]")
            continue

        keys1 = doc1.sections[section].values
        keys2 = doc2.sections[section].values
        all_keys = set(keys1.keys()) | set(keys2.keys())

        for key in sorted(all_keys):
            if key not in keys1:
                diffs.append(f"+ [{section}] {key} = {keys2[key]}")
            elif key not in keys2:
                diffs.append(f"- [{section}] {key} = {keys1[key]}")
            elif keys1[key] != keys2[key]:
                diffs.append(f"~ [{section}] {key}: {keys1[key]} -> {keys2[key]}")

    return diffs


def ini_validate(doc: IniDocument, schema: dict[str, list[str]]) -> list[str]:
    """Validate INI document against schema of required keys per section."""
    errors = []

    for section_name, required_keys in schema.items():
        if section_name not in doc.sections:
            errors.append(f"Missing section: [{section_name}]")
            continue

        section = doc.sections[section_name]
        for key in required_keys:
            if key not in section.values:
                errors.append(f"Missing key: [{section_name}] {key}")

    return errors


def ini_interpolate(doc: IniDocument) -> IniDocument:
    """Expand ${section.key} references in values."""
    result = IniDocument()

    # Copy structure
    for name, section in doc.sections.items():
        result.sections[name] = IniSection(name=name, values=dict(section.values))

    # Interpolate
    pattern = re.compile(r"\$\{([^}]+)\}")

    for section in result.sections.values():
        for key, value in section.values.items():
            new_value = value

            for match in pattern.finditer(value):
                ref = match.group(1)
                parts = ref.split(".")
                if len(parts) == 2:
                    ref_section, ref_key = parts
                    ref_value = result.get(ref_section, ref_key, "")
                    new_value = new_value.replace(match.group(0), ref_value)

            section.values[key] = new_value

    return result


def simulate_ini(operations: list[str]) -> list[str]:
    """Simulate INI operations."""
    results = []
    context: IniDocument | None = None

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "parse":
            context = ini_parse(parts[1])
            results.append("ok")
        elif cmd == "get" and context:
            path = parts[1].split(".")
            if len(path) == 2:
                value = context.get(path[0], path[1])
                results.append(value if value else "null")
        elif cmd == "set" and context:
            path_value = parts[1].split("=", 1)
            path = path_value[0].split(".")
            if len(path) == 2:
                context.set(path[0], path[1], path_value[1])
                results.append("ok")
        elif cmd == "sections" and context:
            results.append(",".join(context.section_names()))
        elif cmd == "keys" and context:
            results.append(",".join(context.keys(parts[1])))
        elif cmd == "has_section" and context:
            results.append("1" if context.has_section(parts[1]) else "0")
        elif cmd == "has_key" and context:
            path = parts[1].split(".")
            if len(path) == 2:
                results.append("1" if context.has_key(path[0], path[1]) else "0")

    return results


def type_infer(value: str) -> Any:
    """Infer type from string value."""
    if value.lower() in ("true", "yes", "on", "1"):
        return True
    if value.lower() in ("false", "no", "off", "0"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def ini_to_typed_dict(doc: IniDocument) -> dict[str, dict[str, Any]]:
    """Convert INI document to dict with type inference."""
    result: dict[str, dict[str, Any]] = {}

    for section_name, section in doc.sections.items():
        result[section_name] = {key: type_infer(value) for key, value in section.values.items()}

    return result


def main() -> int:
    """CLI entry point."""
    import json

    if len(sys.argv) < 2:
        print("Usage: serial_ini_cli.py <command> [args...]")
        print("Commands: parse, get, set, dump, sections, validate")
        return 1

    cmd = sys.argv[1]

    if cmd == "parse":
        text = sys.stdin.read()
        doc = ini_parse(text)
        print(json.dumps(ini_to_dict(doc), indent=2))

    elif cmd == "get":
        if len(sys.argv) < 4:
            print("Usage: get <section> <key>", file=sys.stderr)
            return 1
        text = sys.stdin.read()
        doc = ini_parse(text)
        value = doc.get(sys.argv[2], sys.argv[3])
        print(value)

    elif cmd == "sections":
        text = sys.stdin.read()
        doc = ini_parse(text)
        for section in doc.section_names():
            print(section)

    elif cmd == "dump":
        data = json.loads(sys.stdin.read())
        doc = dict_to_ini(data)
        print(ini_dump(doc))

    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Usage: validate <schema_json>", file=sys.stderr)
            return 1
        schema = json.loads(sys.argv[2])
        text = sys.stdin.read()
        doc = ini_parse(text)
        errors = ini_validate(doc, schema)
        if errors:
            for err in errors:
                print(err)
            return 1
        print("Valid")

    return 0


if __name__ == "__main__":
    sys.exit(main())
