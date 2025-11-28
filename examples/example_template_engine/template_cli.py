#!/usr/bin/env python3
"""Template Engine CLI.

Simple template engine with variable substitution, loops, and conditionals.
"""

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Token types."""

    TEXT = auto()
    VAR_OPEN = auto()
    VAR_CLOSE = auto()
    BLOCK_OPEN = auto()
    BLOCK_CLOSE = auto()
    IDENTIFIER = auto()
    DOT = auto()
    PIPE = auto()
    STRING = auto()


@dataclass
class Token:
    """Lexer token."""

    type: TokenType
    value: str


def tokenize(template: str) -> list[Token]:
    """Tokenize template string."""
    tokens = []
    i = 0

    while i < len(template):
        # Variable {{ }}
        if template[i : i + 2] == "{{":
            tokens.append(Token(TokenType.VAR_OPEN, "{{"))
            i += 2

            # Skip whitespace
            while i < len(template) and template[i].isspace():
                i += 1

            # Read identifier or expression
            while i < len(template) and template[i : i + 2] != "}}":
                if template[i].isalnum() or template[i] == "_":
                    start = i
                    while i < len(template) and (template[i].isalnum() or template[i] == "_"):
                        i += 1
                    tokens.append(Token(TokenType.IDENTIFIER, template[start:i]))
                elif template[i] == ".":
                    tokens.append(Token(TokenType.DOT, "."))
                    i += 1
                elif template[i] == "|":
                    tokens.append(Token(TokenType.PIPE, "|"))
                    i += 1
                elif template[i].isspace():
                    i += 1
                else:
                    i += 1

            if template[i : i + 2] == "}}":
                tokens.append(Token(TokenType.VAR_CLOSE, "}}"))
                i += 2

        # Block {% %}
        elif template[i : i + 2] == "{%":
            tokens.append(Token(TokenType.BLOCK_OPEN, "{%"))
            i += 2

            # Skip whitespace
            while i < len(template) and template[i].isspace():
                i += 1

            # Read block content
            while i < len(template) and template[i : i + 2] != "%}":
                if template[i].isalnum() or template[i] == "_":
                    start = i
                    while i < len(template) and (template[i].isalnum() or template[i] == "_"):
                        i += 1
                    tokens.append(Token(TokenType.IDENTIFIER, template[start:i]))
                elif template[i] == ".":
                    tokens.append(Token(TokenType.DOT, "."))
                    i += 1
                elif template[i] == '"' or template[i] == "'":
                    quote = template[i]
                    i += 1
                    start = i
                    while i < len(template) and template[i] != quote:
                        i += 1
                    tokens.append(Token(TokenType.STRING, template[start:i]))
                    i += 1
                elif template[i].isspace():
                    i += 1
                else:
                    i += 1

            if template[i : i + 2] == "%}":
                tokens.append(Token(TokenType.BLOCK_CLOSE, "%}"))
                i += 2

        # Regular text
        else:
            start = i
            while i < len(template) and template[i : i + 2] not in ("{{", "{%"):
                i += 1
            if i > start:
                tokens.append(Token(TokenType.TEXT, template[start:i]))

    return tokens


def resolve_var(name: str, context: dict) -> any:
    """Resolve variable from context."""
    parts = name.split(".")
    value = context

    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        elif isinstance(value, list) and part.isdigit():
            value = value[int(part)]
        else:
            return None

    return value


def apply_filter(value: any, filter_name: str) -> str:
    """Apply filter to value."""
    if filter_name == "upper":
        return str(value).upper()
    if filter_name == "lower":
        return str(value).lower()
    if filter_name == "title":
        return str(value).title()
    if filter_name == "strip":
        return str(value).strip()
    if filter_name == "length":
        return str(len(value) if hasattr(value, "__len__") else 0)
    if filter_name == "reverse":
        if isinstance(value, str):
            return value[::-1]
        if isinstance(value, list):
            return list(reversed(value))
    if filter_name == "first":
        if isinstance(value, (list, str)) and len(value) > 0:
            return value[0]
    if filter_name == "last":
        if isinstance(value, (list, str)) and len(value) > 0:
            return value[-1]
    if filter_name == "default":
        return value if value else ""
    if filter_name == "join":
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)

    return str(value)


def render(template: str, context: dict) -> str:
    """Render template with context."""
    tokens = tokenize(template)
    result = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token.type == TokenType.TEXT:
            result.append(token.value)
            i += 1

        elif token.type == TokenType.VAR_OPEN:
            i += 1
            var_name = ""
            filters = []

            while i < len(tokens) and tokens[i].type != TokenType.VAR_CLOSE:
                if tokens[i].type == TokenType.IDENTIFIER:
                    if not var_name:
                        var_name = tokens[i].value
                    elif filters:
                        pass  # Filter argument, ignore for now
                    else:
                        var_name = tokens[i].value
                elif tokens[i].type == TokenType.DOT:
                    i += 1
                    if i < len(tokens) and tokens[i].type == TokenType.IDENTIFIER:
                        var_name += "." + tokens[i].value
                elif tokens[i].type == TokenType.PIPE:
                    i += 1
                    if i < len(tokens) and tokens[i].type == TokenType.IDENTIFIER:
                        filters.append(tokens[i].value)
                i += 1

            value = resolve_var(var_name, context)
            for f in filters:
                value = apply_filter(value, f)

            result.append(str(value) if value is not None else "")

            if i < len(tokens) and tokens[i].type == TokenType.VAR_CLOSE:
                i += 1

        elif token.type == TokenType.BLOCK_OPEN:
            i += 1
            block_type = None
            block_var = None
            block_iterable = None

            while i < len(tokens) and tokens[i].type != TokenType.BLOCK_CLOSE:
                if tokens[i].type == TokenType.IDENTIFIER:
                    if block_type is None:
                        block_type = tokens[i].value
                    elif block_type == "for" and block_var is None:
                        block_var = tokens[i].value
                    elif block_type == "for" and tokens[i].value == "in":
                        pass
                    elif block_type == "for":
                        block_iterable = tokens[i].value
                    elif block_type == "if" and block_var is None:
                        block_var = tokens[i].value
                i += 1

            if i < len(tokens) and tokens[i].type == TokenType.BLOCK_CLOSE:
                i += 1

            if block_type == "for" and block_var and block_iterable:
                # Find endfor
                depth = 1
                body_start = i
                while i < len(tokens) and depth > 0:
                    if tokens[i].type == TokenType.BLOCK_OPEN:
                        # Check for for/endfor
                        j = i + 1
                        while j < len(tokens) and tokens[j].type != TokenType.BLOCK_CLOSE:
                            if tokens[j].type == TokenType.IDENTIFIER:
                                if tokens[j].value == "for":
                                    depth += 1
                                elif tokens[j].value == "endfor":
                                    depth -= 1
                                break
                            j += 1
                    i += 1

                body_end = i - 1
                # Find the actual endfor position
                while body_end > body_start:
                    if tokens[body_end].type == TokenType.BLOCK_OPEN:
                        break
                    body_end -= 1

                # Render body for each item
                items = resolve_var(block_iterable, context)
                if isinstance(items, (list, tuple)):
                    for item in items:
                        loop_context = context.copy()
                        loop_context[block_var] = item
                        body_tokens = tokens[body_start:body_end]
                        body_template = reconstruct_template(body_tokens)
                        result.append(render(body_template, loop_context))

            elif block_type == "if" and block_var:
                # Find endif
                depth = 1
                body_start = i
                while i < len(tokens) and depth > 0:
                    if tokens[i].type == TokenType.BLOCK_OPEN:
                        j = i + 1
                        while j < len(tokens) and tokens[j].type != TokenType.BLOCK_CLOSE:
                            if tokens[j].type == TokenType.IDENTIFIER:
                                if tokens[j].value == "if":
                                    depth += 1
                                elif tokens[j].value == "endif":
                                    depth -= 1
                                break
                            j += 1
                    i += 1

                body_end = i - 1
                while body_end > body_start:
                    if tokens[body_end].type == TokenType.BLOCK_OPEN:
                        break
                    body_end -= 1

                # Evaluate condition
                value = resolve_var(block_var, context)
                if value:
                    body_tokens = tokens[body_start:body_end]
                    body_template = reconstruct_template(body_tokens)
                    result.append(render(body_template, context))

            elif block_type in ("endfor", "endif"):
                pass

        else:
            i += 1

    return "".join(result)


def reconstruct_template(tokens: list[Token]) -> str:
    """Reconstruct template string from tokens."""
    result = []

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.type == TokenType.TEXT:
            result.append(token.value)
        elif token.type == TokenType.VAR_OPEN:
            result.append("{{ ")
            i += 1
            while i < len(tokens) and tokens[i].type != TokenType.VAR_CLOSE:
                if tokens[i].type == TokenType.IDENTIFIER:
                    result.append(tokens[i].value)
                elif tokens[i].type == TokenType.DOT:
                    result.append(".")
                elif tokens[i].type == TokenType.PIPE:
                    result.append(" | ")
                i += 1
            result.append(" }}")
        elif token.type == TokenType.BLOCK_OPEN:
            result.append("{% ")
            i += 1
            while i < len(tokens) and tokens[i].type != TokenType.BLOCK_CLOSE:
                if tokens[i].type == TokenType.IDENTIFIER:
                    result.append(tokens[i].value + " ")
                i += 1
            result.append("%}")

        i += 1

    return "".join(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="Template engine")
    parser.add_argument("--template", "-t", help="Template string")
    parser.add_argument("--file", "-f", help="Template file")
    parser.add_argument("--context", "-c", help="JSON context")
    parser.add_argument("--context-file", help="JSON context file")

    args = parser.parse_args()

    # Load template
    if args.file:
        with open(args.file) as f:
            template = f.read()
    elif args.template:
        template = args.template
    else:
        template = sys.stdin.read()

    # Load context
    if args.context_file:
        with open(args.context_file) as f:
            context = json.load(f)
    elif args.context:
        context = json.loads(args.context)
    else:
        context = {}

    result = render(template, context)
    print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
