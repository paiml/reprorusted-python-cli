"""Tests for event_bus_cli.py"""


from event_bus_cli import (
    ChannelBus,
    EventBus,
    Message,
    TypedBus,
    simulate_bus,
)


class TestMessage:
    def test_create(self):
        msg = Message("topic", "payload")
        assert msg.topic == "topic"
        assert msg.payload == "payload"

    def test_with_headers(self):
        msg = Message("topic", "payload", {"key": "value"})
        assert msg.headers["key"] == "value"


class TestEventBus:
    def test_subscribe_publish(self):
        bus = EventBus()
        received = []
        bus.subscribe("test", lambda m: received.append(m.payload))
        bus.publish("test", "data")
        assert received == ["data"]

    def test_multiple_subscribers(self):
        bus = EventBus()
        results = []
        bus.subscribe("event", lambda m: results.append(1))
        bus.subscribe("event", lambda m: results.append(2))
        bus.publish("event", None)
        assert results == [1, 2]

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        unsub = bus.subscribe("test", lambda m: received.append(m.payload))
        unsub()
        bus.publish("test", "data")
        assert received == []

    def test_subscribe_pattern(self):
        bus = EventBus()
        received = []
        bus.subscribe_pattern("user.*", lambda m: received.append(m.topic))
        bus.publish("user.created", None)
        bus.publish("user.updated", None)
        bus.publish("order.created", None)
        assert received == ["user.created", "user.updated"]

    def test_pattern_wildcard(self):
        bus = EventBus()
        received = []
        bus.subscribe_pattern("*", lambda m: received.append(m.topic))
        bus.publish("a", None)
        bus.publish("b", None)
        assert len(received) == 2

    def test_publish_returns_count(self):
        bus = EventBus()
        bus.subscribe("test", lambda m: None)
        bus.subscribe("test", lambda m: None)
        count = bus.publish("test", None)
        assert count == 2

    def test_publish_no_subscribers(self):
        bus = EventBus()
        count = bus.publish("nothing", None)
        assert count == 0

    def test_unsubscribe_all_topic(self):
        bus = EventBus()
        bus.subscribe("a", lambda m: None)
        bus.subscribe("b", lambda m: None)
        bus.unsubscribe_all("a")
        assert "a" not in bus.topics()
        assert "b" in bus.topics()

    def test_unsubscribe_all_global(self):
        bus = EventBus()
        bus.subscribe("a", lambda m: None)
        bus.subscribe("b", lambda m: None)
        bus.unsubscribe_all()
        assert bus.topics() == []

    def test_topics(self):
        bus = EventBus()
        bus.subscribe("a", lambda m: None)
        bus.subscribe("b", lambda m: None)
        topics = bus.topics()
        assert "a" in topics
        assert "b" in topics

    def test_subscriber_count(self):
        bus = EventBus()
        bus.subscribe("test", lambda m: None)
        bus.subscribe("test", lambda m: None)
        assert bus.subscriber_count("test") == 2

    def test_subscriber_count_with_pattern(self):
        bus = EventBus()
        bus.subscribe("user.created", lambda m: None)
        bus.subscribe_pattern("user.*", lambda m: None)
        assert bus.subscriber_count("user.created") == 2

    def test_message_count(self):
        bus = EventBus()
        bus.publish("a", None)
        bus.publish("b", None)
        bus.publish("c", None)
        assert bus.message_count() == 3


class TestTypedBus:
    def test_subscribe_publish(self):
        bus = TypedBus()
        received = []
        bus.subscribe("event", lambda m: received.append(m.payload))
        bus.publish("event", {"key": "value"})
        assert received == [{"key": "value"}]


class TestChannelBus:
    def test_channel_creation(self):
        bus = ChannelBus()
        ch = bus.channel("users")
        assert ch is not None

    def test_same_channel_returned(self):
        bus = ChannelBus()
        ch1 = bus.channel("users")
        ch2 = bus.channel("users")
        assert ch1 is ch2

    def test_channels_list(self):
        bus = ChannelBus()
        bus.channel("a")
        bus.channel("b")
        assert "a" in bus.channels()
        assert "b" in bus.channels()

    def test_channel_isolation(self):
        bus = ChannelBus()
        received_a = []
        received_b = []

        bus.channel("a").subscribe("test", lambda m: received_a.append(m.payload))
        bus.channel("b").subscribe("test", lambda m: received_b.append(m.payload))

        bus.channel("a").publish("test", "A")
        bus.channel("b").publish("test", "B")

        assert received_a == ["A"]
        assert received_b == ["B"]


class TestSimulateBus:
    def test_subscribe(self):
        result = simulate_bus(["subscribe:test"])
        assert result == ["subscribed"]

    def test_publish(self):
        result = simulate_bus([
            "subscribe:test",
            "publish:test,data",
            "received:"
        ])
        assert "delivered=1" in result[1]
        assert "test:data" in result[2]

    def test_pattern_subscribe(self):
        result = simulate_bus([
            "subscribe_pattern:user.*",
            "publish:user.created,alice",
            "received:"
        ])
        assert "delivered=1" in result[1]

    def test_topics(self):
        result = simulate_bus([
            "subscribe:a",
            "subscribe:b",
            "topics:"
        ])
        assert "a" in result[2]
        assert "b" in result[2]


class TestPatternMatching:
    def test_single_asterisk(self):
        bus = EventBus()
        received = []
        bus.subscribe_pattern("logs.*", lambda m: received.append(m.topic))
        bus.publish("logs.info", None)
        bus.publish("logs.error", None)
        bus.publish("metrics.cpu", None)
        assert received == ["logs.info", "logs.error"]

    def test_question_mark(self):
        bus = EventBus()
        received = []
        bus.subscribe_pattern("user?", lambda m: received.append(m.topic))
        bus.publish("user1", None)
        bus.publish("user2", None)
        bus.publish("users", None)  # Also matches: ? is any single char
        bus.publish("userAB", None)  # Does not match: too long
        assert received == ["user1", "user2", "users"]
