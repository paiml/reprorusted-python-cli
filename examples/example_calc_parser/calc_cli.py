#!/usr/bin/env python3
"""Calculator Parser CLI.

Recursive descent parser for arithmetic expressions.
"""

import argparse
import math
import sys
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Token types for the calculator."""

    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    POWER = auto()
    MODULO = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    IDENTIFIER = auto()
    EOF = auto()


@dataclass
class Token:
    """Lexer token."""

    type: TokenType
    value: str | float
    position: int


class Lexer:
    """Tokenizer for arithmetic expressions."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def peek(self) -> str:
        """Look at current character without consuming."""
        if self.pos >= len(self.text):
            return ""
        return self.text[self.pos]

    def advance(self) -> str:
        """Consume and return current character."""
        char = self.peek()
        self.pos += 1
        return char

    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.peek().isspace():
            self.advance()

    def read_number(self) -> float:
        """Read a number (integer or float)."""
        start = self.pos
        has_dot = False

        while self.peek().isdigit() or (self.peek() == "." and not has_dot):
            if self.peek() == ".":
                has_dot = True
            self.advance()

        return float(self.text[start : self.pos])

    def read_identifier(self) -> str:
        """Read an identifier (function name or variable)."""
        start = self.pos
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        return self.text[start : self.pos]

    def next_token(self) -> Token:
        """Get the next token."""
        self.skip_whitespace()

        pos = self.pos

        if self.pos >= len(self.text):
            return Token(TokenType.EOF, "", pos)

        char = self.peek()

        if char.isdigit() or (
            char == "." and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit()
        ):
            return Token(TokenType.NUMBER, self.read_number(), pos)

        if char.isalpha() or char == "_":
            return Token(TokenType.IDENTIFIER, self.read_identifier(), pos)

        self.advance()

        token_map = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "^": TokenType.POWER,
            "%": TokenType.MODULO,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            ",": TokenType.COMMA,
        }

        if char in token_map:
            return Token(token_map[char], char, pos)

        raise SyntaxError(f"Unexpected character '{char}' at position {pos}")

    def tokenize(self) -> list[Token]:
        """Tokenize entire input."""
        tokens = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens


class Parser:
    """Recursive descent parser for arithmetic expressions."""

    FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "abs": abs,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
    }

    CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    def __init__(self, text: str):
        self.lexer = Lexer(text)
        self.current_token = self.lexer.next_token()
        self.variables: dict[str, float] = {}

    def error(self, message: str) -> None:
        """Raise a syntax error."""
        raise SyntaxError(f"{message} at position {self.current_token.position}")

    def eat(self, token_type: TokenType) -> Token:
        """Consume a token of expected type."""
        if self.current_token.type == token_type:
            token = self.current_token
            self.current_token = self.lexer.next_token()
            return token
        self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
        return self.current_token  # unreachable

    def parse(self) -> float:
        """Parse and evaluate the expression."""
        result = self.expression()
        if self.current_token.type != TokenType.EOF:
            self.error("Unexpected token after expression")
        return result

    def expression(self) -> float:
        """Parse addition/subtraction."""
        result = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.current_token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                result += self.term()
            else:
                self.eat(TokenType.MINUS)
                result -= self.term()

        return result

    def term(self) -> float:
        """Parse multiplication/division."""
        result = self.power()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            if self.current_token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
                result *= self.power()
            elif self.current_token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
                divisor = self.power()
                if divisor == 0:
                    raise ZeroDivisionError("Division by zero")
                result /= divisor
            else:
                self.eat(TokenType.MODULO)
                result %= self.power()

        return result

    def power(self) -> float:
        """Parse exponentiation (right associative)."""
        result = self.unary()

        if self.current_token.type == TokenType.POWER:
            self.eat(TokenType.POWER)
            result = result ** self.power()

        return result

    def unary(self) -> float:
        """Parse unary operators."""
        if self.current_token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return -self.unary()
        if self.current_token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return self.unary()

        return self.primary()

    def primary(self) -> float:
        """Parse primary expressions."""
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return float(token.value)

        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.expression()
            self.eat(TokenType.RPAREN)
            return result

        if token.type == TokenType.IDENTIFIER:
            name = str(token.value)
            self.eat(TokenType.IDENTIFIER)

            # Check if it's a function call
            if self.current_token.type == TokenType.LPAREN:
                return self.function_call(name)

            # Check if it's a constant
            if name in self.CONSTANTS:
                return self.CONSTANTS[name]

            # Check if it's a variable
            if name in self.variables:
                return self.variables[name]

            self.error(f"Unknown identifier '{name}'")

        self.error(f"Unexpected token {token.type.name}")
        return 0  # unreachable

    def function_call(self, name: str) -> float:
        """Parse and evaluate function call."""
        if name not in self.FUNCTIONS:
            self.error(f"Unknown function '{name}'")

        self.eat(TokenType.LPAREN)
        args = []

        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expression())

            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expression())

        self.eat(TokenType.RPAREN)

        func = self.FUNCTIONS[name]
        try:
            return func(*args)
        except TypeError as e:
            self.error(f"Function '{name}' error: {e}")
            return 0  # unreachable


def evaluate(expression: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression."""
    parser = Parser(expression)
    if variables:
        parser.variables = variables
    return parser.parse()


def tokenize(expression: str) -> list[Token]:
    """Tokenize an expression."""
    lexer = Lexer(expression)
    return lexer.tokenize()


def format_result(value: float) -> str:
    """Format result for display."""
    if value == int(value):
        return str(int(value))
    return f"{value:.10g}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculator expression parser")
    parser.add_argument("expression", nargs="?", help="Expression to evaluate")
    parser.add_argument("--tokenize", action="store_true", help="Show tokens only")
    parser.add_argument("--var", nargs="*", help="Variables: name=value")

    args = parser.parse_args()

    if not args.expression:
        # Interactive mode
        print("Calculator (type 'quit' to exit)")
        while True:
            try:
                line = input("> ").strip()
                if line.lower() in ("quit", "exit", "q"):
                    break
                if not line:
                    continue

                result = evaluate(line)
                print(f"= {format_result(result)}")
            except (SyntaxError, ZeroDivisionError, ValueError) as e:
                print(f"Error: {e}")
            except EOFError:
                break
        return 0

    # Parse variables
    variables = {}
    if args.var:
        for v in args.var:
            name, value = v.split("=")
            variables[name.strip()] = float(value.strip())

    if args.tokenize:
        tokens = tokenize(args.expression)
        for token in tokens:
            print(f"{token.type.name:12} {token.value!r:15} @ {token.position}")
        return 0

    try:
        result = evaluate(args.expression, variables)
        print(format_result(result))
    except (SyntaxError, ZeroDivisionError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
