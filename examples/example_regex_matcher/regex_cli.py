#!/usr/bin/env python3
"""Regex Matcher CLI.

Simple regex engine implementation for educational purposes.
"""

import argparse
import sys
from dataclasses import dataclass
from enum import Enum, auto


class NodeType(Enum):
    """AST node types."""

    LITERAL = auto()
    DOT = auto()
    STAR = auto()
    PLUS = auto()
    QUESTION = auto()
    CONCAT = auto()
    ALTERNATION = auto()
    GROUP = auto()
    CHAR_CLASS = auto()
    ANCHOR_START = auto()
    ANCHOR_END = auto()


@dataclass
class Node:
    """Regex AST node."""

    type: NodeType
    value: str | None = None
    children: list["Node"] | None = None
    negated: bool = False


class Lexer:
    """Regex tokenizer."""

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.pos = 0

    def peek(self) -> str:
        if self.pos >= len(self.pattern):
            return ""
        return self.pattern[self.pos]

    def advance(self) -> str:
        char = self.peek()
        self.pos += 1
        return char


class Parser:
    """Regex parser."""

    def __init__(self, pattern: str):
        self.lexer = Lexer(pattern)

    def parse(self) -> Node:
        """Parse pattern into AST."""
        return self.alternation()

    def alternation(self) -> Node:
        """Parse alternation (|)."""
        left = self.concatenation()

        if self.lexer.peek() == "|":
            self.lexer.advance()
            right = self.alternation()
            return Node(NodeType.ALTERNATION, children=[left, right])

        return left

    def concatenation(self) -> Node:
        """Parse concatenation."""
        nodes = []

        while self.lexer.peek() and self.lexer.peek() not in "|)":
            nodes.append(self.quantifier())

        if not nodes:
            return Node(NodeType.LITERAL, value="")
        if len(nodes) == 1:
            return nodes[0]

        result = nodes[0]
        for node in nodes[1:]:
            result = Node(NodeType.CONCAT, children=[result, node])

        return result

    def quantifier(self) -> Node:
        """Parse quantifiers (*, +, ?)."""
        node = self.atom()

        if self.lexer.peek() == "*":
            self.lexer.advance()
            return Node(NodeType.STAR, children=[node])

        if self.lexer.peek() == "+":
            self.lexer.advance()
            return Node(NodeType.PLUS, children=[node])

        if self.lexer.peek() == "?":
            self.lexer.advance()
            return Node(NodeType.QUESTION, children=[node])

        return node

    def atom(self) -> Node:
        """Parse atoms."""
        char = self.lexer.peek()

        if char == "(":
            self.lexer.advance()
            node = self.alternation()
            if self.lexer.peek() == ")":
                self.lexer.advance()
            return Node(NodeType.GROUP, children=[node])

        if char == "[":
            return self.char_class()

        if char == ".":
            self.lexer.advance()
            return Node(NodeType.DOT)

        if char == "^":
            self.lexer.advance()
            return Node(NodeType.ANCHOR_START)

        if char == "$":
            self.lexer.advance()
            return Node(NodeType.ANCHOR_END)

        if char == "\\":
            self.lexer.advance()
            escaped = self.lexer.advance()
            return Node(NodeType.LITERAL, value=escaped)

        if char:
            self.lexer.advance()
            return Node(NodeType.LITERAL, value=char)

        return Node(NodeType.LITERAL, value="")

    def char_class(self) -> Node:
        """Parse character class [...]."""
        self.lexer.advance()  # [
        negated = False
        chars = []

        if self.lexer.peek() == "^":
            negated = True
            self.lexer.advance()

        while self.lexer.peek() and self.lexer.peek() != "]":
            char = self.lexer.advance()
            if self.lexer.peek() == "-" and self.lexer.pos + 1 < len(self.lexer.pattern):
                self.lexer.advance()  # -
                end_char = self.lexer.advance()
                # Expand range
                for c in range(ord(char), ord(end_char) + 1):
                    chars.append(chr(c))
            else:
                chars.append(char)

        if self.lexer.peek() == "]":
            self.lexer.advance()

        return Node(NodeType.CHAR_CLASS, value="".join(chars), negated=negated)


def match_node(node: Node, text: str, pos: int) -> list[int]:
    """Match node against text starting at pos. Returns list of end positions."""
    if node.type == NodeType.LITERAL:
        if pos < len(text) and text[pos : pos + len(node.value or "")] == node.value:
            return [pos + len(node.value or "")]
        if not node.value:
            return [pos]
        return []

    if node.type == NodeType.DOT:
        if pos < len(text):
            return [pos + 1]
        return []

    if node.type == NodeType.CHAR_CLASS:
        if pos < len(text):
            in_class = text[pos] in (node.value or "")
            if (in_class and not node.negated) or (not in_class and node.negated):
                return [pos + 1]
        return []

    if node.type == NodeType.ANCHOR_START:
        if pos == 0:
            return [0]
        return []

    if node.type == NodeType.ANCHOR_END:
        if pos == len(text):
            return [pos]
        return []

    if node.type == NodeType.STAR:
        # Zero or more
        child = node.children[0]
        results = [pos]  # Zero matches
        current = [pos]

        while current:
            new_positions = []
            for p in current:
                for np in match_node(child, text, p):
                    if np not in results:
                        results.append(np)
                        new_positions.append(np)
            current = new_positions

        return results

    if node.type == NodeType.PLUS:
        # One or more
        child = node.children[0]
        first = match_node(child, text, pos)
        if not first:
            return []

        results = list(first)
        current = list(first)

        while current:
            new_positions = []
            for p in current:
                for np in match_node(child, text, p):
                    if np not in results:
                        results.append(np)
                        new_positions.append(np)
            current = new_positions

        return results

    if node.type == NodeType.QUESTION:
        # Zero or one
        child = node.children[0]
        results = [pos]  # Zero matches
        results.extend(match_node(child, text, pos))
        return list(set(results))

    if node.type == NodeType.CONCAT:
        left, right = node.children[0], node.children[1]
        left_matches = match_node(left, text, pos)
        results = []
        for lp in left_matches:
            results.extend(match_node(right, text, lp))
        return results

    if node.type == NodeType.ALTERNATION:
        left, right = node.children[0], node.children[1]
        results = match_node(left, text, pos)
        results.extend(match_node(right, text, pos))
        return list(set(results))

    if node.type == NodeType.GROUP:
        return match_node(node.children[0], text, pos)

    return []


def match(pattern: str, text: str) -> bool:
    """Check if pattern matches entire text."""
    parser = Parser(pattern)
    ast = parser.parse()

    end_positions = match_node(ast, text, 0)
    return len(text) in end_positions


def search(pattern: str, text: str) -> tuple[int, int] | None:
    """Find first match in text. Returns (start, end) or None."""
    parser = Parser(pattern)
    ast = parser.parse()

    for start in range(len(text) + 1):
        end_positions = match_node(ast, text, start)
        if end_positions:
            return start, max(end_positions)

    return None


def find_all(pattern: str, text: str) -> list[tuple[int, int]]:
    """Find all non-overlapping matches."""
    parser = Parser(pattern)
    ast = parser.parse()

    matches = []
    pos = 0

    while pos <= len(text):
        end_positions = match_node(ast, text, pos)
        if end_positions:
            end = max(end_positions)
            if end > pos:
                matches.append((pos, end))
                pos = end
            else:
                pos += 1
        else:
            pos += 1

    return matches


def replace(pattern: str, text: str, replacement: str) -> str:
    """Replace all matches with replacement."""
    matches = find_all(pattern, text)

    if not matches:
        return text

    result = []
    last_end = 0

    for start, end in matches:
        result.append(text[last_end:start])
        result.append(replacement)
        last_end = end

    result.append(text[last_end:])
    return "".join(result)


def split(pattern: str, text: str) -> list[str]:
    """Split text by pattern."""
    matches = find_all(pattern, text)

    if not matches:
        return [text]

    result = []
    last_end = 0

    for start, end in matches:
        result.append(text[last_end:start])
        last_end = end

    result.append(text[last_end:])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple regex matcher")
    parser.add_argument("pattern", help="Regex pattern")
    parser.add_argument("text", nargs="?", help="Text to match")
    parser.add_argument(
        "--mode",
        choices=["match", "search", "findall", "replace", "split"],
        default="match",
        help="Operation mode",
    )
    parser.add_argument("--replacement", "-r", help="Replacement string")

    args = parser.parse_args()

    if not args.text:
        text = sys.stdin.read().strip()
    else:
        text = args.text

    if args.mode == "match":
        if match(args.pattern, text):
            print("Match")
            return 0
        print("No match")
        return 1

    elif args.mode == "search":
        result = search(args.pattern, text)
        if result:
            start, end = result
            print(f"Found at [{start}:{end}]: {text[start:end]!r}")
            return 0
        print("Not found")
        return 1

    elif args.mode == "findall":
        matches = find_all(args.pattern, text)
        for start, end in matches:
            print(f"[{start}:{end}]: {text[start:end]!r}")
        print(f"Total: {len(matches)} matches")

    elif args.mode == "replace":
        repl = args.replacement or ""
        result = replace(args.pattern, text, repl)
        print(result)

    elif args.mode == "split":
        parts = split(args.pattern, text)
        for i, part in enumerate(parts):
            print(f"{i}: {part!r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
