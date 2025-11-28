"""Simple Regex Engine CLI.

Demonstrates regex pattern matching using NFA (Non-deterministic Finite Automaton).
"""

import sys
from dataclasses import dataclass, field


@dataclass(eq=False)
class NFAState:
    """NFA state."""

    id: int
    is_accept: bool = False
    epsilon_transitions: list["NFAState"] = field(default_factory=list)
    char_transitions: dict[str, list["NFAState"]] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Make hashable by id."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Compare by id."""
        if not isinstance(other, NFAState):
            return False
        return self.id == other.id

    def add_epsilon(self, state: "NFAState") -> None:
        """Add epsilon transition."""
        self.epsilon_transitions.append(state)

    def add_char(self, char: str, state: "NFAState") -> None:
        """Add character transition."""
        if char not in self.char_transitions:
            self.char_transitions[char] = []
        self.char_transitions[char].append(state)


@dataclass
class NFA:
    """Non-deterministic Finite Automaton."""

    start: NFAState
    accept: NFAState


class RegexCompiler:
    """Compile regex pattern to NFA."""

    def __init__(self) -> None:
        self.state_id = 0

    def new_state(self, is_accept: bool = False) -> NFAState:
        """Create new state."""
        state = NFAState(self.state_id, is_accept)
        self.state_id += 1
        return state

    def compile(self, pattern: str) -> NFA:
        """Compile regex pattern to NFA."""
        self.state_id = 0
        nfa, pos = self._parse_expr(pattern, 0)
        return nfa

    def _parse_expr(self, pattern: str, pos: int) -> tuple[NFA, int]:
        """Parse expression (handles alternation)."""
        nfa, pos = self._parse_concat(pattern, pos)

        while pos < len(pattern) and pattern[pos] == "|":
            pos += 1
            right_nfa, pos = self._parse_concat(pattern, pos)
            nfa = self._alternation(nfa, right_nfa)

        return nfa, pos

    def _parse_concat(self, pattern: str, pos: int) -> tuple[NFA, int]:
        """Parse concatenation."""
        nfa = None

        while pos < len(pattern) and pattern[pos] not in "|)":
            atom_nfa, pos = self._parse_atom(pattern, pos)

            # Check for quantifiers
            if pos < len(pattern) and pattern[pos] in "*+?":
                quantifier = pattern[pos]
                pos += 1
                if quantifier == "*":
                    atom_nfa = self._star(atom_nfa)
                elif quantifier == "+":
                    atom_nfa = self._plus(atom_nfa)
                elif quantifier == "?":
                    atom_nfa = self._question(atom_nfa)

            if nfa is None:
                nfa = atom_nfa
            else:
                nfa = self._concatenation(nfa, atom_nfa)

        if nfa is None:
            start = self.new_state()
            accept = self.new_state(True)
            start.add_epsilon(accept)
            nfa = NFA(start, accept)

        return nfa, pos

    def _parse_atom(self, pattern: str, pos: int) -> tuple[NFA, int]:
        """Parse single atom (char, group, or character class)."""
        if pos >= len(pattern):
            start = self.new_state()
            accept = self.new_state(True)
            start.add_epsilon(accept)
            return NFA(start, accept), pos

        char = pattern[pos]

        if char == "(":
            pos += 1
            nfa, pos = self._parse_expr(pattern, pos)
            if pos < len(pattern) and pattern[pos] == ")":
                pos += 1
            return nfa, pos

        if char == "[":
            pos += 1
            chars = []
            negated = False
            if pos < len(pattern) and pattern[pos] == "^":
                negated = True
                pos += 1
            while pos < len(pattern) and pattern[pos] != "]":
                if pos + 2 < len(pattern) and pattern[pos + 1] == "-":
                    start_char = pattern[pos]
                    end_char = pattern[pos + 2]
                    for c in range(ord(start_char), ord(end_char) + 1):
                        chars.append(chr(c))
                    pos += 3
                else:
                    chars.append(pattern[pos])
                    pos += 1
            if pos < len(pattern):
                pos += 1

            return self._char_class(chars, negated), pos

        if char == ".":
            pos += 1
            return self._dot(), pos

        if char == "\\":
            pos += 1
            if pos < len(pattern):
                escaped = pattern[pos]
                pos += 1
                return self._char(escaped), pos

        pos += 1
        return self._char(char), pos

    def _char(self, c: str) -> NFA:
        """Create NFA for single character."""
        start = self.new_state()
        accept = self.new_state(True)
        start.add_char(c, accept)
        return NFA(start, accept)

    def _dot(self) -> NFA:
        """Create NFA for any character (.)."""
        start = self.new_state()
        accept = self.new_state(True)
        start.add_char(".", accept)
        return NFA(start, accept)

    def _char_class(self, chars: list[str], negated: bool = False) -> NFA:
        """Create NFA for character class."""
        start = self.new_state()
        accept = self.new_state(True)
        if negated:
            start.add_char(f"^{''.join(chars)}", accept)
        else:
            for c in chars:
                start.add_char(c, accept)
        return NFA(start, accept)

    def _concatenation(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """Concatenate two NFAs."""
        nfa1.accept.is_accept = False
        nfa1.accept.add_epsilon(nfa2.start)
        return NFA(nfa1.start, nfa2.accept)

    def _alternation(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """Create alternation of two NFAs."""
        start = self.new_state()
        accept = self.new_state(True)

        start.add_epsilon(nfa1.start)
        start.add_epsilon(nfa2.start)

        nfa1.accept.is_accept = False
        nfa1.accept.add_epsilon(accept)

        nfa2.accept.is_accept = False
        nfa2.accept.add_epsilon(accept)

        return NFA(start, accept)

    def _star(self, nfa: NFA) -> NFA:
        """Create Kleene star (zero or more)."""
        start = self.new_state()
        accept = self.new_state(True)

        start.add_epsilon(nfa.start)
        start.add_epsilon(accept)

        nfa.accept.is_accept = False
        nfa.accept.add_epsilon(nfa.start)
        nfa.accept.add_epsilon(accept)

        return NFA(start, accept)

    def _plus(self, nfa: NFA) -> NFA:
        """Create one or more."""
        start = self.new_state()
        accept = self.new_state(True)

        start.add_epsilon(nfa.start)

        nfa.accept.is_accept = False
        nfa.accept.add_epsilon(nfa.start)
        nfa.accept.add_epsilon(accept)

        return NFA(start, accept)

    def _question(self, nfa: NFA) -> NFA:
        """Create zero or one."""
        start = self.new_state()
        accept = self.new_state(True)

        start.add_epsilon(nfa.start)
        start.add_epsilon(accept)

        nfa.accept.is_accept = False
        nfa.accept.add_epsilon(accept)

        return NFA(start, accept)


class RegexMatcher:
    """Match strings against compiled NFA."""

    def __init__(self, nfa: NFA) -> None:
        self.nfa = nfa

    def match(self, text: str) -> bool:
        """Check if text matches the pattern."""
        current_states = self._epsilon_closure({self.nfa.start})

        for char in text:
            next_states: set[NFAState] = set()
            for state in current_states:
                for trans_char, targets in state.char_transitions.items():
                    if trans_char == char or trans_char == ".":
                        next_states.update(targets)
                    elif trans_char.startswith("^"):
                        if char not in trans_char[1:]:
                            next_states.update(targets)

            current_states = self._epsilon_closure(next_states)

        return any(state.is_accept for state in current_states)

    def _epsilon_closure(self, states: set[NFAState]) -> set[NFAState]:
        """Compute epsilon closure of state set."""
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            for target in state.epsilon_transitions:
                if target not in closure:
                    closure.add(target)
                    stack.append(target)

        return closure


class Regex:
    """High-level regex interface."""

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        compiler = RegexCompiler()
        self.nfa = compiler.compile(pattern)
        self.matcher = RegexMatcher(self.nfa)

    def match(self, text: str) -> bool:
        """Check if text matches pattern exactly."""
        return self.matcher.match(text)

    def search(self, text: str) -> tuple[int, int] | None:
        """Find first match in text."""
        for start in range(len(text)):
            for end in range(start + 1, len(text) + 1):
                if self.matcher.match(text[start:end]):
                    return start, end
        return None

    def find_all(self, text: str) -> list[str]:
        """Find all non-overlapping matches."""
        matches = []
        pos = 0

        while pos < len(text):
            best_match = None
            for end in range(pos + 1, len(text) + 1):
                if self.matcher.match(text[pos:end]):
                    best_match = text[pos:end]

            if best_match:
                matches.append(best_match)
                pos += len(best_match)
            else:
                pos += 1

        return matches


def regex_match(pattern: str, text: str) -> bool:
    """Check if text matches regex pattern."""
    return Regex(pattern).match(text)


def regex_search(pattern: str, text: str) -> tuple[int, int] | None:
    """Search for pattern in text."""
    return Regex(pattern).search(text)


def regex_find_all(pattern: str, text: str) -> list[str]:
    """Find all matches of pattern in text."""
    return Regex(pattern).find_all(text)


def simulate_regex(operations: list[str]) -> list[str]:
    """Simulate regex operations."""
    results = []
    current_regex: Regex | None = None

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "compile":
            current_regex = Regex(parts[1])
            results.append("ok")
        elif cmd == "match" and current_regex:
            results.append("1" if current_regex.match(parts[1]) else "0")
        elif cmd == "search" and current_regex:
            result = current_regex.search(parts[1])
            if result:
                results.append(f"{result[0]},{result[1]}")
            else:
                results.append("none")
        elif cmd == "find_all" and current_regex:
            matches = current_regex.find_all(parts[1])
            results.append(",".join(matches) if matches else "none")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: state_regex_cli.py <pattern> <text>")
        print("  or:  state_regex_cli.py match <pattern> <text>")
        print("  or:  state_regex_cli.py search <pattern> <text>")
        return 1

    cmd = sys.argv[1]

    if cmd == "match":
        pattern, text = sys.argv[2], sys.argv[3]
        result = regex_match(pattern, text)
        print("Match" if result else "No match")
    elif cmd == "search":
        pattern, text = sys.argv[2], sys.argv[3]
        result = regex_search(pattern, text)
        if result:
            print(f"Found at {result[0]}-{result[1]}: {text[result[0] : result[1]]}")
        else:
            print("No match")
    elif cmd == "find":
        pattern, text = sys.argv[2], sys.argv[3]
        matches = regex_find_all(pattern, text)
        print(f"Found {len(matches)} matches: {matches}")
    else:
        pattern, text = cmd, sys.argv[2]
        result = regex_match(pattern, text)
        print("Match" if result else "No match")

    return 0


if __name__ == "__main__":
    sys.exit(main())
