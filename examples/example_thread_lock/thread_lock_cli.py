#!/usr/bin/env python3
"""Thread Lock CLI.

Lock and RLock patterns for thread synchronization.
"""

import argparse
import sys
import threading
from typing import TypeVar

T = TypeVar("T")


class Counter:
    """Thread-safe counter using Lock."""

    def __init__(self) -> None:
        self._value: int = 0
        self._lock: threading.Lock = threading.Lock()

    def increment(self) -> int:
        """Increment counter atomically."""
        with self._lock:
            self._value += 1
            return self._value

    def decrement(self) -> int:
        """Decrement counter atomically."""
        with self._lock:
            self._value -= 1
            return self._value

    def get(self) -> int:
        """Get current value."""
        with self._lock:
            return self._value

    def add(self, n: int) -> int:
        """Add n to counter."""
        with self._lock:
            self._value += n
            return self._value


class ReentrantCounter:
    """Counter using RLock for reentrant access."""

    def __init__(self) -> None:
        self._value: int = 0
        self._lock: threading.RLock = threading.RLock()

    def increment(self) -> int:
        """Increment with reentrant lock."""
        with self._lock:
            self._value += 1
            return self._value

    def increment_twice(self) -> int:
        """Increment twice - demonstrates reentrant locking."""
        with self._lock:
            self.increment()
            return self.increment()

    def get(self) -> int:
        """Get value with lock."""
        with self._lock:
            return self._value


class SharedBuffer:
    """Thread-safe buffer with lock."""

    def __init__(self, capacity: int) -> None:
        self._buffer: list[int] = []
        self._capacity: int = capacity
        self._lock: threading.Lock = threading.Lock()

    def push(self, item: int) -> bool:
        """Push item if space available."""
        with self._lock:
            if len(self._buffer) < self._capacity:
                self._buffer.append(item)
                return True
            return False

    def pop(self) -> int | None:
        """Pop item if available."""
        with self._lock:
            if self._buffer:
                return self._buffer.pop(0)
            return None

    def size(self) -> int:
        """Get buffer size."""
        with self._lock:
            return len(self._buffer)

    def is_empty(self) -> bool:
        """Check if empty."""
        with self._lock:
            return len(self._buffer) == 0

    def is_full(self) -> bool:
        """Check if full."""
        with self._lock:
            return len(self._buffer) >= self._capacity


def with_lock(lock: threading.Lock, value: int) -> int:
    """Execute operation with lock."""
    with lock:
        return value * 2


def try_acquire(lock: threading.Lock) -> bool:
    """Try to acquire lock without blocking."""
    acquired = lock.acquire(blocking=False)
    if acquired:
        lock.release()
    return acquired


def locked_swap(lock: threading.Lock, a: int, b: int) -> tuple[int, int]:
    """Swap values under lock."""
    with lock:
        return (b, a)


def locked_max(lock: threading.Lock, values: list[int]) -> int:
    """Find max under lock."""
    with lock:
        if not values:
            return 0
        return max(values)


def locked_sum(lock: threading.Lock, values: list[int]) -> int:
    """Sum values under lock."""
    with lock:
        return sum(values)


def locked_append(lock: threading.Lock, lst: list[int], item: int) -> list[int]:
    """Append to list under lock."""
    with lock:
        lst.append(item)
        return lst.copy()


def locked_extend(lock: threading.Lock, lst: list[int], items: list[int]) -> list[int]:
    """Extend list under lock."""
    with lock:
        lst.extend(items)
        return lst.copy()


def locked_clear(lock: threading.Lock, lst: list[int]) -> list[int]:
    """Clear list under lock."""
    with lock:
        lst.clear()
        return lst.copy()


def simulate_counter_ops(ops: list[str]) -> int:
    """Simulate counter operations."""
    counter = Counter()
    for op in ops:
        if op == "inc":
            counter.increment()
        elif op == "dec":
            counter.decrement()
        elif op.startswith("add:"):
            n = int(op.split(":")[1])
            counter.add(n)
    return counter.get()


def simulate_buffer_ops(capacity: int, ops: list[str]) -> list[int]:
    """Simulate buffer operations."""
    buffer = SharedBuffer(capacity)
    results: list[int] = []
    for op in ops:
        if op.startswith("push:"):
            n = int(op.split(":")[1])
            buffer.push(n)
        elif op == "pop":
            val = buffer.pop()
            if val is not None:
                results.append(val)
        elif op == "size":
            results.append(buffer.size())
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Thread lock CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # counter
    counter_p = subparsers.add_parser("counter", help="Counter operations")
    counter_p.add_argument("ops", nargs="+", help="Operations: inc, dec, add:N")

    # buffer
    buffer_p = subparsers.add_parser("buffer", help="Buffer operations")
    buffer_p.add_argument("--capacity", type=int, default=10)
    buffer_p.add_argument("ops", nargs="+", help="Operations: push:N, pop, size")

    args = parser.parse_args()

    if args.command == "counter":
        result = simulate_counter_ops(args.ops)
        print(f"Counter: {result}")

    elif args.command == "buffer":
        results = simulate_buffer_ops(args.capacity, args.ops)
        print(f"Results: {results}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
