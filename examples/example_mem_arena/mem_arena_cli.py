"""Arena Allocator CLI.

Demonstrates arena/bump allocation for fast memory management.
"""

import sys
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class ArenaStats:
    """Arena statistics."""

    total_allocated: int = 0
    total_deallocated: int = 0
    current_offset: int = 0
    capacity: int = 0
    allocation_count: int = 0


class Arena:
    """Simple arena allocator with bump allocation."""

    def __init__(self, capacity: int = 4096) -> None:
        self._buffer = bytearray(capacity)
        self._offset = 0
        self._capacity = capacity
        self._allocation_count = 0
        self._total_allocated = 0

    def alloc(self, size: int, align: int = 8) -> int:
        """Allocate memory from arena. Returns offset."""
        # Align offset
        aligned_offset = (self._offset + align - 1) & ~(align - 1)

        if aligned_offset + size > self._capacity:
            raise MemoryError(
                f"Arena exhausted: need {size}, have {self._capacity - aligned_offset}"
            )

        result = aligned_offset
        self._offset = aligned_offset + size
        self._allocation_count += 1
        self._total_allocated += size
        return result

    def alloc_bytes(self, data: bytes) -> int:
        """Allocate and copy bytes to arena."""
        offset = self.alloc(len(data), align=1)
        self._buffer[offset : offset + len(data)] = data
        return offset

    def get_bytes(self, offset: int, size: int) -> bytes:
        """Get bytes from arena at offset."""
        return bytes(self._buffer[offset : offset + size])

    def reset(self) -> None:
        """Reset arena without freeing memory."""
        self._offset = 0
        self._allocation_count = 0
        self._total_allocated = 0

    def stats(self) -> ArenaStats:
        """Get arena statistics."""
        return ArenaStats(
            total_allocated=self._total_allocated,
            total_deallocated=0,  # Arena doesn't deallocate
            current_offset=self._offset,
            capacity=self._capacity,
            allocation_count=self._allocation_count,
        )

    def used(self) -> int:
        """Get used bytes."""
        return self._offset

    def available(self) -> int:
        """Get available bytes."""
        return self._capacity - self._offset


@dataclass
class ArenaObject(Generic[T]):
    """Object allocated in arena."""

    arena: Arena
    offset: int
    size: int
    value: T


class TypedArena(Generic[T]):
    """Arena for objects of a specific type."""

    def __init__(self, capacity: int = 4096, obj_size: int = 64) -> None:
        self._arena = Arena(capacity)
        self._obj_size = obj_size
        self._objects: list[ArenaObject[T]] = []

    def alloc(self, value: T) -> ArenaObject[T]:
        """Allocate and store an object."""
        offset = self._arena.alloc(self._obj_size)
        obj = ArenaObject(self._arena, offset, self._obj_size, value)
        self._objects.append(obj)
        return obj

    def reset(self) -> None:
        """Reset arena and all objects."""
        self._arena.reset()
        self._objects.clear()

    def count(self) -> int:
        """Get number of allocated objects."""
        return len(self._objects)

    def stats(self) -> ArenaStats:
        """Get arena statistics."""
        return self._arena.stats()


class StringArena:
    """Specialized arena for string interning."""

    def __init__(self, capacity: int = 65536) -> None:
        self._arena = Arena(capacity)
        self._strings: dict[str, int] = {}
        self._offsets: dict[int, tuple[int, str]] = {}

    def intern(self, s: str) -> int:
        """Intern a string, returning its offset."""
        if s in self._strings:
            return self._strings[s]

        data = s.encode("utf-8")
        # Store length prefix + data
        size_bytes = len(data).to_bytes(4, "little")
        offset = self._arena.alloc_bytes(size_bytes + data)

        self._strings[s] = offset
        self._offsets[offset] = (len(data), s)
        return offset

    def get(self, offset: int) -> str:
        """Get interned string by offset."""
        if offset in self._offsets:
            return self._offsets[offset][1]

        # Read length and data
        size_bytes = self._arena.get_bytes(offset, 4)
        size = int.from_bytes(size_bytes, "little")
        data = self._arena.get_bytes(offset + 4, size)
        return data.decode("utf-8")

    def count(self) -> int:
        """Get number of interned strings."""
        return len(self._strings)

    def reset(self) -> None:
        """Reset arena."""
        self._arena.reset()
        self._strings.clear()
        self._offsets.clear()


class ChunkedArena:
    """Arena that grows by allocating chunks."""

    def __init__(self, chunk_size: int = 4096) -> None:
        self._chunk_size = chunk_size
        self._chunks: list[Arena] = [Arena(chunk_size)]
        self._current_chunk = 0

    def alloc(self, size: int, align: int = 8) -> tuple[int, int]:
        """Allocate. Returns (chunk_index, offset)."""
        try:
            offset = self._chunks[self._current_chunk].alloc(size, align)
            return self._current_chunk, offset
        except MemoryError:
            # Allocate new chunk
            new_chunk = Arena(max(self._chunk_size, size + align))
            self._chunks.append(new_chunk)
            self._current_chunk = len(self._chunks) - 1
            offset = new_chunk.alloc(size, align)
            return self._current_chunk, offset

    def reset(self) -> None:
        """Reset all chunks."""
        for chunk in self._chunks:
            chunk.reset()
        self._current_chunk = 0

    def chunk_count(self) -> int:
        """Get number of chunks."""
        return len(self._chunks)

    def total_capacity(self) -> int:
        """Get total capacity across chunks."""
        return sum(c._capacity for c in self._chunks)

    def total_used(self) -> int:
        """Get total used across chunks."""
        return sum(c.used() for c in self._chunks)


def simulate_arena(operations: list[str]) -> list[str]:
    """Simulate arena operations."""
    results: list[str] = []
    arena = Arena(1024)

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "alloc":
            size = int(parts[1])
            try:
                offset = arena.alloc(size)
                results.append(f"offset={offset}")
            except MemoryError as e:
                results.append(f"error:{e}")
        elif cmd == "alloc_bytes":
            data = parts[1].encode()
            offset = arena.alloc_bytes(data)
            results.append(f"offset={offset}")
        elif cmd == "get_bytes":
            offset, size = map(int, parts[1].split(","))
            data = arena.get_bytes(offset, size)
            results.append(data.decode())
        elif cmd == "reset":
            arena.reset()
            results.append("reset")
        elif cmd == "used":
            results.append(str(arena.used()))
        elif cmd == "available":
            results.append(str(arena.available()))
        elif cmd == "stats":
            s = arena.stats()
            results.append(f"allocated={s.total_allocated} count={s.allocation_count}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: mem_arena_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        arena = Arena(1024)
        offset1 = arena.alloc(64)
        offset2 = arena.alloc(128)
        print(f"Allocated at offsets: {offset1}, {offset2}")
        print(f"Used: {arena.used()}, Available: {arena.available()}")

        strings = StringArena()
        s1 = strings.intern("hello")
        s2 = strings.intern("world")
        s3 = strings.intern("hello")  # Reuses existing
        print(f"String offsets: {s1}, {s2}, {s3}")
        print(f"s1 == s3: {s1 == s3}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
