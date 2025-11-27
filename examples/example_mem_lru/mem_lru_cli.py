"""LRU Cache CLI.

Demonstrates LRU cache with O(1) operations using doubly-linked list + hash map.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    capacity: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


@dataclass
class Node(Generic[K, V]):
    """Doubly-linked list node."""

    key: K
    value: V
    prev: "Node[K, V] | None" = None
    next: "Node[K, V] | None" = None


class LRUCache(Generic[K, V]):
    """LRU Cache with O(1) get/put operations."""

    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._cache: dict[K, Node[K, V]] = {}
        # Sentinel nodes for easier list manipulation
        self._head: Node[K, V] = Node(None, None)  # type: ignore
        self._tail: Node[K, V] = Node(None, None)  # type: ignore
        self._head.next = self._tail
        self._tail.prev = self._head
        self._stats = CacheStats(capacity=capacity)

    def get(self, key: K) -> V | None:
        """Get value by key. Returns None if not found."""
        if key in self._cache:
            node = self._cache[key]
            self._move_to_front(node)
            self._stats.hits += 1
            return node.value
        self._stats.misses += 1
        return None

    def put(self, key: K, value: V) -> V | None:
        """Put key-value pair. Returns evicted value if any."""
        evicted: V | None = None

        if key in self._cache:
            node = self._cache[key]
            node.value = value
            self._move_to_front(node)
        else:
            if len(self._cache) >= self._capacity:
                evicted = self._evict_lru()

            node = Node(key, value)
            self._cache[key] = node
            self._add_to_front(node)
            self._stats.size = len(self._cache)

        return evicted

    def remove(self, key: K) -> V | None:
        """Remove key from cache. Returns value if found."""
        if key not in self._cache:
            return None

        node = self._cache.pop(key)
        self._remove_node(node)
        self._stats.size = len(self._cache)
        return node.value

    def contains(self, key: K) -> bool:
        """Check if key exists without affecting LRU order."""
        return key in self._cache

    def peek(self, key: K) -> V | None:
        """Get value without affecting LRU order."""
        if key in self._cache:
            return self._cache[key].value
        return None

    def clear(self) -> None:
        """Clear all entries."""
        self._cache.clear()
        self._head.next = self._tail
        self._tail.prev = self._head
        self._stats.size = 0

    def size(self) -> int:
        """Get current size."""
        return len(self._cache)

    def stats(self) -> CacheStats:
        """Get cache statistics."""
        return CacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            size=len(self._cache),
            capacity=self._capacity,
        )

    def keys(self) -> list[K]:
        """Get keys in LRU order (most recent first)."""
        result: list[K] = []
        node = self._head.next
        while node and node != self._tail:
            result.append(node.key)
            node = node.next
        return result

    def _add_to_front(self, node: Node[K, V]) -> None:
        """Add node right after head."""
        node.prev = self._head
        node.next = self._head.next
        if self._head.next:
            self._head.next.prev = node
        self._head.next = node

    def _remove_node(self, node: Node[K, V]) -> None:
        """Remove node from list."""
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev

    def _move_to_front(self, node: Node[K, V]) -> None:
        """Move existing node to front."""
        self._remove_node(node)
        self._add_to_front(node)

    def _evict_lru(self) -> V | None:
        """Evict least recently used entry."""
        lru = self._tail.prev
        if lru and lru != self._head:
            self._remove_node(lru)
            del self._cache[lru.key]
            self._stats.evictions += 1
            return lru.value
        return None


class TTLCache(Generic[K, V]):
    """Cache with time-to-live expiration (simulated)."""

    def __init__(self, capacity: int, ttl: int = 60) -> None:
        self._cache = LRUCache[K, tuple[V, int]](capacity)
        self._ttl = ttl
        self._current_time = 0

    def get(self, key: K) -> V | None:
        """Get value if not expired."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        value, expire_time = entry
        if self._current_time >= expire_time:
            self._cache.remove(key)
            return None
        return value

    def put(self, key: K, value: V) -> None:
        """Put with TTL."""
        expire_time = self._current_time + self._ttl
        self._cache.put(key, (value, expire_time))

    def tick(self, seconds: int = 1) -> None:
        """Advance time (for simulation)."""
        self._current_time += seconds

    def set_time(self, time: int) -> None:
        """Set current time."""
        self._current_time = time


def memoize(cache: LRUCache[Any, Any]) -> Callable:
    """Decorator to memoize function with LRU cache."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any) -> Any:
            key = args
            result = cache.get(key)
            if result is None:
                result = func(*args)
                cache.put(key, result)
            return result

        return wrapper

    return decorator


def simulate_lru(operations: list[str]) -> list[str]:
    """Simulate LRU cache operations."""
    results: list[str] = []
    cache: LRUCache[str, int] = LRUCache(3)

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "put":
            key, value = parts[1].split(",")
            evicted = cache.put(key, int(value))
            results.append(f"evicted={evicted}")
        elif cmd == "get":
            value = cache.get(parts[1])
            results.append(f"value={value}")
        elif cmd == "remove":
            value = cache.remove(parts[1])
            results.append(f"removed={value}")
        elif cmd == "size":
            results.append(str(cache.size()))
        elif cmd == "keys":
            results.append(str(cache.keys()))
        elif cmd == "stats":
            s = cache.stats()
            results.append(f"hits={s.hits} misses={s.misses} rate={s.hit_rate:.2f}")
        elif cmd == "clear":
            cache.clear()
            results.append("cleared")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mem_lru_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        print(f"Keys: {cache.keys()}")
        print(f"Get a: {cache.get('a')}")
        print(f"Keys after get: {cache.keys()}")
        cache.put("d", 4)  # Should evict b
        print(f"After adding d: {cache.keys()}")
        print(f"Stats: {cache.stats()}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
