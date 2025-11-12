#!/usr/bin/env python3
"""
Comprehensive test suite for git_clone.py (example_subcommands).

This test suite follows the extreme TDD approach with 100% coverage goals.
Tests are written BEFORE implementation (RED phase).

Test Categories:
1. Help and version output
2. Global flags
3. Subcommand: clone
4. Subcommand: push
5. Subcommand: pull
6. Error handling (invalid subcommands, missing args)
7. Edge cases
"""

import subprocess
from pathlib import Path

# Path to the script
SCRIPT_PATH = Path(__file__).parent / "git_clone.py"


def run_cli(*args):
    """Helper function to run the CLI with given arguments."""
    result = subprocess.run(
        ["python3", str(SCRIPT_PATH)] + list(args),
        capture_output=True,
        text=True,
    )
    return result


class TestHelpAndVersion:
    """Test help and version output."""

    def test_help_flag(self):
        """Test --help flag displays help message"""
        result = run_cli("--help")
        assert result.returncode == 0, "Help should exit with code 0"
        assert "usage:" in result.stdout.lower(), "Help should show usage"
        assert "clone" in result.stdout.lower(), "Help should mention clone subcommand"
        assert "push" in result.stdout.lower(), "Help should mention push subcommand"
        assert "pull" in result.stdout.lower(), "Help should mention pull subcommand"

    def test_short_help_flag(self):
        """Test -h short form of help"""
        result = run_cli("-h")
        assert result.returncode == 0, "Short help should exit with code 0"
        assert "usage:" in result.stdout.lower(), "Short help should show usage"

    def test_version_flag(self):
        """Test --version flag displays version"""
        result = run_cli("--version")
        assert result.returncode == 0, "Version should exit with code 0"
        assert "1.0.0" in result.stdout, "Should display version 1.0.0"

    def test_no_args_shows_help(self):
        """Test that running with no arguments shows help or error"""
        result = run_cli()
        assert result.returncode != 0, "No arguments should fail"
        # Should either show help or error message
        assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower(), (
            "Should show usage information"
        )


class TestGlobalFlags:
    """Test global flags that apply to all subcommands."""

    def test_verbose_flag_with_clone(self):
        """Test --verbose flag with clone subcommand"""
        result = run_cli("--verbose", "clone", "https://example.com/repo.git")
        assert result.returncode == 0, "Should succeed with verbose flag"
        assert "verbose mode" in result.stdout.lower() or "verbose" in result.stdout.lower()

    def test_verbose_short_form(self):
        """Test -v short form of verbose flag"""
        result = run_cli("-v", "clone", "https://example.com/repo.git")
        assert result.returncode == 0, "Should succeed with -v flag"

    def test_verbose_after_subcommand(self):
        """Test that verbose flag works after subcommand (if supported)"""
        # Some CLIs allow flags after subcommands
        result = run_cli("clone", "--verbose", "https://example.com/repo.git")
        # This might fail depending on implementation, check either way
        assert result.returncode == 0 or "unrecognized" in result.stderr.lower()


class TestCloneSubcommand:
    """Test the 'clone' subcommand."""

    def test_clone_with_url(self):
        """Test clone subcommand with valid URL"""
        result = run_cli("clone", "https://example.com/repo.git")
        assert result.returncode == 0, "Clone should succeed"
        assert "clone" in result.stdout.lower(), "Output should mention cloning"
        assert "https://example.com/repo.git" in result.stdout, "Should display the URL"

    def test_clone_with_ssh_url(self):
        """Test clone with SSH URL format"""
        result = run_cli("clone", "git@github.com:user/repo.git")
        assert result.returncode == 0, "Clone should work with SSH URL"
        assert "git@github.com:user/repo.git" in result.stdout

    def test_clone_with_local_path(self):
        """Test clone with local file path"""
        result = run_cli("clone", "/path/to/local/repo")
        assert result.returncode == 0, "Clone should work with local path"
        assert "/path/to/local/repo" in result.stdout

    def test_clone_without_url(self):
        """Test clone without required URL argument"""
        result = run_cli("clone")
        assert result.returncode != 0, "Clone without URL should fail"
        assert "required" in result.stderr.lower() or "expected" in result.stderr.lower()

    def test_clone_help(self):
        """Test help for clone subcommand"""
        result = run_cli("clone", "--help")
        assert result.returncode == 0, "Clone help should succeed"
        assert "clone" in result.stdout.lower()
        assert "url" in result.stdout.lower(), "Should mention URL argument"


class TestPushSubcommand:
    """Test the 'push' subcommand."""

    def test_push_with_remote(self):
        """Test push subcommand with remote name"""
        result = run_cli("push", "origin")
        assert result.returncode == 0, "Push should succeed"
        assert "push" in result.stdout.lower(), "Output should mention pushing"
        assert "origin" in result.stdout, "Should display the remote name"

    def test_push_with_different_remote(self):
        """Test push with non-standard remote name"""
        result = run_cli("push", "upstream")
        assert result.returncode == 0, "Push should work with any remote name"
        assert "upstream" in result.stdout

    def test_push_without_remote(self):
        """Test push without required remote argument"""
        result = run_cli("push")
        assert result.returncode != 0, "Push without remote should fail"
        assert "required" in result.stderr.lower() or "expected" in result.stderr.lower()

    def test_push_help(self):
        """Test help for push subcommand"""
        result = run_cli("push", "--help")
        assert result.returncode == 0, "Push help should succeed"
        assert "push" in result.stdout.lower()
        assert "remote" in result.stdout.lower(), "Should mention remote argument"


class TestPullSubcommand:
    """Test the 'pull' subcommand."""

    def test_pull_with_remote(self):
        """Test pull subcommand with remote name"""
        result = run_cli("pull", "origin")
        assert result.returncode == 0, "Pull should succeed"
        assert "pull" in result.stdout.lower(), "Output should mention pulling"
        assert "origin" in result.stdout, "Should display the remote name"

    def test_pull_with_different_remote(self):
        """Test pull with non-standard remote name"""
        result = run_cli("pull", "upstream")
        assert result.returncode == 0, "Pull should work with any remote name"
        assert "upstream" in result.stdout

    def test_pull_without_remote(self):
        """Test pull without required remote argument"""
        result = run_cli("pull")
        assert result.returncode != 0, "Pull without remote should fail"
        assert "required" in result.stderr.lower() or "expected" in result.stderr.lower()

    def test_pull_help(self):
        """Test help for pull subcommand"""
        result = run_cli("pull", "--help")
        assert result.returncode == 0, "Pull help should succeed"
        assert "pull" in result.stdout.lower()
        assert "remote" in result.stdout.lower(), "Should mention remote argument"


class TestErrorHandling:
    """Test error handling for invalid commands and arguments."""

    def test_invalid_subcommand(self):
        """Test error handling for unrecognized subcommand"""
        result = run_cli("invalid-command")
        assert result.returncode != 0, "Invalid subcommand should fail"
        assert (
            "invalid choice" in result.stderr.lower() or "unrecognized" in result.stderr.lower()
        ), "Should report invalid/unrecognized command"

    def test_clone_with_extra_args(self):
        """Test clone with too many arguments"""
        result = run_cli("clone", "url1", "url2")
        assert result.returncode != 0, "Clone with extra args should fail"

    def test_push_with_extra_args(self):
        """Test push with too many arguments"""
        result = run_cli("push", "remote1", "remote2")
        assert result.returncode != 0, "Push with extra args should fail"

    def test_typo_in_subcommand(self):
        """Test common typos in subcommands"""
        result = run_cli("clon", "https://example.com/repo.git")
        assert result.returncode != 0, "Typo in subcommand should fail"


class TestVerboseCombinations:
    """Test verbose flag with all subcommands."""

    def test_verbose_clone(self):
        """Test verbose flag with clone"""
        result = run_cli("--verbose", "clone", "https://example.com/repo.git")
        assert result.returncode == 0
        # Verbose output should show more details
        assert "verbose" in result.stdout.lower() or len(result.stdout) > 50

    def test_verbose_push(self):
        """Test verbose flag with push"""
        result = run_cli("--verbose", "push", "origin")
        assert result.returncode == 0
        assert "verbose" in result.stdout.lower() or len(result.stdout) > 50

    def test_verbose_pull(self):
        """Test verbose flag with pull"""
        result = run_cli("--verbose", "pull", "origin")
        assert result.returncode == 0
        assert "verbose" in result.stdout.lower() or len(result.stdout) > 50


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_clone_with_whitespace_in_url(self):
        """Test clone with URL containing whitespace"""
        result = run_cli("clone", "https://example.com/repo with spaces.git")
        assert result.returncode == 0, "Should handle URLs with spaces"
        assert "repo with spaces" in result.stdout

    def test_clone_with_special_chars(self):
        """Test clone with special characters in URL"""
        result = run_cli("clone", "https://example.com/repo-name_v2.0.git")
        assert result.returncode == 0, "Should handle special chars in URL"

    def test_push_remote_with_hyphen(self):
        """Test push with remote name containing hyphen"""
        result = run_cli("push", "my-remote")
        assert result.returncode == 0, "Should handle hyphens in remote name"
        assert "my-remote" in result.stdout

    def test_very_long_url(self):
        """Test clone with very long URL"""
        long_url = "https://example.com/" + "a" * 200 + ".git"
        result = run_cli("clone", long_url)
        assert result.returncode == 0, "Should handle long URLs"

    def test_empty_string_url(self):
        """Test clone with empty string as URL"""
        result = run_cli("clone", "")
        # This might succeed or fail depending on implementation
        # Just check it doesn't crash
        assert result.returncode in [0, 2], "Should handle empty string gracefully"

    def test_stdout_ends_with_newline(self):
        """Test that output ends with newline"""
        result = run_cli("clone", "https://example.com/repo.git")
        assert result.returncode == 0
        if result.stdout:
            assert result.stdout.endswith("\n"), "Output should end with newline"

    def test_deterministic_output(self):
        """Test that output is deterministic across multiple runs"""
        result1 = run_cli("clone", "https://example.com/repo.git")
        result2 = run_cli("clone", "https://example.com/repo.git")
        assert result1.stdout == result2.stdout, "Output should be deterministic"
        assert result1.returncode == result2.returncode, "Return code should be consistent"


class TestSubcommandCaseSensitivity:
    """Test case sensitivity of subcommands."""

    def test_clone_lowercase(self):
        """Test that subcommands are case-sensitive (lowercase required)"""
        result = run_cli("clone", "https://example.com/repo.git")
        assert result.returncode == 0

    def test_clone_uppercase(self):
        """Test uppercase subcommand should fail"""
        result = run_cli("CLONE", "https://example.com/repo.git")
        assert result.returncode != 0, "Uppercase subcommand should not be recognized"

    def test_clone_mixed_case(self):
        """Test mixed case subcommand should fail"""
        result = run_cli("Clone", "https://example.com/repo.git")
        assert result.returncode != 0, "Mixed case subcommand should not be recognized"
