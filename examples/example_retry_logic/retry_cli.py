#!/usr/bin/env python3
"""Retry logic CLI.

Retry strategies with exponential backoff.
"""

import argparse
import random
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class RetryStrategy(Enum):
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"


@dataclass
class RetryConfig:
    """Retry configuration."""

    max_attempts: int
    initial_delay: float
    max_delay: float
    strategy: RetryStrategy
    jitter: float  # 0.0 to 1.0
    timeout: float | None  # Total timeout

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: float = 0.0,
        timeout: float | None = None,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.jitter = jitter
        self.timeout = timeout


@dataclass
class RetryResult:
    """Result of a retry operation."""

    success: bool
    attempts: int
    total_time: float
    final_error: str | None
    delays: list[float]


def calculate_delay(
    config: RetryConfig,
    attempt: int,
) -> float:
    """Calculate delay for a given attempt."""
    if config.strategy == RetryStrategy.FIXED:
        base_delay = config.initial_delay

    elif config.strategy == RetryStrategy.LINEAR:
        base_delay = config.initial_delay * attempt

    elif config.strategy == RetryStrategy.EXPONENTIAL:
        base_delay = config.initial_delay * (2 ** (attempt - 1))

    elif config.strategy == RetryStrategy.FIBONACCI:
        # Fibonacci sequence for delays
        a, b = 1, 1
        for _ in range(attempt - 1):
            a, b = b, a + b
        base_delay = config.initial_delay * a

    else:
        base_delay = config.initial_delay

    # Apply jitter
    if config.jitter > 0:
        jitter_range = base_delay * config.jitter
        base_delay += random.uniform(-jitter_range, jitter_range)

    # Cap at max delay
    return min(max(0, base_delay), config.max_delay)


def simulate_operation(
    success_probability: float,
    fail_until: int = 0,
    attempt: int = 0,
) -> tuple[bool, str]:
    """Simulate an operation that might fail.

    Returns (success, error_message).
    """
    if attempt < fail_until:
        return False, f"Simulated failure (attempt {attempt + 1})"

    if random.random() < success_probability:
        return True, ""

    return False, "Random failure"


def retry_operation(
    operation: Callable[[], tuple[bool, str]],
    config: RetryConfig,
    verbose: bool = False,
) -> RetryResult:
    """Retry an operation according to config."""
    start_time = time.time()
    delays = []

    for attempt in range(1, config.max_attempts + 1):
        # Check timeout
        if config.timeout:
            elapsed = time.time() - start_time
            if elapsed >= config.timeout:
                return RetryResult(
                    success=False,
                    attempts=attempt - 1,
                    total_time=elapsed,
                    final_error="Timeout exceeded",
                    delays=delays,
                )

        # Execute operation
        success, error = operation()

        if success:
            return RetryResult(
                success=True,
                attempts=attempt,
                total_time=time.time() - start_time,
                final_error=None,
                delays=delays,
            )

        if verbose:
            print(f"Attempt {attempt} failed: {error}")

        # Calculate delay for next attempt
        if attempt < config.max_attempts:
            delay = calculate_delay(config, attempt)
            delays.append(delay)

            if verbose:
                print(f"Waiting {delay:.2f}s before retry...")

            time.sleep(delay)

    return RetryResult(
        success=False,
        attempts=config.max_attempts,
        total_time=time.time() - start_time,
        final_error=error,
        delays=delays,
    )


def preview_delays(config: RetryConfig) -> list[float]:
    """Preview delay sequence without running."""
    delays = []
    for attempt in range(1, config.max_attempts):
        # Use deterministic delays for preview (no jitter)
        temp_config = RetryConfig(
            max_attempts=config.max_attempts,
            initial_delay=config.initial_delay,
            max_delay=config.max_delay,
            strategy=config.strategy,
            jitter=0.0,
        )
        delays.append(calculate_delay(temp_config, attempt))
    return delays


def total_max_time(config: RetryConfig) -> float:
    """Calculate maximum total time for all retries."""
    delays = preview_delays(config)
    return sum(delays)


def main() -> int:
    parser = argparse.ArgumentParser(description="Retry logic with backoff strategies")
    parser.add_argument("--attempts", type=int, default=5, help="Maximum retry attempts")
    parser.add_argument("--delay", type=float, default=1.0, help="Initial delay in seconds")
    parser.add_argument("--max-delay", type=float, default=60.0, help="Maximum delay in seconds")
    parser.add_argument(
        "--strategy",
        choices=["fixed", "linear", "exponential", "fibonacci"],
        default="exponential",
        help="Backoff strategy",
    )
    parser.add_argument("--jitter", type=float, default=0.0, help="Jitter factor (0.0 to 1.0)")
    parser.add_argument("--timeout", type=float, help="Total timeout in seconds")
    parser.add_argument("--preview", action="store_true", help="Preview delay sequence")
    parser.add_argument("--simulate", action="store_true", help="Simulate with random failures")
    parser.add_argument(
        "--success-rate", type=float, default=0.5, help="Success probability for simulation"
    )
    parser.add_argument("--fail-until", type=int, default=0, help="Force failure until attempt N")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    config = RetryConfig(
        max_attempts=args.attempts,
        initial_delay=args.delay,
        max_delay=args.max_delay,
        strategy=RetryStrategy(args.strategy),
        jitter=args.jitter,
        timeout=args.timeout,
    )

    if args.preview:
        delays = preview_delays(config)
        total = sum(delays)

        print(f"Strategy: {config.strategy.value}")
        print(f"Attempts: {config.max_attempts}")
        print("\nDelay sequence:")
        for i, delay in enumerate(delays, 1):
            print(f"  After attempt {i}: {delay:.2f}s")
        print(f"\nTotal max wait: {total:.2f}s")
        return 0

    if args.simulate:
        attempt_counter = [0]

        def operation():
            result = simulate_operation(
                args.success_rate,
                args.fail_until,
                attempt_counter[0],
            )
            attempt_counter[0] += 1
            return result

        result = retry_operation(operation, config, args.verbose)

        print(f"\nResult: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"Attempts: {result.attempts}")
        print(f"Total time: {result.total_time:.2f}s")
        if result.final_error:
            print(f"Final error: {result.final_error}")

        return 0 if result.success else 1

    # Default: show config
    print("Retry Configuration:")
    print(f"  Max attempts: {config.max_attempts}")
    print(f"  Initial delay: {config.initial_delay}s")
    print(f"  Max delay: {config.max_delay}s")
    print(f"  Strategy: {config.strategy.value}")
    print(f"  Jitter: {config.jitter}")
    if config.timeout:
        print(f"  Timeout: {config.timeout}s")
    print(f"\nMax total wait: {total_max_time(config):.2f}s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
