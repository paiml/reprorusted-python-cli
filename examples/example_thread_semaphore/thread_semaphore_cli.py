#!/usr/bin/env python3
"""Thread Semaphore CLI.

Semaphore and BoundedSemaphore patterns.
"""

import argparse
import sys
import threading


class ResourcePool:
    """Pool of limited resources using Semaphore."""

    def __init__(self, size: int) -> None:
        self._size: int = size
        self._available: int = size
        self._semaphore: threading.Semaphore = threading.Semaphore(size)
        self._lock: threading.Lock = threading.Lock()

    def acquire(self) -> bool:
        """Acquire a resource."""
        acquired = self._semaphore.acquire(blocking=False)
        if acquired:
            with self._lock:
                self._available -= 1
        return acquired

    def release(self) -> bool:
        """Release a resource."""
        with self._lock:
            if self._available < self._size:
                self._available += 1
                self._semaphore.release()
                return True
            return False

    def available(self) -> int:
        """Get available count."""
        with self._lock:
            return self._available

    def size(self) -> int:
        """Get pool size."""
        return self._size


class BoundedPool:
    """Pool using BoundedSemaphore (prevents over-release)."""

    def __init__(self, size: int) -> None:
        self._size: int = size
        self._semaphore: threading.BoundedSemaphore = threading.BoundedSemaphore(size)
        self._acquired: int = 0
        self._lock: threading.Lock = threading.Lock()

    def acquire(self) -> bool:
        """Acquire resource."""
        acquired = self._semaphore.acquire(blocking=False)
        if acquired:
            with self._lock:
                self._acquired += 1
        return acquired

    def release(self) -> bool:
        """Release resource (bounded - can't over-release)."""
        with self._lock:
            if self._acquired > 0:
                self._acquired -= 1
                self._semaphore.release()
                return True
            return False

    def acquired_count(self) -> int:
        """Get acquired count."""
        with self._lock:
            return self._acquired


class ConnectionPool:
    """Simulated connection pool."""

    def __init__(self, max_connections: int) -> None:
        self._max: int = max_connections
        self._semaphore: threading.Semaphore = threading.Semaphore(max_connections)
        self._connections: list[int] = []
        self._next_id: int = 1
        self._lock: threading.Lock = threading.Lock()

    def connect(self) -> int | None:
        """Get a connection."""
        if self._semaphore.acquire(blocking=False):
            with self._lock:
                conn_id = self._next_id
                self._next_id += 1
                self._connections.append(conn_id)
                return conn_id
        return None

    def disconnect(self, conn_id: int) -> bool:
        """Release a connection."""
        with self._lock:
            if conn_id in self._connections:
                self._connections.remove(conn_id)
                self._semaphore.release()
                return True
            return False

    def active_connections(self) -> list[int]:
        """Get active connection IDs."""
        with self._lock:
            return self._connections.copy()


class RateLimiter:
    """Simple rate limiter using semaphore."""

    def __init__(self, max_concurrent: int) -> None:
        self._semaphore: threading.Semaphore = threading.Semaphore(max_concurrent)
        self._active: int = 0
        self._total: int = 0
        self._lock: threading.Lock = threading.Lock()

    def try_acquire(self) -> bool:
        """Try to acquire a slot."""
        if self._semaphore.acquire(blocking=False):
            with self._lock:
                self._active += 1
                self._total += 1
            return True
        return False

    def release(self) -> None:
        """Release a slot."""
        with self._lock:
            if self._active > 0:
                self._active -= 1
        self._semaphore.release()

    def active(self) -> int:
        """Get active count."""
        with self._lock:
            return self._active

    def total_acquired(self) -> int:
        """Get total acquisitions."""
        with self._lock:
            return self._total


def semaphore_count(permits: int, acquires: int, releases: int) -> int:
    """Simulate semaphore operations and return available count."""
    sem = threading.Semaphore(permits)
    acquired = 0

    for _ in range(acquires):
        if sem.acquire(blocking=False):
            acquired += 1

    released = min(releases, acquired)
    for _ in range(released):
        sem.release()

    return permits - acquired + released


def simulate_pool(size: int, ops: list[str]) -> list[int]:
    """Simulate pool operations."""
    pool = ResourcePool(size)
    results: list[int] = []

    for op in ops:
        if op == "acquire":
            pool.acquire()
        elif op == "release":
            pool.release()
        elif op == "available":
            results.append(pool.available())

    return results


def simulate_connections(max_conn: int, ops: list[str]) -> list[int]:
    """Simulate connection pool."""
    pool = ConnectionPool(max_conn)
    conn_map: dict[str, int] = {}
    results: list[int] = []

    for op in ops:
        if op.startswith("connect:"):
            name = op.split(":")[1]
            conn_id = pool.connect()
            if conn_id is not None:
                conn_map[name] = conn_id
                results.append(conn_id)
        elif op.startswith("disconnect:"):
            name = op.split(":")[1]
            if name in conn_map:
                pool.disconnect(conn_map[name])
                del conn_map[name]
        elif op == "count":
            results.append(len(pool.active_connections()))

    return results


def bounded_test(size: int, acquires: int, releases: int) -> tuple[int, int]:
    """Test bounded semaphore behavior."""
    pool = BoundedPool(size)

    for _ in range(acquires):
        pool.acquire()

    successful_releases = 0
    for _ in range(releases):
        if pool.release():
            successful_releases += 1

    return (pool.acquired_count(), successful_releases)


def main() -> int:
    parser = argparse.ArgumentParser(description="Thread semaphore CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # pool
    pool_p = subparsers.add_parser("pool", help="Resource pool")
    pool_p.add_argument("--size", type=int, default=5)
    pool_p.add_argument("ops", nargs="+")

    # connections
    conn_p = subparsers.add_parser("connections", help="Connection pool")
    conn_p.add_argument("--max", type=int, default=3)
    conn_p.add_argument("ops", nargs="+")

    # bounded
    bounded_p = subparsers.add_parser("bounded", help="Bounded semaphore test")
    bounded_p.add_argument("size", type=int)
    bounded_p.add_argument("acquires", type=int)
    bounded_p.add_argument("releases", type=int)

    args = parser.parse_args()

    if args.command == "pool":
        results = simulate_pool(args.size, args.ops)
        print(f"Available: {results}")

    elif args.command == "connections":
        results = simulate_connections(args.max, args.ops)
        print(f"Results: {results}")

    elif args.command == "bounded":
        acquired, released = bounded_test(args.size, args.acquires, args.releases)
        print(f"Acquired: {acquired}, Released: {released}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
