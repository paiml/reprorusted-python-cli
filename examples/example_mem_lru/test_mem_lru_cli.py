"""Tests for mem_lru_cli.py"""


from mem_lru_cli import (
    CacheStats,
    LRUCache,
    Node,
    TTLCache,
    memoize,
    simulate_lru,
)


class TestCacheStats:
    def test_default(self):
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0

    def test_hit_rate_zero(self):
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        stats = CacheStats(hits=80, misses=20)
        assert stats.hit_rate == 0.8


class TestNode:
    def test_create(self):
        node = Node("key", "value")
        assert node.key == "key"
        assert node.value == "value"


class TestLRUCache:
    def test_put_get(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_get_missing(self):
        cache: LRUCache[str, int] = LRUCache(3)
        assert cache.get("missing") is None

    def test_put_updates_value(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.put("a", 2)
        assert cache.get("a") == 2
        assert cache.size() == 1

    def test_eviction(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        evicted = cache.put("d", 4)  # Evicts "a"
        assert evicted == 1
        assert cache.get("a") is None
        assert cache.get("d") == 4

    def test_lru_order_on_get(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.get("a")  # Makes "a" most recent
        cache.put("d", 4)  # Should evict "b"
        assert cache.get("a") == 1
        assert cache.get("b") is None

    def test_lru_order_on_put(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("a", 10)  # Update "a", makes it most recent
        cache.put("d", 4)  # Should evict "b"
        assert cache.get("a") == 10
        assert cache.get("b") is None

    def test_remove(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        removed = cache.remove("a")
        assert removed == 1
        assert cache.get("a") is None
        assert cache.size() == 0

    def test_remove_missing(self):
        cache: LRUCache[str, int] = LRUCache(3)
        assert cache.remove("missing") is None

    def test_contains(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        assert cache.contains("a")
        assert not cache.contains("b")

    def test_peek(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.peek("a") == 1
        # Peek shouldn't affect order
        cache.put("d", 4)
        assert cache.peek("a") is None  # "a" should be evicted

    def test_clear(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert cache.size() == 0
        assert cache.get("a") is None

    def test_keys(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        keys = cache.keys()
        assert keys == ["c", "b", "a"]

    def test_stats(self):
        cache: LRUCache[str, int] = LRUCache(3)
        cache.put("a", 1)
        cache.get("a")  # Hit
        cache.get("b")  # Miss
        stats = cache.stats()
        assert stats.hits == 1
        assert stats.misses == 1


class TestTTLCache:
    def test_put_get(self):
        cache: TTLCache[str, int] = TTLCache(10, ttl=60)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_expiration(self):
        cache: TTLCache[str, int] = TTLCache(10, ttl=60)
        cache.put("a", 1)
        cache.tick(30)  # 30 seconds
        assert cache.get("a") == 1  # Still valid
        cache.tick(31)  # 61 seconds total
        assert cache.get("a") is None  # Expired

    def test_set_time(self):
        cache: TTLCache[str, int] = TTLCache(10, ttl=60)
        cache.put("a", 1)
        cache.set_time(100)
        assert cache.get("a") is None


class TestMemoize:
    def test_basic(self):
        cache: LRUCache[tuple, int] = LRUCache(10)
        call_count = [0]

        @memoize(cache)
        def expensive(n):
            call_count[0] += 1
            return n * 2

        assert expensive(5) == 10
        assert expensive(5) == 10  # Cached
        assert call_count[0] == 1

    def test_different_args(self):
        cache: LRUCache[tuple, int] = LRUCache(10)
        call_count = [0]

        @memoize(cache)
        def double(n):
            call_count[0] += 1
            return n * 2

        assert double(5) == 10
        assert double(3) == 6
        assert call_count[0] == 2


class TestSimulateLru:
    def test_put(self):
        result = simulate_lru(["put:a,1"])
        assert result == ["evicted=None"]

    def test_get(self):
        result = simulate_lru(["put:a,1", "get:a"])
        assert "value=1" in result[1]

    def test_get_miss(self):
        result = simulate_lru(["get:missing"])
        assert "value=None" in result[0]

    def test_eviction(self):
        result = simulate_lru([
            "put:a,1", "put:b,2", "put:c,3", "put:d,4"
        ])
        assert "evicted=1" in result[3]

    def test_keys(self):
        result = simulate_lru(["put:a,1", "put:b,2", "keys:"])
        assert "['b', 'a']" in result[2]

    def test_stats(self):
        result = simulate_lru(["put:a,1", "get:a", "get:b", "stats:"])
        assert "hits=1" in result[3]
        assert "misses=1" in result[3]


class TestLRUCacheEdgeCases:
    def test_capacity_one(self):
        cache: LRUCache[str, int] = LRUCache(1)
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.get("a") is None
        assert cache.get("b") == 2

    def test_integer_keys(self):
        cache: LRUCache[int, str] = LRUCache(3)
        cache.put(1, "one")
        cache.put(2, "two")
        assert cache.get(1) == "one"
