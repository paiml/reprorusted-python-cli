#!/usr/bin/env python3
"""Async Gather CLI.

Concurrent async execution patterns with asyncio.gather.
"""

import argparse
import asyncio
import sys


async def async_delay_value(value: int, delay_ms: int) -> int:
    """Return value after delay."""
    await asyncio.sleep(delay_ms / 1000.0)
    return value


async def async_compute(x: int) -> int:
    """Simulate computation."""
    await asyncio.sleep(0.001)  # Minimal delay
    return x * x


async def async_may_fail(value: int, should_fail: bool) -> int:
    """Operation that may fail."""
    if should_fail:
        raise ValueError(f"Failed for {value}")
    return value * 2


async def gather_all(values: list[int]) -> list[int]:
    """Gather all results concurrently."""
    tasks = [async_compute(v) for v in values]
    results = await asyncio.gather(*tasks)
    return list(results)


async def gather_with_exceptions(values: list[int], fail_indices: list[int]) -> list[object]:
    """Gather with return_exceptions=True."""
    tasks = [async_may_fail(v, i in fail_indices) for i, v in enumerate(values)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return list(results)


async def gather_first_completed(values: list[int]) -> int:
    """Get first completed result using wait."""
    tasks = [asyncio.create_task(async_compute(v)) for v in values]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    # Cancel pending tasks
    for task in pending:
        task.cancel()
    # Return first completed result
    for task in done:
        return task.result()
    return -1


async def gather_all_completed(values: list[int]) -> list[int]:
    """Wait for all tasks using wait."""
    tasks = [asyncio.create_task(async_compute(v)) for v in values]
    done, _ = await asyncio.wait(tasks)
    return [task.result() for task in done]


async def gather_with_timeout(values: list[int], timeout_sec: float) -> list[int]:
    """Gather with timeout."""
    tasks = [async_delay_value(v, v * 10) for v in values]  # Delay proportional to value
    try:
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout_sec)
        return list(results)
    except TimeoutError:
        return []


async def concurrent_map(values: list[int], transform: int) -> list[int]:
    """Map operation executed concurrently."""

    async def add_transform(v: int) -> int:
        await asyncio.sleep(0.001)
        return v + transform

    tasks = [add_transform(v) for v in values]
    results = await asyncio.gather(*tasks)
    return list(results)


async def concurrent_filter_compute(values: list[int], threshold: int) -> list[int]:
    """Filter values concurrently, then compute on results."""

    async def check_and_compute(v: int) -> tuple[bool, int]:
        await asyncio.sleep(0.001)
        return (v >= threshold, v * v if v >= threshold else 0)

    tasks = [check_and_compute(v) for v in values]
    results = await asyncio.gather(*tasks)
    return [r[1] for r in results if r[0]]


async def fan_out_fan_in(value: int) -> int:
    """Fan out to multiple operations, then combine."""

    async def op1(v: int) -> int:
        await asyncio.sleep(0.001)
        return v + 1

    async def op2(v: int) -> int:
        await asyncio.sleep(0.001)
        return v * 2

    async def op3(v: int) -> int:
        await asyncio.sleep(0.001)
        return v**2

    results = await asyncio.gather(op1(value), op2(value), op3(value))
    return sum(results)


async def parallel_reduce(values: list[int]) -> int:
    """Parallel tree reduction."""
    if len(values) == 0:
        return 0
    if len(values) == 1:
        return values[0]

    async def add(a: int, b: int) -> int:
        await asyncio.sleep(0.001)
        return a + b

    # Pair up and reduce
    current = values
    while len(current) > 1:
        tasks = []
        for i in range(0, len(current) - 1, 2):
            tasks.append(add(current[i], current[i + 1]))
        if len(current) % 2 == 1:
            # Capture last value in default argument to bind loop variable
            last_val = current[-1]

            async def identity(v: int = last_val) -> int:
                return v

            tasks.append(identity())
        results = await asyncio.gather(*tasks)
        current = list(results)

    return current[0]


async def concurrent_find_any(values: list[int], target: int) -> bool:
    """Find if any value matches target concurrently."""

    async def check(v: int) -> bool:
        await asyncio.sleep(0.001)
        return v == target

    tasks = [check(v) for v in values]
    results = await asyncio.gather(*tasks)
    return any(results)


async def concurrent_all_positive(values: list[int]) -> bool:
    """Check if all values are positive concurrently."""

    async def is_positive(v: int) -> bool:
        await asyncio.sleep(0.001)
        return v > 0

    tasks = [is_positive(v) for v in values]
    results = await asyncio.gather(*tasks)
    return all(results)


async def batch_process(values: list[int], batch_size: int) -> list[int]:
    """Process values in concurrent batches."""
    results: list[int] = []
    for i in range(0, len(values), batch_size):
        batch = values[i : i + batch_size]
        batch_results = await gather_all(batch)
        results.extend(batch_results)
    return results


async def parallel_max(values: list[int]) -> int:
    """Find maximum value using parallel comparison."""
    if len(values) == 0:
        return 0
    if len(values) == 1:
        return values[0]

    async def max_pair(a: int, b: int) -> int:
        await asyncio.sleep(0.001)
        return a if a > b else b

    current = values
    while len(current) > 1:
        tasks = []
        for i in range(0, len(current) - 1, 2):
            tasks.append(max_pair(current[i], current[i + 1]))
        if len(current) % 2 == 1:
            tasks.append(asyncio.sleep(0, current[-1]))  # type: ignore
        results = await asyncio.gather(*tasks)
        current = [r for r in results if isinstance(r, int)]

    return current[0]


async def parallel_sum(values: list[int]) -> int:
    """Sum values using parallel reduction."""
    if len(values) == 0:
        return 0

    results = await gather_all(values)  # Compute squares
    # Sum results
    total = 0
    for r in results:
        total += r
    return total


def run_async(coro: object) -> object:
    """Run async function synchronously."""
    return asyncio.run(coro)  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Async gather CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # gather
    gather_p = subparsers.add_parser("gather", help="Gather concurrent results")
    gather_p.add_argument("values", type=int, nargs="+")

    # fanout
    fanout_p = subparsers.add_parser("fanout", help="Fan out computation")
    fanout_p.add_argument("value", type=int)

    # batch
    batch_p = subparsers.add_parser("batch", help="Batch process")
    batch_p.add_argument("values", type=int, nargs="+")
    batch_p.add_argument("--size", type=int, default=3)

    args = parser.parse_args()

    if args.command == "gather":
        result = run_async(gather_all(args.values))
        print(f"Results: {result}")

    elif args.command == "fanout":
        result = run_async(fan_out_fan_in(args.value))
        print(f"Combined result: {result}")

    elif args.command == "batch":
        result = run_async(batch_process(args.values, args.size))
        print(f"Batch results: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
