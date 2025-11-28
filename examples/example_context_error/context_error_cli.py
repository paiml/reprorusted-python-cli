#!/usr/bin/env python3
"""Context Error CLI.

Context managers with error handling patterns.
"""

import argparse
import sys
from contextlib import contextmanager


class Resource:
    """Simulated resource with cleanup."""

    def __init__(self, name: str):
        self.name = name
        self.is_open = False
        self.data: list[str] = []

    def open(self) -> None:
        if self.is_open:
            raise RuntimeError(f"Resource {self.name} already open")
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def write(self, data: str) -> None:
        if not self.is_open:
            raise RuntimeError(f"Resource {self.name} not open")
        self.data.append(data)

    def read(self) -> list[str]:
        if not self.is_open:
            raise RuntimeError(f"Resource {self.name} not open")
        return self.data.copy()


class ManagedResource:
    """Resource with context manager protocol."""

    def __init__(self, name: str, fail_on_enter: bool = False, fail_on_exit: bool = False):
        self.name = name
        self.fail_on_enter = fail_on_enter
        self.fail_on_exit = fail_on_exit
        self.entered = False
        self.exited = False
        self.data: list[str] = []

    def __enter__(self) -> "ManagedResource":
        if self.fail_on_enter:
            raise RuntimeError(f"Failed to enter {self.name}")
        self.entered = True
        return self

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object) -> bool:
        self.exited = True
        if self.fail_on_exit:
            raise RuntimeError(f"Failed to exit {self.name}")
        # Return False to not suppress exceptions
        return False

    def write(self, data: str) -> None:
        self.data.append(data)


class SuppressingResource:
    """Resource that suppresses specific exceptions."""

    def __init__(self, name: str, suppress_types: list[type]):
        self.name = name
        self.suppress_types = suppress_types
        self.suppressed: Exception | None = None

    def __enter__(self) -> "SuppressingResource":
        return self

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object) -> bool:
        if exc_type is not None and exc_type in self.suppress_types:
            self.suppressed = exc_val
            return True
        return False


class TransactionResource:
    """Resource with rollback on error."""

    def __init__(self, name: str):
        self.name = name
        self.operations: list[str] = []
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> "TransactionResource":
        return self

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object) -> bool:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        return False

    def execute(self, op: str) -> None:
        self.operations.append(op)

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True
        self.operations.clear()


@contextmanager
def managed_open(name: str, fail: bool = False):
    """Context manager using generator."""
    resource = Resource(name)
    resource.open()
    try:
        if fail:
            raise RuntimeError("Simulated failure")
        yield resource
    finally:
        resource.close()


@contextmanager
def error_handler(operation: str):
    """Context manager that logs errors."""
    errors: list[str] = []
    try:
        yield errors
    except Exception as e:
        errors.append(f"{operation}: {type(e).__name__}: {e}")
        raise


@contextmanager
def suppress_errors(*exception_types: type):
    """Context manager that suppresses specific errors."""
    try:
        yield
    except exception_types:
        pass


@contextmanager
def transaction():
    """Simple transaction context manager."""
    ops: list[str] = []
    committed = [False]
    try:
        yield ops
        committed[0] = True
    except Exception:
        ops.clear()
        raise


def use_managed_resource(name: str, data: str) -> str:
    """Use managed resource to write data."""
    with ManagedResource(name) as res:
        res.write(data)
        return f"wrote:{data}"


def use_managed_resource_with_error(name: str) -> str:
    """Use managed resource that fails."""
    try:
        with ManagedResource(name, fail_on_enter=True) as res:
            res.write("test")
            return "success"
    except RuntimeError:
        return "failed_enter"


def use_suppressing_resource(name: str, raise_error: bool) -> str:
    """Use resource that suppresses ValueError."""
    with SuppressingResource(name, [ValueError]) as res:
        if raise_error:
            raise ValueError("suppressed error")
        return "no_error"
    if res.suppressed:
        return f"suppressed:{res.suppressed}"
    return "completed"


def use_transaction(ops_to_do: list[str], fail_at: int | None) -> tuple[list[str], bool]:
    """Use transaction resource."""
    tx = TransactionResource("tx")
    try:
        with tx:
            for i, op in enumerate(ops_to_do):
                if fail_at is not None and i == fail_at:
                    raise RuntimeError("Transaction failed")
                tx.execute(op)
    except RuntimeError:
        pass
    return (tx.operations, tx.committed)


def nested_contexts(outer_name: str, inner_name: str) -> str:
    """Nested context managers."""
    with ManagedResource(outer_name) as outer:
        outer.write("outer_start")
        with ManagedResource(inner_name) as inner:
            inner.write("inner")
        outer.write("outer_end")
    return f"outer:{len(outer.data)},inner:{len(inner.data)}"


def multiple_contexts(names: list[str]) -> list[str]:
    """Multiple context managers in one with statement."""
    resources = [ManagedResource(n) for n in names]
    results: list[str] = []
    # Simulate multiple context managers
    for res in resources:
        res.__enter__()
    try:
        for res in resources:
            res.write("data")
            results.append(res.name)
    finally:
        for res in reversed(resources):
            res.__exit__(None, None, None)
    return results


def context_with_return(name: str) -> str:
    """Context manager with early return."""
    with ManagedResource(name) as res:
        res.write("before")
        if name == "early":
            return "early_return"
        res.write("after")
    return "normal_return"


def context_cleanup_on_error(name: str, should_fail: bool) -> tuple[bool, bool]:
    """Verify cleanup happens on error."""
    res = ManagedResource(name)
    try:
        with res:
            if should_fail:
                raise ValueError("test error")
    except ValueError:
        pass
    return (res.entered, res.exited)


def generator_context_test(name: str, fail: bool) -> str:
    """Test generator-based context manager."""
    try:
        with managed_open(name, fail=fail) as res:
            res.write("test")
            return f"success:{len(res.data)}"
    except RuntimeError:
        return "error"


def accumulate_with_transaction(values: list[str]) -> tuple[int, bool]:
    """Accumulate values in transaction."""
    total = 0
    with transaction() as ops:
        for v in values:
            num = int(v)
            total += num
            ops.append(f"add:{num}")
    return (total, len(ops) > 0)


def safe_accumulate(values: list[str]) -> tuple[int, list[str]]:
    """Safely accumulate, collecting errors."""
    total = 0
    errors: list[str] = []
    for v in values:
        with SuppressingResource("parse", [ValueError]) as res:
            total += int(v)
        if res.suppressed:
            errors.append(f"invalid:{v}")
    return (total, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Context error CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # resource
    res_p = subparsers.add_parser("resource", help="Use resource")
    res_p.add_argument("name")
    res_p.add_argument("data")

    # transaction
    tx_p = subparsers.add_parser("transaction", help="Run transaction")
    tx_p.add_argument("ops", nargs="+")
    tx_p.add_argument("--fail-at", type=int)

    # nested
    nest_p = subparsers.add_parser("nested", help="Nested contexts")
    nest_p.add_argument("outer")
    nest_p.add_argument("inner")

    args = parser.parse_args()

    if args.command == "resource":
        result = use_managed_resource(args.name, args.data)
        print(result)

    elif args.command == "transaction":
        ops, committed = use_transaction(args.ops, args.fail_at)
        print(f"Operations: {ops}")
        print(f"Committed: {committed}")

    elif args.command == "nested":
        result = nested_contexts(args.outer, args.inner)
        print(result)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
