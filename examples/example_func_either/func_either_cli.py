"""Either Monad CLI.

Demonstrates the Either monad for error handling.
"""

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

L = TypeVar("L")  # Left (error) type
R = TypeVar("R")  # Right (success) type
T = TypeVar("T")
U = TypeVar("U")


class Either(ABC, Generic[L, R]):
    """Either monad - represents success (Right) or failure (Left)."""

    @abstractmethod
    def is_left(self) -> bool:
        """Check if this is a Left."""
        pass

    @abstractmethod
    def is_right(self) -> bool:
        """Check if this is a Right."""
        pass

    @abstractmethod
    def map(self, f: Callable[[R], T]) -> "Either[L, T]":
        """Apply function to Right value."""
        pass

    @abstractmethod
    def map_left(self, f: Callable[[L], T]) -> "Either[T, R]":
        """Apply function to Left value."""
        pass

    @abstractmethod
    def flat_map(self, f: Callable[[R], "Either[L, T]"]) -> "Either[L, T]":
        """Chain computations that may fail."""
        pass

    @abstractmethod
    def get_or(self, default: R) -> R:
        """Get Right value or default."""
        pass

    @abstractmethod
    def get_or_else(self, f: Callable[[L], R]) -> R:
        """Get Right value or compute from Left."""
        pass

    @abstractmethod
    def fold(self, on_left: Callable[[L], T], on_right: Callable[[R], T]) -> T:
        """Fold both cases to single value."""
        pass

    @abstractmethod
    def swap(self) -> "Either[R, L]":
        """Swap Left and Right."""
        pass

    @abstractmethod
    def to_option(self) -> R | None:
        """Convert to optional (Right becomes Some)."""
        pass


@dataclass(frozen=True)
class Left(Either[L, R]):
    """Left case - represents failure/error."""

    value: L

    def is_left(self) -> bool:
        return True

    def is_right(self) -> bool:
        return False

    def map(self, f: Callable[[R], T]) -> Either[L, T]:
        return Left(self.value)

    def map_left(self, f: Callable[[L], T]) -> Either[T, R]:
        return Left(f(self.value))

    def flat_map(self, f: Callable[[R], Either[L, T]]) -> Either[L, T]:
        return Left(self.value)

    def get_or(self, default: R) -> R:
        return default

    def get_or_else(self, f: Callable[[L], R]) -> R:
        return f(self.value)

    def fold(self, on_left: Callable[[L], T], on_right: Callable[[R], T]) -> T:
        return on_left(self.value)

    def swap(self) -> Either[R, L]:
        return Right(self.value)

    def to_option(self) -> R | None:
        return None

    def __repr__(self) -> str:
        return f"Left({self.value!r})"


@dataclass(frozen=True)
class Right(Either[L, R]):
    """Right case - represents success."""

    value: R

    def is_left(self) -> bool:
        return False

    def is_right(self) -> bool:
        return True

    def map(self, f: Callable[[R], T]) -> Either[L, T]:
        return Right(f(self.value))

    def map_left(self, f: Callable[[L], T]) -> Either[T, R]:
        return Right(self.value)

    def flat_map(self, f: Callable[[R], Either[L, T]]) -> Either[L, T]:
        return f(self.value)

    def get_or(self, default: R) -> R:
        return self.value

    def get_or_else(self, f: Callable[[L], R]) -> R:
        return self.value

    def fold(self, on_left: Callable[[L], T], on_right: Callable[[R], T]) -> T:
        return on_right(self.value)

    def swap(self) -> Either[R, L]:
        return Left(self.value)

    def to_option(self) -> R | None:
        return self.value

    def __repr__(self) -> str:
        return f"Right({self.value!r})"


# Constructors
def left(value: L) -> Either[L, R]:
    """Create a Left value."""
    return Left(value)


def right(value: R) -> Either[L, R]:
    """Create a Right value."""
    return Right(value)


# Error types
@dataclass(frozen=True)
class ValidationError:
    """Validation error."""

    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"


@dataclass(frozen=True)
class ParseError:
    """Parse error."""

    input: str
    reason: str

    def __str__(self) -> str:
        return f"Failed to parse '{self.input}': {self.reason}"


# Utility functions
def try_except(f: Callable[[], R]) -> Either[str, R]:
    """Wrap a function that may raise."""
    try:
        return Right(f())
    except Exception as e:
        return Left(str(e))


def parse_int(s: str) -> Either[ParseError, int]:
    """Parse string to int."""
    try:
        return Right(int(s))
    except ValueError:
        return Left(ParseError(s, "not a valid integer"))


def parse_float(s: str) -> Either[ParseError, float]:
    """Parse string to float."""
    try:
        return Right(float(s))
    except ValueError:
        return Left(ParseError(s, "not a valid float"))


def parse_positive(s: str) -> Either[str, int]:
    """Parse string to positive int."""
    return parse_int(s).flat_map(lambda n: Right(n) if n > 0 else Left(f"{n} is not positive"))


def validate_non_empty(field: str, value: str) -> Either[ValidationError, str]:
    """Validate string is non-empty."""
    if value.strip():
        return Right(value.strip())
    return Left(ValidationError(field, "cannot be empty"))


def validate_min_length(field: str, value: str, min_len: int) -> Either[ValidationError, str]:
    """Validate string minimum length."""
    if len(value) >= min_len:
        return Right(value)
    return Left(ValidationError(field, f"must be at least {min_len} characters"))


def validate_email(value: str) -> Either[ValidationError, str]:
    """Validate email format."""
    if "@" in value and "." in value.split("@")[-1]:
        return Right(value)
    return Left(ValidationError("email", "invalid email format"))


def validate_range(
    field: str, value: int, min_val: int, max_val: int
) -> Either[ValidationError, int]:
    """Validate number is in range."""
    if min_val <= value <= max_val:
        return Right(value)
    return Left(ValidationError(field, f"must be between {min_val} and {max_val}"))


# Combining Either values
def sequence(eithers: list[Either[L, R]]) -> Either[L, list[R]]:
    """Convert list of Eithers to Either of list."""
    results: list[R] = []
    for e in eithers:
        if e.is_left():
            return e  # type: ignore
        results.append(e.get_or(None))  # type: ignore
    return Right(results)


def traverse(f: Callable[[T], Either[L, R]], lst: list[T]) -> Either[L, list[R]]:
    """Map function over list, collecting into Either."""
    return sequence([f(x) for x in lst])


def partition_eithers(eithers: list[Either[L, R]]) -> tuple[list[L], list[R]]:
    """Partition list of Eithers into lefts and rights."""
    lefts: list[L] = []
    rights: list[R] = []
    for e in eithers:
        if e.is_left():
            lefts.append(e.fold(lambda x: x, lambda x: x))  # type: ignore
        else:
            rights.append(e.get_or(None))  # type: ignore
    return lefts, rights


def simulate_either(operations: list[str]) -> list[str]:
    """Simulate either operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "left":
            e = left(parts[1])
            results.append(repr(e))
        elif cmd == "right":
            e = right(int(parts[1]))
            results.append(repr(e))
        elif cmd == "parse_int":
            e = parse_int(parts[1])
            results.append(repr(e))
        elif cmd == "parse_positive":
            e = parse_positive(parts[1])
            results.append(repr(e))
        elif cmd == "validate_email":
            e = validate_email(parts[1])
            results.append(repr(e))
        elif cmd == "map":
            val, func = parts[1].split(",")
            e = right(int(val))
            if func == "double":
                e = e.map(lambda x: x * 2)
            results.append(repr(e))
        elif cmd == "get_or":
            val, default = parts[1].split(",")
            if val == "left":
                e: Either[str, int] = left("error")
            else:
                e = right(int(val))
            results.append(str(e.get_or(int(default))))
        elif cmd == "fold":
            val = parts[1]
            if val.startswith("left:"):
                e = left(val[5:])
            else:
                e = right(int(val))
            result = e.fold(lambda err: f"Error: {err}", lambda val: f"Success: {val}")
            results.append(result)

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: func_either_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "parse-int" and len(sys.argv) > 2:
        result = parse_int(sys.argv[2])
        print(f"Result: {result}")
    elif cmd == "validate-email" and len(sys.argv) > 2:
        result = validate_email(sys.argv[2])
        print(f"Result: {result}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
