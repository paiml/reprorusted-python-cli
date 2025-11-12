"""
Test suite for trivial_cli.py
Ensures 100% coverage before transpilation

Following extreme TDD methodology:
1. Write tests first (RED)
2. Implement code to pass tests (GREEN)
3. Refactor (REFACTOR)
"""

import subprocess
import pytest
from pathlib import Path

# Path to the CLI script
SCRIPT = Path(__file__).parent / "trivial_cli.py"


def run_cli(*args):
    """
    Helper to run CLI and capture output

    Args:
        *args: Command-line arguments to pass to the script

    Returns:
        subprocess.CompletedProcess: Result with returncode, stdout, stderr
    """
    result = subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True
    )
    return result


class TestTrivialCLI:
    """Test suite for trivial_cli.py"""

    def test_help_flag(self):
        """Test --help displays usage information"""
        result = run_cli("--help")
        assert result.returncode == 0, "Help should exit successfully"
        assert "usage:" in result.stdout.lower(), "Help should show usage"
        assert "trivial_cli.py" in result.stdout, "Should show script name"
        assert "--name" in result.stdout, "--name argument should be documented"
        assert "Name to greet" in result.stdout or "name to greet" in result.stdout.lower(), \
            "Should describe --name argument"

    def test_version_flag(self):
        """Test --version displays version information"""
        result = run_cli("--version")
        assert result.returncode == 0, "Version should exit successfully"
        assert "1.0.0" in result.stdout, "Should display version 1.0.0"

    def test_basic_execution_with_name(self):
        """Test basic CLI execution with --name argument"""
        result = run_cli("--name", "Alice")
        assert result.returncode == 0, "Should execute successfully"
        assert "Hello, Alice!" in result.stdout, "Should greet Alice"

    def test_missing_required_argument(self):
        """Test error handling when required --name argument is missing"""
        result = run_cli()
        assert result.returncode != 0, "Should fail when --name is missing"
        assert "required" in result.stderr.lower(), "Error should mention 'required'"
        assert "--name" in result.stderr, "Error should mention --name"

    @pytest.mark.parametrize("name,expected", [
        ("Alice", "Hello, Alice!"),
        ("Bob", "Hello, Bob!"),
        ("Charlie", "Hello, Charlie!"),
        ("Dr. Smith", "Hello, Dr. Smith!"),
        ("123", "Hello, 123!"),
        ("", "Hello, !"),  # Edge case: empty string
    ])
    def test_parametrized_names(self, name, expected):
        """
        Test various input names to ensure consistent behavior

        Args:
            name: Name to pass to --name argument
            expected: Expected output string
        """
        result = run_cli("--name", name)
        assert result.returncode == 0, f"Should succeed for name='{name}'"
        assert expected in result.stdout, f"Should output '{expected}' for name='{name}'"

    def test_name_with_special_characters(self):
        """Test handling of special characters in names"""
        special_names = [
            "O'Brien",
            "José",
            "François",
            "北京",  # Chinese characters
            "مرحبا",  # Arabic
        ]

        for name in special_names:
            result = run_cli("--name", name)
            assert result.returncode == 0, f"Should handle special chars: {name}"
            assert name in result.stdout, f"Should preserve special chars in output: {name}"

    def test_long_name(self):
        """Test handling of very long names"""
        long_name = "A" * 1000
        result = run_cli("--name", long_name)
        assert result.returncode == 0, "Should handle long names"
        assert long_name in result.stdout, "Should output full long name"

    def test_name_with_whitespace(self):
        """Test handling of names with leading/trailing whitespace"""
        result = run_cli("--name", "  Alice  ")
        assert result.returncode == 0, "Should handle whitespace"
        # Argparse preserves whitespace
        assert "  Alice  " in result.stdout, "Should preserve whitespace"

    def test_invalid_flag(self):
        """Test error handling for invalid flags"""
        result = run_cli("--invalid-flag")
        assert result.returncode != 0, "Should fail for invalid flag"
        assert "unrecognized" in result.stderr.lower() or "invalid" in result.stderr.lower(), \
            "Error should mention unrecognized/invalid argument"

    def test_name_flag_without_value(self):
        """Test error handling when --name is provided without a value"""
        result = run_cli("--name")
        assert result.returncode != 0, "Should fail when --name has no value"
        assert "expected one argument" in result.stderr.lower() or \
               "argument --name" in result.stderr.lower(), \
            "Error should mention missing value for --name"

    def test_duplicate_name_flag(self):
        """Test behavior when --name is specified multiple times"""
        result = run_cli("--name", "Alice", "--name", "Bob")
        assert result.returncode == 0, "Should accept duplicate flags"
        # Argparse uses the last value
        assert "Hello, Bob!" in result.stdout, "Should use last provided value"

    def test_stderr_is_empty_on_success(self):
        """Test that stderr is empty on successful execution"""
        result = run_cli("--name", "Alice")
        assert result.returncode == 0
        assert result.stderr == "", "stderr should be empty on success"

    def test_stdout_ends_with_newline(self):
        """Test that output ends with newline (proper CLI behavior)"""
        result = run_cli("--name", "Alice")
        assert result.returncode == 0
        assert result.stdout.endswith("\n"), "Output should end with newline"

    def test_script_is_executable_as_main(self):
        """Test that script can be executed as __main__"""
        # This is tested implicitly by all other tests
        # but we explicitly verify the script structure
        result = run_cli("--name", "Test")
        assert result.returncode == 0
        # If this passes, __main__ block is working

    def test_deterministic_output(self):
        """Test that output is deterministic across multiple runs"""
        results = [run_cli("--name", "Alice") for _ in range(3)]

        # All should succeed
        assert all(r.returncode == 0 for r in results), "All runs should succeed"

        # All should have identical output
        first_output = results[0].stdout
        assert all(r.stdout == first_output for r in results), \
            "Output should be deterministic"


class TestEdgeCases:
    """Additional edge case tests for robustness"""

    def test_empty_args_list(self):
        """Test behavior with absolutely no arguments"""
        result = run_cli()
        assert result.returncode != 0, "Should fail with no arguments"

    def test_help_with_other_args(self):
        """Test that --help takes precedence over other arguments"""
        result = run_cli("--help", "--name", "Alice")
        assert result.returncode == 0, "Help should succeed"
        assert "usage:" in result.stdout.lower(), "Should show help"
        # When --help is present, other args are ignored

    def test_version_with_other_args(self):
        """Test that --version takes precedence over other arguments"""
        result = run_cli("--version", "--name", "Alice")
        assert result.returncode == 0, "Version should succeed"
        assert "1.0.0" in result.stdout, "Should show version"
        # When --version is present, other args are ignored
