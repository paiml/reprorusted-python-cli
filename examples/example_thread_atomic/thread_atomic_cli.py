#!/usr/bin/env python3
"""Thread Atomic CLI.

Atomic counter and CAS patterns.
"""

import argparse
import sys
import threading


class AtomicInt:
    """Atomic integer with CAS operations."""

    def __init__(self, value: int = 0) -> None:
        self._value: int = value
        self._lock: threading.Lock = threading.Lock()

    def get(self) -> int:
        """Get current value."""
        with self._lock:
            return self._value

    def set(self, value: int) -> None:
        """Set value."""
        with self._lock:
            self._value = value

    def add(self, delta: int) -> int:
        """Add and return new value."""
        with self._lock:
            self._value += delta
            return self._value

    def sub(self, delta: int) -> int:
        """Subtract and return new value."""
        with self._lock:
            self._value -= delta
            return self._value

    def increment(self) -> int:
        """Increment and return new value."""
        return self.add(1)

    def decrement(self) -> int:
        """Decrement and return new value."""
        return self.sub(1)

    def compare_and_swap(self, expected: int, new_value: int) -> bool:
        """Compare and swap. Returns True if successful."""
        with self._lock:
            if self._value == expected:
                self._value = new_value
                return True
            return False

    def get_and_set(self, new_value: int) -> int:
        """Get current value and set new value."""
        with self._lock:
            old = self._value
            self._value = new_value
            return old

    def add_and_get(self, delta: int) -> int:
        """Add delta and return new value."""
        return self.add(delta)

    def get_and_add(self, delta: int) -> int:
        """Get current value then add delta."""
        with self._lock:
            old = self._value
            self._value += delta
            return old


class AtomicBool:
    """Atomic boolean."""

    def __init__(self, value: bool = False) -> None:
        self._value: bool = value
        self._lock: threading.Lock = threading.Lock()

    def get(self) -> bool:
        """Get current value."""
        with self._lock:
            return self._value

    def set(self, value: bool) -> None:
        """Set value."""
        with self._lock:
            self._value = value

    def compare_and_swap(self, expected: bool, new_value: bool) -> bool:
        """CAS for bool."""
        with self._lock:
            if self._value == expected:
                self._value = new_value
                return True
            return False

    def get_and_set(self, new_value: bool) -> bool:
        """Get and set."""
        with self._lock:
            old = self._value
            self._value = new_value
            return old


class AtomicReference:
    """Atomic reference to any object."""

    def __init__(self, value: object = None) -> None:
        self._value: object = value
        self._lock: threading.Lock = threading.Lock()

    def get(self) -> object:
        """Get current value."""
        with self._lock:
            return self._value

    def set(self, value: object) -> None:
        """Set value."""
        with self._lock:
            self._value = value

    def compare_and_swap(self, expected: object, new_value: object) -> bool:
        """CAS for reference."""
        with self._lock:
            if self._value is expected:
                self._value = new_value
                return True
            return False

    def get_and_set(self, new_value: object) -> object:
        """Get and set."""
        with self._lock:
            old = self._value
            self._value = new_value
            return old


class SpinLock:
    """Simple spinlock using atomic CAS."""

    def __init__(self) -> None:
        self._locked: AtomicBool = AtomicBool(False)

    def try_lock(self) -> bool:
        """Try to acquire lock (non-blocking)."""
        return self._locked.compare_and_swap(False, True)

    def unlock(self) -> None:
        """Release lock."""
        self._locked.set(False)

    def is_locked(self) -> bool:
        """Check if locked."""
        return self._locked.get()


class AtomicCounter:
    """High-level atomic counter with statistics."""

    def __init__(self) -> None:
        self._value: AtomicInt = AtomicInt(0)
        self._increments: AtomicInt = AtomicInt(0)
        self._decrements: AtomicInt = AtomicInt(0)

    def increment(self) -> int:
        """Increment counter."""
        self._increments.increment()
        return self._value.increment()

    def decrement(self) -> int:
        """Decrement counter."""
        self._decrements.increment()
        return self._value.decrement()

    def get(self) -> int:
        """Get current value."""
        return self._value.get()

    def reset(self) -> int:
        """Reset and return old value."""
        return self._value.get_and_set(0)

    def stats(self) -> dict[str, int]:
        """Get statistics."""
        return {
            "value": self._value.get(),
            "increments": self._increments.get(),
            "decrements": self._decrements.get(),
        }


def atomic_ops(initial: int, ops: list[str]) -> int:
    """Execute atomic operations and return result."""
    atom = AtomicInt(initial)

    for op in ops:
        if op == "inc":
            atom.increment()
        elif op == "dec":
            atom.decrement()
        elif op.startswith("add:"):
            delta = int(op.split(":")[1])
            atom.add(delta)
        elif op.startswith("sub:"):
            delta = int(op.split(":")[1])
            atom.sub(delta)
        elif op.startswith("set:"):
            val = int(op.split(":")[1])
            atom.set(val)
        elif op.startswith("cas:"):
            parts = op.split(":")
            expected = int(parts[1])
            new_val = int(parts[2])
            atom.compare_and_swap(expected, new_val)

    return atom.get()


def cas_sequence(initial: int, operations: list[tuple[int, int]]) -> list[bool]:
    """Execute CAS sequence and return results."""
    atom = AtomicInt(initial)
    results: list[bool] = []

    for expected, new_val in operations:
        success = atom.compare_and_swap(expected, new_val)
        results.append(success)

    return results


def spinlock_sequence(ops: list[str]) -> list[bool]:
    """Execute spinlock sequence."""
    lock = SpinLock()
    results: list[bool] = []

    for op in ops:
        if op == "try":
            results.append(lock.try_lock())
        elif op == "unlock":
            lock.unlock()
        elif op == "check":
            results.append(lock.is_locked())

    return results


def counter_simulation(ops: list[str]) -> dict[str, int]:
    """Simulate counter with statistics."""
    counter = AtomicCounter()

    for op in ops:
        if op == "inc":
            counter.increment()
        elif op == "dec":
            counter.decrement()
        elif op == "reset":
            counter.reset()

    return counter.stats()


def atomic_max(values: list[int]) -> int:
    """Find max using atomic compare-and-swap."""
    if not values:
        return 0

    result = AtomicInt(values[0])

    for val in values[1:]:
        while True:
            current = result.get()
            if val <= current:
                break
            if result.compare_and_swap(current, val):
                break

    return result.get()


def atomic_min(values: list[int]) -> int:
    """Find min using atomic compare-and-swap."""
    if not values:
        return 0

    result = AtomicInt(values[0])

    for val in values[1:]:
        while True:
            current = result.get()
            if val >= current:
                break
            if result.compare_and_swap(current, val):
                break

    return result.get()


def main() -> int:
    parser = argparse.ArgumentParser(description="Thread atomic CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # ops
    ops_p = subparsers.add_parser("ops", help="Atomic operations")
    ops_p.add_argument("--initial", type=int, default=0)
    ops_p.add_argument("ops", nargs="+")

    # cas
    cas_p = subparsers.add_parser("cas", help="CAS sequence")
    cas_p.add_argument("initial", type=int)
    cas_p.add_argument("operations", nargs="+", help="expected:new pairs")

    # counter
    counter_p = subparsers.add_parser("counter", help="Counter with stats")
    counter_p.add_argument("ops", nargs="+")

    # max
    max_p = subparsers.add_parser("max", help="Atomic max")
    max_p.add_argument("values", type=int, nargs="+")

    args = parser.parse_args()

    if args.command == "ops":
        result = atomic_ops(args.initial, args.ops)
        print(f"Result: {result}")

    elif args.command == "cas":
        operations = []
        for op in args.operations:
            parts = op.split(":")
            operations.append((int(parts[0]), int(parts[1])))
        results = cas_sequence(args.initial, operations)
        print(f"Results: {results}")

    elif args.command == "counter":
        stats = counter_simulation(args.ops)
        print(f"Stats: {stats}")

    elif args.command == "max":
        result = atomic_max(args.values)
        print(f"Max: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
