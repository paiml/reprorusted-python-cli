#!/usr/bin/env python3
"""Batch processor CLI.

Process items in batches with progress tracking.
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass


@dataclass
class BatchResult:
    """Result of processing a batch."""

    batch_index: int
    items_processed: int
    items_failed: int
    duration: float
    errors: list[str]


@dataclass
class ProcessingStats:
    """Overall processing statistics."""

    total_items: int
    processed_items: int
    failed_items: int
    total_batches: int
    completed_batches: int
    start_time: float
    end_time: float | None

    def __init__(self, total_items: int, batch_size: int):
        self.total_items = total_items
        self.processed_items = 0
        self.failed_items = 0
        self.total_batches = (total_items + batch_size - 1) // batch_size
        self.completed_batches = 0
        self.start_time = time.time()
        self.end_time = None

    def elapsed(self) -> float:
        """Get elapsed time."""
        end = self.end_time or time.time()
        return end - self.start_time

    def progress(self) -> float:
        """Get progress percentage."""
        if self.total_items == 0:
            return 100.0
        return (self.processed_items / self.total_items) * 100

    def items_per_second(self) -> float:
        """Get processing rate."""
        elapsed = self.elapsed()
        if elapsed == 0:
            return 0.0
        return self.processed_items / elapsed

    def estimated_remaining(self) -> float:
        """Get estimated time remaining."""
        rate = self.items_per_second()
        if rate == 0:
            return 0.0
        remaining_items = self.total_items - self.processed_items
        return remaining_items / rate

    def to_dict(self) -> dict:
        return {
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "failed_items": self.failed_items,
            "total_batches": self.total_batches,
            "completed_batches": self.completed_batches,
            "elapsed_seconds": self.elapsed(),
            "progress_percent": self.progress(),
            "items_per_second": self.items_per_second(),
            "estimated_remaining_seconds": self.estimated_remaining(),
        }


def chunk_list(items: list, chunk_size: int) -> list[list]:
    """Split list into chunks."""
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def process_item_dummy(item: str, fail_rate: float = 0.0) -> tuple[bool, str]:
    """Dummy item processor for demonstration."""
    import random

    if random.random() < fail_rate:
        return False, f"Failed to process: {item}"
    return True, ""


def process_batch(
    batch: list,
    batch_index: int,
    processor=None,
    delay: float = 0.0,
) -> BatchResult:
    """Process a single batch of items."""
    if processor is None:
        processor = process_item_dummy

    start = time.time()
    processed = 0
    failed = 0
    errors = []

    for item in batch:
        success, error = processor(item)
        if success:
            processed += 1
        else:
            failed += 1
            errors.append(error)

        if delay > 0:
            time.sleep(delay)

    return BatchResult(
        batch_index=batch_index,
        items_processed=processed,
        items_failed=failed,
        duration=time.time() - start,
        errors=errors,
    )


def process_all(
    items: list,
    batch_size: int,
    processor=None,
    delay: float = 0.0,
    on_batch_complete=None,
) -> tuple[ProcessingStats, list[BatchResult]]:
    """Process all items in batches."""
    stats = ProcessingStats(len(items), batch_size)
    batches = chunk_list(items, batch_size)
    results = []

    for i, batch in enumerate(batches):
        result = process_batch(batch, i, processor, delay)
        results.append(result)

        stats.processed_items += result.items_processed
        stats.failed_items += result.items_failed
        stats.completed_batches += 1

        if on_batch_complete:
            on_batch_complete(stats, result)

    stats.end_time = time.time()
    return stats, results


def format_progress(stats: ProcessingStats, width: int = 30) -> str:
    """Format progress as a status line."""
    progress = stats.progress()
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)

    rate = stats.items_per_second()
    remaining = stats.estimated_remaining()

    return (
        f"[{bar}] {progress:.1f}% "
        f"({stats.processed_items}/{stats.total_items}) "
        f"{rate:.1f}/s "
        f"ETA: {remaining:.1f}s"
    )


def generate_items(count: int, prefix: str = "item") -> list[str]:
    """Generate test items."""
    return [f"{prefix}_{i}" for i in range(count)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch processing tool")
    parser.add_argument("input", nargs="?", help="Input file with items (one per line)")
    parser.add_argument(
        "-n", "--count", type=int, default=100, help="Number of items to generate (if no input)"
    )
    parser.add_argument("-b", "--batch-size", type=int, default=10, help="Batch size")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay per item (seconds)")
    parser.add_argument(
        "--fail-rate", type=float, default=0.0, help="Simulated failure rate (0.0 to 1.0)"
    )
    parser.add_argument("--progress", action="store_true", help="Show progress bar")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--dry-run", action="store_true", help="Show batch plan without processing")

    args = parser.parse_args()

    # Get items
    if args.input:
        if args.input == "-":
            items = [line.strip() for line in sys.stdin if line.strip()]
        else:
            with open(args.input) as f:
                items = [line.strip() for line in f if line.strip()]
    else:
        items = generate_items(args.count)

    if not items:
        print("No items to process")
        return 0

    batches = chunk_list(items, args.batch_size)

    if args.dry_run:
        print(f"Total items: {len(items)}")
        print(f"Batch size: {args.batch_size}")
        print(f"Total batches: {len(batches)}")
        print("\nBatch plan:")
        for i, batch in enumerate(batches):
            print(f"  Batch {i + 1}: {len(batch)} items")
        return 0

    # Create processor with fail rate
    def processor(item):
        return process_item_dummy(item, args.fail_rate)

    # Progress callback
    def on_progress(stats, result):
        if args.progress:
            print(f"\r{format_progress(stats)}", end="", flush=True)

    stats, results = process_all(
        items,
        args.batch_size,
        processor,
        args.delay,
        on_progress,
    )

    if args.progress:
        print()  # Newline after progress bar

    if args.json:
        output = {
            "stats": stats.to_dict(),
            "batches": [
                {
                    "index": r.batch_index,
                    "processed": r.items_processed,
                    "failed": r.items_failed,
                    "duration": r.duration,
                    "errors": r.errors,
                }
                for r in results
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print("\nProcessing complete:")
        print(f"  Total items: {stats.total_items}")
        print(f"  Processed: {stats.processed_items}")
        print(f"  Failed: {stats.failed_items}")
        print(f"  Total time: {stats.elapsed():.2f}s")
        print(f"  Rate: {stats.items_per_second():.1f} items/s")

        if stats.failed_items > 0:
            print(f"\nErrors ({stats.failed_items}):")
            for result in results:
                for error in result.errors[:5]:  # Limit errors shown
                    print(f"  - {error}")

    return 0 if stats.failed_items == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
