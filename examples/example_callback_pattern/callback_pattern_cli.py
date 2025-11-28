#!/usr/bin/env python3
"""Callback Pattern CLI.

Callback and handler function patterns.
"""

import argparse
import sys
from collections.abc import Callable

# Event types
EventHandler = Callable[[str, dict[str, object]], None]
DataProcessor = Callable[[list[int]], list[int]]
Validator = Callable[[object], bool]
ErrorHandler = Callable[[Exception], None]


class EventEmitter:
    """Simple event emitter with callbacks."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event: str, handler: EventHandler) -> None:
        """Register event handler."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def off(self, event: str, handler: EventHandler) -> None:
        """Remove event handler."""
        if event in self._handlers:
            self._handlers[event] = [h for h in self._handlers[event] if h != handler]

    def emit(self, event: str, data: dict[str, object]) -> None:
        """Emit event to all handlers."""
        if event in self._handlers:
            for handler in self._handlers[event]:
                handler(event, data)

    def once(self, event: str, handler: EventHandler) -> None:
        """Register one-time handler."""

        def wrapper(evt: str, data: dict[str, object]) -> None:
            handler(evt, data)
            self.off(event, wrapper)

        self.on(event, wrapper)


class DataPipeline:
    """Data processing pipeline with callbacks."""

    def __init__(self) -> None:
        self._processors: list[DataProcessor] = []
        self._error_handler: ErrorHandler | None = None

    def add_processor(self, processor: DataProcessor) -> "DataPipeline":
        """Add processor to pipeline."""
        self._processors.append(processor)
        return self

    def on_error(self, handler: ErrorHandler) -> "DataPipeline":
        """Set error handler."""
        self._error_handler = handler
        return self

    def process(self, data: list[int]) -> list[int]:
        """Process data through pipeline."""
        result = data
        for processor in self._processors:
            try:
                result = processor(result)
            except Exception as e:
                if self._error_handler:
                    self._error_handler(e)
                raise
        return result


class FormValidator:
    """Form validator with validation callbacks."""

    def __init__(self) -> None:
        self._validators: dict[str, list[Validator]] = {}

    def add_rule(self, field: str, validator: Validator) -> "FormValidator":
        """Add validation rule for field."""
        if field not in self._validators:
            self._validators[field] = []
        self._validators[field].append(validator)
        return self

    def validate(self, data: dict[str, object]) -> tuple[bool, list[str]]:
        """Validate data, return (valid, errors)."""
        errors: list[str] = []
        for field, validators in self._validators.items():
            value = data.get(field)
            for validator in validators:
                if not validator(value):
                    errors.append(f"Validation failed for {field}")
        return (len(errors) == 0, errors)


def create_logger_callback(prefix: str) -> EventHandler:
    """Create logging callback."""

    def handler(event: str, data: dict[str, object]) -> None:
        print(f"[{prefix}] {event}: {data}")

    return handler


def create_filter_callback(predicate: Callable[[int], bool]) -> DataProcessor:
    """Create filter processor callback."""

    def processor(data: list[int]) -> list[int]:
        return [x for x in data if predicate(x)]

    return processor


def create_map_callback(transform: Callable[[int], int]) -> DataProcessor:
    """Create map processor callback."""

    def processor(data: list[int]) -> list[int]:
        return [transform(x) for x in data]

    return processor


def create_range_validator(min_val: int, max_val: int) -> Validator:
    """Create range validator."""

    def validator(value: object) -> bool:
        if not isinstance(value, int):
            return False
        return min_val <= value <= max_val

    return validator


def create_length_validator(min_len: int, max_len: int) -> Validator:
    """Create string length validator."""

    def validator(value: object) -> bool:
        if not isinstance(value, str):
            return False
        return min_len <= len(value) <= max_len

    return validator


def create_pattern_validator(pattern: str) -> Validator:
    """Create pattern validator."""
    import re

    def validator(value: object) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(pattern, value))

    return validator


def with_callback(
    func: Callable[..., object], callback: Callable[[object], None]
) -> Callable[..., object]:
    """Wrap function to call callback with result."""

    def wrapper(*args: object, **kwargs: object) -> object:
        result = func(*args, **kwargs)
        callback(result)
        return result

    return wrapper


def with_error_callback(
    func: Callable[..., object], on_error: ErrorHandler
) -> Callable[..., object]:
    """Wrap function to call error handler on exception."""

    def wrapper(*args: object, **kwargs: object) -> object:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            on_error(e)
            raise

    return wrapper


def async_like(
    func: Callable[..., object], on_complete: Callable[[object], None], on_error: ErrorHandler
) -> Callable[..., None]:
    """Simulate async-style callbacks."""

    def wrapper(*args: object, **kwargs: object) -> None:
        try:
            result = func(*args, **kwargs)
            on_complete(result)
        except Exception as e:
            on_error(e)

    return wrapper


def retry_with_callback(
    func: Callable[[], object], max_retries: int, on_retry: Callable[[int, Exception], None]
) -> object:
    """Retry function with callback on each retry."""
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                on_retry(attempt + 1, e)
    if last_error:
        raise last_error
    raise RuntimeError("No attempts made")


def map_with_callback(
    items: list[int], transform: Callable[[int], int], on_item: Callable[[int, int, int], None]
) -> list[int]:
    """Map with callback for each item (index, old, new)."""
    result: list[int] = []
    for i, item in enumerate(items):
        new_val = transform(item)
        on_item(i, item, new_val)
        result.append(new_val)
    return result


def reduce_with_callback(
    items: list[int],
    func: Callable[[int, int], int],
    initial: int,
    on_step: Callable[[int, int, int], None],
) -> int:
    """Reduce with callback for each step (acc, item, new_acc)."""
    acc = initial
    for item in items:
        new_acc = func(acc, item)
        on_step(acc, item, new_acc)
        acc = new_acc
    return acc


def main() -> int:
    parser = argparse.ArgumentParser(description="Callback pattern CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # events
    subparsers.add_parser("events", help="Test event emitter")

    # pipeline
    pipe_p = subparsers.add_parser("pipeline", help="Test data pipeline")
    pipe_p.add_argument("items", type=int, nargs="+")
    pipe_p.add_argument("--filter-positive", action="store_true")
    pipe_p.add_argument("--double", action="store_true")

    # validate
    val_p = subparsers.add_parser("validate", help="Test form validator")
    val_p.add_argument("--age", type=int)
    val_p.add_argument("--name")

    args = parser.parse_args()

    if args.command == "events":
        emitter = EventEmitter()
        log_handler = create_logger_callback("LOG")
        emitter.on("data", log_handler)
        emitter.emit("data", {"value": 42})
        emitter.emit("data", {"value": 100})

    elif args.command == "pipeline":
        pipeline = DataPipeline()
        if args.filter_positive:
            pipeline.add_processor(create_filter_callback(lambda x: x > 0))
        if args.double:
            pipeline.add_processor(create_map_callback(lambda x: x * 2))
        result = pipeline.process(args.items)
        print(f"Result: {result}")

    elif args.command == "validate":
        validator = FormValidator()
        if args.age is not None:
            validator.add_rule("age", create_range_validator(0, 150))
        if args.name is not None:
            validator.add_rule("name", create_length_validator(1, 50))

        data: dict[str, object] = {}
        if args.age is not None:
            data["age"] = args.age
        if args.name is not None:
            data["name"] = args.name

        valid, errors = validator.validate(data)
        if valid:
            print("Valid!")
        else:
            print(f"Invalid: {', '.join(errors)}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
