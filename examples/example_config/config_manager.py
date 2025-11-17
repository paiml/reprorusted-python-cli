#!/usr/bin/env python3
"""
Config File Example - Configuration management

Demonstrates:
- Reading/writing JSON config files
- Merging CLI args with config file defaults
- Subcommands for config operations (get, set, list, init)
- File I/O operations
- Nested dict handling

This validates depyler's ability to transpile file operations
and JSON handling to Rust (serde_json + std::fs).
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_CONFIG = {
    "database": {"host": "localhost", "port": 5432},
    "logging": {"level": "INFO", "file": "app.log"},
    "features": {"debug": False, "verbose": False},
}


def load_config(path):
    """
    Load config from JSON file

    Returns default config if file doesn't exist.
    Depyler: proven to terminate
    """
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(path, config):
    """
    Save config to JSON file

    Depyler: proven to terminate
    """
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def get_nested_value(config, key):
    """
    Get value from nested dict using dot notation

    Example: "database.host" -> config["database"]["host"]
    Depyler: proven to terminate
    """
    keys = key.split(".")
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None
    return value


def set_nested_value(config, key, value):
    """
    Set value in nested dict using dot notation

    Example: "database.host", "db.example.com" -> config["database"]["host"] = "db.example.com"
    Depyler: proven to terminate
    """
    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value


def main():
    """
    Main entry point for config manager CLI

    Supports subcommands: init, get, set, list
    """
    parser = argparse.ArgumentParser(
        description="Configuration file management CLI",
        prog="config_manager.py",
    )

    parser.add_argument(
        "--config", default="config.json", help="Path to config file (default: config.json)"
    )

    subparsers = parser.add_subparsers(dest="action", required=True, help="Action to perform")

    # Init command - create default config
    subparsers.add_parser("init", help="Initialize default config file")

    # Get command - retrieve config value
    get_parser = subparsers.add_parser("get", help="Get config value by key")
    get_parser.add_argument("key", help="Config key using dot notation (e.g., database.host)")

    # Set command - update config value
    set_parser = subparsers.add_parser("set", help="Set config value")
    set_parser.add_argument("key", help="Config key using dot notation")
    set_parser.add_argument("value", help="Config value to set")

    # List command - show all config
    subparsers.add_parser("list", help="List all config values")

    args = parser.parse_args()

    # Handle init action
    if args.action == "init":
        save_config(args.config, DEFAULT_CONFIG)
        print(f"Initialized config at {args.config}")
        return

    # Load config for other actions
    config = load_config(args.config)

    # Handle list action
    if args.action == "list":
        print(json.dumps(config, indent=2))

    # Handle get action
    elif args.action == "get":
        value = get_nested_value(config, args.key)
        if value is None:
            print(f"Error: Key not found: {args.key}", file=sys.stderr)
            sys.exit(1)
        # Format output based on type
        if isinstance(value, (dict, list)):
            print(json.dumps(value, indent=2))
        else:
            print(value)

    # Handle set action
    elif args.action == "set":
        set_nested_value(config, args.key, args.value)
        save_config(args.config, config)
        print(f"Set {args.key} = {args.value}")


if __name__ == "__main__":
    main()
