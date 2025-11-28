#!/usr/bin/env python3
"""Async Context CLI.

Async context managers and resource management patterns.
"""

import argparse
import asyncio
import sys
from typing import Any


class AsyncResource:
    """Simple async resource with enter/exit."""

    def __init__(self, name: str) -> None:
        self._name: str = name
        self._open: bool = False
        self._operations: list[str] = []

    async def __aenter__(self) -> "AsyncResource":
        self._open = True
        self._operations.append(f"opened:{self._name}")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self._open = False
        self._operations.append(f"closed:{self._name}")
        return False

    def is_open(self) -> bool:
        return self._open

    def get_name(self) -> str:
        return self._name

    def get_operations(self) -> list[str]:
        return self._operations.copy()

    async def read(self) -> str:
        if not self._open:
            raise RuntimeError("Resource not open")
        self._operations.append(f"read:{self._name}")
        return f"data_from_{self._name}"

    async def write(self, data: str) -> None:
        if not self._open:
            raise RuntimeError("Resource not open")
        self._operations.append(f"write:{self._name}:{data}")


class AsyncLock:
    """Simple async lock implementation."""

    def __init__(self) -> None:
        self._locked: bool = False
        self._history: list[str] = []

    async def __aenter__(self) -> "AsyncLock":
        await self.acquire()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self.release()
        return False

    async def acquire(self) -> None:
        self._locked = True
        self._history.append("acquired")

    def release(self) -> None:
        self._locked = False
        self._history.append("released")

    def is_locked(self) -> bool:
        return self._locked

    def get_history(self) -> list[str]:
        return self._history.copy()


class AsyncTransaction:
    """Async transaction with commit/rollback."""

    def __init__(self) -> None:
        self._operations: list[str] = []
        self._committed: bool = False
        self._rolled_back: bool = False

    async def __aenter__(self) -> "AsyncTransaction":
        self._operations.append("begin")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_type is not None:
            await self.rollback()
            return True  # Suppress the exception
        if not self._committed:
            await self.commit()
        return False

    async def commit(self) -> None:
        self._operations.append("commit")
        self._committed = True

    async def rollback(self) -> None:
        self._operations.append("rollback")
        self._rolled_back = True

    def add_operation(self, op: str) -> None:
        self._operations.append(op)

    def get_operations(self) -> list[str]:
        return self._operations.copy()

    def is_committed(self) -> bool:
        return self._committed

    def is_rolled_back(self) -> bool:
        return self._rolled_back


class AsyncPool:
    """Simple async connection pool."""

    def __init__(self, max_size: int) -> None:
        self._max_size: int = max_size
        self._available: list[int] = list(range(max_size))
        self._in_use: list[int] = []
        self._history: list[str] = []

    async def acquire(self) -> int:
        if not self._available:
            raise RuntimeError("Pool exhausted")
        conn = self._available.pop(0)
        self._in_use.append(conn)
        self._history.append(f"acquire:{conn}")
        return conn

    async def release(self, conn: int) -> None:
        if conn in self._in_use:
            self._in_use.remove(conn)
            self._available.append(conn)
            self._history.append(f"release:{conn}")

    def available_count(self) -> int:
        return len(self._available)

    def in_use_count(self) -> int:
        return len(self._in_use)

    def get_history(self) -> list[str]:
        return self._history.copy()


class PooledConnection:
    """Context manager for pooled connection."""

    def __init__(self, pool: AsyncPool) -> None:
        self._pool: AsyncPool = pool
        self._conn: int = -1

    async def __aenter__(self) -> int:
        self._conn = await self._pool.acquire()
        return self._conn

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        await self._pool.release(self._conn)
        return False


async def use_resource(name: str) -> list[str]:
    """Use async resource with context manager."""
    async with AsyncResource(name) as res:
        await res.read()
        await res.write("test_data")
    return res.get_operations()


async def use_lock() -> list[str]:
    """Use async lock with context manager."""
    lock = AsyncLock()
    async with lock:
        pass  # Critical section
    return lock.get_history()


async def nested_resources(name1: str, name2: str) -> tuple[list[str], list[str]]:
    """Nested async resource usage."""
    async with AsyncResource(name1) as res1:
        async with AsyncResource(name2) as res2:
            await res1.read()
            await res2.write("nested_data")
    return (res1.get_operations(), res2.get_operations())


async def transaction_success() -> list[str]:
    """Successful transaction."""
    async with AsyncTransaction() as tx:
        tx.add_operation("insert_a")
        tx.add_operation("insert_b")
    return tx.get_operations()


async def transaction_failure() -> list[str]:
    """Failed transaction with rollback."""
    async with AsyncTransaction() as tx:
        tx.add_operation("insert_a")
        raise ValueError("Simulated failure")  # Will trigger rollback
    return tx.get_operations()


async def pool_operations(max_size: int) -> list[str]:
    """Pool acquire/release operations."""
    pool = AsyncPool(max_size)
    async with PooledConnection(pool) as conn1:
        async with PooledConnection(pool) as conn2:
            _ = conn1  # Use connections
            _ = conn2
    return pool.get_history()


async def sequential_resources(names: list[str]) -> list[str]:
    """Use resources sequentially."""
    all_ops: list[str] = []
    for name in names:
        async with AsyncResource(name) as res:
            data = await res.read()
            all_ops.append(data)
    return all_ops


async def resource_with_error(name: str, should_fail: bool) -> tuple[bool, list[str]]:
    """Resource that may encounter an error."""
    try:
        async with AsyncResource(name) as res:
            await res.read()
            if should_fail:
                raise RuntimeError("Intentional failure")
            await res.write("success")
        return (True, res.get_operations())
    except RuntimeError:
        return (False, res.get_operations())


async def scoped_lock_operations(operations: list[str]) -> list[str]:
    """Perform operations within a lock scope."""
    lock = AsyncLock()
    results: list[str] = []
    for op in operations:
        async with lock:
            results.append(f"locked:{op}")
    return results


def run_async(coro: object) -> object:
    """Run async function synchronously."""
    return asyncio.run(coro)  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Async context CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # resource
    res_p = subparsers.add_parser("resource", help="Use async resource")
    res_p.add_argument("name")

    # transaction
    tx_p = subparsers.add_parser("transaction", help="Run transaction")
    tx_p.add_argument("--fail", action="store_true")

    # pool
    pool_p = subparsers.add_parser("pool", help="Test connection pool")
    pool_p.add_argument("--size", type=int, default=5)

    args = parser.parse_args()

    if args.command == "resource":
        ops = run_async(use_resource(args.name))
        print(f"Operations: {ops}")

    elif args.command == "transaction":
        if args.fail:
            ops = run_async(transaction_failure())
        else:
            ops = run_async(transaction_success())
        print(f"Operations: {ops}")

    elif args.command == "pool":
        ops = run_async(pool_operations(args.size))
        print(f"Operations: {ops}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
