#!/usr/bin/env python3
"""
Comprehensive test suite for complex_cli.py (example_complex).

This test suite follows the extreme TDD approach with 100% coverage goals.
Tests are written BEFORE implementation (RED phase).

Features Tested:
1. Mutually exclusive groups (--json, --xml, --yaml output formats)
2. Argument groups (input options, output options, processing options)
3. Custom types (port number, positive integer, valid email)
4. File I/O arguments (input file, output file with argparse.FileType)
5. Environment variable fallback (default output format, config file)
6. Default values and validation
7. Error handling

Test Categories:
1. Help and version output
2. Mutually exclusive groups
3. Argument groups
4. Custom type validation
5. File I/O
6. Environment variables
7. Combined features
8. Edge cases and error handling
"""

import os
import subprocess
from pathlib import Path

# Path to the script
SCRIPT_PATH = Path(__file__).parent / "complex_cli.py"


def run_cli(*args, env=None):
    """Helper function to run the CLI with given arguments and optional environment."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)

    result = subprocess.run(
        ["python3", str(SCRIPT_PATH)] + list(args),
        capture_output=True,
        text=True,
        env=full_env,
    )
    return result


class TestHelpAndVersion:
    """Test help and version output."""

    def test_help_flag(self):
        """Test --help flag displays comprehensive help"""
        result = run_cli("--help")
        assert result.returncode == 0, "Help should exit with code 0"
        assert "usage:" in result.stdout.lower(), "Help should show usage"
        # Check for argument groups in help
        assert "input" in result.stdout.lower(), "Help should mention input options"
        assert "output" in result.stdout.lower(), "Help should mention output options"

    def test_version_flag(self):
        """Test --version flag displays version"""
        result = run_cli("--version")
        assert result.returncode == 0, "Version should exit with code 0"
        assert "1.0.0" in result.stdout, "Should display version 1.0.0"


class TestMutuallyExclusiveGroups:
    """Test mutually exclusive argument groups."""

    def test_json_format(self):
        """Test --json output format"""
        result = run_cli("--json", "--input", "test.txt")
        assert result.returncode == 0, "Should succeed with --json"
        assert "json" in result.stdout.lower(), "Output should mention JSON format"

    def test_xml_format(self):
        """Test --xml output format"""
        result = run_cli("--xml", "--input", "test.txt")
        assert result.returncode == 0, "Should succeed with --xml"
        assert "xml" in result.stdout.lower(), "Output should mention XML format"

    def test_yaml_format(self):
        """Test --yaml output format"""
        result = run_cli("--yaml", "--input", "test.txt")
        assert result.returncode == 0, "Should succeed with --yaml"
        assert "yaml" in result.stdout.lower(), "Output should mention YAML format"

    def test_json_and_xml_mutually_exclusive(self):
        """Test that --json and --xml cannot be used together"""
        result = run_cli("--json", "--xml", "--input", "test.txt")
        assert result.returncode != 0, "Should fail when both --json and --xml specified"
        assert (
            "not allowed" in result.stderr.lower() or "mutually exclusive" in result.stderr.lower()
        )

    def test_json_and_yaml_mutually_exclusive(self):
        """Test that --json and --yaml cannot be used together"""
        result = run_cli("--json", "--yaml", "--input", "test.txt")
        assert result.returncode != 0, "Should fail when both --json and --yaml specified"

    def test_xml_and_yaml_mutually_exclusive(self):
        """Test that --xml and --yaml cannot be used together"""
        result = run_cli("--xml", "--yaml", "--input", "test.txt")
        assert result.returncode != 0, "Should fail when both --xml and --yaml specified"

    def test_all_three_formats_mutually_exclusive(self):
        """Test that all three formats cannot be used together"""
        result = run_cli("--json", "--xml", "--yaml", "--input", "test.txt")
        assert result.returncode != 0, "Should fail when all three formats specified"


class TestCustomTypes:
    """Test custom type validation."""

    def test_valid_port_number(self):
        """Test valid port number (1-65535)"""
        result = run_cli("--port", "8080", "--input", "test.txt")
        assert result.returncode == 0, "Should accept valid port number"
        assert "8080" in result.stdout, "Output should show port number"

    def test_port_too_low(self):
        """Test port number below valid range"""
        result = run_cli("--port", "0", "--input", "test.txt")
        assert result.returncode != 0, "Should reject port 0"

    def test_port_too_high(self):
        """Test port number above valid range"""
        result = run_cli("--port", "65536", "--input", "test.txt")
        assert result.returncode != 0, "Should reject port > 65535"

    def test_port_negative(self):
        """Test negative port number"""
        result = run_cli("--port", "-1", "--input", "test.txt")
        assert result.returncode != 0, "Should reject negative port"

    def test_valid_count(self):
        """Test valid positive integer count"""
        result = run_cli("--count", "10", "--input", "test.txt")
        assert result.returncode == 0, "Should accept positive integer"
        assert "10" in result.stdout, "Output should show count"

    def test_count_zero(self):
        """Test count of zero (should fail for positive integer)"""
        result = run_cli("--count", "0", "--input", "test.txt")
        assert result.returncode != 0, "Should reject count of 0"

    def test_count_negative(self):
        """Test negative count"""
        result = run_cli("--count", "-5", "--input", "test.txt")
        assert result.returncode != 0, "Should reject negative count"

    def test_valid_email(self):
        """Test valid email address"""
        result = run_cli("--email", "user@example.com", "--input", "test.txt")
        assert result.returncode == 0, "Should accept valid email"
        assert "user@example.com" in result.stdout

    def test_invalid_email_no_at(self):
        """Test invalid email without @ symbol"""
        result = run_cli("--email", "userexample.com", "--input", "test.txt")
        assert result.returncode != 0, "Should reject email without @"

    def test_invalid_email_no_domain(self):
        """Test invalid email without domain"""
        result = run_cli("--email", "user@", "--input", "test.txt")
        assert result.returncode != 0, "Should reject email without domain"


class TestFileIO:
    """Test file I/O arguments."""

    def test_input_file_required(self):
        """Test that --input is required"""
        result = run_cli()
        assert result.returncode != 0, "Should fail without --input"
        assert "required" in result.stderr.lower() or "expected" in result.stderr.lower()

    def test_input_file_specified(self):
        """Test with input file specified"""
        result = run_cli("--input", "data.txt")
        assert result.returncode == 0, "Should succeed with --input"
        assert "data.txt" in result.stdout, "Output should mention input file"

    def test_output_file_optional(self):
        """Test output file is optional (defaults to stdout)"""
        result = run_cli("--input", "data.txt")
        assert result.returncode == 0, "Should succeed without --output"

    def test_output_file_specified(self):
        """Test with output file specified"""
        result = run_cli("--input", "data.txt", "--output", "result.txt")
        assert result.returncode == 0, "Should succeed with --output"
        assert "result.txt" in result.stdout, "Output should mention output file"

    def test_input_file_with_path(self):
        """Test input file with path"""
        result = run_cli("--input", "/path/to/data.txt")
        assert result.returncode == 0, "Should handle file paths"
        assert "/path/to/data.txt" in result.stdout


class TestEnvironmentVariables:
    """Test environment variable fallback."""

    def test_default_format_from_env(self):
        """Test DEFAULT_FORMAT environment variable"""
        result = run_cli("--input", "test.txt", env={"DEFAULT_FORMAT": "xml"})
        assert result.returncode == 0, "Should succeed with env var"
        # When no format flag is given, should use env var default
        assert "xml" in result.stdout.lower() or "format" in result.stdout.lower()

    def test_format_flag_overrides_env(self):
        """Test that explicit --json overrides DEFAULT_FORMAT env var"""
        result = run_cli("--json", "--input", "test.txt", env={"DEFAULT_FORMAT": "xml"})
        assert result.returncode == 0, "Should succeed"
        assert "json" in result.stdout.lower(), "Explicit flag should override env var"

    def test_config_file_from_env(self):
        """Test CONFIG_FILE environment variable"""
        result = run_cli("--input", "test.txt", env={"CONFIG_FILE": "/etc/config.yaml"})
        assert result.returncode == 0, "Should accept config file from env"


class TestArgumentGroups:
    """Test that argument groups work correctly."""

    def test_input_group_arguments(self):
        """Test input group arguments work together"""
        result = run_cli("--input", "data.txt", "--encoding", "utf-8")
        assert result.returncode == 0, "Input group args should work"
        assert "utf-8" in result.stdout, "Output should show encoding"

    def test_output_group_arguments(self):
        """Test output group arguments work together"""
        result = run_cli("--input", "data.txt", "--output", "result.txt", "--json")
        assert result.returncode == 0, "Output group args should work"

    def test_processing_group_arguments(self):
        """Test processing group arguments work together"""
        result = run_cli("--input", "data.txt", "--count", "5", "--port", "8080")
        assert result.returncode == 0, "Processing group args should work"


class TestCombinedFeatures:
    """Test combinations of features."""

    def test_full_command_json(self):
        """Test full command with JSON output"""
        result = run_cli(
            "--input",
            "data.txt",
            "--output",
            "result.txt",
            "--json",
            "--port",
            "8080",
            "--count",
            "10",
            "--email",
            "user@example.com",
        )
        assert result.returncode == 0, "Full command should succeed"
        assert "json" in result.stdout.lower()
        assert "8080" in result.stdout
        assert "10" in result.stdout
        assert "user@example.com" in result.stdout

    def test_full_command_xml(self):
        """Test full command with XML output"""
        result = run_cli(
            "--input",
            "data.txt",
            "--xml",
            "--count",
            "5",
        )
        assert result.returncode == 0, "Full command should succeed"
        assert "xml" in result.stdout.lower()

    def test_minimal_command(self):
        """Test minimal required arguments only"""
        result = run_cli("--input", "data.txt")
        assert result.returncode == 0, "Minimal command should succeed"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_port_boundary_1(self):
        """Test port number at lower boundary (1)"""
        result = run_cli("--port", "1", "--input", "test.txt")
        assert result.returncode == 0, "Port 1 should be valid"

    def test_port_boundary_65535(self):
        """Test port number at upper boundary (65535)"""
        result = run_cli("--port", "65535", "--input", "test.txt")
        assert result.returncode == 0, "Port 65535 should be valid"

    def test_count_boundary_1(self):
        """Test count at lower boundary (1)"""
        result = run_cli("--count", "1", "--input", "test.txt")
        assert result.returncode == 0, "Count 1 should be valid"

    def test_very_long_input_path(self):
        """Test with very long file path"""
        long_path = "a" * 200 + ".txt"
        result = run_cli("--input", long_path)
        assert result.returncode == 0, "Should handle long paths"

    def test_special_chars_in_filename(self):
        """Test filename with special characters"""
        result = run_cli("--input", "file-name_2024.txt")
        assert result.returncode == 0, "Should handle special chars in filename"

    def test_stdout_ends_with_newline(self):
        """Test that output ends with newline"""
        result = run_cli("--input", "test.txt")
        if result.stdout:
            assert result.stdout.endswith("\n"), "Output should end with newline"

    def test_deterministic_output(self):
        """Test that output is deterministic across multiple runs"""
        result1 = run_cli("--input", "test.txt", "--json")
        result2 = run_cli("--input", "test.txt", "--json")
        assert result1.stdout == result2.stdout, "Output should be deterministic"
        assert result1.returncode == result2.returncode


class TestErrorMessages:
    """Test error messages are helpful."""

    def test_missing_input_error_message(self):
        """Test error message when --input is missing"""
        result = run_cli("--json")
        assert result.returncode != 0
        assert "--input" in result.stderr or "input" in result.stderr.lower()

    def test_invalid_port_error_message(self):
        """Test error message for invalid port"""
        result = run_cli("--port", "99999", "--input", "test.txt")
        assert result.returncode != 0
        assert "port" in result.stderr.lower() or "invalid" in result.stderr.lower()

    def test_mutual_exclusion_error_message(self):
        """Test error message for mutually exclusive args"""
        result = run_cli("--json", "--xml", "--input", "test.txt")
        assert result.returncode != 0
        # Error should clearly indicate the conflict
        assert (
            "not allowed" in result.stderr.lower()
            or "mutually exclusive" in result.stderr.lower()
            or "one of" in result.stderr.lower()
        )
