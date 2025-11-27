"""Tests for mem_ring_cli.py"""


from mem_ring_cli import (
    ByteRing,
    MovingAverage,
    RingBuffer,
    RingStats,
    SlidingWindow,
    simulate_ring,
)


class TestRingStats:
    def test_default(self):
        stats = RingStats()
        assert stats.capacity == 0
        assert stats.overflows == 0


class TestRingBuffer:
    def test_push(self):
        ring: RingBuffer[int] = RingBuffer(4)
        result = ring.push(1)
        assert result is None
        assert ring.size() == 1

    def test_push_overflow(self):
        ring: RingBuffer[int] = RingBuffer(2)
        ring.push(1)
        ring.push(2)
        evicted = ring.push(3)
        assert evicted == 1

    def test_pop(self):
        ring: RingBuffer[int] = RingBuffer(4)
        ring.push(1)
        ring.push(2)
        assert ring.pop() == 1
        assert ring.pop() == 2

    def test_pop_empty(self):
        ring: RingBuffer[int] = RingBuffer(4)
        assert ring.pop() is None

    def test_peek(self):
        ring: RingBuffer[int] = RingBuffer(4)
        ring.push(1)
        ring.push(2)
        assert ring.peek() == 1
        assert ring.size() == 2  # Unchanged

    def test_peek_newest(self):
        ring: RingBuffer[int] = RingBuffer(4)
        ring.push(1)
        ring.push(2)
        ring.push(3)
        assert ring.peek_newest() == 3

    def test_clear(self):
        ring: RingBuffer[int] = RingBuffer(4)
        ring.push(1)
        ring.push(2)
        ring.clear()
        assert ring.is_empty()

    def test_is_empty(self):
        ring: RingBuffer[int] = RingBuffer(4)
        assert ring.is_empty()
        ring.push(1)
        assert not ring.is_empty()

    def test_is_full(self):
        ring: RingBuffer[int] = RingBuffer(2)
        assert not ring.is_full()
        ring.push(1)
        ring.push(2)
        assert ring.is_full()

    def test_to_list(self):
        ring: RingBuffer[int] = RingBuffer(4)
        ring.push(1)
        ring.push(2)
        ring.push(3)
        assert ring.to_list() == [1, 2, 3]

    def test_to_list_with_overflow(self):
        ring: RingBuffer[int] = RingBuffer(3)
        ring.push(1)
        ring.push(2)
        ring.push(3)
        ring.push(4)
        assert ring.to_list() == [2, 3, 4]

    def test_iter(self):
        ring: RingBuffer[int] = RingBuffer(4)
        ring.push(1)
        ring.push(2)
        assert list(ring) == [1, 2]

    def test_len(self):
        ring: RingBuffer[int] = RingBuffer(4)
        ring.push(1)
        ring.push(2)
        assert len(ring) == 2

    def test_stats(self):
        ring: RingBuffer[int] = RingBuffer(3)
        ring.push(1)
        ring.push(2)
        ring.push(3)
        ring.push(4)  # Overflow
        stats = ring.stats()
        assert stats.capacity == 3
        assert stats.size == 3
        assert stats.overflows == 1

    def test_fifo_order(self):
        ring: RingBuffer[str] = RingBuffer(4)
        ring.push("a")
        ring.push("b")
        ring.push("c")
        assert ring.pop() == "a"
        assert ring.pop() == "b"
        assert ring.pop() == "c"


class TestByteRing:
    def test_write_read(self):
        ring = ByteRing(10)
        ring.write(b"hello")
        data = ring.read(5)
        assert data == b"hello"

    def test_partial_read(self):
        ring = ByteRing(10)
        ring.write(b"hello")
        assert ring.read(3) == b"hel"
        assert ring.read(2) == b"lo"

    def test_overflow(self):
        ring = ByteRing(5)
        ring.write(b"hello")
        ring.write(b"XY")  # Overwrites "he"
        assert ring.read(5) == b"lloXY"

    def test_peek(self):
        ring = ByteRing(10)
        ring.write(b"test")
        assert ring.peek(2) == b"te"
        assert ring.available() == 4  # Unchanged

    def test_available(self):
        ring = ByteRing(10)
        ring.write(b"abc")
        assert ring.available() == 3

    def test_free_space(self):
        ring = ByteRing(10)
        ring.write(b"abc")
        assert ring.free_space() == 7

    def test_clear(self):
        ring = ByteRing(10)
        ring.write(b"test")
        ring.clear()
        assert ring.available() == 0


class TestSlidingWindow:
    def test_add(self):
        window: SlidingWindow[int] = SlidingWindow(3)
        window.add(1)
        window.add(2)
        assert window.values() == [1, 2]

    def test_overflow(self):
        window: SlidingWindow[int] = SlidingWindow(3)
        window.add(1)
        window.add(2)
        window.add(3)
        window.add(4)
        assert window.values() == [2, 3, 4]

    def test_is_full(self):
        window: SlidingWindow[int] = SlidingWindow(2)
        assert not window.is_full()
        window.add(1)
        window.add(2)
        assert window.is_full()


class TestMovingAverage:
    def test_single_value(self):
        ma = MovingAverage(3)
        avg = ma.add(10.0)
        assert avg == 10.0

    def test_partial_window(self):
        ma = MovingAverage(3)
        ma.add(1.0)
        avg = ma.add(2.0)
        assert avg == 1.5

    def test_full_window(self):
        ma = MovingAverage(3)
        ma.add(1.0)
        ma.add(2.0)
        avg = ma.add(3.0)
        assert avg == 2.0

    def test_sliding(self):
        ma = MovingAverage(3)
        ma.add(1.0)
        ma.add(2.0)
        ma.add(3.0)
        avg = ma.add(4.0)  # Evicts 1.0
        assert avg == 3.0  # (2+3+4)/3

    def test_average_empty(self):
        ma = MovingAverage(3)
        assert ma.average() == 0.0


class TestSimulateRing:
    def test_push(self):
        result = simulate_ring(["push:1"])
        assert result == ["evicted=None"]

    def test_push_overflow(self):
        result = simulate_ring([
            "push:1", "push:2", "push:3", "push:4", "push:5"
        ])
        assert "evicted=1" in result[4]

    def test_pop(self):
        result = simulate_ring(["push:42", "pop:"])
        assert "value=42" in result[1]

    def test_peek(self):
        result = simulate_ring(["push:1", "push:2", "peek:"])
        assert "peek=1" in result[2]

    def test_size(self):
        result = simulate_ring(["push:1", "push:2", "size:"])
        assert result[2] == "2"

    def test_is_full(self):
        result = simulate_ring([
            "push:1", "push:2", "push:3", "push:4", "is_full:"
        ])
        assert result[4] == "True"

    def test_to_list(self):
        result = simulate_ring(["push:1", "push:2", "to_list:"])
        assert result[2] == "[1, 2]"


class TestRingBufferEdgeCases:
    def test_capacity_one(self):
        ring: RingBuffer[int] = RingBuffer(1)
        ring.push(1)
        assert ring.push(2) == 1
        assert ring.to_list() == [2]

    def test_wrap_around(self):
        ring: RingBuffer[int] = RingBuffer(3)
        ring.push(1)
        ring.push(2)
        ring.push(3)
        ring.pop()
        ring.pop()
        ring.push(4)
        ring.push(5)
        assert ring.to_list() == [3, 4, 5]
