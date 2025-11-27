"""Tests for event_observable_cli.py"""


from event_observable_cli import (
    BehaviorSubject,
    FunctionObserver,
    Subject,
    Subscription,
    empty,
    from_list,
    of,
    simulate_observable,
)


class TestSubscription:
    def test_unsubscribe(self):
        called = [False]
        sub = Subscription(lambda: called.__setitem__(0, True))
        sub.unsubscribe()
        assert called[0]
        assert sub.closed

    def test_unsubscribe_twice(self):
        count = [0]
        sub = Subscription(lambda: count.__setitem__(0, count[0] + 1))
        sub.unsubscribe()
        sub.unsubscribe()
        assert count[0] == 1


class TestFunctionObserver:
    def test_on_next(self):
        received = []
        obs = FunctionObserver(on_next=lambda x: received.append(x))
        obs.on_next(1)
        obs.on_next(2)
        assert received == [1, 2]

    def test_on_error(self):
        errors = []
        obs = FunctionObserver(on_error=lambda e: errors.append(e))
        obs.on_error(ValueError("test"))
        assert len(errors) == 1

    def test_on_complete(self):
        completed = [False]
        obs = FunctionObserver(on_complete=lambda: completed.__setitem__(0, True))
        obs.on_complete()
        assert completed[0]


class TestObservable:
    def test_subscribe(self):
        received = []
        obs = of(1, 2, 3)
        obs.subscribe(on_next=lambda x: received.append(x))
        assert received == [1, 2, 3]

    def test_complete_called(self):
        completed = [False]
        of(1).subscribe(on_complete=lambda: completed.__setitem__(0, True))
        assert completed[0]

    def test_map(self):
        received = []
        of(1, 2, 3).map(lambda x: x * 2).subscribe(on_next=lambda x: received.append(x))
        assert received == [2, 4, 6]

    def test_filter(self):
        received = []
        of(1, 2, 3, 4, 5).filter(lambda x: x % 2 == 0).subscribe(
            on_next=lambda x: received.append(x)
        )
        assert received == [2, 4]

    def test_take(self):
        received = []
        of(1, 2, 3, 4, 5).take(3).subscribe(on_next=lambda x: received.append(x))
        assert received == [1, 2, 3]

    def test_chain(self):
        received = []
        of(1, 2, 3, 4, 5, 6).filter(lambda x: x % 2 == 0).map(lambda x: x * 10).take(2).subscribe(
            on_next=lambda x: received.append(x)
        )
        assert received == [20, 40]


class TestSubject:
    def test_emit_receive(self):
        received = []
        subj: Subject[int] = Subject()
        subj.subscribe(on_next=lambda x: received.append(x))
        subj.on_next(1)
        subj.on_next(2)
        assert received == [1, 2]

    def test_multiple_subscribers(self):
        results1, results2 = [], []
        subj: Subject[int] = Subject()
        subj.subscribe(on_next=lambda x: results1.append(x))
        subj.subscribe(on_next=lambda x: results2.append(x))
        subj.on_next(1)
        assert results1 == [1]
        assert results2 == [1]

    def test_unsubscribe(self):
        received = []
        subj: Subject[int] = Subject()
        sub = subj.subscribe(on_next=lambda x: received.append(x))
        subj.on_next(1)
        sub.unsubscribe()
        subj.on_next(2)
        assert received == [1]

    def test_complete(self):
        completed = [False]
        subj: Subject[int] = Subject()
        subj.subscribe(on_complete=lambda: completed.__setitem__(0, True))
        subj.on_complete()
        assert completed[0]

    def test_no_emit_after_complete(self):
        received = []
        subj: Subject[int] = Subject()
        subj.subscribe(on_next=lambda x: received.append(x))
        subj.on_complete()
        subj.on_next(1)
        assert received == []

    def test_error(self):
        errors = []
        subj: Subject[int] = Subject()
        subj.subscribe(on_error=lambda e: errors.append(str(e)))
        subj.on_error(ValueError("oops"))
        assert len(errors) == 1


class TestBehaviorSubject:
    def test_initial_value(self):
        subj = BehaviorSubject(0)
        assert subj.value == 0

    def test_update_value(self):
        subj = BehaviorSubject(0)
        subj.on_next(5)
        assert subj.value == 5


class TestOf:
    def test_single(self):
        received = []
        of(42).subscribe(on_next=lambda x: received.append(x))
        assert received == [42]

    def test_multiple(self):
        received = []
        of("a", "b", "c").subscribe(on_next=lambda x: received.append(x))
        assert received == ["a", "b", "c"]


class TestFromList:
    def test_basic(self):
        received = []
        from_list([1, 2, 3]).subscribe(on_next=lambda x: received.append(x))
        assert received == [1, 2, 3]


class TestEmpty:
    def test_completes_immediately(self):
        received = []
        completed = [False]
        empty().subscribe(
            on_next=lambda x: received.append(x),
            on_complete=lambda: completed.__setitem__(0, True)
        )
        assert received == []
        assert completed[0]


class TestSimulateObservable:
    def test_of(self):
        result = simulate_observable(["of:1,2,3", "received:"])
        assert "emitted=3" in result[0]
        assert "[1, 2, 3]" in result[1]

    def test_map(self):
        result = simulate_observable(["map:1,2,3", "received:"])
        assert "[2, 4, 6]" in result[1]

    def test_filter(self):
        result = simulate_observable(["filter:1,2,3,4", "received:"])
        assert "[2, 4]" in result[1]

    def test_subject(self):
        result = simulate_observable(["subject:", "received:"])
        assert "subject_done" in result[0]
        assert "[1, 2]" in result[1]
