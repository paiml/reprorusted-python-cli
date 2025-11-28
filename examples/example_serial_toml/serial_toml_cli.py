"""TOML Parser and Writer CLI.

Demonstrates TOML parsing, writing, and manipulation patterns.
Implements a subset of TOML format for educational purposes.
"""

import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any


@dataclass
class TomlToken:
    """Token from TOML lexer."""

    kind: str
    value: str
    line: int
    col: int


class TomlLexer:
    """TOML lexer."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> list[TomlToken]:
        """Tokenize TOML text."""
        tokens = []

        while self.pos < len(self.text):
            ch = self.text[self.pos]

            # Skip whitespace (not newlines)
            if ch in " \t":
                self._advance()
                continue

            # Newline
            if ch == "\n":
                tokens.append(TomlToken("newline", "\n", self.line, self.col))
                self._advance()
                self.line += 1
                self.col = 1
                continue

            # Comment
            if ch == "#":
                while self.pos < len(self.text) and self.text[self.pos] != "\n":
                    self._advance()
                continue

            # Table header
            if ch == "[":
                tokens.append(self._read_table_header())
                continue

            # String
            if ch in "\"'":
                tokens.append(self._read_string())
                continue

            # Number or date
            if ch.isdigit() or ch == "-" or ch == "+":
                tokens.append(self._read_number_or_date())
                continue

            # Boolean or identifier
            if ch.isalpha() or ch == "_":
                tokens.append(self._read_identifier())
                continue

            # Operators
            if ch == "=":
                tokens.append(TomlToken("equals", "=", self.line, self.col))
                self._advance()
                continue

            if ch == ",":
                tokens.append(TomlToken("comma", ",", self.line, self.col))
                self._advance()
                continue

            if ch == "{":
                tokens.append(TomlToken("lbrace", "{", self.line, self.col))
                self._advance()
                continue

            if ch == "}":
                tokens.append(TomlToken("rbrace", "}", self.line, self.col))
                self._advance()
                continue

            self._advance()

        return tokens

    def _advance(self) -> str:
        ch = self.text[self.pos]
        self.pos += 1
        self.col += 1
        return ch

    def _read_table_header(self) -> TomlToken:
        """Read table header [name] or [[name]]."""
        start_line, start_col = self.line, self.col
        self._advance()  # Skip first [

        is_array = False
        if self.pos < len(self.text) and self.text[self.pos] == "[":
            is_array = True
            self._advance()

        name = ""
        while self.pos < len(self.text) and self.text[self.pos] != "]":
            name += self._advance()

        self._advance()  # Skip ]
        if is_array and self.pos < len(self.text) and self.text[self.pos] == "]":
            self._advance()

        kind = "array_table" if is_array else "table"
        return TomlToken(kind, name.strip(), start_line, start_col)

    def _read_string(self) -> TomlToken:
        """Read string literal."""
        start_line, start_col = self.line, self.col
        quote = self._advance()
        value = ""

        while self.pos < len(self.text) and self.text[self.pos] != quote:
            ch = self._advance()
            if ch == "\\":
                if self.pos < len(self.text):
                    escaped = self._advance()
                    if escaped == "n":
                        value += "\n"
                    elif escaped == "t":
                        value += "\t"
                    elif escaped == "\\":
                        value += "\\"
                    elif escaped == '"':
                        value += '"'
                    else:
                        value += escaped
            else:
                value += ch

        if self.pos < len(self.text):
            self._advance()  # Skip closing quote

        return TomlToken("string", value, start_line, start_col)

    def _read_number_or_date(self) -> TomlToken:
        """Read number or date/time literal."""
        start_line, start_col = self.line, self.col
        value = ""

        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch in "0123456789+-.:TZeE_":
                value += self._advance()
            elif ch.isalpha():
                value += self._advance()
            else:
                break

        # Remove underscores from numbers
        clean_value = value.replace("_", "")

        # Determine type
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", clean_value):
            return TomlToken("datetime", clean_value, start_line, start_col)
        if re.match(r"^\d{4}-\d{2}-\d{2}$", clean_value):
            return TomlToken("date", clean_value, start_line, start_col)
        if re.match(r"^\d{2}:\d{2}:\d{2}", clean_value):
            return TomlToken("time", clean_value, start_line, start_col)
        if "." in clean_value or "e" in clean_value.lower():
            return TomlToken("float", clean_value, start_line, start_col)

        return TomlToken("integer", clean_value, start_line, start_col)

    def _read_identifier(self) -> TomlToken:
        """Read identifier or boolean."""
        start_line, start_col = self.line, self.col
        value = ""

        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch.isalnum() or ch in "_-":
                value += self._advance()
            else:
                break

        if value == "true":
            return TomlToken("boolean", "true", start_line, start_col)
        if value == "false":
            return TomlToken("boolean", "false", start_line, start_col)

        return TomlToken("identifier", value, start_line, start_col)


class TomlParser:
    """TOML parser."""

    def __init__(self, tokens: list[TomlToken]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.result: dict[str, Any] = {}
        self.current_table: dict[str, Any] = self.result

    def parse(self) -> dict[str, Any]:
        """Parse tokens into a dict."""
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.kind == "newline":
                self.pos += 1
                continue

            if token.kind == "table":
                self._handle_table(token.value)
                self.pos += 1
                continue

            if token.kind == "array_table":
                self._handle_array_table(token.value)
                self.pos += 1
                continue

            if token.kind == "identifier":
                self._handle_key_value()
                continue

            self.pos += 1

        return self.result

    def _handle_table(self, name: str) -> None:
        """Handle table header."""
        parts = name.split(".")
        self.current_table = self.result

        for part in parts:
            if part not in self.current_table:
                self.current_table[part] = {}
            self.current_table = self.current_table[part]

    def _handle_array_table(self, name: str) -> None:
        """Handle array of tables header."""
        parts = name.split(".")
        current = self.result

        for _i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]

        final = parts[-1]
        if final not in current:
            current[final] = []

        new_table: dict[str, Any] = {}
        current[final].append(new_table)
        self.current_table = new_table

    def _handle_key_value(self) -> None:
        """Handle key = value."""
        key = self.tokens[self.pos].value
        self.pos += 1

        # Skip newlines
        while self.pos < len(self.tokens) and self.tokens[self.pos].kind == "newline":
            self.pos += 1

        # Expect equals
        if self.pos < len(self.tokens) and self.tokens[self.pos].kind == "equals":
            self.pos += 1

        # Skip newlines
        while self.pos < len(self.tokens) and self.tokens[self.pos].kind == "newline":
            self.pos += 1

        # Get value
        if self.pos < len(self.tokens):
            value = self._parse_value()
            self.current_table[key] = value

    def _parse_value(self) -> Any:
        """Parse a value."""
        token = self.tokens[self.pos]
        self.pos += 1

        if token.kind == "string":
            return token.value
        if token.kind == "integer":
            return int(token.value)
        if token.kind == "float":
            return float(token.value)
        if token.kind == "boolean":
            return token.value == "true"
        if token.kind == "datetime":
            return datetime.fromisoformat(token.value.replace("Z", "+00:00"))
        if token.kind == "date":
            return date.fromisoformat(token.value)
        if token.kind == "time":
            return time.fromisoformat(token.value)
        if token.kind == "lbrace":
            return self._parse_inline_table()

        return token.value

    def _parse_inline_table(self) -> dict[str, Any]:
        """Parse inline table { key = value, ... }."""
        result: dict[str, Any] = {}

        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.kind == "rbrace":
                self.pos += 1
                break

            if token.kind == "comma":
                self.pos += 1
                continue

            if token.kind == "identifier":
                key = token.value
                self.pos += 1

                if self.pos < len(self.tokens) and self.tokens[self.pos].kind == "equals":
                    self.pos += 1

                if self.pos < len(self.tokens):
                    result[key] = self._parse_value()

        return result


def toml_parse(text: str) -> dict[str, Any]:
    """Parse TOML text."""
    lexer = TomlLexer(text)
    tokens = lexer.tokenize()
    parser = TomlParser(tokens)
    return parser.parse()


def toml_dump(data: dict[str, Any], prefix: str = "") -> str:
    """Convert dict to TOML string."""
    lines = []
    tables = []

    for key, value in data.items():
        if isinstance(value, dict):
            table_name = f"{prefix}.{key}" if prefix else key
            tables.append((table_name, value))
        else:
            lines.append(f"{key} = {_value_to_toml(value)}")

    result = "\n".join(lines)

    for table_name, table_data in tables:
        if result:
            result += "\n\n"
        result += f"[{table_name}]\n"
        result += toml_dump(table_data, table_name)

    return result


def _value_to_toml(value: Any) -> str:
    """Convert a value to TOML representation."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return value.isoformat()
    if isinstance(value, list):
        items = ", ".join(_value_to_toml(v) for v in value)
        return f"[{items}]"
    if isinstance(value, dict):
        items = ", ".join(f"{k} = {_value_to_toml(v)}" for k, v in value.items())
        return f"{{ {items} }}"
    return str(value)


def toml_get(data: dict[str, Any], path: str) -> Any:
    """Get value at dotted path."""
    parts = path.split(".")
    current = data

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None

    return current


def toml_set(data: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """Set value at dotted path."""
    import json

    result = json.loads(json.dumps(data, default=str))
    parts = path.split(".")
    current = result

    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value
    return result


def toml_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Merge two TOML documents."""
    import json

    result = json.loads(json.dumps(base, default=str))

    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = toml_merge(result[key], value)
        else:
            result[key] = json.loads(json.dumps(value, default=str))

    return result


def toml_tables(data: dict[str, Any], prefix: str = "") -> list[str]:
    """List all table names in TOML data."""
    tables = []

    for key, value in data.items():
        if isinstance(value, dict):
            table_name = f"{prefix}.{key}" if prefix else key
            tables.append(table_name)
            tables.extend(toml_tables(value, table_name))

    return tables


def simulate_toml(operations: list[str]) -> list[str]:
    """Simulate TOML operations."""
    results = []
    context: dict[str, Any] = {}

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "parse":
            context["data"] = toml_parse(parts[1])
            results.append("ok")
        elif cmd == "get":
            value = toml_get(context.get("data", {}), parts[1])
            results.append(str(value) if value is not None else "null")
        elif cmd == "set":
            path_value = parts[1].split("=", 1)
            context["data"] = toml_set(context.get("data", {}), path_value[0], path_value[1])
            results.append("ok")
        elif cmd == "tables":
            tables = toml_tables(context.get("data", {}))
            results.append(",".join(tables))
        elif cmd == "dump":
            results.append(toml_dump(context.get("data", {})))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: serial_toml_cli.py <command> [args...]")
        print("Commands: parse, get, dump, tables")
        return 1

    cmd = sys.argv[1]

    if cmd == "parse":
        text = sys.stdin.read()
        data = toml_parse(text)
        import json

        print(json.dumps(data, indent=2, default=str))

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: get <path>", file=sys.stderr)
            return 1
        text = sys.stdin.read()
        data = toml_parse(text)
        value = toml_get(data, sys.argv[2])
        print(value)

    elif cmd == "dump":
        import json

        data = json.loads(sys.stdin.read())
        print(toml_dump(data))

    elif cmd == "tables":
        text = sys.stdin.read()
        data = toml_parse(text)
        for table in toml_tables(data):
            print(table)

    return 0


if __name__ == "__main__":
    sys.exit(main())
