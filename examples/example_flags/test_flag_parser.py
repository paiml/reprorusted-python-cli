"""
Test suite for flag_parser.py
Tests boolean flags and their combinations

Following extreme TDD methodology with comprehensive edge cases
"""

import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "flag_parser.py"


def run_cli(*args):
    """Helper to run CLI and capture output"""
    result = subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True)
    return result


class TestFlagParser:
    """Test suite for flag_parser.py"""

    def test_help_flag(self):
        """Test --help displays usage"""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "--verbose" in result.stdout
        assert "--debug" in result.stdout
        assert "--quiet" in result.stdout

    def test_version_flag(self):
        """Test --version displays version"""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_no_flags(self):
        """Test execution with no flags (all defaults)"""
        result = run_cli()
        assert result.returncode == 0
        assert "Verbose: False" in result.stdout
        assert "Debug: False" in result.stdout
        assert "Quiet: False" in result.stdout

    def test_verbose_flag_alone(self):
        """Test --verbose flag by itself"""
        result = run_cli("--verbose")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: False" in result.stdout
        assert "Quiet: False" in result.stdout
        assert "VERBOSE MODE ENABLED" in result.stdout

    def test_verbose_flag_short_form(self):
        """Test -v short form for verbose"""
        result = run_cli("-v")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "VERBOSE MODE ENABLED" in result.stdout

    def test_debug_flag_alone(self):
        """Test --debug flag by itself"""
        result = run_cli("--debug")
        assert result.returncode == 0
        assert "Verbose: False" in result.stdout
        assert "Debug: True" in result.stdout
        assert "Quiet: False" in result.stdout
        assert "DEBUG MODE ENABLED" in result.stdout

    def test_debug_flag_short_form(self):
        """Test -d short form for debug"""
        result = run_cli("-d")
        assert result.returncode == 0
        assert "Debug: True" in result.stdout
        assert "DEBUG MODE ENABLED" in result.stdout

    def test_quiet_flag_alone(self):
        """Test --quiet flag by itself"""
        result = run_cli("--quiet")
        assert result.returncode == 0
        assert "Verbose: False" in result.stdout
        assert "Debug: False" in result.stdout
        assert "Quiet: True" in result.stdout
        assert "QUIET MODE ENABLED" in result.stdout

    def test_quiet_flag_short_form(self):
        """Test -q short form for quiet"""
        result = run_cli("-q")
        assert result.returncode == 0
        assert "Quiet: True" in result.stdout
        assert "QUIET MODE ENABLED" in result.stdout

    def test_verbose_and_debug(self):
        """Test --verbose and --debug together"""
        result = run_cli("--verbose", "--debug")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: True" in result.stdout
        assert "Quiet: False" in result.stdout
        assert "VERBOSE MODE ENABLED" in result.stdout
        assert "DEBUG MODE ENABLED" in result.stdout

    def test_verbose_and_debug_short_form(self):
        """Test -v and -d together"""
        result = run_cli("-v", "-d")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: True" in result.stdout

    def test_verbose_and_quiet(self):
        """Test --verbose and --quiet together (both can be set)"""
        result = run_cli("--verbose", "--quiet")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Quiet: True" in result.stdout
        # Both modes enabled (not mutually exclusive in this implementation)
        assert "VERBOSE MODE ENABLED" in result.stdout
        assert "QUIET MODE ENABLED" in result.stdout

    def test_debug_and_quiet(self):
        """Test --debug and --quiet together"""
        result = run_cli("--debug", "--quiet")
        assert result.returncode == 0
        assert "Debug: True" in result.stdout
        assert "Quiet: True" in result.stdout
        assert "DEBUG MODE ENABLED" in result.stdout
        assert "QUIET MODE ENABLED" in result.stdout

    def test_all_three_flags(self):
        """Test all three flags together"""
        result = run_cli("--verbose", "--debug", "--quiet")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: True" in result.stdout
        assert "Quiet: True" in result.stdout
        assert "VERBOSE MODE ENABLED" in result.stdout
        assert "DEBUG MODE ENABLED" in result.stdout
        assert "QUIET MODE ENABLED" in result.stdout

    def test_all_three_flags_short_form(self):
        """Test all flags with short forms"""
        result = run_cli("-v", "-d", "-q")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: True" in result.stdout
        assert "Quiet: True" in result.stdout

    def test_combined_short_flags(self):
        """Test combined short flags like -vdq"""
        result = run_cli("-vdq")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: True" in result.stdout
        assert "Quiet: True" in result.stdout

    def test_flag_order_doesnt_matter(self):
        """Test that flag order doesn't affect outcome"""
        result1 = run_cli("--verbose", "--debug")
        result2 = run_cli("--debug", "--verbose")

        assert result1.returncode == 0
        assert result2.returncode == 0
        # Both should have same flags set
        assert "Verbose: True" in result1.stdout and "Verbose: True" in result2.stdout
        assert "Debug: True" in result1.stdout and "Debug: True" in result2.stdout

    def test_duplicate_flags(self):
        """Test duplicate flags (should work, argparse stores last value)"""
        result = run_cli("--verbose", "--verbose")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout

    def test_invalid_flag(self):
        """Test error handling for invalid flags"""
        result = run_cli("--invalid")
        assert result.returncode != 0
        assert "unrecognized" in result.stderr.lower() or "invalid" in result.stderr.lower()

    def test_mixed_valid_invalid_flags(self):
        """Test that invalid flags cause error even with valid ones"""
        result = run_cli("--verbose", "--invalid")
        assert result.returncode != 0
        assert "unrecognized" in result.stderr.lower() or "invalid" in result.stderr.lower()

    def test_stderr_empty_on_success(self):
        """Test that stderr is empty on successful execution"""
        result = run_cli("--verbose")
        assert result.returncode == 0
        assert result.stderr == ""

    def test_output_format_consistency(self):
        """Test that output format is consistent"""
        result = run_cli("--verbose")
        lines = result.stdout.strip().split("\n")

        # Should have status lines and mode notification
        assert any("Verbose:" in line for line in lines)
        assert any("Debug:" in line for line in lines)
        assert any("Quiet:" in line for line in lines)

    def test_deterministic_output(self):
        """Test that output is deterministic"""
        results = [run_cli("--verbose", "--debug") for _ in range(3)]

        assert all(r.returncode == 0 for r in results)
        first_output = results[0].stdout
        assert all(r.stdout == first_output for r in results)

    @pytest.mark.parametrize(
        "flag,short",
        [
            ("--verbose", "-v"),
            ("--debug", "-d"),
            ("--quiet", "-q"),
        ],
    )
    def test_long_and_short_forms_equivalent(self, flag, short):
        """Test that long and short forms produce identical output"""
        result_long = run_cli(flag)
        result_short = run_cli(short)

        assert result_long.returncode == result_short.returncode
        assert result_long.stdout == result_short.stdout


class TestEdgeCases:
    """Additional edge case tests"""

    def test_help_with_flags(self):
        """Test that --help takes precedence"""
        result = run_cli("--help", "--verbose", "--debug")
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()

    def test_version_with_flags(self):
        """Test that --version takes precedence"""
        result = run_cli("--version", "--verbose")
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_only_short_flags(self):
        """Test using only short forms"""
        result = run_cli("-v", "-d", "-q")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: True" in result.stdout
        assert "Quiet: True" in result.stdout

    def test_only_long_flags(self):
        """Test using only long forms"""
        result = run_cli("--verbose", "--debug", "--quiet")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: True" in result.stdout
        assert "Quiet: True" in result.stdout

    def test_mixed_long_and_short(self):
        """Test mixing long and short forms"""
        result = run_cli("-v", "--debug", "-q")
        assert result.returncode == 0
        assert "Verbose: True" in result.stdout
        assert "Debug: True" in result.stdout
        assert "Quiet: True" in result.stdout
