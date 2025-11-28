#!/usr/bin/env python3
"""Async Queue CLI.

Async queue patterns for producer-consumer scenarios.
"""

import argparse
import asyncio
import sys
from typing import Generic, TypeVar

T = TypeVar("T")


class AsyncQueue(Generic[T]):
    """Simple async queue implementation."""

    def __init__(self, maxsize: int = 0) -> None:
        self._items: list[T] = []
        self._maxsize: int = maxsize
        self._closed: bool = False

    async def put(self, item: T) -> None:
        """Put item into queue."""
        if self._closed:
            raise RuntimeError("Queue is closed")
        if self._maxsize > 0:
            while len(self._items) >= self._maxsize:
                await asyncio.sleep(0.001)  # Simple backpressure
        self._items.append(item)

    async def get(self) -> T:
        """Get item from queue."""
        while len(self._items) == 0:
            if self._closed:
                raise RuntimeError("Queue is closed and empty")
            await asyncio.sleep(0.001)
        return self._items.pop(0)

    def get_nowait(self) -> T:
        """Get item without waiting."""
        if len(self._items) == 0:
            raise RuntimeError("Queue is empty")
        return self._items.pop(0)

    def put_nowait(self, item: T) -> None:
        """Put item without waiting."""
        if self._closed:
            raise RuntimeError("Queue is closed")
        if self._maxsize > 0 and len(self._items) >= self._maxsize:
            raise RuntimeError("Queue is full")
        self._items.append(item)

    def qsize(self) -> int:
        """Get current queue size."""
        return len(self._items)

    def empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._items) == 0

    def full(self) -> bool:
        """Check if queue is full."""
        return self._maxsize > 0 and len(self._items) >= self._maxsize

    def close(self) -> None:
        """Close the queue."""
        self._closed = True

    def is_closed(self) -> bool:
        """Check if queue is closed."""
        return self._closed


class AsyncChannel(Generic[T]):
    """Async channel for communication between tasks."""

    def __init__(self) -> None:
        self._queue: AsyncQueue[T] = AsyncQueue()
        self._producers: int = 0
        self._consumers: int = 0

    def add_producer(self) -> None:
        """Register a producer."""
        self._producers += 1

    def remove_producer(self) -> None:
        """Unregister a producer."""
        self._producers -= 1
        if self._producers == 0:
            self._queue.close()

    def add_consumer(self) -> None:
        """Register a consumer."""
        self._consumers += 1

    def remove_consumer(self) -> None:
        """Unregister a consumer."""
        self._consumers -= 1

    async def send(self, item: T) -> None:
        """Send item to channel."""
        await self._queue.put(item)

    async def receive(self) -> T:
        """Receive item from channel."""
        return await self._queue.get()

    def is_closed(self) -> bool:
        """Check if channel is closed."""
        return self._queue.is_closed()


async def producer(queue: AsyncQueue[int], values: list[int]) -> int:
    """Producer that puts values into queue."""
    count = 0
    for value in values:
        await queue.put(value)
        count += 1
    return count


async def consumer(queue: AsyncQueue[int], count: int) -> list[int]:
    """Consumer that gets values from queue."""
    results: list[int] = []
    for _ in range(count):
        try:
            item = await queue.get()
            results.append(item)
        except RuntimeError:
            break
    return results


async def worker(queue: AsyncQueue[int], results: list[int]) -> int:
    """Worker that processes items from queue."""
    processed = 0
    while True:
        try:
            item = queue.get_nowait()
            results.append(item * 2)
            processed += 1
        except RuntimeError:
            break
    return processed


async def simple_producer_consumer(values: list[int]) -> list[int]:
    """Simple producer-consumer pattern."""
    queue: AsyncQueue[int] = AsyncQueue()

    # Produce all items
    for v in values:
        await queue.put(v)

    # Consume all items
    results: list[int] = []
    while not queue.empty():
        item = await queue.get()
        results.append(item)

    return results


async def bounded_queue_test(values: list[int], maxsize: int) -> list[int]:
    """Test bounded queue behavior."""
    queue: AsyncQueue[int] = AsyncQueue(maxsize)

    # Try to fill queue
    for v in values[:maxsize]:
        queue.put_nowait(v)

    # Drain queue
    results: list[int] = []
    while not queue.empty():
        results.append(queue.get_nowait())

    return results


async def transform_pipeline(values: list[int]) -> list[int]:
    """Transform values through queue pipeline."""
    queue1: AsyncQueue[int] = AsyncQueue()
    queue2: AsyncQueue[int] = AsyncQueue()

    # Stage 1: Add values to first queue
    for v in values:
        await queue1.put(v)

    # Stage 2: Transform and move to second queue
    while not queue1.empty():
        item = await queue1.get()
        await queue2.put(item * 2)

    # Stage 3: Collect results
    results: list[int] = []
    while not queue2.empty():
        results.append(await queue2.get())

    return results


async def filter_pipeline(values: list[int], threshold: int) -> list[int]:
    """Filter values through queue pipeline."""
    input_queue: AsyncQueue[int] = AsyncQueue()
    output_queue: AsyncQueue[int] = AsyncQueue()

    # Add input values
    for v in values:
        await input_queue.put(v)

    # Filter
    while not input_queue.empty():
        item = await input_queue.get()
        if item >= threshold:
            await output_queue.put(item)

    # Collect results
    results: list[int] = []
    while not output_queue.empty():
        results.append(await output_queue.get())

    return results


async def accumulator_pattern(values: list[int]) -> int:
    """Accumulate values from queue."""
    queue: AsyncQueue[int] = AsyncQueue()

    # Add values
    for v in values:
        await queue.put(v)

    # Accumulate
    total = 0
    while not queue.empty():
        total += await queue.get()

    return total


async def batch_collector(values: list[int], batch_size: int) -> list[list[int]]:
    """Collect values into batches."""
    queue: AsyncQueue[int] = AsyncQueue()

    # Add values
    for v in values:
        await queue.put(v)

    # Collect batches
    batches: list[list[int]] = []
    current_batch: list[int] = []

    while not queue.empty():
        item = await queue.get()
        current_batch.append(item)
        if len(current_batch) >= batch_size:
            batches.append(current_batch)
            current_batch = []

    if current_batch:
        batches.append(current_batch)

    return batches


async def priority_queue_simulation(items: list[tuple[int, int]]) -> list[int]:
    """Simulate priority queue using sorted insert."""
    queue: AsyncQueue[tuple[int, int]] = AsyncQueue()

    # Add items (priority, value)
    for item in items:
        await queue.put(item)

    # Drain and sort by priority
    all_items: list[tuple[int, int]] = []
    while not queue.empty():
        all_items.append(await queue.get())

    # Sort by priority (lower is higher priority)
    all_items.sort(key=lambda x: x[0])

    return [item[1] for item in all_items]


async def round_robin_queues(values: list[int], num_queues: int) -> list[list[int]]:
    """Distribute values across multiple queues."""
    queues: list[AsyncQueue[int]] = [AsyncQueue() for _ in range(num_queues)]

    # Distribute values
    for i, v in enumerate(values):
        await queues[i % num_queues].put(v)

    # Collect from each queue
    results: list[list[int]] = []
    for q in queues:
        queue_items: list[int] = []
        while not q.empty():
            queue_items.append(await q.get())
        results.append(queue_items)

    return results


async def dedup_queue(values: list[int]) -> list[int]:
    """Remove duplicates while maintaining order."""
    queue: AsyncQueue[int] = AsyncQueue()
    seen: set[int] = set()

    # Add values
    for v in values:
        await queue.put(v)

    # Dedup
    results: list[int] = []
    while not queue.empty():
        item = await queue.get()
        if item not in seen:
            seen.add(item)
            results.append(item)

    return results


def run_async(coro: object) -> object:
    """Run async function synchronously."""
    return asyncio.run(coro)  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Async queue CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # transform
    transform_p = subparsers.add_parser("transform", help="Transform pipeline")
    transform_p.add_argument("values", type=int, nargs="+")

    # filter
    filter_p = subparsers.add_parser("filter", help="Filter pipeline")
    filter_p.add_argument("values", type=int, nargs="+")
    filter_p.add_argument("--threshold", type=int, default=5)

    # batch
    batch_p = subparsers.add_parser("batch", help="Batch collector")
    batch_p.add_argument("values", type=int, nargs="+")
    batch_p.add_argument("--size", type=int, default=3)

    args = parser.parse_args()

    if args.command == "transform":
        result = run_async(transform_pipeline(args.values))
        print(f"Transformed: {result}")

    elif args.command == "filter":
        result = run_async(filter_pipeline(args.values, args.threshold))
        print(f"Filtered: {result}")

    elif args.command == "batch":
        result = run_async(batch_collector(args.values, args.size))
        print(f"Batches: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
