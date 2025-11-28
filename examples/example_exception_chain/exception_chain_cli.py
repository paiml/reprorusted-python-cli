#!/usr/bin/env python3
"""Exception Chain CLI.

Exception chaining patterns with raise from.
"""

import argparse
import sys


class DatabaseError(Exception):
    """Database operation error."""

    pass


class ConnectionError(Exception):
    """Connection error."""

    pass


class ConfigError(Exception):
    """Configuration error."""

    pass


class ParseError(Exception):
    """Parsing error."""

    pass


class ProcessingError(Exception):
    """Processing error."""

    pass


def parse_config_line(line: str) -> tuple[str, str]:
    """Parse a config line into key-value pair."""
    try:
        key, value = line.split("=", 1)
        return (key.strip(), value.strip())
    except ValueError as e:
        raise ConfigError(f"Invalid config line: {line}") from e


def load_config_value(config: dict[str, str], key: str) -> str:
    """Load a config value, raise if missing."""
    try:
        return config[key]
    except KeyError as e:
        raise ConfigError(f"Missing required config: {key}") from e


def parse_int_config(value: str, name: str) -> int:
    """Parse integer config value."""
    try:
        return int(value)
    except ValueError as e:
        raise ConfigError(f"Invalid integer for {name}: {value}") from e


def connect_database(host: str, port: int) -> str:
    """Simulate database connection."""
    if not host:
        raise ConnectionError("Empty host")
    if port < 1 or port > 65535:
        raise ConnectionError(f"Invalid port: {port}")
    return f"connected:{host}:{port}"


def initialize_database(config: dict[str, str]) -> str:
    """Initialize database from config."""
    try:
        host = load_config_value(config, "db_host")
        port_str = load_config_value(config, "db_port")
        port = parse_int_config(port_str, "db_port")
        return connect_database(host, port)
    except (ConfigError, ConnectionError) as e:
        raise DatabaseError("Failed to initialize database") from e


def parse_json_field(data: str, field: str) -> str:
    """Extract field from simple JSON-like string."""
    try:
        # Simple parsing for demo
        for part in data.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip().strip('"{}')
                value = value.strip().strip('"{}')
                if key == field:
                    return value
        raise KeyError(field)
    except (ValueError, KeyError) as e:
        raise ParseError(f"Cannot parse field '{field}' from data") from e


def process_record(record: str) -> dict[str, str]:
    """Process a record string."""
    try:
        name = parse_json_field(record, "name")
        value = parse_json_field(record, "value")
        return {"name": name, "value": value}
    except ParseError as e:
        raise ProcessingError(f"Failed to process record: {record}") from e


def chain_multiple_operations(data: str) -> str:
    """Chain multiple operations that can fail."""
    try:
        record = process_record(data)
        return f"processed:{record['name']}={record['value']}"
    except ProcessingError as e:
        raise RuntimeError("Operation chain failed") from e


def safe_chain_with_default(data: str, default: str) -> str:
    """Safely chain operations with default."""
    try:
        return chain_multiple_operations(data)
    except RuntimeError:
        return default


def wrap_exception(operation: str, exc: Exception) -> ProcessingError:
    """Wrap an exception with context."""
    new_exc = ProcessingError(f"Error during {operation}")
    new_exc.__cause__ = exc
    return new_exc


def reraise_with_context(value: str, context: str) -> int:
    """Re-raise exception with added context."""
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f"{context}: {e}") from e


def nested_exception_chain(value: str) -> int:
    """Create nested exception chain."""
    try:
        return reraise_with_context(value, "parsing input")
    except ValueError as e:
        raise ProcessingError("Failed to process value") from e


def suppress_original_exception(value: str) -> int:
    """Raise new exception, suppressing original (raise from None)."""
    try:
        return int(value)
    except ValueError:
        raise ProcessingError("Invalid input") from None


def get_exception_chain(exc: Exception) -> list[str]:
    """Get list of exception messages in chain."""
    chain: list[str] = []
    current: Exception | None = exc
    while current is not None:
        chain.append(str(current))
        current = current.__cause__
    return chain


def has_cause(exc: Exception) -> bool:
    """Check if exception has a cause."""
    return exc.__cause__ is not None


def get_root_cause(exc: Exception) -> Exception:
    """Get root cause of exception chain."""
    current = exc
    while current.__cause__ is not None:
        current = current.__cause__
    return current


def count_chain_depth(exc: Exception) -> int:
    """Count depth of exception chain."""
    depth = 0
    current: Exception | None = exc
    while current is not None:
        depth += 1
        current = current.__cause__
    return depth


def format_exception_chain(exc: Exception) -> str:
    """Format exception chain as string."""
    parts: list[str] = []
    current: Exception | None = exc
    level = 0
    while current is not None:
        prefix = "  " * level
        parts.append(f"{prefix}{type(current).__name__}: {current}")
        current = current.__cause__
        level += 1
    return "\n".join(parts)


def try_with_chain_handling(value: str) -> str:
    """Try operation and handle chain appropriately."""
    try:
        result = nested_exception_chain(value)
        return f"success:{result}"
    except ProcessingError as e:
        if e.__cause__ is not None:
            return f"error:{type(e.__cause__).__name__}"
        return "error:unknown"


def batch_process_with_chains(values: list[str]) -> tuple[list[int], list[str]]:
    """Process batch, collecting results and error chains."""
    results: list[int] = []
    errors: list[str] = []
    for v in values:
        try:
            results.append(nested_exception_chain(v))
        except ProcessingError as e:
            chain = format_exception_chain(e)
            errors.append(chain)
    return (results, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Exception chain CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # config
    config_p = subparsers.add_parser("config", help="Parse config")
    config_p.add_argument("line")

    # db
    db_p = subparsers.add_parser("db", help="Initialize DB")
    db_p.add_argument("--host", required=True)
    db_p.add_argument("--port", required=True)

    # process
    proc_p = subparsers.add_parser("process", help="Process record")
    proc_p.add_argument("data")

    # chain
    chain_p = subparsers.add_parser("chain", help="Test chain")
    chain_p.add_argument("value")

    args = parser.parse_args()

    if args.command == "config":
        try:
            key, value = parse_config_line(args.line)
            print(f"Key: {key}, Value: {value}")
        except ConfigError as e:
            print(f"Config error: {e}")
            if e.__cause__:
                print(f"Caused by: {e.__cause__}")
            return 1

    elif args.command == "db":
        try:
            config = {"db_host": args.host, "db_port": args.port}
            result = initialize_database(config)
            print(f"Database: {result}")
        except DatabaseError as e:
            print(f"Database error: {e}")
            chain = format_exception_chain(e)
            print(f"Chain:\n{chain}")
            return 1

    elif args.command == "process":
        try:
            result = process_record(args.data)
            print(f"Result: {result}")
        except ProcessingError as e:
            print(f"Processing error: {e}")
            return 1

    elif args.command == "chain":
        result = try_with_chain_handling(args.value)
        print(f"Result: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
