"""Tests for mem_slab_cli.py"""

import pytest
from mem_slab_cli import (
    Entity,
    EntityPool,
    Slab,
    SlabAllocator,
    SlabStats,
    simulate_slab,
)


class TestSlabStats:
    def test_default(self):
        stats = SlabStats()
        assert stats.total_slots == 0
        assert stats.used_slots == 0


class TestSlab:
    def test_alloc(self):
        slab: Slab[dict] = Slab(4, dict)
        result = slab.alloc()
        assert result is not None
        slot_idx, obj = result
        assert isinstance(obj, dict)

    def test_alloc_all(self):
        slab: Slab[list] = Slab(4, list)
        for _ in range(4):
            assert slab.alloc() is not None
        assert slab.alloc() is None

    def test_free(self):
        slab: Slab[dict] = Slab(4, dict)
        result = slab.alloc()
        assert result is not None
        slot_idx, _ = result
        assert slab.free(slot_idx)

    def test_free_invalid(self):
        slab: Slab[dict] = Slab(4, dict)
        assert slab.free(999) is False

    def test_is_full(self):
        slab: Slab[dict] = Slab(2, dict)
        assert not slab.is_full()
        slab.alloc()
        slab.alloc()
        assert slab.is_full()

    def test_is_empty(self):
        slab: Slab[dict] = Slab(2, dict)
        assert slab.is_empty()
        result = slab.alloc()
        assert not slab.is_empty()
        if result:
            slab.free(result[0])
        assert slab.is_empty()

    def test_reuse_slot(self):
        slab: Slab[dict] = Slab(1, dict)
        result1 = slab.alloc()
        assert result1 is not None
        slot1, obj1 = result1
        slab.free(slot1)
        result2 = slab.alloc()
        assert result2 is not None
        slot2, obj2 = result2
        assert slot1 == slot2
        assert obj1 is obj2  # Same object reused


class TestSlabAllocator:
    def test_alloc(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=4, factory=dict)
        handle, obj = allocator.alloc()
        assert handle >= 0
        assert isinstance(obj, dict)

    def test_free(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=4, factory=dict)
        handle, _ = allocator.alloc()
        assert allocator.free(handle)

    def test_free_invalid(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=4, factory=dict)
        assert not allocator.free(999)

    def test_get(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=4, factory=dict)
        handle, obj = allocator.alloc()
        obj["key"] = "value"
        retrieved = allocator.get(handle)
        assert retrieved is not None
        assert retrieved["key"] == "value"

    def test_get_invalid(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=4, factory=dict)
        assert allocator.get(999) is None

    def test_creates_new_slab(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=2, factory=dict)
        allocator.alloc()
        allocator.alloc()
        stats = allocator.stats()
        assert stats.slab_count == 1
        allocator.alloc()  # Triggers new slab
        stats = allocator.stats()
        assert stats.slab_count == 2

    def test_max_slabs(self):
        allocator: SlabAllocator[dict] = SlabAllocator(
            slots_per_slab=1, factory=dict, max_slabs=2
        )
        allocator.alloc()
        allocator.alloc()
        with pytest.raises(MemoryError):
            allocator.alloc()

    def test_stats(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=4, factory=dict)
        allocator.alloc()
        allocator.alloc()
        stats = allocator.stats()
        assert stats.used_slots == 2
        assert stats.total_slots == 4

    def test_shrink(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=2, factory=dict)
        h1, _ = allocator.alloc()
        h2, _ = allocator.alloc()
        h3, _ = allocator.alloc()  # New slab
        allocator.free(h3)
        removed = allocator.shrink()
        assert removed == 1


class TestEntity:
    def test_create(self):
        e = Entity()
        assert e.x == 0.0
        assert e.health == 100

    def test_with_values(self):
        e = Entity(x=10.0, y=20.0, health=50, name="Test")
        assert e.x == 10.0
        assert e.name == "Test"


class TestEntityPool:
    def test_spawn(self):
        pool = EntityPool(slots_per_slab=8)
        handle = pool.spawn("Player", 5.0, 10.0)
        assert handle >= 0

    def test_get(self):
        pool = EntityPool(slots_per_slab=8)
        handle = pool.spawn("Player", 5.0, 10.0)
        entity = pool.get(handle)
        assert entity is not None
        assert entity.name == "Player"
        assert entity.x == 5.0

    def test_despawn(self):
        pool = EntityPool(slots_per_slab=8)
        handle = pool.spawn("Enemy")
        assert pool.despawn(handle)
        assert pool.get(handle) is None

    def test_count(self):
        pool = EntityPool(slots_per_slab=8)
        assert pool.count() == 0
        pool.spawn("A")
        pool.spawn("B")
        assert pool.count() == 2

    def test_stats(self):
        pool = EntityPool(slots_per_slab=4)
        pool.spawn("A")
        pool.spawn("B")
        stats = pool.stats()
        assert stats.used_slots == 2


class TestSimulateSlab:
    def test_alloc(self):
        result = simulate_slab(["alloc:"])
        assert "handle=0" in result[0]

    def test_free(self):
        result = simulate_slab(["alloc:", "free:0"])
        assert "freed=True" in result[1]

    def test_get(self):
        result = simulate_slab(["alloc:", "get:0"])
        assert "found=True" in result[1]

    def test_stats(self):
        result = simulate_slab(["alloc:", "stats:"])
        assert "used=1" in result[1]


class TestSlabEdgeCases:
    def test_many_allocations(self):
        allocator: SlabAllocator[int] = SlabAllocator(
            slots_per_slab=10, factory=lambda: 0, max_slabs=100
        )
        handles = []
        for _ in range(100):
            h, _ = allocator.alloc()
            handles.append(h)
        assert allocator.stats().used_slots == 100

    def test_alloc_free_pattern(self):
        allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=4, factory=dict)
        handles = []
        for _ in range(8):
            h, _ = allocator.alloc()
            handles.append(h)
        for h in handles[:4]:
            allocator.free(h)
        stats = allocator.stats()
        assert stats.used_slots == 4
