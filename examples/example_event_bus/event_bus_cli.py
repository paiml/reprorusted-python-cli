"""Event Bus CLI.

Demonstrates message bus with topic routing.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Any

Handler = Callable[[Any], None]


@dataclass
class Message:
    """Message on the bus."""

    topic: str
    payload: Any
    headers: dict[str, str] = field(default_factory=dict)


class EventBus:
    """Publish/subscribe event bus with topic patterns."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = {}
        self._pattern_subscribers: list[tuple[str, Handler]] = []
        self._message_count = 0

    def subscribe(self, topic: str, handler: Handler) -> Callable[[], None]:
        """Subscribe to exact topic. Returns unsubscribe function."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

        def unsubscribe() -> None:
            if topic in self._subscribers and handler in self._subscribers[topic]:
                self._subscribers[topic].remove(handler)

        return unsubscribe

    def subscribe_pattern(self, pattern: str, handler: Handler) -> Callable[[], None]:
        """Subscribe to topic pattern (supports * and ?). Returns unsubscribe."""
        entry = (pattern, handler)
        self._pattern_subscribers.append(entry)

        def unsubscribe() -> None:
            if entry in self._pattern_subscribers:
                self._pattern_subscribers.remove(entry)

        return unsubscribe

    def publish(self, topic: str, payload: Any = None) -> int:
        """Publish message. Returns number of handlers invoked."""
        self._message_count += 1
        count = 0

        # Exact subscribers
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                handler(Message(topic, payload))
                count += 1

        # Pattern subscribers
        for pattern, handler in self._pattern_subscribers:
            if fnmatch(topic, pattern):
                handler(Message(topic, payload))
                count += 1

        return count

    def unsubscribe_all(self, topic: str | None = None) -> None:
        """Remove all subscribers for topic or all."""
        if topic is None:
            self._subscribers.clear()
            self._pattern_subscribers.clear()
        elif topic in self._subscribers:
            del self._subscribers[topic]

    def topics(self) -> list[str]:
        """Get all subscribed topics."""
        return list(self._subscribers.keys())

    def subscriber_count(self, topic: str) -> int:
        """Get subscriber count for topic."""
        count = len(self._subscribers.get(topic, []))
        for pattern, _ in self._pattern_subscribers:
            if fnmatch(topic, pattern):
                count += 1
        return count

    def message_count(self) -> int:
        """Get total message count."""
        return self._message_count


class TypedBus:
    """Type-safe event bus."""

    def __init__(self) -> None:
        self._bus = EventBus()

    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> Callable[[], None]:
        return self._bus.subscribe(topic, handler)

    def publish(self, topic: str, payload: Any) -> int:
        return self._bus.publish(topic, payload)


class ChannelBus:
    """Event bus with named channels."""

    def __init__(self) -> None:
        self._channels: dict[str, EventBus] = {}

    def channel(self, name: str) -> EventBus:
        """Get or create channel."""
        if name not in self._channels:
            self._channels[name] = EventBus()
        return self._channels[name]

    def channels(self) -> list[str]:
        """Get all channel names."""
        return list(self._channels.keys())


def simulate_bus(operations: list[str]) -> list[str]:
    """Simulate event bus operations."""
    results: list[str] = []
    bus = EventBus()
    received: list[str] = []

    def handler(msg: Message) -> None:
        received.append(f"{msg.topic}:{msg.payload}")

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "subscribe":
            bus.subscribe(parts[1], handler)
            results.append("subscribed")
        elif cmd == "subscribe_pattern":
            bus.subscribe_pattern(parts[1], handler)
            results.append("subscribed_pattern")
        elif cmd == "publish":
            topic, payload = parts[1].split(",", 1)
            count = bus.publish(topic, payload)
            results.append(f"delivered={count}")
        elif cmd == "received":
            results.append(str(received))
            received.clear()
        elif cmd == "topics":
            results.append(str(bus.topics()))
        elif cmd == "count":
            results.append(str(bus.subscriber_count(parts[1])))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: event_bus_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        bus = EventBus()
        messages: list[str] = []

        bus.subscribe("user.created", lambda m: messages.append(f"User: {m.payload}"))
        bus.subscribe_pattern("user.*", lambda m: messages.append(f"Pattern: {m.topic}"))

        bus.publish("user.created", "alice")
        bus.publish("user.updated", "bob")
        bus.publish("order.created", "order1")

        print(f"Messages: {messages}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
