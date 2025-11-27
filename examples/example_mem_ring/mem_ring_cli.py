"""Ring Buffer CLI.

Demonstrates circular buffer/ring buffer implementation.
"""

import sys
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class RingStats:
    """Ring buffer statistics."""

    capacity: int = 0
    size: int = 0
    head: int = 0
    tail: int = 0
    overflows: int = 0


class RingBuffer(Generic[T]):
    """Fixed-size circular buffer."""

    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._buffer: list[T | None] = [None] * capacity
        self._head = 0  # Next write position
        self._tail = 0  # Next read position
        self._size = 0
        self._overflows = 0

    def push(self, item: T) -> T | None:
        """Push item. Returns overwritten item if buffer was full."""
        overwritten: T | None = None

        if self._size == self._capacity:
            overwritten = self._buffer[self._tail]
            self._tail = (self._tail + 1) % self._capacity
            self._overflows += 1
        else:
            self._size += 1

        self._buffer[self._head] = item
        self._head = (self._head + 1) % self._capacity
        return overwritten

    def pop(self) -> T | None:
        """Pop oldest item (FIFO)."""
        if self._size == 0:
            return None

        item = self._buffer[self._tail]
        self._buffer[self._tail] = None
        self._tail = (self._tail + 1) % self._capacity
        self._size -= 1
        return item

    def peek(self) -> T | None:
        """Peek at oldest item without removing."""
        if self._size == 0:
            return None
        return self._buffer[self._tail]

    def peek_newest(self) -> T | None:
        """Peek at newest item."""
        if self._size == 0:
            return None
        idx = (self._head - 1) % self._capacity
        return self._buffer[idx]

    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer = [None] * self._capacity
        self._head = 0
        self._tail = 0
        self._size = 0

    def size(self) -> int:
        """Get current size."""
        return self._size

    def capacity(self) -> int:
        """Get capacity."""
        return self._capacity

    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self._size == 0

    def is_full(self) -> bool:
        """Check if buffer is full."""
        return self._size == self._capacity

    def stats(self) -> RingStats:
        """Get buffer statistics."""
        return RingStats(
            capacity=self._capacity,
            size=self._size,
            head=self._head,
            tail=self._tail,
            overflows=self._overflows,
        )

    def to_list(self) -> list[T]:
        """Convert to list (oldest to newest)."""
        result: list[T] = []
        if self._size == 0:
            return result

        idx = self._tail
        for _ in range(self._size):
            item = self._buffer[idx]
            if item is not None:
                result.append(item)
            idx = (idx + 1) % self._capacity
        return result

    def __iter__(self) -> Iterator[T]:
        """Iterate from oldest to newest."""
        yield from self.to_list()

    def __len__(self) -> int:
        return self._size


class ByteRing:
    """Ring buffer optimized for bytes."""

    def __init__(self, capacity: int) -> None:
        self._buffer = bytearray(capacity)
        self._capacity = capacity
        self._head = 0
        self._tail = 0
        self._size = 0

    def write(self, data: bytes) -> int:
        """Write bytes. Returns number written."""
        written = 0
        for byte in data:
            if self._size == self._capacity:
                # Overwrite oldest
                self._tail = (self._tail + 1) % self._capacity
            else:
                self._size += 1

            self._buffer[self._head] = byte
            self._head = (self._head + 1) % self._capacity
            written += 1
        return written

    def read(self, count: int) -> bytes:
        """Read up to count bytes."""
        to_read = min(count, self._size)
        result = bytearray(to_read)

        for i in range(to_read):
            result[i] = self._buffer[self._tail]
            self._tail = (self._tail + 1) % self._capacity
            self._size -= 1

        return bytes(result)

    def peek(self, count: int) -> bytes:
        """Peek up to count bytes without consuming."""
        to_read = min(count, self._size)
        result = bytearray(to_read)

        idx = self._tail
        for i in range(to_read):
            result[i] = self._buffer[idx]
            idx = (idx + 1) % self._capacity

        return bytes(result)

    def available(self) -> int:
        """Get available bytes to read."""
        return self._size

    def free_space(self) -> int:
        """Get free space for writing (before overwrite)."""
        return self._capacity - self._size

    def clear(self) -> None:
        """Clear the buffer."""
        self._head = 0
        self._tail = 0
        self._size = 0


class SlidingWindow(Generic[T]):
    """Sliding window over a stream of values."""

    def __init__(self, size: int) -> None:
        self._ring: RingBuffer[T] = RingBuffer(size)

    def add(self, value: T) -> None:
        """Add value to window."""
        self._ring.push(value)

    def values(self) -> list[T]:
        """Get all values in window."""
        return self._ring.to_list()

    def size(self) -> int:
        """Get current window size."""
        return self._ring.size()

    def is_full(self) -> bool:
        """Check if window is full."""
        return self._ring.is_full()


class MovingAverage:
    """Moving average calculator using ring buffer."""

    def __init__(self, window_size: int) -> None:
        self._ring: RingBuffer[float] = RingBuffer(window_size)
        self._sum = 0.0

    def add(self, value: float) -> float:
        """Add value and return current average."""
        evicted = self._ring.push(value)
        if evicted is not None:
            self._sum -= evicted
        self._sum += value
        return self.average()

    def average(self) -> float:
        """Get current average."""
        if self._ring.is_empty():
            return 0.0
        return self._sum / self._ring.size()

    def size(self) -> int:
        """Get number of values."""
        return self._ring.size()


def simulate_ring(operations: list[str]) -> list[str]:
    """Simulate ring buffer operations."""
    results: list[str] = []
    ring: RingBuffer[int] = RingBuffer(4)

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "push":
            evicted = ring.push(int(parts[1]))
            results.append(f"evicted={evicted}")
        elif cmd == "pop":
            value = ring.pop()
            results.append(f"value={value}")
        elif cmd == "peek":
            value = ring.peek()
            results.append(f"peek={value}")
        elif cmd == "size":
            results.append(str(ring.size()))
        elif cmd == "is_full":
            results.append(str(ring.is_full()))
        elif cmd == "to_list":
            results.append(str(ring.to_list()))
        elif cmd == "stats":
            s = ring.stats()
            results.append(f"size={s.size} overflows={s.overflows}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mem_ring_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        ring: RingBuffer[str] = RingBuffer(3)
        for item in ["a", "b", "c", "d", "e"]:
            evicted = ring.push(item)
            print(f"Push {item}, evicted={evicted}, buffer={ring.to_list()}")

        print(f"\nFinal buffer: {ring.to_list()}")
        print(f"Stats: {ring.stats()}")

        # Moving average demo
        ma = MovingAverage(3)
        for val in [1.0, 2.0, 3.0, 4.0, 5.0]:
            avg = ma.add(val)
            print(f"Add {val}, average={avg:.2f}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
