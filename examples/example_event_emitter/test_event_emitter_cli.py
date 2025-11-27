"""Tests for event_emitter_cli.py"""


from event_emitter_cli import (
    AsyncEventEmitter,
    Event,
    EventEmitter,
    EventStats,
    TypedEventEmitter,
    simulate_emitter,
)


class TestEventStats:
    def test_default(self):
        stats = EventStats()
        assert stats.events_emitted == 0
        assert stats.handlers_invoked == 0


class TestEventEmitter:
    def test_on(self):
        emitter = EventEmitter()
        received = []
        emitter.on("test", lambda x: received.append(x))
        emitter.emit("test", "data")
        assert received == ["data"]

    def test_on_multiple_handlers(self):
        emitter = EventEmitter()
        results = []
        emitter.on("event", lambda: results.append(1))
        emitter.on("event", lambda: results.append(2))
        emitter.emit("event")
        assert results == [1, 2]

    def test_on_chaining(self):
        emitter = EventEmitter()
        result = emitter.on("a", lambda: None).on("b", lambda: None)
        assert result is emitter

    def test_once(self):
        emitter = EventEmitter()
        count = [0]
        emitter.once("event", lambda: count.__setitem__(0, count[0] + 1))
        emitter.emit("event")
        emitter.emit("event")
        assert count[0] == 1

    def test_off_specific_handler(self):
        emitter = EventEmitter()
        results = []
        def handler1():
            return results.append(1)
        def handler2():
            return results.append(2)
        emitter.on("event", handler1)
        emitter.on("event", handler2)
        emitter.off("event", handler1)
        emitter.emit("event")
        assert results == [2]

    def test_off_all_handlers(self):
        emitter = EventEmitter()
        results = []
        emitter.on("event", lambda: results.append(1))
        emitter.on("event", lambda: results.append(2))
        emitter.off("event")
        emitter.emit("event")
        assert results == []

    def test_emit_returns_true_when_handled(self):
        emitter = EventEmitter()
        emitter.on("event", lambda: None)
        assert emitter.emit("event") is True

    def test_emit_returns_false_when_not_handled(self):
        emitter = EventEmitter()
        assert emitter.emit("no_handler") is False

    def test_emit_with_args(self):
        emitter = EventEmitter()
        received = []
        emitter.on("event", lambda a, b: received.extend([a, b]))
        emitter.emit("event", 1, 2)
        assert received == [1, 2]

    def test_emit_with_kwargs(self):
        emitter = EventEmitter()
        received = {}
        def handler(**kwargs):
            received.update(kwargs)
        emitter.on("event", handler)
        emitter.emit("event", key="value")
        assert received == {"key": "value"}

    def test_listeners(self):
        emitter = EventEmitter()
        def h1():
            return None
        def h2():
            return None
        emitter.on("event", h1)
        emitter.once("event", h2)
        listeners = emitter.listeners("event")
        assert h1 in listeners
        assert h2 in listeners

    def test_listener_count(self):
        emitter = EventEmitter()
        emitter.on("event", lambda: None)
        emitter.on("event", lambda: None)
        assert emitter.listener_count("event") == 2

    def test_event_names(self):
        emitter = EventEmitter()
        emitter.on("a", lambda: None)
        emitter.on("b", lambda: None)
        names = emitter.event_names()
        assert "a" in names
        assert "b" in names

    def test_remove_all_listeners_specific(self):
        emitter = EventEmitter()
        emitter.on("a", lambda: None)
        emitter.on("b", lambda: None)
        emitter.remove_all_listeners("a")
        assert "a" not in emitter.event_names()
        assert "b" in emitter.event_names()

    def test_remove_all_listeners_global(self):
        emitter = EventEmitter()
        emitter.on("a", lambda: None)
        emitter.on("b", lambda: None)
        emitter.remove_all_listeners()
        assert emitter.event_names() == []

    def test_stats(self):
        emitter = EventEmitter()
        emitter.on("event", lambda: None)
        emitter.emit("event")
        emitter.emit("other")
        stats = emitter.stats()
        assert stats.events_emitted == 2
        assert stats.handlers_invoked == 1
        assert stats.handlers_registered == 1


class TestTypedEventEmitter:
    def test_on_emit(self):
        emitter = TypedEventEmitter()
        received = []
        emitter.on("data", lambda d: received.append(d))
        emitter.emit("data", {"key": "value"})
        assert received == [{"key": "value"}]


class TestEvent:
    def test_create(self):
        event = Event("click", {"x": 10, "y": 20})
        assert event.name == "click"
        assert event.data == {"x": 10, "y": 20}


class TestAsyncEventEmitter:
    def test_emit_queues(self):
        emitter = AsyncEventEmitter()
        received = []
        emitter.on("event", lambda x: received.append(x))
        emitter.emit("event", "data")
        assert received == []  # Not processed yet
        assert emitter.pending_count() == 1

    def test_process(self):
        emitter = AsyncEventEmitter()
        received = []
        emitter.on("event", lambda x: received.append(x))
        emitter.emit("event", "data")
        count = emitter.process()
        assert count == 1
        assert received == ["data"]

    def test_process_multiple(self):
        emitter = AsyncEventEmitter()
        received = []
        emitter.on("event", lambda x: received.append(x))
        emitter.emit("event", 1)
        emitter.emit("event", 2)
        emitter.emit("event", 3)
        count = emitter.process()
        assert count == 3
        assert received == [1, 2, 3]


class TestSimulateEmitter:
    def test_on(self):
        result = simulate_emitter(["on:test"])
        assert result == ["registered"]

    def test_emit(self):
        result = simulate_emitter([
            "on:test",
            "emit:test,data",
            "values:"
        ])
        assert "invoked=True" in result[1]
        assert "data" in result[2]

    def test_once(self):
        result = simulate_emitter([
            "once:test",
            "emit:test,1",
            "emit:test,2",
            "count:test"
        ])
        assert result[3] == "0"  # Handler removed after first emit

    def test_off(self):
        result = simulate_emitter([
            "on:test",
            "off:test",
            "count:test"
        ])
        assert result[2] == "0"

    def test_events(self):
        result = simulate_emitter([
            "on:a",
            "on:b",
            "events:"
        ])
        assert "a" in result[2]
        assert "b" in result[2]

    def test_stats(self):
        result = simulate_emitter([
            "on:test",
            "emit:test,x",
            "stats:"
        ])
        assert "emitted=1" in result[2]


class TestEventEmitterEdgeCases:
    def test_emit_no_handlers(self):
        emitter = EventEmitter()
        assert emitter.emit("nothing") is False

    def test_off_nonexistent(self):
        emitter = EventEmitter()
        emitter.off("nonexistent")  # Should not raise

    def test_handler_receives_nothing(self):
        emitter = EventEmitter()
        called = [False]
        emitter.on("event", lambda: called.__setitem__(0, True))
        emitter.emit("event")
        assert called[0] is True
