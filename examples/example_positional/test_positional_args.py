"""
Test suite for positional_args.py
Tests positional arguments with choices and nargs

Following extreme TDD methodology
"""

import subprocess
import pytest
from pathlib import Path

SCRIPT = Path(__file__).parent / "positional_args.py"


def run_cli(*args):
    """Helper to run CLI and capture output"""
    result = subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True
    )
    return result


class TestPositionalArgs:
    """Test suite for positional_args.py"""

    def test_help_flag(self):
        """Test --help displays usage"""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "command" in result.stdout.lower()
        assert "targets" in result.stdout.lower()

    def test_version_flag(self):
        """Test --version displays version"""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_start_command_no_targets(self):
        """Test 'start' command with no targets (uses default)"""
        result = run_cli("start")
        assert result.returncode == 0
        assert "Command: start" in result.stdout
        assert "Targets: ['all']" in result.stdout

    def test_start_command_single_target(self):
        """Test 'start' command with single target"""
        result = run_cli("start", "web")
        assert result.returncode == 0
        assert "Command: start" in result.stdout
        assert "Targets: ['web']" in result.stdout

    def test_start_command_multiple_targets(self):
        """Test 'start' command with multiple targets"""
        result = run_cli("start", "web", "db", "cache")
        assert result.returncode == 0
        assert "Command: start" in result.stdout
        assert "'web'" in result.stdout
        assert "'db'" in result.stdout
        assert "'cache'" in result.stdout

    def test_stop_command_no_targets(self):
        """Test 'stop' command with no targets"""
        result = run_cli("stop")
        assert result.returncode == 0
        assert "Command: stop" in result.stdout
        assert "Targets: ['all']" in result.stdout

    def test_stop_command_single_target(self):
        """Test 'stop' command with single target"""
        result = run_cli("stop", "db")
        assert result.returncode == 0
        assert "Command: stop" in result.stdout
        assert "Targets: ['db']" in result.stdout

    def test_restart_command_no_targets(self):
        """Test 'restart' command with no targets"""
        result = run_cli("restart")
        assert result.returncode == 0
        assert "Command: restart" in result.stdout
        assert "Targets: ['all']" in result.stdout

    def test_restart_command_multiple_targets(self):
        """Test 'restart' command with multiple targets"""
        result = run_cli("restart", "web", "api")
        assert result.returncode == 0
        assert "Command: restart" in result.stdout
        assert "'web'" in result.stdout
        assert "'api'" in result.stdout

    def test_invalid_command(self):
        """Test error handling for invalid command"""
        result = run_cli("invalid")
        assert result.returncode != 0
        assert "invalid choice" in result.stderr.lower()

    def test_missing_command(self):
        """Test error handling when command is missing"""
        result = run_cli()
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "following arguments are required" in result.stderr.lower()

    @pytest.mark.parametrize("command", ["start", "stop", "restart"])
    def test_all_commands_valid(self, command):
        """Test that all three commands work"""
        result = run_cli(command)
        assert result.returncode == 0
        assert f"Command: {command}" in result.stdout

    def test_command_case_sensitive(self):
        """Test that commands are case-sensitive"""
        result = run_cli("START")  # Capital letters
        assert result.returncode != 0
        assert "invalid choice" in result.stderr.lower()

    def test_targets_order_preserved(self):
        """Test that target order is preserved"""
        result = run_cli("start", "web", "db", "cache")
        assert result.returncode == 0
        # Check that order is maintained in output
        output = result.stdout
        web_pos = output.find("'web'")
        db_pos = output.find("'db'")
        cache_pos = output.find("'cache'")
        assert web_pos < db_pos < cache_pos, "Order should be preserved"

    def test_duplicate_targets_allowed(self):
        """Test that duplicate targets are allowed (argparse doesn't prevent)"""
        result = run_cli("start", "web", "web")
        assert result.returncode == 0
        assert "'web'" in result.stdout

    def test_many_targets(self):
        """Test with many targets"""
        targets = ["target" + str(i) for i in range(10)]
        result = run_cli("start", *targets)
        assert result.returncode == 0
        for target in targets:
            assert f"'{target}'" in result.stdout

    def test_targets_with_special_chars(self):
        """Test targets with hyphens and underscores"""
        result = run_cli("start", "web-server", "db_cache")
        assert result.returncode == 0
        assert "'web-server'" in result.stdout
        assert "'db_cache'" in result.stdout

    def test_stderr_empty_on_success(self):
        """Test that stderr is empty on success"""
        result = run_cli("start", "web")
        assert result.returncode == 0
        assert result.stderr == ""

    def test_deterministic_output(self):
        """Test that output is deterministic"""
        results = [run_cli("start", "web", "db") for _ in range(3)]
        assert all(r.returncode == 0 for r in results)
        first_output = results[0].stdout
        assert all(r.stdout == first_output for r in results)


class TestEdgeCases:
    """Additional edge case tests"""

    def test_help_with_command(self):
        """Test that --help works even with command specified"""
        result = run_cli("--help", "start")
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()

    def test_version_with_command(self):
        """Test that --version works even with command specified"""
        result = run_cli("--version", "start")
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_empty_string_target(self):
        """Test behavior with empty string as target"""
        result = run_cli("start", "")
        assert result.returncode == 0
        # Argparse should accept empty string as valid
        assert "Command: start" in result.stdout

    def test_only_help_choices_shown(self):
        """Test that help shows only valid choices"""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "start" in result.stdout
        assert "stop" in result.stdout
        assert "restart" in result.stdout
        # Should show choices in help
        assert "{start,stop,restart}" in result.stdout or "start, stop, restart" in result.stdout.lower()
