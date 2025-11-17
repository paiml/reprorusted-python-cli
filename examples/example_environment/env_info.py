#!/usr/bin/env python3
"""
Environment Example - Environment variables and system information

Demonstrates:
- os.environ access (get, set, check existence)
- os.path operations (join, exists, expanduser, dirname, basename)
- sys module (platform, version, argv, exit)
- platform module (system, machine, python_version)
- Cross-platform path handling

This validates depyler's ability to transpile common system interactions
to Rust (std::env, std::path, conditional compilation).
"""

import argparse
import os
import platform
import sys


def show_system_info():
    """
    Display system information

    Depyler: proven to terminate
    """
    print("System Information:")
    print(f"  Platform: {sys.platform}")
    print(f"  OS: {platform.system()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Python: {platform.python_version()}")


def show_environment(var_name=None):
    """
    Display environment variables

    Args:
        var_name: Specific variable to show, or None for common vars

    Depyler: proven to terminate
    """
    if var_name:
        value = os.environ.get(var_name)
        if value:
            print(f"{var_name}={value}")
        else:
            print(f"{var_name} not set")
    else:
        # Show common environment variables
        common_vars = ["HOME", "USER", "PATH", "SHELL", "PWD"]
        print("Common environment variables:")
        for var in common_vars:
            value = os.environ.get(var, "(not set)")
            # Truncate PATH for readability
            if var == "PATH" and len(value) > 50:
                value = value[:47] + "..."
            print(f"  {var}={value}")


def check_path(path):
    """
    Check if path exists and show information

    Args:
        path: Path to check

    Depyler: proven to terminate
    """
    # Expand user home directory
    expanded = os.path.expanduser(path)

    print(f"Path: {path}")
    if path != expanded:
        print(f"Expanded: {expanded}")

    print(f"Exists: {os.path.exists(expanded)}")

    if os.path.exists(expanded):
        print(f"Is file: {os.path.isfile(expanded)}")
        print(f"Is directory: {os.path.isdir(expanded)}")
        print(f"Absolute: {os.path.abspath(expanded)}")
        print(f"Dirname: {os.path.dirname(expanded)}")
        print(f"Basename: {os.path.basename(expanded)}")


def join_paths(*parts):
    """
    Join path components and display result

    Args:
        parts: Path components to join

    Depyler: proven to terminate
    """
    result = os.path.join(*parts)
    print(f"Joined path: {result}")
    return result


def main():
    """
    Main entry point for environment info CLI

    Demonstrates environment variable and path operations.
    """
    parser = argparse.ArgumentParser(
        description="Environment variables and system information",
        prog="env_info.py",
    )

    parser.add_argument("--version", action="version", version="1.0.0")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # System info command
    subparsers.add_parser("system", help="Show system information")

    # Environment variable command
    env_parser = subparsers.add_parser("env", help="Show environment variables")
    env_parser.add_argument("variable", nargs="?", help="Specific variable to show")

    # Path check command
    path_parser = subparsers.add_parser("path", help="Check if path exists")
    path_parser.add_argument("target", help="Path to check")

    # Path join command
    join_parser = subparsers.add_parser("join", help="Join path components")
    join_parser.add_argument("parts", nargs="+", help="Path components to join")

    args = parser.parse_args()

    # Execute command
    if args.command == "system":
        show_system_info()

    elif args.command == "env":
        show_environment(args.variable)

    elif args.command == "path":
        check_path(args.target)

    elif args.command == "join":
        join_paths(*args.parts)


if __name__ == "__main__":
    main()
