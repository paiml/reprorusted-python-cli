"""Observable Pattern CLI.

Demonstrates Observable/Observer reactive pattern.
"""

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Observer(ABC, Generic[T]):
    """Observer interface."""

    @abstractmethod
    def on_next(self, value: T) -> None:
        """Handle next value."""
        pass

    @abstractmethod
    def on_error(self, error: Exception) -> None:
        """Handle error."""
        pass

    @abstractmethod
    def on_complete(self) -> None:
        """Handle completion."""
        pass


@dataclass
class Subscription:
    """Subscription handle."""

    _unsubscribe: Callable[[], None]
    _closed: bool = False

    def unsubscribe(self) -> None:
        if not self._closed:
            self._unsubscribe()
            self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed


class FunctionObserver(Observer[T]):
    """Observer from callback functions."""

    def __init__(
        self,
        on_next: Callable[[T], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        self._on_next = on_next or (lambda x: None)
        self._on_error = on_error or (lambda e: None)
        self._on_complete = on_complete or (lambda: None)

    def on_next(self, value: T) -> None:
        self._on_next(value)

    def on_error(self, error: Exception) -> None:
        self._on_error(error)

    def on_complete(self) -> None:
        self._on_complete()


class Observable(Generic[T]):
    """Observable stream of values."""

    def __init__(self, subscribe_fn: Callable[[Observer[T]], Callable[[], None]]) -> None:
        self._subscribe_fn = subscribe_fn

    def subscribe(
        self,
        on_next: Callable[[T], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        on_complete: Callable[[], None] | None = None,
    ) -> Subscription:
        observer = FunctionObserver(on_next, on_error, on_complete)
        unsubscribe = self._subscribe_fn(observer)
        return Subscription(unsubscribe)

    def map(self, fn: Callable[[T], Any]) -> "Observable[Any]":
        """Transform values with a function."""
        source = self

        def subscribe_fn(observer: Observer[Any]) -> Callable[[], None]:
            return source._subscribe_fn(
                FunctionObserver(
                    on_next=lambda x: observer.on_next(fn(x)),
                    on_error=observer.on_error,
                    on_complete=observer.on_complete,
                )
            )

        return Observable(subscribe_fn)

    def filter(self, pred: Callable[[T], bool]) -> "Observable[T]":
        """Filter values by predicate."""
        source = self

        def subscribe_fn(observer: Observer[T]) -> Callable[[], None]:
            return source._subscribe_fn(
                FunctionObserver(
                    on_next=lambda x: observer.on_next(x) if pred(x) else None,
                    on_error=observer.on_error,
                    on_complete=observer.on_complete,
                )
            )

        return Observable(subscribe_fn)

    def take(self, count: int) -> "Observable[T]":
        """Take first n values."""
        source = self

        def subscribe_fn(observer: Observer[T]) -> Callable[[], None]:
            remaining = [count]

            def on_next(x: T) -> None:
                if remaining[0] > 0:
                    remaining[0] -= 1
                    observer.on_next(x)
                    if remaining[0] == 0:
                        observer.on_complete()

            return source._subscribe_fn(
                FunctionObserver(on_next, observer.on_error, observer.on_complete)
            )

        return Observable(subscribe_fn)


class Subject(Observable[T], Observer[T]):
    """Both Observable and Observer."""

    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []
        self._completed = False
        self._error: Exception | None = None

        def subscribe_fn(observer: Observer[T]) -> Callable[[], None]:
            if self._completed:
                observer.on_complete()
                return lambda: None
            if self._error:
                observer.on_error(self._error)
                return lambda: None

            self._observers.append(observer)
            return lambda: self._observers.remove(observer) if observer in self._observers else None

        super().__init__(subscribe_fn)

    def on_next(self, value: T) -> None:
        if not self._completed:
            for observer in list(self._observers):
                observer.on_next(value)

    def on_error(self, error: Exception) -> None:
        if not self._completed:
            self._error = error
            for observer in list(self._observers):
                observer.on_error(error)
            self._observers.clear()

    def on_complete(self) -> None:
        if not self._completed:
            self._completed = True
            for observer in list(self._observers):
                observer.on_complete()
            self._observers.clear()


class BehaviorSubject(Subject[T]):
    """Subject that emits current value to new subscribers."""

    def __init__(self, initial: T) -> None:
        self._value = initial
        super().__init__()

    def on_next(self, value: T) -> None:
        self._value = value
        super().on_next(value)

    def subscribe(self, *args, **kwargs) -> Subscription:
        sub = super().subscribe(*args, **kwargs)
        if args and args[0]:
            args[0](self._value)
        return sub

    @property
    def value(self) -> T:
        return self._value


# Factory functions
def of(*values: T) -> Observable[T]:
    """Create Observable from values."""

    def subscribe_fn(observer: Observer[T]) -> Callable[[], None]:
        for v in values:
            observer.on_next(v)
        observer.on_complete()
        return lambda: None

    return Observable(subscribe_fn)


def from_list(lst: list[T]) -> Observable[T]:
    """Create Observable from list."""
    return of(*lst)


def empty() -> Observable[Any]:
    """Create empty Observable."""

    def subscribe_fn(observer: Observer[Any]) -> Callable[[], None]:
        observer.on_complete()
        return lambda: None

    return Observable(subscribe_fn)


def simulate_observable(operations: list[str]) -> list[str]:
    """Simulate observable operations."""
    results: list[str] = []
    received: list[Any] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "of":
            values = [int(x) for x in parts[1].split(",")]
            obs = of(*values)
            obs.subscribe(on_next=lambda x: received.append(x))
            results.append(f"emitted={len(values)}")
        elif cmd == "map":
            values = [int(x) for x in parts[1].split(",")]
            of(*values).map(lambda x: x * 2).subscribe(on_next=lambda x: received.append(x))
            results.append("mapped")
        elif cmd == "filter":
            values = [int(x) for x in parts[1].split(",")]
            of(*values).filter(lambda x: x % 2 == 0).subscribe(on_next=lambda x: received.append(x))
            results.append("filtered")
        elif cmd == "received":
            results.append(str(received))
            received.clear()
        elif cmd == "subject":
            subj: Subject[int] = Subject()
            subj.subscribe(on_next=lambda x: received.append(x))
            subj.on_next(1)
            subj.on_next(2)
            subj.on_complete()
            results.append("subject_done")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: event_observable_cli.py <command>")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        received: list[int] = []
        of(1, 2, 3, 4, 5).filter(lambda x: x % 2 == 0).map(lambda x: x * 10).subscribe(
            on_next=lambda x: received.append(x), on_complete=lambda: print("Complete!")
        )
        print(f"Received: {received}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
