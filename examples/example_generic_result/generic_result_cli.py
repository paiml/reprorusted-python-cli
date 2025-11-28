"""Generic Result/Either Pattern CLI.

Demonstrates Result type for error handling without exceptions.
"""

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")
F = TypeVar("F")


class Result(ABC, Generic[T, E]):
    """Result type representing success or failure."""

    @abstractmethod
    def is_ok(self) -> bool:
        """Check if result is Ok."""
        ...

    @abstractmethod
    def is_err(self) -> bool:
        """Check if result is Err."""
        ...

    @abstractmethod
    def unwrap(self) -> T:
        """Get Ok value or raise."""
        ...

    @abstractmethod
    def unwrap_err(self) -> E:
        """Get Err value or raise."""
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Get Ok value or return default."""
        ...

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Result[U, E]":
        """Apply function to Ok value."""
        ...

    @abstractmethod
    def map_err(self, f: Callable[[E], F]) -> "Result[T, F]":
        """Apply function to Err value."""
        ...


@dataclass
class Ok(Result[T, Any]):
    """Successful result containing a value."""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_err(self) -> Any:
        raise ValueError(f"Called unwrap_err on Ok({self.value})")

    def unwrap_or(self, default: T) -> T:
        return self.value

    def map(self, f: Callable[[T], U]) -> Result[U, Any]:
        return Ok(f(self.value))

    def map_err(self, f: Callable[[Any], F]) -> Result[T, F]:
        return Ok(self.value)

    def and_then(self, f: Callable[[T], Result[U, Any]]) -> Result[U, Any]:
        """Chain results."""
        return f(self.value)

    def or_else(self, f: Callable[[Any], Result[T, F]]) -> Result[T, Any]:
        """Return self for Ok."""
        return self


@dataclass
class Err(Result[Any, E]):
    """Error result containing an error value."""

    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> Any:
        raise ValueError(f"Called unwrap on Err({self.error})")

    def unwrap_err(self) -> E:
        return self.error

    def unwrap_or(self, default: T) -> T:
        return default

    def map(self, f: Callable[[Any], U]) -> Result[U, E]:
        return Err(self.error)

    def map_err(self, f: Callable[[E], F]) -> Result[Any, F]:
        return Err(f(self.error))

    def and_then(self, f: Callable[[Any], Result[U, E]]) -> Result[U, E]:
        """Chain results."""
        return Err(self.error)

    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Apply function on error."""
        return f(self.error)


def try_catch(f: Callable[[], T]) -> Result[T, str]:
    """Convert exception-throwing code to Result."""
    try:
        return Ok(f())
    except Exception as e:
        return Err(str(e))


def safe_divide(a: float, b: float) -> Result[float, str]:
    """Safely divide two numbers."""
    if b == 0:
        return Err("division by zero")
    return Ok(a / b)


def safe_parse_int(s: str) -> Result[int, str]:
    """Safely parse string to int."""
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"invalid integer: {s}")


def safe_parse_float(s: str) -> Result[float, str]:
    """Safely parse string to float."""
    try:
        return Ok(float(s))
    except ValueError:
        return Err(f"invalid float: {s}")


def collect_results(results: list[Result[T, E]]) -> Result[list[T], E]:
    """Collect list of Results into Result of list."""
    values: list[T] = []
    for result in results:
        if result.is_err():
            return Err(result.unwrap_err())
        values.append(result.unwrap())
    return Ok(values)


def partition_results(results: list[Result[T, E]]) -> tuple[list[T], list[E]]:
    """Partition Results into successes and failures."""
    oks: list[T] = []
    errs: list[E] = []
    for result in results:
        if result.is_ok():
            oks.append(result.unwrap())
        else:
            errs.append(result.unwrap_err())
    return oks, errs


def combine_results(r1: Result[T, E], r2: Result[U, E], f: Callable[[T, U], Any]) -> Result[Any, E]:
    """Combine two results with a function."""
    if r1.is_err():
        return Err(r1.unwrap_err())
    if r2.is_err():
        return Err(r2.unwrap_err())
    return Ok(f(r1.unwrap(), r2.unwrap()))


@dataclass
class Either(Generic[T, U]):
    """Either type holding one of two values."""

    _left: T | None = None
    _right: U | None = None
    _is_left: bool = True

    @staticmethod
    def left(value: T) -> "Either[T, Any]":
        """Create Left value."""
        return Either(_left=value, _is_left=True)

    @staticmethod
    def right(value: U) -> "Either[Any, U]":
        """Create Right value."""
        return Either(_right=value, _is_left=False)

    def is_left(self) -> bool:
        """Check if Left."""
        return self._is_left

    def is_right(self) -> bool:
        """Check if Right."""
        return not self._is_left

    def left_value(self) -> T:
        """Get Left value."""
        if not self._is_left:
            raise ValueError("Called left_value on Right")
        return self._left  # type: ignore

    def right_value(self) -> U:
        """Get Right value."""
        if self._is_left:
            raise ValueError("Called right_value on Left")
        return self._right  # type: ignore

    def map_left(self, f: Callable[[T], Any]) -> "Either[Any, U]":
        """Apply function to Left value."""
        if self._is_left:
            return Either.left(f(self._left))  # type: ignore
        return self  # type: ignore

    def map_right(self, f: Callable[[U], Any]) -> "Either[T, Any]":
        """Apply function to Right value."""
        if not self._is_left:
            return Either.right(f(self._right))  # type: ignore
        return self  # type: ignore

    def fold(self, left_f: Callable[[T], Any], right_f: Callable[[U], Any]) -> Any:
        """Apply one of two functions depending on variant."""
        if self._is_left:
            return left_f(self._left)  # type: ignore
        return right_f(self._right)  # type: ignore


@dataclass
class Validated(Generic[T, E]):
    """Validated type that accumulates errors."""

    _value: T | None = None
    _errors: list[E] | None = None
    _is_valid: bool = True

    @staticmethod
    def valid(value: T) -> "Validated[T, Any]":
        """Create valid value."""
        return Validated(_value=value, _is_valid=True)

    @staticmethod
    def invalid(errors: list[E]) -> "Validated[Any, E]":
        """Create invalid value with errors."""
        return Validated(_errors=errors, _is_valid=False)

    @staticmethod
    def error(error: E) -> "Validated[Any, E]":
        """Create invalid value with single error."""
        return Validated(_errors=[error], _is_valid=False)

    def is_valid(self) -> bool:
        """Check if valid."""
        return self._is_valid

    def value(self) -> T:
        """Get value."""
        if not self._is_valid:
            raise ValueError("Called value on invalid")
        return self._value  # type: ignore

    def errors(self) -> list[E]:
        """Get errors."""
        if self._is_valid:
            return []
        return self._errors or []


def combine_validated(
    v1: Validated[T, E], v2: Validated[U, E], f: Callable[[T, U], Any]
) -> Validated[Any, E]:
    """Combine two validated values, accumulating errors."""
    if v1.is_valid() and v2.is_valid():
        return Validated.valid(f(v1.value(), v2.value()))

    all_errors: list[E] = []
    if not v1.is_valid():
        all_errors.extend(v1.errors())
    if not v2.is_valid():
        all_errors.extend(v2.errors())

    return Validated.invalid(all_errors)


def validate_positive(n: int) -> Validated[int, str]:
    """Validate number is positive."""
    if n > 0:
        return Validated.valid(n)
    return Validated.error(f"must be positive, got {n}")


def validate_non_empty(s: str) -> Validated[str, str]:
    """Validate string is non-empty."""
    if s:
        return Validated.valid(s)
    return Validated.error("must be non-empty")


def simulate_result(operations: list[str]) -> list[str]:
    """Simulate Result operations."""
    results_list: list[str] = []
    current: Result[int, str] = Ok(0)

    for op in operations:
        parts = op.split(":")
        cmd = parts[0]

        if cmd == "ok":
            current = Ok(int(parts[1]))
            results_list.append("ok")
        elif cmd == "err":
            current = Err(parts[1])
            results_list.append("err")
        elif cmd == "is_ok":
            results_list.append("1" if current.is_ok() else "0")
        elif cmd == "is_err":
            results_list.append("1" if current.is_err() else "0")
        elif cmd == "unwrap":
            results_list.append(str(current.unwrap_or(-1)))
        elif cmd == "map":
            current = current.map(lambda x: x * int(parts[1]))  # noqa: B023
            results_list.append("ok")
        elif cmd == "divide":
            a, b = int(parts[1]), int(parts[2])
            current = safe_divide(a, b).map(int)
            if current.is_ok():
                results_list.append(str(current.unwrap()))
            else:
                results_list.append(f"error:{current.unwrap_err()}")
        elif cmd == "parse":
            current = safe_parse_int(parts[1])
            if current.is_ok():
                results_list.append(str(current.unwrap()))
            else:
                results_list.append("error")

    return results_list


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: generic_result_cli.py <command> [args...]")
        print("Commands: divide, parse, validate")
        return 1

    cmd = sys.argv[1]

    if cmd == "divide":
        if len(sys.argv) < 4:
            print("Usage: divide <a> <b>", file=sys.stderr)
            return 1
        result = safe_divide(float(sys.argv[2]), float(sys.argv[3]))
        if result.is_ok():
            print(f"Ok({result.unwrap()})")
        else:
            print(f"Err({result.unwrap_err()})")

    elif cmd == "parse":
        if len(sys.argv) < 3:
            print("Usage: parse <value>", file=sys.stderr)
            return 1
        result = safe_parse_int(sys.argv[2])
        if result.is_ok():
            print(f"Ok({result.unwrap()})")
        else:
            print(f"Err({result.unwrap_err()})")

    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Usage: validate <number>", file=sys.stderr)
            return 1
        parsed = safe_parse_int(sys.argv[2])
        if parsed.is_err():
            print(f"Err({parsed.unwrap_err()})")
            return 1

        validated = validate_positive(parsed.unwrap())
        if validated.is_valid():
            print(f"Valid({validated.value()})")
        else:
            print(f"Invalid({validated.errors()})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
