"""Tests for event_stream_cli.py"""


from event_stream_cli import (
    concat,
    iterate,
    merge,
    repeat,
    simulate_stream,
    stream,
)


class TestStream:
    def test_iter(self):
        s = stream([1, 2, 3])
        assert list(s) == [1, 2, 3]

    def test_map(self):
        result = stream([1, 2, 3]).map(lambda x: x * 2).collect()
        assert result == [2, 4, 6]

    def test_filter(self):
        result = stream([1, 2, 3, 4, 5]).filter(lambda x: x % 2 == 0).collect()
        assert result == [2, 4]

    def test_take(self):
        result = stream(range(100)).take(5).collect()
        assert result == [0, 1, 2, 3, 4]

    def test_skip(self):
        result = stream([1, 2, 3, 4, 5]).skip(2).collect()
        assert result == [3, 4, 5]

    def test_flat_map(self):
        result = stream([1, 2]).flat_map(lambda x: stream([x, x * 10])).collect()
        assert result == [1, 10, 2, 20]

    def test_scan(self):
        result = stream([1, 2, 3]).scan(lambda a, b: a + b, 0).collect()
        assert result == [1, 3, 6]

    def test_distinct(self):
        result = stream([1, 2, 2, 3, 1, 4]).distinct().collect()
        assert result == [1, 2, 3, 4]

    def test_chunk(self):
        result = stream([1, 2, 3, 4, 5]).chunk(2).collect()
        assert result == [[1, 2], [3, 4], [5]]

    def test_window(self):
        result = stream([1, 2, 3, 4, 5]).window(3).collect()
        assert result == [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

    def test_enumerate(self):
        result = stream(["a", "b", "c"]).enumerate().collect()
        assert result == [(0, "a"), (1, "b"), (2, "c")]

    def test_zip_with(self):
        s1 = stream([1, 2, 3])
        s2 = stream(["a", "b", "c"])
        result = s1.zip_with(s2).collect()
        assert result == [(1, "a"), (2, "b"), (3, "c")]

    def test_foreach(self):
        items = []
        stream([1, 2, 3]).foreach(lambda x: items.append(x))
        assert items == [1, 2, 3]

    def test_reduce(self):
        result = stream([1, 2, 3, 4]).reduce(lambda a, b: a + b, 0)
        assert result == 10

    def test_count(self):
        assert stream([1, 2, 3]).count() == 3

    def test_first(self):
        assert stream([1, 2, 3]).first() == 1
        assert stream([]).first() is None

    def test_last(self):
        assert stream([1, 2, 3]).last() == 3
        assert stream([]).last() is None

    def test_any(self):
        assert stream([1, 2, 3]).any(lambda x: x > 2)
        assert not stream([1, 2, 3]).any(lambda x: x > 5)

    def test_all(self):
        assert stream([2, 4, 6]).all(lambda x: x % 2 == 0)
        assert not stream([2, 3, 4]).all(lambda x: x % 2 == 0)


class TestStreamChaining:
    def test_complex_chain(self):
        result = (
            stream(range(1, 20))
            .filter(lambda x: x % 2 == 0)
            .map(lambda x: x * x)
            .take(3)
            .collect()
        )
        assert result == [4, 16, 36]

    def test_lazy_evaluation(self):
        calls = [0]

        def track(x):
            calls[0] += 1
            return x * 2

        s = stream([1, 2, 3, 4, 5]).map(track).take(2)
        assert calls[0] == 0  # Not evaluated yet
        result = s.collect()
        assert result == [2, 4]
        assert calls[0] <= 3  # At most 3 evaluations (may check one extra)


class TestRepeat:
    def test_finite(self):
        result = repeat("x", 3).collect()
        assert result == ["x", "x", "x"]

    def test_with_take(self):
        result = repeat(1).take(5).collect()
        assert result == [1, 1, 1, 1, 1]


class TestIterate:
    def test_basic(self):
        result = iterate(lambda x: x * 2, 1).take(5).collect()
        assert result == [1, 2, 4, 8, 16]


class TestConcat:
    def test_two_streams(self):
        s1 = stream([1, 2])
        s2 = stream([3, 4])
        result = concat(s1, s2).collect()
        assert result == [1, 2, 3, 4]

    def test_three_streams(self):
        result = concat(stream([1]), stream([2]), stream([3])).collect()
        assert result == [1, 2, 3]


class TestMerge:
    def test_interleave(self):
        s1 = stream([1, 2, 3])
        s2 = stream(["a", "b", "c"])
        result = merge(s1, s2).collect()
        assert result == [1, "a", 2, "b", 3, "c"]

    def test_different_lengths(self):
        s1 = stream([1, 2])
        s2 = stream(["a", "b", "c", "d"])
        result = merge(s1, s2).collect()
        assert len(result) == 6


class TestSimulateStream:
    def test_map(self):
        result = simulate_stream(["map:1,2,3"])
        assert result == ["[2, 4, 6]"]

    def test_filter(self):
        result = simulate_stream(["filter:1,2,3,4"])
        assert result == ["[2, 4]"]

    def test_take(self):
        result = simulate_stream(["take:5"])
        assert result == ["[0, 1, 2, 3, 4]"]

    def test_chunk(self):
        result = simulate_stream(["chunk:1,2,3,4,5"])
        assert "[[1, 2, 3], [4, 5]]" in result[0]

    def test_reduce(self):
        result = simulate_stream(["reduce:1,2,3,4"])
        assert result == ["10"]

    def test_distinct(self):
        result = simulate_stream(["distinct:1,2,2,3,3,3"])
        assert result == ["[1, 2, 3]"]

    def test_scan(self):
        result = simulate_stream(["scan:1,2,3"])
        assert result == ["[1, 3, 6]"]
