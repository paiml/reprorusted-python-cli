#!/usr/bin/env python3
"""
Subprocess Example - System calls and process management

Demonstrates:
- subprocess.run() for executing commands
- Capturing stdout/stderr
- Process return codes
- Working directory control
- Error handling for subprocess operations

This validates depyler's ability to transpile subprocess calls
to Rust (std::process::Command).
"""

import argparse
import subprocess
import sys


def run_command(cmd, capture=False, check=False, cwd=None):
    """
    Execute a system command

    Args:
        cmd: List of command and arguments
        capture: Whether to capture output
        check: Whether to raise error on non-zero exit
        cwd: Working directory for command

    Returns:
        Tuple of (returncode, stdout, stderr)

    Depyler: proven to terminate
    """
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, check=check)
        return result.returncode, result.stdout, result.stderr
    else:
        result = subprocess.run(cmd, cwd=cwd, check=check)
        return result.returncode, "", ""


def main():
    """
    Main entry point for task runner CLI

    Executes system commands with various options.
    """
    parser = argparse.ArgumentParser(
        description="Execute system commands with options", prog="task_runner.py"
    )

    parser.add_argument("command", help="Command to execute")

    parser.add_argument("args", nargs="*", default=[], help="Arguments to pass to command")

    parser.add_argument("--capture", action="store_true", help="Capture and display output")

    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with error if command fails",
    )

    parser.add_argument("--cwd", help="Working directory for command")

    parser.add_argument("--version", action="version", version="1.0.0")

    args = parser.parse_args()

    # Build command list
    cmd = [args.command] + args.args

    # Display what we're running
    print(f"Running: {' '.join(cmd)}")

    if args.cwd:
        print(f"Working directory: {args.cwd}")

    # Execute command
    try:
        returncode, stdout, stderr = run_command(
            cmd, capture=args.capture, check=args.check, cwd=args.cwd
        )

        # Display results
        print(f"Exit code: {returncode}")

        if args.capture:
            if stdout:
                print(f"Output:\n{stdout}")
            if stderr:
                print(f"Errors:\n{stderr}", file=sys.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"Command not found: {args.command}", file=sys.stderr)
        sys.exit(127)


if __name__ == "__main__":
    main()
