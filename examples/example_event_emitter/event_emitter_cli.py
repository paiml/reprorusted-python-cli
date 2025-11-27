"""Event Emitter CLI.

Demonstrates the EventEmitter pattern (on/emit/off).
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class EventStats:
    """Event statistics."""

    events_emitted: int = 0
    handlers_invoked: int = 0
    handlers_registered: int = 0


Handler = Callable[..., None]


class EventEmitter:
    """Node.js-style event emitter."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = {}
        self._once_handlers: dict[str, list[Handler]] = {}
        self._stats = EventStats()

    def on(self, event: str, handler: Handler) -> "EventEmitter":
        """Register event handler."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        self._stats.handlers_registered += 1
        return self

    def once(self, event: str, handler: Handler) -> "EventEmitter":
        """Register one-time event handler."""
        if event not in self._once_handlers:
            self._once_handlers[event] = []
        self._once_handlers[event].append(handler)
        self._stats.handlers_registered += 1
        return self

    def off(self, event: str, handler: Handler | None = None) -> "EventEmitter":
        """Remove event handler(s)."""
        if handler is None:
            # Remove all handlers for event
            if event in self._handlers:
                self._stats.handlers_registered -= len(self._handlers[event])
                del self._handlers[event]
            if event in self._once_handlers:
                self._stats.handlers_registered -= len(self._once_handlers[event])
                del self._once_handlers[event]
        else:
            # Remove specific handler
            if event in self._handlers and handler in self._handlers[event]:
                self._handlers[event].remove(handler)
                self._stats.handlers_registered -= 1
            if event in self._once_handlers and handler in self._once_handlers[event]:
                self._once_handlers[event].remove(handler)
                self._stats.handlers_registered -= 1
        return self

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        """Emit event. Returns True if any handlers were invoked."""
        invoked = False
        self._stats.events_emitted += 1

        # Regular handlers
        if event in self._handlers:
            for handler in self._handlers[event]:
                handler(*args, **kwargs)
                self._stats.handlers_invoked += 1
                invoked = True

        # Once handlers
        if event in self._once_handlers:
            handlers = self._once_handlers.pop(event)
            self._stats.handlers_registered -= len(handlers)
            for handler in handlers:
                handler(*args, **kwargs)
                self._stats.handlers_invoked += 1
                invoked = True

        return invoked

    def listeners(self, event: str) -> list[Handler]:
        """Get all listeners for event."""
        result = []
        if event in self._handlers:
            result.extend(self._handlers[event])
        if event in self._once_handlers:
            result.extend(self._once_handlers[event])
        return result

    def listener_count(self, event: str) -> int:
        """Get number of listeners for event."""
        return len(self.listeners(event))

    def event_names(self) -> list[str]:
        """Get all event names with registered handlers."""
        names = set(self._handlers.keys()) | set(self._once_handlers.keys())
        return list(names)

    def remove_all_listeners(self, event: str | None = None) -> "EventEmitter":
        """Remove all listeners."""
        if event is None:
            self._handlers.clear()
            self._once_handlers.clear()
            self._stats.handlers_registered = 0
        else:
            self.off(event)
        return self

    def stats(self) -> EventStats:
        """Get emitter statistics."""
        return EventStats(
            events_emitted=self._stats.events_emitted,
            handlers_invoked=self._stats.handlers_invoked,
            handlers_registered=self._stats.handlers_registered,
        )


class TypedEventEmitter:
    """Event emitter with typed events."""

    def __init__(self) -> None:
        self._emitter = EventEmitter()

    def on(self, event: str, handler: Handler) -> "TypedEventEmitter":
        self._emitter.on(event, handler)
        return self

    def emit(self, event: str, data: Any) -> bool:
        return self._emitter.emit(event, data)


@dataclass
class Event:
    """Generic event with name and data."""

    name: str
    data: Any = None
    timestamp: float = 0.0


class AsyncEventEmitter:
    """Event emitter that collects events for later processing."""

    def __init__(self) -> None:
        self._emitter = EventEmitter()
        self._pending: list[Event] = []

    def on(self, event: str, handler: Handler) -> "AsyncEventEmitter":
        self._emitter.on(event, handler)
        return self

    def emit(self, event: str, *args: Any) -> None:
        """Queue event for later processing."""
        self._pending.append(Event(event, args))

    def process(self) -> int:
        """Process all pending events. Returns count processed."""
        count = 0
        while self._pending:
            event = self._pending.pop(0)
            if isinstance(event.data, tuple):
                self._emitter.emit(event.name, *event.data)
            else:
                self._emitter.emit(event.name, event.data)
            count += 1
        return count

    def pending_count(self) -> int:
        """Get number of pending events."""
        return len(self._pending)


def simulate_emitter(operations: list[str]) -> list[str]:
    """Simulate event emitter operations."""
    results: list[str] = []
    emitter = EventEmitter()
    values: list[Any] = []

    def capture(*args: Any) -> None:
        values.extend(args)

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "on":
            emitter.on(parts[1], capture)
            results.append("registered")
        elif cmd == "once":
            emitter.once(parts[1], capture)
            results.append("registered_once")
        elif cmd == "emit":
            event, *data = parts[1].split(",")
            invoked = emitter.emit(event, *data)
            results.append(f"invoked={invoked}")
        elif cmd == "off":
            emitter.off(parts[1])
            results.append("removed")
        elif cmd == "count":
            count = emitter.listener_count(parts[1])
            results.append(str(count))
        elif cmd == "events":
            names = emitter.event_names()
            results.append(str(sorted(names)))
        elif cmd == "values":
            results.append(str(values))
            values.clear()
        elif cmd == "stats":
            s = emitter.stats()
            results.append(f"emitted={s.events_emitted} invoked={s.handlers_invoked}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: event_emitter_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        emitter = EventEmitter()

        received: list[str] = []
        emitter.on("message", lambda msg: received.append(msg))
        emitter.on("message", lambda msg: print(f"Handler 2: {msg}"))

        emitter.emit("message", "Hello!")
        emitter.emit("message", "World!")

        print(f"Received: {received}")
        print(f"Stats: {emitter.stats()}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
