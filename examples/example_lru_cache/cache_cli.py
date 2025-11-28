#!/usr/bin/env python3
"""LRU Cache CLI.

Implementation of LRU (Least Recently Used) cache with various features.
"""

import argparse
import sys
from collections import OrderedDict


class LRUCache:
    """LRU Cache using OrderedDict."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> int | None:
        """Get value from cache. Returns None if not found."""
        if key not in self.cache:
            self.misses += 1
            return None

        self.hits += 1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: int) -> None:
        """Put value in cache. Evicts LRU item if at capacity."""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)

        self.cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete key from cache. Returns True if deleted."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all items from cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def size(self) -> int:
        """Get current size of cache."""
        return len(self.cache)

    def keys(self) -> list[str]:
        """Get all keys in LRU order (oldest first)."""
        return list(self.cache.keys())

    def values(self) -> list[int]:
        """Get all values in LRU order (oldest first)."""
        return list(self.cache.values())

    def items(self) -> list[tuple[str, int]]:
        """Get all items in LRU order (oldest first)."""
        return list(self.cache.items())

    def peek(self, key: str) -> int | None:
        """Get value without updating access order."""
        return self.cache.get(key)

    def contains(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache

    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "capacity": self.capacity,
            "size": self.size(),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate(),
        }

    def to_dict(self) -> dict:
        """Serialize cache to dict."""
        return {
            "capacity": self.capacity,
            "items": list(self.cache.items()),
            "hits": self.hits,
            "misses": self.misses,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LRUCache":
        """Deserialize cache from dict."""
        cache = cls(data["capacity"])
        for key, value in data["items"]:
            cache.cache[key] = value
        cache.hits = data.get("hits", 0)
        cache.misses = data.get("misses", 0)
        return cache


class TTLCache(LRUCache):
    """LRU Cache with TTL (time-to-live) support."""

    def __init__(self, capacity: int, default_ttl: int):
        super().__init__(capacity)
        self.default_ttl = default_ttl
        self.timestamps: dict[str, int] = {}
        self.ttls: dict[str, int] = {}
        self.current_time = 0

    def set_time(self, time: int) -> None:
        """Set current time for TTL checking."""
        self.current_time = time

    def put_with_ttl(self, key: str, value: int, ttl: int | None = None) -> None:
        """Put value with specific TTL."""
        self.put(key, value)
        self.timestamps[key] = self.current_time
        self.ttls[key] = ttl if ttl is not None else self.default_ttl

    def get(self, key: str) -> int | None:
        """Get value, checking TTL."""
        if key in self.cache:
            if self.is_expired(key):
                self.delete(key)
                self.misses += 1
                return None

        return super().get(key)

    def is_expired(self, key: str) -> bool:
        """Check if key is expired."""
        if key not in self.timestamps:
            return False

        elapsed = self.current_time - self.timestamps[key]
        ttl = self.ttls.get(key, self.default_ttl)
        return elapsed > ttl

    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        expired = [k for k in list(self.cache.keys()) if self.is_expired(k)]
        for key in expired:
            self.delete(key)
            if key in self.timestamps:
                del self.timestamps[key]
            if key in self.ttls:
                del self.ttls[key]
        return len(expired)


def cache_simulation(operations: list[tuple[str, str, int | None]], capacity: int) -> list[str]:
    """Simulate cache operations and return results."""
    cache = LRUCache(capacity)
    results = []

    for op, key, value in operations:
        if op == "get":
            result = cache.get(key)
            if result is not None:
                results.append(f"GET {key} = {result}")
            else:
                results.append(f"GET {key} = MISS")
        elif op == "put":
            cache.put(key, value)
            results.append(f"PUT {key} = {value}")
        elif op == "delete":
            if cache.delete(key):
                results.append(f"DELETE {key} = OK")
            else:
                results.append(f"DELETE {key} = NOT_FOUND")

    return results


def optimal_cache_size(access_pattern: list[str], max_capacity: int) -> dict:
    """Find optimal cache size for given access pattern."""
    results = {}

    for capacity in range(1, max_capacity + 1):
        cache = LRUCache(capacity)
        for key in access_pattern:
            if cache.get(key) is None:
                cache.put(key, 1)

        results[capacity] = {
            "hits": cache.hits,
            "misses": cache.misses,
            "hit_rate": cache.hit_rate(),
        }

    best_capacity = max(results.keys(), key=lambda c: results[c]["hit_rate"])
    return {
        "best_capacity": best_capacity,
        "best_hit_rate": results[best_capacity]["hit_rate"],
        "all_results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LRU Cache operations")
    parser.add_argument("--capacity", type=int, default=3, help="Cache capacity")
    parser.add_argument(
        "--mode",
        choices=["interactive", "simulate", "stats"],
        default="interactive",
        help="Operation mode",
    )
    parser.add_argument("operations", nargs="*", help="Operations: get:key or put:key:value")

    args = parser.parse_args()

    cache = LRUCache(args.capacity)

    if args.mode == "simulate" and args.operations:
        parsed_ops = []
        for op in args.operations:
            parts = op.split(":")
            if parts[0] == "get":
                parsed_ops.append(("get", parts[1], None))
            elif parts[0] == "put":
                parsed_ops.append(("put", parts[1], int(parts[2])))
            elif parts[0] == "delete":
                parsed_ops.append(("delete", parts[1], None))

        results = cache_simulation(parsed_ops, args.capacity)
        for result in results:
            print(result)
        return 0

    for op in args.operations:
        parts = op.split(":")
        if parts[0] == "get":
            result = cache.get(parts[1])
            if result is not None:
                print(f"GET {parts[1]} = {result}")
            else:
                print(f"GET {parts[1]} = MISS")
        elif parts[0] == "put":
            cache.put(parts[1], int(parts[2]))
            print(f"PUT {parts[1]} = {parts[2]}")
        elif parts[0] == "delete":
            if cache.delete(parts[1]):
                print(f"DELETE {parts[1]} = OK")
            else:
                print(f"DELETE {parts[1]} = NOT_FOUND")

    if args.mode == "stats":
        stats = cache.stats()
        print(f"Capacity: {stats['capacity']}")
        print(f"Size: {stats['size']}")
        print(f"Hits: {stats['hits']}")
        print(f"Misses: {stats['misses']}")
        print(f"Hit Rate: {stats['hit_rate']:.2%}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
