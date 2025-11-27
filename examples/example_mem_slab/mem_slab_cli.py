"""Slab Allocator CLI.

Demonstrates slab allocation for fixed-size objects.
"""

import sys
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class SlabStats:
    """Slab statistics."""

    total_slots: int = 0
    used_slots: int = 0
    free_slots: int = 0
    slab_count: int = 0


class Slab(Generic[T]):
    """A single slab containing fixed-size slots."""

    def __init__(self, slot_count: int, factory: Any) -> None:
        self._slot_count = slot_count
        self._factory = factory
        self._slots: list[T | None] = [None] * slot_count
        self._free_list: list[int] = list(range(slot_count))
        self._used: set[int] = set()

    def alloc(self) -> tuple[int, T] | None:
        """Allocate a slot. Returns (slot_index, object) or None."""
        if not self._free_list:
            return None

        slot_idx = self._free_list.pop()
        if self._slots[slot_idx] is None:
            self._slots[slot_idx] = self._factory()

        self._used.add(slot_idx)
        return slot_idx, self._slots[slot_idx]  # type: ignore

    def free(self, slot_idx: int) -> bool:
        """Free a slot."""
        if slot_idx not in self._used:
            return False

        self._used.remove(slot_idx)
        self._free_list.append(slot_idx)
        return True

    def is_full(self) -> bool:
        """Check if slab is full."""
        return len(self._free_list) == 0

    def is_empty(self) -> bool:
        """Check if slab is empty (all slots free)."""
        return len(self._used) == 0

    def used_count(self) -> int:
        """Get number of used slots."""
        return len(self._used)

    def free_count(self) -> int:
        """Get number of free slots."""
        return len(self._free_list)


class SlabAllocator(Generic[T]):
    """Slab allocator managing multiple slabs."""

    def __init__(
        self,
        slots_per_slab: int = 64,
        factory: Any = None,
        max_slabs: int = 100,
    ) -> None:
        self._slots_per_slab = slots_per_slab
        self._factory = factory or (lambda: {})
        self._max_slabs = max_slabs
        self._slabs: list[Slab[T]] = []
        self._allocations: dict[int, tuple[int, int]] = {}  # obj_id -> (slab_idx, slot_idx)
        self._next_id = 0

    def alloc(self) -> tuple[int, T]:
        """Allocate an object. Returns (handle, object)."""
        # Find a slab with free slots
        for slab_idx, slab in enumerate(self._slabs):
            if not slab.is_full():
                result = slab.alloc()
                if result:
                    slot_idx, obj = result
                    handle = self._next_id
                    self._next_id += 1
                    self._allocations[handle] = (slab_idx, slot_idx)
                    return handle, obj

        # Need new slab
        if len(self._slabs) >= self._max_slabs:
            raise MemoryError("Max slabs exceeded")

        new_slab: Slab[T] = Slab(self._slots_per_slab, self._factory)
        self._slabs.append(new_slab)
        result = new_slab.alloc()
        if result:
            slot_idx, obj = result
            handle = self._next_id
            self._next_id += 1
            self._allocations[handle] = (len(self._slabs) - 1, slot_idx)
            return handle, obj

        raise MemoryError("Failed to allocate")

    def free(self, handle: int) -> bool:
        """Free an allocation by handle."""
        if handle not in self._allocations:
            return False

        slab_idx, slot_idx = self._allocations.pop(handle)
        return self._slabs[slab_idx].free(slot_idx)

    def get(self, handle: int) -> T | None:
        """Get object by handle."""
        if handle not in self._allocations:
            return None

        slab_idx, slot_idx = self._allocations[handle]
        return self._slabs[slab_idx]._slots[slot_idx]

    def stats(self) -> SlabStats:
        """Get allocator statistics."""
        total = sum(s._slot_count for s in self._slabs)
        used = sum(s.used_count() for s in self._slabs)
        return SlabStats(
            total_slots=total,
            used_slots=used,
            free_slots=total - used,
            slab_count=len(self._slabs),
        )

    def shrink(self) -> int:
        """Remove empty slabs. Returns number removed."""
        original = len(self._slabs)
        # Only remove trailing empty slabs to avoid handle invalidation
        while self._slabs and self._slabs[-1].is_empty():
            self._slabs.pop()
        return original - len(self._slabs)


@dataclass
class Entity:
    """Game entity for slab allocation demo."""

    x: float = 0.0
    y: float = 0.0
    health: int = 100
    name: str = ""


class EntityPool:
    """Pool of game entities using slab allocation."""

    def __init__(self, slots_per_slab: int = 64) -> None:
        self._allocator: SlabAllocator[Entity] = SlabAllocator(
            slots_per_slab=slots_per_slab,
            factory=Entity,
        )
        self._entities: dict[int, Entity] = {}

    def spawn(self, name: str, x: float = 0.0, y: float = 0.0) -> int:
        """Spawn a new entity. Returns handle."""
        handle, entity = self._allocator.alloc()
        entity.name = name
        entity.x = x
        entity.y = y
        entity.health = 100
        self._entities[handle] = entity
        return handle

    def despawn(self, handle: int) -> bool:
        """Despawn an entity."""
        if handle in self._entities:
            del self._entities[handle]
            return self._allocator.free(handle)
        return False

    def get(self, handle: int) -> Entity | None:
        """Get entity by handle."""
        return self._entities.get(handle)

    def count(self) -> int:
        """Get active entity count."""
        return len(self._entities)

    def stats(self) -> SlabStats:
        """Get pool statistics."""
        return self._allocator.stats()


def simulate_slab(operations: list[str]) -> list[str]:
    """Simulate slab operations."""
    results: list[str] = []
    allocator: SlabAllocator[dict] = SlabAllocator(slots_per_slab=4, factory=dict)

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "alloc":
            handle, obj = allocator.alloc()
            results.append(f"handle={handle}")
        elif cmd == "free":
            handle = int(parts[1])
            success = allocator.free(handle)
            results.append(f"freed={success}")
        elif cmd == "get":
            handle = int(parts[1])
            obj = allocator.get(handle)
            results.append(f"found={obj is not None}")
        elif cmd == "stats":
            s = allocator.stats()
            results.append(f"used={s.used_slots} total={s.total_slots}")
        elif cmd == "shrink":
            removed = allocator.shrink()
            results.append(f"removed={removed}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mem_slab_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        pool = EntityPool(slots_per_slab=8)
        handles = [
            pool.spawn("Player", 0, 0),
            pool.spawn("Enemy1", 10, 5),
            pool.spawn("Enemy2", -5, 8),
        ]
        print(f"Spawned entities: {handles}")
        print(f"Stats: {pool.stats()}")

        pool.despawn(handles[1])
        print(f"After despawn: {pool.stats()}")
        print(f"Player: {pool.get(handles[0])}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
