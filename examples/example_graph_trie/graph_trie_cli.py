#!/usr/bin/env python3
"""Trie (Prefix Tree) CLI.

Trie data structure for string operations.
"""

import argparse
import sys


class TrieNode:
    """Node in a Trie."""

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_end: bool = False
        self.count: int = 0  # Number of words ending here
        self.prefix_count: int = 0  # Number of words with this prefix


class Trie:
    """Trie (Prefix Tree) implementation."""

    def __init__(self) -> None:
        self.root: TrieNode = TrieNode()
        self._word_count: int = 0

    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.prefix_count += 1
        node.is_end = True
        node.count += 1
        self._word_count += 1

    def search(self, word: str) -> bool:
        """Check if exact word exists."""
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """Check if any word starts with prefix."""
        return self._find_node(prefix) is not None

    def _find_node(self, prefix: str) -> TrieNode | None:
        """Find node for given prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def count_words_with_prefix(self, prefix: str) -> int:
        """Count words starting with prefix."""
        node = self._find_node(prefix)
        return node.prefix_count if node else 0

    def get_words_with_prefix(self, prefix: str) -> list[str]:
        """Get all words starting with prefix."""
        node = self._find_node(prefix)
        if node is None:
            return []

        words: list[str] = []
        self._collect_words(node, prefix, words)
        return words

    def _collect_words(self, node: TrieNode, prefix: str, words: list[str]) -> None:
        """Collect all words from node."""
        if node.is_end:
            words.extend([prefix] * node.count)
        for char, child in sorted(node.children.items()):
            self._collect_words(child, prefix + char, words)

    def delete(self, word: str) -> bool:
        """Delete a word from trie."""
        if not self.search(word):
            return False

        node = self.root
        for char in word:
            node = node.children[char]
            node.prefix_count -= 1

        node.count -= 1
        if node.count == 0:
            node.is_end = False

        self._word_count -= 1
        return True

    def word_count(self) -> int:
        """Get total word count."""
        return self._word_count

    def all_words(self) -> list[str]:
        """Get all words in trie."""
        words: list[str] = []
        self._collect_words(self.root, "", words)
        return words


def longest_common_prefix(words: list[str]) -> str:
    """Find longest common prefix using trie."""
    if not words:
        return ""

    trie = Trie()
    for word in words:
        trie.insert(word)

    prefix: list[str] = []
    node = trie.root

    while len(node.children) == 1 and not node.is_end:
        char = list(node.children.keys())[0]
        prefix.append(char)
        node = node.children[char]

    return "".join(prefix)


def autocomplete(trie: Trie, prefix: str, limit: int = 10) -> list[str]:
    """Get autocomplete suggestions."""
    words = trie.get_words_with_prefix(prefix)
    return sorted(set(words))[:limit]


def spell_check(trie: Trie, word: str) -> list[str]:
    """Simple spell check - find words with edit distance 1."""
    suggestions: set[str] = set()

    # Deletions
    for i in range(len(word)):
        candidate = word[:i] + word[i + 1 :]
        if trie.search(candidate):
            suggestions.add(candidate)

    # Insertions
    for i in range(len(word) + 1):
        for c in "abcdefghijklmnopqrstuvwxyz":
            candidate = word[:i] + c + word[i:]
            if trie.search(candidate):
                suggestions.add(candidate)

    # Substitutions
    for i in range(len(word)):
        for c in "abcdefghijklmnopqrstuvwxyz":
            if c != word[i]:
                candidate = word[:i] + c + word[i + 1 :]
                if trie.search(candidate):
                    suggestions.add(candidate)

    return sorted(suggestions)


def word_break(trie: Trie, s: str) -> bool:
    """Check if string can be segmented into dictionary words."""
    n = len(s)
    dp: list[bool] = [False] * (n + 1)
    dp[0] = True

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and trie.search(s[j:i]):
                dp[i] = True
                break

    return dp[n]


def word_search_2d(board: list[list[str]], words: list[str]) -> list[str]:
    """Find words from dictionary in 2D board."""
    if not board or not board[0]:
        return []

    trie = Trie()
    for word in words:
        trie.insert(word)

    rows, cols = len(board), len(board[0])
    found: set[str] = set()

    def dfs(r: int, c: int, node: TrieNode, path: str) -> None:
        if node.is_end:
            found.add(path)

        if r < 0 or r >= rows or c < 0 or c >= cols:
            return

        char = board[r][c]
        if char not in node.children:
            return

        board[r][c] = "#"  # Mark visited
        next_node = node.children[char]

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            dfs(r + dr, c + dc, next_node, path + char)

        board[r][c] = char  # Restore

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, "")

    return sorted(found)


def count_distinct_substrings(s: str) -> int:
    """Count distinct substrings using trie."""
    trie = Trie()
    count = 0

    for i in range(len(s)):
        node = trie.root
        for j in range(i, len(s)):
            char = s[j]
            if char not in node.children:
                node.children[char] = TrieNode()
                count += 1
            node = node.children[char]

    return count


def simulate_trie(ops: list[str]) -> list[str]:
    """Simulate trie operations."""
    trie = Trie()
    results: list[str] = []

    for op in ops:
        parts = op.split(":")
        cmd = parts[0]

        if cmd == "insert":
            trie.insert(parts[1])
        elif cmd == "search":
            results.append("1" if trie.search(parts[1]) else "0")
        elif cmd == "prefix":
            results.append("1" if trie.starts_with(parts[1]) else "0")
        elif cmd == "count":
            results.append(str(trie.count_words_with_prefix(parts[1])))
        elif cmd == "words":
            words = trie.get_words_with_prefix(parts[1])
            results.append(",".join(words) if words else "none")
        elif cmd == "delete":
            results.append("1" if trie.delete(parts[1]) else "0")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Trie CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # ops
    ops_p = subparsers.add_parser("ops", help="Trie operations")
    ops_p.add_argument("ops", nargs="+")

    # lcp
    lcp_p = subparsers.add_parser("lcp", help="Longest common prefix")
    lcp_p.add_argument("words", nargs="+")

    # autocomplete
    auto_p = subparsers.add_parser("autocomplete", help="Autocomplete")
    auto_p.add_argument("prefix")
    auto_p.add_argument("words", nargs="+")

    # substrings
    sub_p = subparsers.add_parser("substrings", help="Count distinct substrings")
    sub_p.add_argument("string")

    args = parser.parse_args()

    if args.command == "ops":
        results = simulate_trie(args.ops)
        print(f"Results: {results}")

    elif args.command == "lcp":
        result = longest_common_prefix(args.words)
        print(f"LCP: '{result}'")

    elif args.command == "autocomplete":
        trie = Trie()
        for word in args.words:
            trie.insert(word)
        suggestions = autocomplete(trie, args.prefix)
        print(f"Suggestions: {suggestions}")

    elif args.command == "substrings":
        count = count_distinct_substrings(args.string)
        print(f"Distinct substrings: {count}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
