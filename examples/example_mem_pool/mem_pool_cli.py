"""Object Pool CLI.

Demonstrates object pooling with acquire/release semantics.
"""

import sys
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import Lock
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class PoolStats:
    """Pool statistics."""

    total_created: int = 0
    total_acquired: int = 0
    total_released: int = 0
    current_in_use: int = 0
    current_available: int = 0
    high_water_mark: int = 0


class ObjectPool(Generic[T]):
    """Generic object pool with acquire/release semantics."""

    def __init__(
        self,
        factory: Callable[[], T],
        reset: Callable[[T], None] | None = None,
        max_size: int = 100,
        initial_size: int = 0,
    ) -> None:
        self._factory = factory
        self._reset = reset or (lambda x: None)
        self._max_size = max_size
        self._pool: list[T] = []
        self._in_use: set[int] = set()
        self._lock = Lock()
        self._stats = PoolStats()

        # Pre-allocate initial objects
        for _ in range(initial_size):
            obj = self._factory()
            self._pool.append(obj)
            self._stats.total_created += 1
            self._stats.current_available += 1

    def acquire(self) -> T:
        """Acquire an object from the pool."""
        with self._lock:
            if self._pool:
                obj = self._pool.pop()
                self._stats.current_available -= 1
            else:
                obj = self._factory()
                self._stats.total_created += 1

            obj_id = id(obj)
            self._in_use.add(obj_id)
            self._stats.total_acquired += 1
            self._stats.current_in_use += 1

            if self._stats.current_in_use > self._stats.high_water_mark:
                self._stats.high_water_mark = self._stats.current_in_use

            return obj

    def release(self, obj: T) -> bool:
        """Release an object back to the pool."""
        with self._lock:
            obj_id = id(obj)
            if obj_id not in self._in_use:
                return False  # Object not from this pool or already released

            self._in_use.remove(obj_id)
            self._stats.total_released += 1
            self._stats.current_in_use -= 1

            if len(self._pool) < self._max_size:
                self._reset(obj)
                self._pool.append(obj)
                self._stats.current_available += 1
                return True
            return True  # Released but not pooled (pool full)

    @contextmanager
    def checkout(self):
        """Context manager for automatic release."""
        obj = self.acquire()
        try:
            yield obj
        finally:
            self.release(obj)

    def stats(self) -> PoolStats:
        """Get pool statistics."""
        with self._lock:
            return PoolStats(
                total_created=self._stats.total_created,
                total_acquired=self._stats.total_acquired,
                total_released=self._stats.total_released,
                current_in_use=self._stats.current_in_use,
                current_available=self._stats.current_available,
                high_water_mark=self._stats.high_water_mark,
            )

    def size(self) -> int:
        """Get number of available objects."""
        with self._lock:
            return len(self._pool)

    def in_use_count(self) -> int:
        """Get number of objects in use."""
        with self._lock:
            return len(self._in_use)

    def clear(self) -> int:
        """Clear the pool, returning count of cleared objects."""
        with self._lock:
            count = len(self._pool)
            self._pool.clear()
            self._stats.current_available = 0
            return count


# Specialized pools
@dataclass
class Connection:
    """A simulated database connection."""

    id: int
    is_open: bool = True
    query_count: int = 0

    def execute(self, query: str) -> str:
        """Execute a query."""
        self.query_count += 1
        return f"Result from conn-{self.id}: {query}"

    def reset(self) -> None:
        """Reset connection state."""
        self.query_count = 0


class ConnectionPool:
    """Database connection pool."""

    def __init__(self, max_size: int = 10) -> None:
        self._next_id = 0
        self._pool = ObjectPool(
            factory=self._create_connection,
            reset=lambda c: c.reset(),
            max_size=max_size,
        )

    def _create_connection(self) -> Connection:
        """Create a new connection."""
        conn_id = self._next_id
        self._next_id += 1
        return Connection(conn_id)

    def get_connection(self) -> Connection:
        """Get a connection from the pool."""
        return self._pool.acquire()

    def return_connection(self, conn: Connection) -> None:
        """Return a connection to the pool."""
        self._pool.release(conn)

    @contextmanager
    def connection(self):
        """Context manager for connection."""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.return_connection(conn)

    def stats(self) -> PoolStats:
        """Get pool statistics."""
        return self._pool.stats()


@dataclass
class Buffer:
    """A byte buffer."""

    data: bytearray = field(default_factory=lambda: bytearray(1024))
    position: int = 0
    limit: int = 1024

    def write(self, data: bytes) -> int:
        """Write data to buffer."""
        available = self.limit - self.position
        to_write = min(len(data), available)
        self.data[self.position : self.position + to_write] = data[:to_write]
        self.position += to_write
        return to_write

    def read(self, size: int) -> bytes:
        """Read data from buffer."""
        end = min(self.position, size)
        result = bytes(self.data[:end])
        return result

    def reset(self) -> None:
        """Reset buffer."""
        self.position = 0


class BufferPool:
    """Pool of byte buffers."""

    def __init__(self, buffer_size: int = 1024, max_size: int = 100) -> None:
        self._buffer_size = buffer_size

        def create_buffer() -> Buffer:
            return Buffer(
                data=bytearray(buffer_size),
                limit=buffer_size,
            )

        self._pool = ObjectPool(
            factory=create_buffer,
            reset=lambda b: b.reset(),
            max_size=max_size,
        )

    def acquire(self) -> Buffer:
        """Acquire a buffer."""
        return self._pool.acquire()

    def release(self, buf: Buffer) -> None:
        """Release a buffer."""
        self._pool.release(buf)

    @contextmanager
    def buffer(self):
        """Context manager for buffer."""
        buf = self.acquire()
        try:
            yield buf
        finally:
            self.release(buf)

    def stats(self) -> PoolStats:
        """Get pool statistics."""
        return self._pool.stats()


def simulate_pool(operations: list[str]) -> list[str]:
    """Simulate pool operations."""
    results: list[str] = []
    pool: ObjectPool[list] = ObjectPool(
        factory=lambda: [],
        reset=lambda x: x.clear(),
        max_size=10,
    )

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "acquire":
            obj = pool.acquire()
            results.append(f"acquired id={id(obj)}")
        elif cmd == "release":
            # For simulation, acquire then release
            obj = pool.acquire()
            pool.release(obj)
            results.append("released")
        elif cmd == "size":
            results.append(str(pool.size()))
        elif cmd == "in_use":
            results.append(str(pool.in_use_count()))
        elif cmd == "stats":
            s = pool.stats()
            results.append(f"created={s.total_created} acquired={s.total_acquired}")
        elif cmd == "checkout":
            with pool.checkout() as obj:
                obj.append(1)
            results.append("checkout complete")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mem_pool_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    pool = ConnectionPool(max_size=5)

    if cmd == "demo":
        # Demo connection pooling
        conn = pool.get_connection()
        print(f"Got connection: {conn.id}")
        result = conn.execute("SELECT * FROM users")
        print(f"Query result: {result}")
        pool.return_connection(conn)
        print(f"Stats: {pool.stats()}")
    elif cmd == "context":
        with pool.connection() as conn:
            print(f"Using connection: {conn.id}")
            print(conn.execute("INSERT INTO logs VALUES(1)"))
        print(f"Stats: {pool.stats()}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
