"""Tests for mem_arena_cli.py"""

import pytest
from mem_arena_cli import (
    Arena,
    ArenaStats,
    ChunkedArena,
    StringArena,
    TypedArena,
    simulate_arena,
)


class TestArenaStats:
    def test_default(self):
        stats = ArenaStats()
        assert stats.total_allocated == 0
        assert stats.capacity == 0


class TestArena:
    def test_create(self):
        arena = Arena(1024)
        assert arena.available() == 1024
        assert arena.used() == 0

    def test_alloc_basic(self):
        arena = Arena(1024)
        offset = arena.alloc(64)
        assert offset == 0
        assert arena.used() >= 64

    def test_alloc_aligned(self):
        arena = Arena(1024)
        arena.alloc(1)  # Allocate 1 byte
        offset2 = arena.alloc(8, align=8)  # Should be aligned
        assert offset2 % 8 == 0

    def test_alloc_exhausted(self):
        arena = Arena(64)
        arena.alloc(32)
        with pytest.raises(MemoryError):
            arena.alloc(64)

    def test_alloc_bytes(self):
        arena = Arena(1024)
        data = b"hello world"
        offset = arena.alloc_bytes(data)
        assert arena.get_bytes(offset, len(data)) == data

    def test_reset(self):
        arena = Arena(1024)
        arena.alloc(256)
        arena.reset()
        assert arena.used() == 0
        assert arena.available() == 1024

    def test_stats(self):
        arena = Arena(1024)
        arena.alloc(64)
        arena.alloc(128)
        stats = arena.stats()
        assert stats.allocation_count == 2
        assert stats.total_allocated == 192
        assert stats.capacity == 1024


class TestTypedArena:
    def test_alloc(self):
        arena = TypedArena[dict](capacity=1024, obj_size=32)
        obj = arena.alloc({"key": "value"})
        assert obj.value == {"key": "value"}

    def test_count(self):
        arena = TypedArena[int](capacity=1024, obj_size=8)
        arena.alloc(1)
        arena.alloc(2)
        arena.alloc(3)
        assert arena.count() == 3

    def test_reset(self):
        arena = TypedArena[str](capacity=1024, obj_size=16)
        arena.alloc("hello")
        arena.reset()
        assert arena.count() == 0


class TestStringArena:
    def test_intern(self):
        strings = StringArena(1024)
        offset = strings.intern("hello")
        assert offset >= 0

    def test_intern_same_string(self):
        strings = StringArena(1024)
        offset1 = strings.intern("hello")
        offset2 = strings.intern("hello")
        assert offset1 == offset2

    def test_intern_different_strings(self):
        strings = StringArena(1024)
        offset1 = strings.intern("hello")
        offset2 = strings.intern("world")
        assert offset1 != offset2

    def test_get(self):
        strings = StringArena(1024)
        offset = strings.intern("test string")
        assert strings.get(offset) == "test string"

    def test_count(self):
        strings = StringArena(1024)
        strings.intern("a")
        strings.intern("b")
        strings.intern("a")  # Duplicate
        assert strings.count() == 2

    def test_reset(self):
        strings = StringArena(1024)
        strings.intern("test")
        strings.reset()
        assert strings.count() == 0


class TestChunkedArena:
    def test_create(self):
        arena = ChunkedArena(chunk_size=256)
        assert arena.chunk_count() == 1

    def test_alloc_single_chunk(self):
        arena = ChunkedArena(chunk_size=256)
        chunk_idx, offset = arena.alloc(64)
        assert chunk_idx == 0
        assert offset >= 0

    def test_alloc_new_chunk(self):
        arena = ChunkedArena(chunk_size=64)
        arena.alloc(32)
        arena.alloc(32)
        # This should trigger new chunk
        chunk_idx, _ = arena.alloc(32)
        assert arena.chunk_count() >= 2

    def test_large_allocation(self):
        arena = ChunkedArena(chunk_size=64)
        chunk_idx, offset = arena.alloc(128)  # Larger than chunk
        assert offset >= 0

    def test_reset(self):
        arena = ChunkedArena(chunk_size=64)
        arena.alloc(32)
        arena.alloc(32)
        arena.alloc(32)  # Creates new chunk
        arena.reset()
        assert arena.total_used() == 0

    def test_total_capacity(self):
        arena = ChunkedArena(chunk_size=256)
        assert arena.total_capacity() == 256
        arena.alloc(128)
        arena.alloc(128)
        arena.alloc(128)  # New chunk
        assert arena.total_capacity() >= 512


class TestSimulateArena:
    def test_alloc(self):
        result = simulate_arena(["alloc:64"])
        assert "offset=" in result[0]

    def test_alloc_bytes_and_get(self):
        result = simulate_arena([
            "alloc_bytes:hello",
            "get_bytes:0,5"
        ])
        assert result[1] == "hello"

    def test_reset(self):
        result = simulate_arena(["alloc:64", "reset:", "used:"])
        assert result[2] == "0"

    def test_used_available(self):
        result = simulate_arena(["used:", "available:"])
        assert result[0] == "0"
        assert result[1] == "1024"

    def test_stats(self):
        result = simulate_arena(["alloc:64", "stats:"])
        assert "allocated=" in result[1]


class TestArenaAlignment:
    def test_default_alignment(self):
        arena = Arena(256)
        # All allocations should be 8-byte aligned by default
        for _ in range(10):
            offset = arena.alloc(1)
            assert offset % 8 == 0

    def test_custom_alignment(self):
        arena = Arena(256)
        offset = arena.alloc(1, align=16)
        assert offset % 16 == 0


class TestArenaEdgeCases:
    def test_zero_size_alloc(self):
        arena = Arena(256)
        offset = arena.alloc(0)
        assert offset >= 0

    def test_exact_fit(self):
        arena = Arena(64)
        arena.alloc(64, align=1)  # Exact fit
        assert arena.available() == 0
