"""Tests for cache_cli.py"""

import pytest
from cache_cli import (
    LRUCache,
    TTLCache,
    cache_simulation,
    optimal_cache_size,
)


class TestLRUCache:
    def test_init(self):
        cache = LRUCache(3)
        assert cache.capacity == 3
        assert cache.size() == 0

    def test_put_and_get(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_get_miss(self):
        cache = LRUCache(3)
        assert cache.get("missing") is None

    def test_eviction(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Should evict "a"

        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_access_updates_order(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # Access "a" to make it recently used
        cache.put("c", 3)  # Should evict "b"

        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_update_value(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("a", 10)
        assert cache.get("a") == 10
        assert cache.size() == 1

    def test_delete(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        assert cache.delete("a") is True
        assert cache.get("a") is None

    def test_delete_missing(self):
        cache = LRUCache(3)
        assert cache.delete("missing") is False

    def test_clear(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()

        assert cache.size() == 0
        assert cache.get("a") is None

    def test_keys(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)

        assert cache.keys() == ["a", "b", "c"]

    def test_values(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)

        assert cache.values() == [1, 2]

    def test_items(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)

        assert cache.items() == [("a", 1), ("b", 2)]

    def test_peek(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)

        # Peek doesn't update access order
        assert cache.peek("a") == 1

        cache.put("c", 3)  # Should still evict "a" since peek didn't update
        assert cache.get("a") is None

    def test_contains(self):
        cache = LRUCache(3)
        cache.put("a", 1)

        assert cache.contains("a") is True
        assert cache.contains("b") is False

    def test_hit_rate(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)

        cache.get("a")  # Hit
        cache.get("b")  # Hit
        cache.get("c")  # Miss

        assert cache.hit_rate() == pytest.approx(2 / 3, rel=0.01)

    def test_stats(self):
        cache = LRUCache(5)
        cache.put("a", 1)
        cache.get("a")
        cache.get("missing")

        stats = cache.stats()
        assert stats["capacity"] == 5
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_to_from_dict(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")
        cache.get("c")  # Miss

        original_hits = cache.hits
        original_misses = cache.misses
        data = cache.to_dict()
        restored = LRUCache.from_dict(data)

        assert restored.capacity == 3
        # Check hits/misses before accessing (get increments counters)
        assert restored.hits == original_hits
        assert restored.misses == original_misses
        # Now verify data was restored correctly
        assert restored.get("a") == 1
        assert restored.get("b") == 2


class TestTTLCache:
    def test_init(self):
        cache = TTLCache(3, 10)
        assert cache.capacity == 3
        assert cache.default_ttl == 10

    def test_put_with_ttl(self):
        cache = TTLCache(3, 10)
        cache.set_time(0)
        cache.put_with_ttl("a", 1, 5)

        assert cache.get("a") == 1

    def test_expired(self):
        cache = TTLCache(3, 10)
        cache.set_time(0)
        cache.put_with_ttl("a", 1, 5)

        cache.set_time(10)  # Past TTL
        assert cache.get("a") is None

    def test_not_expired(self):
        cache = TTLCache(3, 10)
        cache.set_time(0)
        cache.put_with_ttl("a", 1, 10)

        cache.set_time(5)  # Within TTL
        assert cache.get("a") == 1

    def test_default_ttl(self):
        cache = TTLCache(3, 5)
        cache.set_time(0)
        cache.put_with_ttl("a", 1)  # Uses default TTL of 5

        cache.set_time(3)
        assert cache.get("a") == 1

        cache.set_time(10)
        assert cache.get("a") is None

    def test_cleanup_expired(self):
        cache = TTLCache(5, 10)
        cache.set_time(0)
        cache.put_with_ttl("a", 1, 5)
        cache.put_with_ttl("b", 2, 15)
        cache.put_with_ttl("c", 3, 5)

        cache.set_time(10)
        removed = cache.cleanup_expired()

        assert removed == 2
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") is None


class TestCacheSimulation:
    def test_basic(self):
        ops = [
            ("put", "a", 1),
            ("put", "b", 2),
            ("get", "a", None),
            ("get", "c", None),
        ]
        results = cache_simulation(ops, 3)

        assert results[0] == "PUT a = 1"
        assert results[1] == "PUT b = 2"
        assert results[2] == "GET a = 1"
        assert results[3] == "GET c = MISS"

    def test_eviction(self):
        ops = [
            ("put", "a", 1),
            ("put", "b", 2),
            ("put", "c", 3),
            ("get", "a", None),  # Should be evicted
        ]
        results = cache_simulation(ops, 2)

        assert results[3] == "GET a = MISS"

    def test_delete(self):
        ops = [
            ("put", "a", 1),
            ("delete", "a", None),
            ("delete", "b", None),
        ]
        results = cache_simulation(ops, 3)

        assert results[1] == "DELETE a = OK"
        assert results[2] == "DELETE b = NOT_FOUND"


class TestOptimalCacheSize:
    def test_basic(self):
        pattern = ["a", "b", "c", "a", "b", "c", "d", "a", "b"]
        result = optimal_cache_size(pattern, 5)

        assert "best_capacity" in result
        assert "best_hit_rate" in result
        assert result["best_capacity"] >= 1
        assert result["best_capacity"] <= 5

    def test_repeating_pattern(self):
        pattern = ["a", "a", "a", "a"]  # All same key
        result = optimal_cache_size(pattern, 3)

        # With repeating keys, even capacity 1 has high hit rate
        assert result["best_hit_rate"] >= 0.5

    def test_unique_pattern(self):
        pattern = ["a", "b", "c", "d", "e"]  # All unique - no repeats
        result = optimal_cache_size(pattern, 5)

        # With unique keys and no repetition, hit rate will be 0
        # So any capacity gives the same result
        assert result["best_hit_rate"] == 0.0
        assert "all_results" in result
