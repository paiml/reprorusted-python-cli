"""Lexer/Tokenizer CLI.

Demonstrates lexical analysis patterns for tokenizing source code.
"""

import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokType(Enum):
    """Token types."""

    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()
    BOOL = auto()

    # Identifiers and keywords
    IDENTIFIER = auto()
    KEYWORD = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()
    AMPERSAND = auto()
    PIPE = auto()
    TILDE = auto()
    BANG = auto()
    QUESTION = auto()

    # Comparison
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    # Assignment
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    STAR_ASSIGN = auto()
    SLASH_ASSIGN = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()
    ARROW = auto()

    # Special
    NEWLINE = auto()
    COMMENT = auto()
    WHITESPACE = auto()
    EOF = auto()
    ERROR = auto()


@dataclass
class Token:
    """Lexer token."""

    type: TokType
    value: Any
    line: int
    column: int
    length: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


@dataclass
class LexerConfig:
    """Lexer configuration."""

    keywords: set[str]
    skip_whitespace: bool = True
    skip_comments: bool = True
    string_delimiters: str = "\"'"
    single_line_comment: str = "//"
    multi_line_comment: tuple[str, str] = ("/*", "*/")


DEFAULT_KEYWORDS = {
    "if",
    "else",
    "while",
    "for",
    "return",
    "break",
    "continue",
    "fn",
    "let",
    "const",
    "var",
    "true",
    "false",
    "null",
    "class",
    "struct",
    "enum",
    "import",
    "export",
}


class Lexer:
    """Source code lexer."""

    def __init__(self, source: str, config: LexerConfig | None = None) -> None:
        self.source = source
        self.config = config or LexerConfig(keywords=DEFAULT_KEYWORDS)
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """Tokenize the source code."""
        self.tokens = []

        while not self.is_at_end():
            self.scan_token()

        self.tokens.append(Token(TokType.EOF, None, self.line, self.column, 0))
        return self.tokens

    def scan_token(self) -> None:
        """Scan next token."""
        start_pos = self.pos
        start_line = self.line
        start_col = self.column

        char = self.advance()

        # Whitespace
        if char in " \t\r":
            if not self.config.skip_whitespace:
                self.add_token(TokType.WHITESPACE, char, start_line, start_col, 1)
            return

        if char == "\n":
            self.line += 1
            self.column = 1
            if not self.config.skip_whitespace:
                self.add_token(TokType.NEWLINE, "\n", start_line, start_col, 1)
            return

        # Comments
        if char == "/" and self.peek() == "/":
            self.advance()
            comment = self.read_until("\n")
            if not self.config.skip_comments:
                self.add_token(TokType.COMMENT, comment, start_line, start_col, len(comment) + 2)
            return

        if char == "/" and self.peek() == "*":
            self.advance()
            comment = self.read_multi_line_comment()
            if not self.config.skip_comments:
                self.add_token(TokType.COMMENT, comment, start_line, start_col, len(comment) + 4)
            return

        # Strings
        if char in self.config.string_delimiters:
            string = self.read_string(char)
            self.add_token(TokType.STRING, string, start_line, start_col, len(string) + 2)
            return

        # Numbers
        if char.isdigit():
            number, is_float = self.read_number(char)
            tok_type = TokType.FLOAT if is_float else TokType.INTEGER
            self.add_token(tok_type, number, start_line, start_col, self.pos - start_pos)
            return

        # Identifiers and keywords
        if char.isalpha() or char == "_":
            identifier = self.read_identifier(char)
            if identifier in self.config.keywords:
                self.add_token(TokType.KEYWORD, identifier, start_line, start_col, len(identifier))
            elif identifier in ("true", "false"):
                self.add_token(
                    TokType.BOOL, identifier == "true", start_line, start_col, len(identifier)
                )
            else:
                self.add_token(
                    TokType.IDENTIFIER, identifier, start_line, start_col, len(identifier)
                )
            return

        # Operators and delimiters
        token = self.scan_operator(char, start_line, start_col)
        if token:
            self.tokens.append(token)
            return

        # Unknown character
        self.add_token(TokType.ERROR, char, start_line, start_col, 1)

    def scan_operator(self, char: str, line: int, col: int) -> Token | None:
        """Scan operator or delimiter."""
        # Two-character operators
        two_char = char + self.peek() if not self.is_at_end() else char

        two_char_ops = {
            "==": TokType.EQ,
            "!=": TokType.NE,
            "<=": TokType.LE,
            ">=": TokType.GE,
            "+=": TokType.PLUS_ASSIGN,
            "-=": TokType.MINUS_ASSIGN,
            "*=": TokType.STAR_ASSIGN,
            "/=": TokType.SLASH_ASSIGN,
            "->": TokType.ARROW,
        }

        if two_char in two_char_ops:
            self.advance()
            return Token(two_char_ops[two_char], two_char, line, col, 2)

        # Single-character operators
        single_char_ops = {
            "+": TokType.PLUS,
            "-": TokType.MINUS,
            "*": TokType.STAR,
            "/": TokType.SLASH,
            "%": TokType.PERCENT,
            "^": TokType.CARET,
            "&": TokType.AMPERSAND,
            "|": TokType.PIPE,
            "~": TokType.TILDE,
            "!": TokType.BANG,
            "?": TokType.QUESTION,
            "<": TokType.LT,
            ">": TokType.GT,
            "=": TokType.ASSIGN,
            "(": TokType.LPAREN,
            ")": TokType.RPAREN,
            "[": TokType.LBRACKET,
            "]": TokType.RBRACKET,
            "{": TokType.LBRACE,
            "}": TokType.RBRACE,
            ",": TokType.COMMA,
            ".": TokType.DOT,
            ":": TokType.COLON,
            ";": TokType.SEMICOLON,
        }

        if char in single_char_ops:
            return Token(single_char_ops[char], char, line, col, 1)

        return None

    def read_string(self, quote: str) -> str:
        """Read string literal."""
        chars = []
        while not self.is_at_end() and self.peek() != quote:
            char = self.advance()
            if char == "\\":
                escaped = self.advance()
                escape_map = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'"}
                chars.append(escape_map.get(escaped, escaped))
            else:
                chars.append(char)

        if not self.is_at_end():
            self.advance()  # Closing quote

        return "".join(chars)

    def read_number(self, first: str) -> tuple[float | int, bool]:
        """Read numeric literal."""
        chars = [first]
        is_float = False

        while not self.is_at_end() and (self.peek().isdigit() or self.peek() == "."):
            if self.peek() == ".":
                if is_float:
                    break
                is_float = True
            chars.append(self.advance())

        # Handle exponent
        if not self.is_at_end() and self.peek().lower() == "e":
            chars.append(self.advance())
            if not self.is_at_end() and self.peek() in "+-":
                chars.append(self.advance())
            while not self.is_at_end() and self.peek().isdigit():
                chars.append(self.advance())
            is_float = True

        value = "".join(chars)
        return (float(value), True) if is_float else (int(value), False)

    def read_identifier(self, first: str) -> str:
        """Read identifier."""
        chars = [first]
        while not self.is_at_end() and (self.peek().isalnum() or self.peek() == "_"):
            chars.append(self.advance())
        return "".join(chars)

    def read_until(self, delimiter: str) -> str:
        """Read until delimiter."""
        chars = []
        while not self.is_at_end() and self.peek() != delimiter:
            chars.append(self.advance())
        return "".join(chars)

    def read_multi_line_comment(self) -> str:
        """Read multi-line comment."""
        chars = []
        while not self.is_at_end():
            if (
                self.peek() == "*"
                and self.pos + 1 < len(self.source)
                and self.source[self.pos + 1] == "/"
            ):
                self.advance()
                self.advance()
                break
            if self.peek() == "\n":
                self.line += 1
                self.column = 0
            chars.append(self.advance())
        return "".join(chars)

    def advance(self) -> str:
        """Advance position and return character."""
        char = self.source[self.pos]
        self.pos += 1
        self.column += 1
        return char

    def peek(self) -> str:
        """Peek at current character."""
        if self.is_at_end():
            return "\0"
        return self.source[self.pos]

    def is_at_end(self) -> bool:
        """Check if at end of source."""
        return self.pos >= len(self.source)

    def add_token(self, type: TokType, value: Any, line: int, col: int, length: int) -> None:
        """Add token to list."""
        self.tokens.append(Token(type, value, line, col, length))


def tokenize(source: str) -> list[Token]:
    """Tokenize source code."""
    return Lexer(source).tokenize()


def token_summary(tokens: list[Token]) -> dict[str, int]:
    """Get summary of token types."""
    summary: dict[str, int] = {}
    for token in tokens:
        name = token.type.name
        summary[name] = summary.get(name, 0) + 1
    return summary


def format_tokens(tokens: list[Token]) -> str:
    """Format tokens as string."""
    lines = []
    for token in tokens:
        if token.type == TokType.EOF:
            continue
        lines.append(f"{token.line}:{token.column} {token.type.name} {token.value!r}")
    return "\n".join(lines)


def simulate_lexer(operations: list[str]) -> list[str]:
    """Simulate lexer operations."""
    results = []
    tokens: list[Token] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "tokenize":
            tokens = tokenize(parts[1])
            results.append(str(len(tokens)))
        elif cmd == "count":
            count = sum(1 for t in tokens if t.type.name == parts[1])
            results.append(str(count))
        elif cmd == "types":
            types = [t.type.name for t in tokens if t.type != TokType.EOF]
            results.append(",".join(types))
        elif cmd == "values":
            values = [str(t.value) for t in tokens if t.type != TokType.EOF]
            results.append(",".join(values))
        elif cmd == "summary":
            summary = token_summary(tokens)
            results.append(",".join(f"{k}:{v}" for k, v in sorted(summary.items())))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: state_lexer_cli.py <command> [args...]")
        print("Commands: tokenize, summary, format")
        return 1

    cmd = sys.argv[1]

    if cmd == "tokenize":
        source = sys.stdin.read() if len(sys.argv) < 3 else sys.argv[2]
        tokens = tokenize(source)
        for token in tokens:
            if token.type != TokType.EOF:
                print(f"{token.type.name}: {token.value!r}")

    elif cmd == "summary":
        source = sys.stdin.read() if len(sys.argv) < 3 else sys.argv[2]
        tokens = tokenize(source)
        summary = token_summary(tokens)
        for name, count in sorted(summary.items()):
            print(f"{name}: {count}")

    elif cmd == "format":
        source = sys.stdin.read() if len(sys.argv) < 3 else sys.argv[2]
        tokens = tokenize(source)
        print(format_tokens(tokens))

    return 0


if __name__ == "__main__":
    sys.exit(main())
