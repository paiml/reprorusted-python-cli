#!/usr/bin/env python3
"""Thread Queue CLI.

Thread-safe queue patterns for producer-consumer scenarios.
"""

import argparse
import sys
import threading
from typing import Generic, TypeVar

T = TypeVar("T")


class ThreadSafeQueue(Generic[T]):
    """Thread-safe FIFO queue."""

    def __init__(self, maxsize: int = 0) -> None:
        self._items: list[T] = []
        self._maxsize: int = maxsize
        self._lock: threading.Lock = threading.Lock()

    def put(self, item: T) -> bool:
        """Put item in queue. Returns False if full."""
        with self._lock:
            if self._maxsize > 0 and len(self._items) >= self._maxsize:
                return False
            self._items.append(item)
            return True

    def get(self) -> T | None:
        """Get item from queue. Returns None if empty."""
        with self._lock:
            if self._items:
                return self._items.pop(0)
            return None

    def peek(self) -> T | None:
        """Peek at front item without removing."""
        with self._lock:
            if self._items:
                return self._items[0]
            return None

    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._items)

    def empty(self) -> bool:
        """Check if empty."""
        with self._lock:
            return len(self._items) == 0

    def full(self) -> bool:
        """Check if full."""
        with self._lock:
            return self._maxsize > 0 and len(self._items) >= self._maxsize

    def clear(self) -> int:
        """Clear queue and return count of removed items."""
        with self._lock:
            count = len(self._items)
            self._items.clear()
            return count


class PriorityQueue(Generic[T]):
    """Thread-safe priority queue (min-heap simulation)."""

    def __init__(self) -> None:
        self._items: list[tuple[int, T]] = []
        self._lock: threading.Lock = threading.Lock()

    def put(self, priority: int, item: T) -> None:
        """Put item with priority (lower = higher priority)."""
        with self._lock:
            self._items.append((priority, item))
            self._items.sort(key=lambda x: x[0])

    def get(self) -> T | None:
        """Get highest priority item."""
        with self._lock:
            if self._items:
                return self._items.pop(0)[1]
            return None

    def peek(self) -> tuple[int, T] | None:
        """Peek at highest priority item."""
        with self._lock:
            if self._items:
                return self._items[0]
            return None

    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._items)


class LifoQueue(Generic[T]):
    """Thread-safe LIFO queue (stack)."""

    def __init__(self, maxsize: int = 0) -> None:
        self._items: list[T] = []
        self._maxsize: int = maxsize
        self._lock: threading.Lock = threading.Lock()

    def put(self, item: T) -> bool:
        """Push item onto stack."""
        with self._lock:
            if self._maxsize > 0 and len(self._items) >= self._maxsize:
                return False
            self._items.append(item)
            return True

    def get(self) -> T | None:
        """Pop item from stack."""
        with self._lock:
            if self._items:
                return self._items.pop()
            return None

    def peek(self) -> T | None:
        """Peek at top item."""
        with self._lock:
            if self._items:
                return self._items[-1]
            return None

    def size(self) -> int:
        """Get stack size."""
        with self._lock:
            return len(self._items)


class Deque(Generic[T]):
    """Thread-safe double-ended queue."""

    def __init__(self, maxsize: int = 0) -> None:
        self._items: list[T] = []
        self._maxsize: int = maxsize
        self._lock: threading.Lock = threading.Lock()

    def push_front(self, item: T) -> bool:
        """Push to front."""
        with self._lock:
            if self._maxsize > 0 and len(self._items) >= self._maxsize:
                return False
            self._items.insert(0, item)
            return True

    def push_back(self, item: T) -> bool:
        """Push to back."""
        with self._lock:
            if self._maxsize > 0 and len(self._items) >= self._maxsize:
                return False
            self._items.append(item)
            return True

    def pop_front(self) -> T | None:
        """Pop from front."""
        with self._lock:
            if self._items:
                return self._items.pop(0)
            return None

    def pop_back(self) -> T | None:
        """Pop from back."""
        with self._lock:
            if self._items:
                return self._items.pop()
            return None

    def size(self) -> int:
        """Get size."""
        with self._lock:
            return len(self._items)


def simulate_fifo(maxsize: int, ops: list[str]) -> list[int]:
    """Simulate FIFO queue operations."""
    queue: ThreadSafeQueue[int] = ThreadSafeQueue(maxsize)
    results: list[int] = []

    for op in ops:
        if op.startswith("put:"):
            val = int(op.split(":")[1])
            queue.put(val)
        elif op == "get":
            val = queue.get()
            if val is not None:
                results.append(val)
        elif op == "size":
            results.append(queue.size())
        elif op == "peek":
            val = queue.peek()
            if val is not None:
                results.append(val)

    return results


def simulate_lifo(maxsize: int, ops: list[str]) -> list[int]:
    """Simulate LIFO queue operations."""
    stack: LifoQueue[int] = LifoQueue(maxsize)
    results: list[int] = []

    for op in ops:
        if op.startswith("put:"):
            val = int(op.split(":")[1])
            stack.put(val)
        elif op == "get":
            val = stack.get()
            if val is not None:
                results.append(val)
        elif op == "size":
            results.append(stack.size())

    return results


def simulate_priority(ops: list[str]) -> list[int]:
    """Simulate priority queue operations."""
    pq: PriorityQueue[int] = PriorityQueue()
    results: list[int] = []

    for op in ops:
        if op.startswith("put:"):
            parts = op.split(":")
            priority = int(parts[1])
            value = int(parts[2])
            pq.put(priority, value)
        elif op == "get":
            val = pq.get()
            if val is not None:
                results.append(val)
        elif op == "size":
            results.append(pq.size())

    return results


def simulate_deque(maxsize: int, ops: list[str]) -> list[int]:
    """Simulate deque operations."""
    deque: Deque[int] = Deque(maxsize)
    results: list[int] = []

    for op in ops:
        if op.startswith("pf:"):
            val = int(op.split(":")[1])
            deque.push_front(val)
        elif op.startswith("pb:"):
            val = int(op.split(":")[1])
            deque.push_back(val)
        elif op == "gf":
            val = deque.pop_front()
            if val is not None:
                results.append(val)
        elif op == "gb":
            val = deque.pop_back()
            if val is not None:
                results.append(val)
        elif op == "size":
            results.append(deque.size())

    return results


def producer_consumer_sim(items: list[int], batch_size: int) -> list[int]:
    """Simulate producer-consumer pattern."""
    queue: ThreadSafeQueue[int] = ThreadSafeQueue()
    results: list[int] = []

    # Producer adds all items
    for item in items:
        queue.put(item)

    # Consumer gets in batches
    while not queue.empty():
        batch: list[int] = []
        for _ in range(batch_size):
            val = queue.get()
            if val is not None:
                batch.append(val)
        results.extend(batch)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Thread queue CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # fifo
    fifo_p = subparsers.add_parser("fifo", help="FIFO queue")
    fifo_p.add_argument("--maxsize", type=int, default=0)
    fifo_p.add_argument("ops", nargs="+")

    # lifo
    lifo_p = subparsers.add_parser("lifo", help="LIFO queue")
    lifo_p.add_argument("--maxsize", type=int, default=0)
    lifo_p.add_argument("ops", nargs="+")

    # priority
    priority_p = subparsers.add_parser("priority", help="Priority queue")
    priority_p.add_argument("ops", nargs="+")

    # deque
    deque_p = subparsers.add_parser("deque", help="Double-ended queue")
    deque_p.add_argument("--maxsize", type=int, default=0)
    deque_p.add_argument("ops", nargs="+")

    args = parser.parse_args()

    if args.command == "fifo":
        results = simulate_fifo(args.maxsize, args.ops)
        print(f"Results: {results}")

    elif args.command == "lifo":
        results = simulate_lifo(args.maxsize, args.ops)
        print(f"Results: {results}")

    elif args.command == "priority":
        results = simulate_priority(args.ops)
        print(f"Results: {results}")

    elif args.command == "deque":
        results = simulate_deque(args.maxsize, args.ops)
        print(f"Results: {results}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
