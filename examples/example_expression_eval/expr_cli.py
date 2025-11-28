#!/usr/bin/env python3
"""Expression Evaluator CLI.

Evaluates mathematical and logical expressions with variables and functions.
"""

import argparse
import math
import sys
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Token types for lexer."""

    NUMBER = auto()
    IDENTIFIER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    TRUE = auto()
    FALSE = auto()
    EOF = auto()


@dataclass
class Token:
    """Lexer token."""

    type: TokenType
    value: str | float | bool


class Lexer:
    """Expression tokenizer."""

    KEYWORDS = {
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def peek(self) -> str:
        if self.pos >= len(self.text):
            return ""
        return self.text[self.pos]

    def advance(self) -> str:
        char = self.peek()
        self.pos += 1
        return char

    def skip_whitespace(self) -> None:
        while self.peek().isspace():
            self.advance()

    def number(self) -> Token:
        """Parse number."""
        result = ""
        while self.peek().isdigit() or self.peek() == ".":
            result += self.advance()
        return Token(TokenType.NUMBER, float(result))

    def identifier(self) -> Token:
        """Parse identifier or keyword."""
        result = ""
        while self.peek().isalnum() or self.peek() == "_":
            result += self.advance()

        lower = result.lower()
        if lower in self.KEYWORDS:
            token_type = self.KEYWORDS[lower]
            if token_type == TokenType.TRUE:
                return Token(token_type, True)
            if token_type == TokenType.FALSE:
                return Token(token_type, False)
            return Token(token_type, lower)

        return Token(TokenType.IDENTIFIER, result)

    def tokenize(self) -> list[Token]:
        """Tokenize expression."""
        tokens = []

        while self.pos < len(self.text):
            self.skip_whitespace()
            if self.pos >= len(self.text):
                break

            char = self.peek()

            if char.isdigit() or (
                char == "." and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit()
            ):
                tokens.append(self.number())
            elif char.isalpha() or char == "_":
                tokens.append(self.identifier())
            elif char == "+":
                self.advance()
                tokens.append(Token(TokenType.PLUS, "+"))
            elif char == "-":
                self.advance()
                tokens.append(Token(TokenType.MINUS, "-"))
            elif char == "*":
                self.advance()
                tokens.append(Token(TokenType.STAR, "*"))
            elif char == "/":
                self.advance()
                tokens.append(Token(TokenType.SLASH, "/"))
            elif char == "%":
                self.advance()
                tokens.append(Token(TokenType.PERCENT, "%"))
            elif char == "^":
                self.advance()
                tokens.append(Token(TokenType.CARET, "^"))
            elif char == "(":
                self.advance()
                tokens.append(Token(TokenType.LPAREN, "("))
            elif char == ")":
                self.advance()
                tokens.append(Token(TokenType.RPAREN, ")"))
            elif char == ",":
                self.advance()
                tokens.append(Token(TokenType.COMMA, ","))
            elif char == "=" and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == "=":
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.EQ, "=="))
            elif char == "!" and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == "=":
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.NEQ, "!="))
            elif char == "<" and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == "=":
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.LE, "<="))
            elif char == ">" and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == "=":
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.GE, ">="))
            elif char == "<":
                self.advance()
                tokens.append(Token(TokenType.LT, "<"))
            elif char == ">":
                self.advance()
                tokens.append(Token(TokenType.GT, ">"))
            else:
                self.advance()

        tokens.append(Token(TokenType.EOF, ""))
        return tokens


class NodeType(Enum):
    """AST node types."""

    NUMBER = auto()
    VARIABLE = auto()
    BOOLEAN = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    FUNCTION_CALL = auto()


@dataclass
class ASTNode:
    """AST node."""

    type: NodeType
    value: any = None
    left: "ASTNode | None" = None
    right: "ASTNode | None" = None
    operator: str | None = None
    name: str | None = None
    args: list["ASTNode"] | None = None


class Parser:
    """Expression parser using recursive descent."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        if self.pos >= len(self.tokens):
            return Token(TokenType.EOF, "")
        return self.tokens[self.pos]

    def advance(self) -> Token:
        token = self.peek()
        self.pos += 1
        return token

    def parse(self) -> ASTNode:
        """Parse expression into AST."""
        return self.or_expr()

    def or_expr(self) -> ASTNode:
        """Parse OR expression."""
        left = self.and_expr()

        while self.peek().type == TokenType.OR:
            self.advance()
            right = self.and_expr()
            left = ASTNode(NodeType.BINARY_OP, operator="or", left=left, right=right)

        return left

    def and_expr(self) -> ASTNode:
        """Parse AND expression."""
        left = self.not_expr()

        while self.peek().type == TokenType.AND:
            self.advance()
            right = self.not_expr()
            left = ASTNode(NodeType.BINARY_OP, operator="and", left=left, right=right)

        return left

    def not_expr(self) -> ASTNode:
        """Parse NOT expression."""
        if self.peek().type == TokenType.NOT:
            self.advance()
            operand = self.not_expr()
            return ASTNode(NodeType.UNARY_OP, operator="not", right=operand)

        return self.comparison()

    def comparison(self) -> ASTNode:
        """Parse comparison expression."""
        left = self.additive()

        while self.peek().type in (
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.LT,
            TokenType.LE,
            TokenType.GT,
            TokenType.GE,
        ):
            op_token = self.advance()
            op_map = {
                TokenType.EQ: "==",
                TokenType.NEQ: "!=",
                TokenType.LT: "<",
                TokenType.LE: "<=",
                TokenType.GT: ">",
                TokenType.GE: ">=",
            }
            right = self.additive()
            left = ASTNode(
                NodeType.BINARY_OP, operator=op_map[op_token.type], left=left, right=right
            )

        return left

    def additive(self) -> ASTNode:
        """Parse additive expression."""
        left = self.multiplicative()

        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.multiplicative()
            op = "+" if op_token.type == TokenType.PLUS else "-"
            left = ASTNode(NodeType.BINARY_OP, operator=op, left=left, right=right)

        return left

    def multiplicative(self) -> ASTNode:
        """Parse multiplicative expression."""
        left = self.power()

        while self.peek().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self.advance()
            right = self.power()
            op_map = {TokenType.STAR: "*", TokenType.SLASH: "/", TokenType.PERCENT: "%"}
            left = ASTNode(
                NodeType.BINARY_OP, operator=op_map[op_token.type], left=left, right=right
            )

        return left

    def power(self) -> ASTNode:
        """Parse power expression (right associative)."""
        left = self.unary()

        if self.peek().type == TokenType.CARET:
            self.advance()
            right = self.power()
            return ASTNode(NodeType.BINARY_OP, operator="^", left=left, right=right)

        return left

    def unary(self) -> ASTNode:
        """Parse unary expression."""
        if self.peek().type == TokenType.MINUS:
            self.advance()
            operand = self.unary()
            return ASTNode(NodeType.UNARY_OP, operator="-", right=operand)

        if self.peek().type == TokenType.PLUS:
            self.advance()
            return self.unary()

        return self.primary()

    def primary(self) -> ASTNode:
        """Parse primary expression."""
        token = self.peek()

        if token.type == TokenType.NUMBER:
            self.advance()
            return ASTNode(NodeType.NUMBER, value=token.value)

        if token.type in (TokenType.TRUE, TokenType.FALSE):
            self.advance()
            return ASTNode(NodeType.BOOLEAN, value=token.value)

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            name = token.value

            if self.peek().type == TokenType.LPAREN:
                self.advance()
                args = []

                if self.peek().type != TokenType.RPAREN:
                    args.append(self.parse())
                    while self.peek().type == TokenType.COMMA:
                        self.advance()
                        args.append(self.parse())

                if self.peek().type == TokenType.RPAREN:
                    self.advance()

                return ASTNode(NodeType.FUNCTION_CALL, name=name, args=args)

            return ASTNode(NodeType.VARIABLE, name=name)

        if token.type == TokenType.LPAREN:
            self.advance()
            node = self.parse()
            if self.peek().type == TokenType.RPAREN:
                self.advance()
            return node

        return ASTNode(NodeType.NUMBER, value=0)


class Evaluator:
    """Expression evaluator."""

    BUILTIN_FUNCTIONS = {
        "abs": lambda args: abs(args[0]),
        "min": lambda args: min(args),
        "max": lambda args: max(args),
        "sqrt": lambda args: math.sqrt(args[0]),
        "sin": lambda args: math.sin(args[0]),
        "cos": lambda args: math.cos(args[0]),
        "tan": lambda args: math.tan(args[0]),
        "log": lambda args: math.log(args[0]) if len(args) == 1 else math.log(args[0], args[1]),
        "log10": lambda args: math.log10(args[0]),
        "exp": lambda args: math.exp(args[0]),
        "floor": lambda args: math.floor(args[0]),
        "ceil": lambda args: math.ceil(args[0]),
        "round": lambda args: round(args[0]) if len(args) == 1 else round(args[0], int(args[1])),
        "pow": lambda args: math.pow(args[0], args[1]),
    }

    BUILTIN_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    def __init__(self, variables: dict[str, float] | None = None):
        self.variables = variables or {}

    def evaluate(self, node: ASTNode) -> float | bool:
        """Evaluate AST node."""
        if node.type == NodeType.NUMBER:
            return node.value

        if node.type == NodeType.BOOLEAN:
            return node.value

        if node.type == NodeType.VARIABLE:
            name = node.name
            if name in self.variables:
                return self.variables[name]
            if name in self.BUILTIN_CONSTANTS:
                return self.BUILTIN_CONSTANTS[name]
            raise ValueError(f"Unknown variable: {name}")

        if node.type == NodeType.UNARY_OP:
            operand = self.evaluate(node.right)
            if node.operator == "-":
                return -operand
            if node.operator == "not":
                return not operand
            raise ValueError(f"Unknown unary operator: {node.operator}")

        if node.type == NodeType.BINARY_OP:
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            if node.operator == "+":
                return left + right
            if node.operator == "-":
                return left - right
            if node.operator == "*":
                return left * right
            if node.operator == "/":
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right
            if node.operator == "%":
                return left % right
            if node.operator == "^":
                return left**right
            if node.operator == "==":
                return left == right
            if node.operator == "!=":
                return left != right
            if node.operator == "<":
                return left < right
            if node.operator == "<=":
                return left <= right
            if node.operator == ">":
                return left > right
            if node.operator == ">=":
                return left >= right
            if node.operator == "and":
                return left and right
            if node.operator == "or":
                return left or right

            raise ValueError(f"Unknown operator: {node.operator}")

        if node.type == NodeType.FUNCTION_CALL:
            name = node.name.lower()
            args = [self.evaluate(arg) for arg in node.args]

            if name in self.BUILTIN_FUNCTIONS:
                return self.BUILTIN_FUNCTIONS[name](args)

            raise ValueError(f"Unknown function: {name}")

        raise ValueError(f"Unknown node type: {node.type}")


def tokenize(expr: str) -> list[Token]:
    """Tokenize expression string."""
    lexer = Lexer(expr)
    return lexer.tokenize()


def parse(tokens: list[Token]) -> ASTNode:
    """Parse tokens into AST."""
    parser = Parser(tokens)
    return parser.parse()


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float | bool:
    """Evaluate expression string."""
    tokens = tokenize(expr)
    ast = parse(tokens)
    evaluator = Evaluator(variables)
    return evaluator.evaluate(ast)


def format_result(value: float | bool) -> str:
    """Format result for display."""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Expression evaluator")
    parser.add_argument("expression", nargs="?", help="Expression to evaluate")
    parser.add_argument("--var", "-v", action="append", help="Variable assignment (name=value)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    variables = {}
    if args.var:
        for v in args.var:
            name, value = v.split("=", 1)
            variables[name.strip()] = float(value.strip())

    if args.interactive:
        print("Expression Evaluator (type 'quit' to exit)")
        while True:
            try:
                line = input("> ").strip()
                if line.lower() in ("quit", "exit", "q"):
                    break
                if not line:
                    continue

                if "=" in line and not any(op in line for op in ["==", "!=", "<=", ">="]):
                    parts = line.split("=", 1)
                    if parts[0].strip().isidentifier():
                        name = parts[0].strip()
                        expr = parts[1].strip()
                        variables[name] = evaluate(expr, variables)
                        print(f"{name} = {format_result(variables[name])}")
                        continue

                result = evaluate(line, variables)
                print(format_result(result))
            except ValueError as e:
                print(f"Error: {e}")
            except (KeyboardInterrupt, EOFError):
                break
        return 0

    if args.expression:
        expr = args.expression
    else:
        expr = sys.stdin.read().strip()

    try:
        result = evaluate(expr, variables)
        print(format_result(result))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
