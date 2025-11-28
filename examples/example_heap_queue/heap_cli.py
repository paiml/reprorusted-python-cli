#!/usr/bin/env python3
"""Heap Queue CLI.

Min heap and max heap implementations with priority queue operations.
"""

import argparse
import sys


class MinHeap:
    """Min heap implementation."""

    def __init__(self):
        self.heap: list[int] = []

    def parent(self, i: int) -> int:
        """Get parent index."""
        return (i - 1) // 2

    def left_child(self, i: int) -> int:
        """Get left child index."""
        return 2 * i + 1

    def right_child(self, i: int) -> int:
        """Get right child index."""
        return 2 * i + 2

    def push(self, value: int) -> None:
        """Push a value onto the heap."""
        self.heap.append(value)
        self._sift_up(len(self.heap) - 1)

    def pop(self) -> int | None:
        """Pop and return the minimum value."""
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def peek(self) -> int | None:
        """Return the minimum value without removing it."""
        return self.heap[0] if self.heap else None

    def _sift_up(self, i: int) -> None:
        """Move element up to maintain heap property."""
        while i > 0:
            parent = self.parent(i)
            if self.heap[i] < self.heap[parent]:
                self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        """Move element down to maintain heap property."""
        size = len(self.heap)

        while True:
            smallest = i
            left = self.left_child(i)
            right = self.right_child(i)

            if left < size and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < size and self.heap[right] < self.heap[smallest]:
                smallest = right

            if smallest != i:
                self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
                i = smallest
            else:
                break

    def size(self) -> int:
        """Return the number of elements."""
        return len(self.heap)

    def is_empty(self) -> bool:
        """Check if heap is empty."""
        return len(self.heap) == 0

    def to_list(self) -> list[int]:
        """Return heap as list."""
        return self.heap.copy()


class MaxHeap:
    """Max heap implementation using negation."""

    def __init__(self):
        self.min_heap = MinHeap()

    def push(self, value: int) -> None:
        """Push a value onto the heap."""
        self.min_heap.push(-value)

    def pop(self) -> int | None:
        """Pop and return the maximum value."""
        result = self.min_heap.pop()
        return -result if result is not None else None

    def peek(self) -> int | None:
        """Return the maximum value without removing it."""
        result = self.min_heap.peek()
        return -result if result is not None else None

    def size(self) -> int:
        """Return the number of elements."""
        return self.min_heap.size()

    def is_empty(self) -> bool:
        """Check if heap is empty."""
        return self.min_heap.is_empty()

    def to_list(self) -> list[int]:
        """Return heap as list (negated back)."""
        return [-x for x in self.min_heap.to_list()]


class PriorityQueue:
    """Priority queue with key-value pairs."""

    def __init__(self, max_priority: bool = False):
        self.entries: list[tuple[int, str]] = []
        self.max_priority = max_priority

    def push(self, priority: int, value: str) -> None:
        """Push item with priority."""
        self.entries.append((priority, value))
        self._sift_up(len(self.entries) - 1)

    def pop(self) -> tuple[int, str] | None:
        """Pop highest priority item."""
        if not self.entries:
            return None

        if len(self.entries) == 1:
            return self.entries.pop()

        root = self.entries[0]
        self.entries[0] = self.entries.pop()
        self._sift_down(0)
        return root

    def peek(self) -> tuple[int, str] | None:
        """Return highest priority item without removing."""
        return self.entries[0] if self.entries else None

    def _compare(self, a: tuple[int, str], b: tuple[int, str]) -> bool:
        """Compare two entries based on priority direction."""
        if self.max_priority:
            return a[0] > b[0]
        return a[0] < b[0]

    def _sift_up(self, i: int) -> None:
        """Move element up to maintain heap property."""
        while i > 0:
            parent = (i - 1) // 2
            if self._compare(self.entries[i], self.entries[parent]):
                self.entries[i], self.entries[parent] = self.entries[parent], self.entries[i]
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        """Move element down to maintain heap property."""
        size = len(self.entries)

        while True:
            best = i
            left = 2 * i + 1
            right = 2 * i + 2

            if left < size and self._compare(self.entries[left], self.entries[best]):
                best = left
            if right < size and self._compare(self.entries[right], self.entries[best]):
                best = right

            if best != i:
                self.entries[i], self.entries[best] = self.entries[best], self.entries[i]
                i = best
            else:
                break

    def size(self) -> int:
        """Return the number of elements."""
        return len(self.entries)

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self.entries) == 0


def heapify(arr: list[int]) -> list[int]:
    """Convert array to min heap in-place."""
    result = arr.copy()
    n = len(result)

    for i in range(n // 2 - 1, -1, -1):
        _heapify_down(result, n, i)

    return result


def _heapify_down(arr: list[int], n: int, i: int) -> None:
    """Helper for heapify."""
    smallest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] < arr[smallest]:
        smallest = left
    if right < n and arr[right] < arr[smallest]:
        smallest = right

    if smallest != i:
        arr[i], arr[smallest] = arr[smallest], arr[i]
        _heapify_down(arr, n, smallest)


def heap_sort(arr: list[int], reverse: bool = False) -> list[int]:
    """Sort array using heap sort."""
    if not arr:
        return []

    result = arr.copy()
    n = len(result)

    # Build max heap for ascending, min heap for descending
    for i in range(n // 2 - 1, -1, -1):
        _heap_sort_down(result, n, i, reverse)

    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        result[0], result[i] = result[i], result[0]
        _heap_sort_down(result, i, 0, reverse)

    return result


def _heap_sort_down(arr: list[int], n: int, i: int, reverse: bool) -> None:
    """Helper for heap sort."""
    extreme = i
    left = 2 * i + 1
    right = 2 * i + 2

    if reverse:
        if left < n and arr[left] < arr[extreme]:
            extreme = left
        if right < n and arr[right] < arr[extreme]:
            extreme = right
    else:
        if left < n and arr[left] > arr[extreme]:
            extreme = left
        if right < n and arr[right] > arr[extreme]:
            extreme = right

    if extreme != i:
        arr[i], arr[extreme] = arr[extreme], arr[i]
        _heap_sort_down(arr, n, extreme, reverse)


def k_smallest(arr: list[int], k: int) -> list[int]:
    """Find k smallest elements."""
    if k <= 0 or not arr:
        return []

    heap = MinHeap()
    for x in arr:
        heap.push(x)

    result = []
    for _ in range(min(k, len(arr))):
        val = heap.pop()
        if val is not None:
            result.append(val)

    return result


def k_largest(arr: list[int], k: int) -> list[int]:
    """Find k largest elements."""
    if k <= 0 or not arr:
        return []

    heap = MaxHeap()
    for x in arr:
        heap.push(x)

    result = []
    for _ in range(min(k, len(arr))):
        val = heap.pop()
        if val is not None:
            result.append(val)

    return result


def merge_k_sorted_arrays(arrays: list[list[int]]) -> list[int]:
    """Merge k sorted arrays using a min heap."""
    if not arrays:
        return []

    result = []
    # Track (value, array_index, element_index)
    heap: list[tuple[int, int, int]] = []

    # Initialize with first element from each array
    for i, arr in enumerate(arrays):
        if arr:
            heap.append((arr[0], i, 0))

    # Heapify
    n = len(heap)
    for i in range(n // 2 - 1, -1, -1):
        _heapify_tuple(heap, n, i)

    while heap:
        # Extract min
        val, arr_idx, elem_idx = heap[0]
        result.append(val)

        # Replace with next element from same array or last element
        next_idx = elem_idx + 1
        if next_idx < len(arrays[arr_idx]):
            heap[0] = (arrays[arr_idx][next_idx], arr_idx, next_idx)
        else:
            heap[0] = heap[-1]
            heap.pop()

        if heap:
            _heapify_tuple(heap, len(heap), 0)

    return result


def _heapify_tuple(arr: list[tuple[int, int, int]], n: int, i: int) -> None:
    """Heapify for tuple comparisons."""
    smallest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left][0] < arr[smallest][0]:
        smallest = left
    if right < n and arr[right][0] < arr[smallest][0]:
        smallest = right

    if smallest != i:
        arr[i], arr[smallest] = arr[smallest], arr[i]
        _heapify_tuple(arr, n, smallest)


def is_valid_heap(arr: list[int], max_heap: bool = False) -> bool:
    """Check if array represents a valid heap."""
    n = len(arr)

    for i in range((n - 2) // 2 + 1):
        left = 2 * i + 1
        right = 2 * i + 2

        if max_heap:
            if left < n and arr[i] < arr[left]:
                return False
            if right < n and arr[i] < arr[right]:
                return False
        else:
            if left < n and arr[i] > arr[left]:
                return False
            if right < n and arr[i] > arr[right]:
                return False

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Heap queue operations")
    parser.add_argument("values", nargs="*", type=int, help="Values to process")
    parser.add_argument(
        "--mode",
        choices=["heap", "sort", "ksmallest", "klargest", "validate"],
        default="heap",
        help="Operation mode",
    )
    parser.add_argument("--max", action="store_true", help="Use max heap")
    parser.add_argument("-k", type=int, default=3, help="K for k-smallest/largest")

    args = parser.parse_args()

    if not args.values:
        values = [int(x) for x in sys.stdin.read().split()]
    else:
        values = args.values

    if args.mode == "heap":
        result = heapify(values)
        if args.max:
            result = [-x for x in heapify([-x for x in values])]
        print(f"Heapified: {' '.join(map(str, result))}")

    elif args.mode == "sort":
        result = heap_sort(values, reverse=args.max)
        print(f"Sorted: {' '.join(map(str, result))}")

    elif args.mode == "ksmallest":
        result = k_smallest(values, args.k)
        print(f"K smallest: {' '.join(map(str, result))}")

    elif args.mode == "klargest":
        result = k_largest(values, args.k)
        print(f"K largest: {' '.join(map(str, result))}")

    elif args.mode == "validate":
        if is_valid_heap(values, args.max):
            heap_type = "max" if args.max else "min"
            print(f"Valid {heap_type} heap: Yes")
        else:
            print("Valid heap: No")

    return 0


if __name__ == "__main__":
    sys.exit(main())
