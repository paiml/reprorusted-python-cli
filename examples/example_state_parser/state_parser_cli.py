"""Pratt Parser CLI.

Demonstrates Pratt parsing technique for expression parsing with operator precedence.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    """Token types for expression parser."""

    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    LPAREN = auto()
    RPAREN = auto()
    IDENTIFIER = auto()
    COMMA = auto()
    EOF = auto()


@dataclass
class Token:
    """Parser token."""

    type: TokenType
    value: Any
    pos: int


class Lexer:
    """Tokenize expression strings."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def tokenize(self) -> list[Token]:
        """Tokenize the input text."""
        tokens = []

        while self.pos < len(self.text):
            self._skip_whitespace()
            if self.pos >= len(self.text):
                break

            char = self.text[self.pos]
            start_pos = self.pos

            if char.isdigit() or (char == "." and self._peek_digit()):
                tokens.append(self._read_number(start_pos))
            elif char.isalpha() or char == "_":
                tokens.append(self._read_identifier(start_pos))
            elif char == "+":
                tokens.append(Token(TokenType.PLUS, "+", start_pos))
                self.pos += 1
            elif char == "-":
                tokens.append(Token(TokenType.MINUS, "-", start_pos))
                self.pos += 1
            elif char == "*":
                tokens.append(Token(TokenType.STAR, "*", start_pos))
                self.pos += 1
            elif char == "/":
                tokens.append(Token(TokenType.SLASH, "/", start_pos))
                self.pos += 1
            elif char == "^":
                tokens.append(Token(TokenType.CARET, "^", start_pos))
                self.pos += 1
            elif char == "(":
                tokens.append(Token(TokenType.LPAREN, "(", start_pos))
                self.pos += 1
            elif char == ")":
                tokens.append(Token(TokenType.RPAREN, ")", start_pos))
                self.pos += 1
            elif char == ",":
                tokens.append(Token(TokenType.COMMA, ",", start_pos))
                self.pos += 1
            else:
                self.pos += 1

        tokens.append(Token(TokenType.EOF, None, self.pos))
        return tokens

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def _peek_digit(self) -> bool:
        return self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit()

    def _read_number(self, start_pos: int) -> Token:
        has_dot = False
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isdigit():
                self.pos += 1
            elif char == "." and not has_dot:
                has_dot = True
                self.pos += 1
            else:
                break

        value = self.text[start_pos : self.pos]
        return Token(TokenType.NUMBER, float(value), start_pos)

    def _read_identifier(self, start_pos: int) -> Token:
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isalnum() or char == "_":
                self.pos += 1
            else:
                break

        value = self.text[start_pos : self.pos]
        return Token(TokenType.IDENTIFIER, value, start_pos)


@dataclass
class Expr:
    """Base expression node."""

    pass


@dataclass
class NumberExpr(Expr):
    """Number literal."""

    value: float


@dataclass
class IdentifierExpr(Expr):
    """Variable or function name."""

    name: str


@dataclass
class BinaryExpr(Expr):
    """Binary operation."""

    left: Expr
    op: str
    right: Expr


@dataclass
class UnaryExpr(Expr):
    """Unary operation."""

    op: str
    operand: Expr


@dataclass
class CallExpr(Expr):
    """Function call."""

    name: str
    args: list[Expr]


@dataclass
class GroupExpr(Expr):
    """Grouped expression (parentheses)."""

    expr: Expr


class Precedence(Enum):
    """Operator precedence levels."""

    NONE = 0
    ASSIGNMENT = 1
    OR = 2
    AND = 3
    EQUALITY = 4
    COMPARISON = 5
    TERM = 6
    FACTOR = 7
    UNARY = 8
    CALL = 9
    PRIMARY = 10


class PrattParser:
    """Pratt parser for expressions."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Expr:
        """Parse tokens into expression tree."""
        return self.parse_precedence(Precedence.NONE)

    def parse_precedence(self, precedence: Precedence) -> Expr:
        """Parse expression with given precedence."""
        token = self.advance()

        left = self.prefix(token)
        if left is None:
            raise ValueError(f"Unexpected token: {token}")

        while precedence.value < self.get_precedence(self.current()).value:
            token = self.advance()
            left = self.infix(token, left)

        return left

    def prefix(self, token: Token) -> Expr | None:
        """Handle prefix expressions."""
        if token.type == TokenType.NUMBER:
            return NumberExpr(token.value)

        if token.type == TokenType.IDENTIFIER:
            if self.check(TokenType.LPAREN):
                return self.call_expr(token.value)
            return IdentifierExpr(token.value)

        if token.type == TokenType.LPAREN:
            expr = self.parse_precedence(Precedence.NONE)
            self.consume(TokenType.RPAREN)
            return GroupExpr(expr)

        if token.type == TokenType.MINUS:
            operand = self.parse_precedence(Precedence.UNARY)
            return UnaryExpr("-", operand)

        return None

    def infix(self, token: Token, left: Expr) -> Expr:
        """Handle infix expressions."""
        if token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH):
            precedence = self.get_precedence(token)
            right = self.parse_precedence(precedence)
            return BinaryExpr(left, token.value, right)

        if token.type == TokenType.CARET:
            # Right associative
            right = self.parse_precedence(Precedence(self.get_precedence(token).value - 1))
            return BinaryExpr(left, "^", right)

        return left

    def call_expr(self, name: str) -> CallExpr:
        """Parse function call."""
        self.consume(TokenType.LPAREN)
        args: list[Expr] = []

        if not self.check(TokenType.RPAREN):
            args.append(self.parse_precedence(Precedence.NONE))
            while self.match(TokenType.COMMA):
                args.append(self.parse_precedence(Precedence.NONE))

        self.consume(TokenType.RPAREN)
        return CallExpr(name, args)

    def get_precedence(self, token: Token) -> Precedence:
        """Get precedence for token."""
        precedences = {
            TokenType.PLUS: Precedence.TERM,
            TokenType.MINUS: Precedence.TERM,
            TokenType.STAR: Precedence.FACTOR,
            TokenType.SLASH: Precedence.FACTOR,
            TokenType.CARET: Precedence.UNARY,
            TokenType.LPAREN: Precedence.CALL,
        }
        return precedences.get(token.type, Precedence.NONE)

    def current(self) -> Token:
        """Get current token."""
        return self.tokens[self.pos]

    def advance(self) -> Token:
        """Advance to next token."""
        token = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def check(self, type: TokenType) -> bool:
        """Check if current token is of given type."""
        return self.current().type == type

    def match(self, type: TokenType) -> bool:
        """Match and consume token if it matches."""
        if self.check(type):
            self.advance()
            return True
        return False

    def consume(self, type: TokenType) -> Token:
        """Consume token of expected type."""
        if not self.check(type):
            raise ValueError(f"Expected {type}, got {self.current().type}")
        return self.advance()


class Evaluator:
    """Evaluate parsed expressions."""

    def __init__(self, env: dict[str, float] | None = None) -> None:
        self.env = env or {}
        self.functions: dict[str, Callable[..., float]] = {
            "abs": abs,
            "min": min,
            "max": max,
            "sqrt": lambda x: x**0.5,
            "pow": pow,
            "sin": lambda x: __import__("math").sin(x),
            "cos": lambda x: __import__("math").cos(x),
        }

    def evaluate(self, expr: Expr) -> float:
        """Evaluate expression."""
        if isinstance(expr, NumberExpr):
            return expr.value

        if isinstance(expr, IdentifierExpr):
            if expr.name not in self.env:
                raise ValueError(f"Undefined variable: {expr.name}")
            return self.env[expr.name]

        if isinstance(expr, BinaryExpr):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)

            ops = {
                "+": lambda a, b: a + b,
                "-": lambda a, b: a - b,
                "*": lambda a, b: a * b,
                "/": lambda a, b: a / b if b != 0 else float("inf"),
                "^": lambda a, b: a**b,
            }
            return ops[expr.op](left, right)

        if isinstance(expr, UnaryExpr):
            operand = self.evaluate(expr.operand)
            if expr.op == "-":
                return -operand
            return operand

        if isinstance(expr, CallExpr):
            if expr.name not in self.functions:
                raise ValueError(f"Undefined function: {expr.name}")
            args = [self.evaluate(arg) for arg in expr.args]
            return self.functions[expr.name](*args)

        if isinstance(expr, GroupExpr):
            return self.evaluate(expr.expr)

        raise ValueError(f"Unknown expression type: {type(expr)}")


class Printer:
    """Print expressions in different formats."""

    def to_string(self, expr: Expr) -> str:
        """Convert expression to string."""
        if isinstance(expr, NumberExpr):
            if expr.value == int(expr.value):
                return str(int(expr.value))
            return str(expr.value)

        if isinstance(expr, IdentifierExpr):
            return expr.name

        if isinstance(expr, BinaryExpr):
            left = self.to_string(expr.left)
            right = self.to_string(expr.right)
            return f"({left} {expr.op} {right})"

        if isinstance(expr, UnaryExpr):
            operand = self.to_string(expr.operand)
            return f"({expr.op}{operand})"

        if isinstance(expr, CallExpr):
            args = ", ".join(self.to_string(arg) for arg in expr.args)
            return f"{expr.name}({args})"

        if isinstance(expr, GroupExpr):
            return self.to_string(expr.expr)

        return str(expr)

    def to_rpn(self, expr: Expr) -> str:
        """Convert expression to reverse polish notation."""
        if isinstance(expr, NumberExpr):
            if expr.value == int(expr.value):
                return str(int(expr.value))
            return str(expr.value)

        if isinstance(expr, IdentifierExpr):
            return expr.name

        if isinstance(expr, BinaryExpr):
            left = self.to_rpn(expr.left)
            right = self.to_rpn(expr.right)
            return f"{left} {right} {expr.op}"

        if isinstance(expr, UnaryExpr):
            operand = self.to_rpn(expr.operand)
            return f"{operand} {expr.op}"

        if isinstance(expr, GroupExpr):
            return self.to_rpn(expr.expr)

        return str(expr)


def parse(text: str) -> Expr:
    """Parse expression string."""
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = PrattParser(tokens)
    return parser.parse()


def evaluate(text: str, env: dict[str, float] | None = None) -> float:
    """Parse and evaluate expression."""
    expr = parse(text)
    return Evaluator(env).evaluate(expr)


def to_string(text: str) -> str:
    """Parse and convert to string."""
    expr = parse(text)
    return Printer().to_string(expr)


def to_rpn(text: str) -> str:
    """Parse and convert to RPN."""
    expr = parse(text)
    return Printer().to_rpn(expr)


def simulate_parser(operations: list[str]) -> list[str]:
    """Simulate parser operations."""
    results = []
    env: dict[str, float] = {}

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "eval":
            try:
                value = evaluate(parts[1], env)
                results.append(str(value))
            except ValueError as e:
                results.append(f"error:{e}")
        elif cmd == "set":
            name_val = parts[1].split("=")
            env[name_val[0]] = float(name_val[1])
            results.append("ok")
        elif cmd == "string":
            try:
                results.append(to_string(parts[1]))
            except ValueError as e:
                results.append(f"error:{e}")
        elif cmd == "rpn":
            try:
                results.append(to_rpn(parts[1]))
            except ValueError as e:
                results.append(f"error:{e}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: state_parser_cli.py <command> <expr>")
        print("Commands: eval, string, rpn")
        return 1

    cmd = sys.argv[1]
    expr = sys.argv[2]

    if cmd == "eval":
        result = evaluate(expr)
        print(result)
    elif cmd == "string":
        result = to_string(expr)
        print(result)
    elif cmd == "rpn":
        result = to_rpn(expr)
        print(result)
    else:
        print(f"Unknown command: {cmd}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
