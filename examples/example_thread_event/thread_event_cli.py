#!/usr/bin/env python3
"""Thread Event CLI.

Event and Barrier patterns for thread coordination.
"""

import argparse
import sys
import threading


class Signal:
    """Simple signal using Event."""

    def __init__(self) -> None:
        self._event: threading.Event = threading.Event()
        self._signal_count: int = 0
        self._lock: threading.Lock = threading.Lock()

    def set(self) -> None:
        """Set the signal."""
        with self._lock:
            self._signal_count += 1
        self._event.set()

    def clear(self) -> None:
        """Clear the signal."""
        self._event.clear()

    def is_set(self) -> bool:
        """Check if signal is set."""
        return self._event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        """Wait for signal."""
        return self._event.wait(timeout)

    def signal_count(self) -> int:
        """Get number of times signal was set."""
        with self._lock:
            return self._signal_count


class Gate:
    """Gate that blocks until opened."""

    def __init__(self) -> None:
        self._event: threading.Event = threading.Event()
        self._waiters: int = 0
        self._lock: threading.Lock = threading.Lock()

    def open(self) -> None:
        """Open the gate."""
        self._event.set()

    def close(self) -> None:
        """Close the gate."""
        self._event.clear()

    def is_open(self) -> bool:
        """Check if gate is open."""
        return self._event.is_set()

    def pass_through(self) -> bool:
        """Try to pass through gate (non-blocking)."""
        return self._event.is_set()

    def wait_for_open(self, timeout: float | None = None) -> bool:
        """Wait for gate to open."""
        with self._lock:
            self._waiters += 1
        result = self._event.wait(timeout)
        with self._lock:
            self._waiters -= 1
        return result

    def waiting_count(self) -> int:
        """Get number of waiters."""
        with self._lock:
            return self._waiters


class Latch:
    """Countdown latch - opens when count reaches zero."""

    def __init__(self, count: int) -> None:
        self._count: int = count
        self._initial: int = count
        self._event: threading.Event = threading.Event()
        self._lock: threading.Lock = threading.Lock()
        if count <= 0:
            self._event.set()

    def count_down(self) -> int:
        """Decrement count, open when zero."""
        with self._lock:
            if self._count > 0:
                self._count -= 1
                if self._count == 0:
                    self._event.set()
            return self._count

    def get_count(self) -> int:
        """Get current count."""
        with self._lock:
            return self._count

    def is_open(self) -> bool:
        """Check if latch is open."""
        return self._event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        """Wait for latch to open."""
        return self._event.wait(timeout)

    def reset(self) -> None:
        """Reset latch to initial count."""
        with self._lock:
            self._count = self._initial
            self._event.clear()


class PulseEvent:
    """Event that auto-clears after being set (pulse)."""

    def __init__(self) -> None:
        self._event: threading.Event = threading.Event()
        self._pulse_count: int = 0
        self._lock: threading.Lock = threading.Lock()

    def pulse(self) -> None:
        """Set and immediately clear."""
        with self._lock:
            self._pulse_count += 1
        self._event.set()
        self._event.clear()

    def is_set(self) -> bool:
        """Check current state."""
        return self._event.is_set()

    def pulse_count(self) -> int:
        """Get total pulses."""
        with self._lock:
            return self._pulse_count


class BarrierSimulator:
    """Simulate barrier behavior without actual threading."""

    def __init__(self, parties: int) -> None:
        self._parties: int = parties
        self._waiting: int = 0
        self._generation: int = 0
        self._lock: threading.Lock = threading.Lock()

    def wait(self) -> int:
        """Simulate barrier wait, return arrival index."""
        with self._lock:
            index = self._waiting
            self._waiting += 1
            if self._waiting >= self._parties:
                self._generation += 1
                self._waiting = 0
            return index

    def parties(self) -> int:
        """Get number of parties."""
        return self._parties

    def n_waiting(self) -> int:
        """Get number currently waiting."""
        with self._lock:
            return self._waiting

    def generation(self) -> int:
        """Get current generation."""
        with self._lock:
            return self._generation


def simulate_signal(ops: list[str]) -> list[bool]:
    """Simulate signal operations."""
    signal = Signal()
    results: list[bool] = []

    for op in ops:
        if op == "set":
            signal.set()
        elif op == "clear":
            signal.clear()
        elif op == "check":
            results.append(signal.is_set())
        elif op == "count":
            results.append(signal.signal_count() > 0)

    return results


def simulate_gate(ops: list[str]) -> list[bool]:
    """Simulate gate operations."""
    gate = Gate()
    results: list[bool] = []

    for op in ops:
        if op == "open":
            gate.open()
        elif op == "close":
            gate.close()
        elif op == "check":
            results.append(gate.is_open())
        elif op == "pass":
            results.append(gate.pass_through())

    return results


def simulate_latch(count: int, ops: list[str]) -> list[int]:
    """Simulate latch operations."""
    latch = Latch(count)
    results: list[int] = []

    for op in ops:
        if op == "down":
            latch.count_down()
        elif op == "count":
            results.append(latch.get_count())
        elif op == "open":
            results.append(1 if latch.is_open() else 0)
        elif op == "reset":
            latch.reset()

    return results


def simulate_barrier(parties: int, waits: int) -> tuple[int, int]:
    """Simulate barrier with given parties and waits."""
    barrier = BarrierSimulator(parties)

    for _ in range(waits):
        barrier.wait()

    return (barrier.n_waiting(), barrier.generation())


def event_sequence(sequence: list[str]) -> list[bool]:
    """Execute event sequence and return states."""
    event = threading.Event()
    states: list[bool] = []

    for op in sequence:
        if op == "set":
            event.set()
        elif op == "clear":
            event.clear()
        elif op == "toggle":
            if event.is_set():
                event.clear()
            else:
                event.set()
        states.append(event.is_set())

    return states


def main() -> int:
    parser = argparse.ArgumentParser(description="Thread event CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # signal
    signal_p = subparsers.add_parser("signal", help="Signal operations")
    signal_p.add_argument("ops", nargs="+")

    # gate
    gate_p = subparsers.add_parser("gate", help="Gate operations")
    gate_p.add_argument("ops", nargs="+")

    # latch
    latch_p = subparsers.add_parser("latch", help="Latch operations")
    latch_p.add_argument("--count", type=int, default=3)
    latch_p.add_argument("ops", nargs="+")

    # barrier
    barrier_p = subparsers.add_parser("barrier", help="Barrier simulation")
    barrier_p.add_argument("parties", type=int)
    barrier_p.add_argument("waits", type=int)

    args = parser.parse_args()

    if args.command == "signal":
        results = simulate_signal(args.ops)
        print(f"States: {results}")

    elif args.command == "gate":
        results = simulate_gate(args.ops)
        print(f"States: {results}")

    elif args.command == "latch":
        results = simulate_latch(args.count, args.ops)
        print(f"Results: {results}")

    elif args.command == "barrier":
        waiting, gen = simulate_barrier(args.parties, args.waits)
        print(f"Waiting: {waiting}, Generation: {gen}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
