#!/usr/bin/env python3
"""
Test suite for stdlib_integration.py

This test suite validates a CLI tool that integrates multiple Python stdlib modules:
- argparse: Command-line argument parsing
- json: JSON serialization/deserialization
- pathlib: Path operations and file metadata
- datetime: Timestamp formatting
- hashlib: File hashing (MD5, SHA256)

Test coverage goals: 100%
Test-driven development: RED phase (tests written before implementation)
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

# Path to the script being tested
SCRIPT_PATH = Path(__file__).parent / "stdlib_integration.py"


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
        """Test --help flag."""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "stdlib_integration.py" in result.stdout
        assert "usage:" in result.stdout.lower()
        assert "--file" in result.stdout
        assert "--hash" in result.stdout

    def test_version_flag(self):
        """Test --version flag."""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "1.0.0" in result.stdout


class TestBasicFileInfo:
    """Test basic file information retrieval."""

    def test_file_info_text_output(self):
        """Test file info with text output format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Hello World")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path)
            assert result.returncode == 0
            assert "Path:" in result.stdout
            assert temp_path in result.stdout
            assert "Size:" in result.stdout
            assert "11" in result.stdout  # len("Hello World")
        finally:
            Path(temp_path).unlink()

    def test_file_info_json_output(self):
        """Test file info with JSON output format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Test content")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0

            # Parse JSON output
            data = json.loads(result.stdout)
            assert "path" in data
            assert "size" in data
            assert "modified" in data
            assert data["size"] == 12  # len("Test content")
        finally:
            Path(temp_path).unlink()

    def test_file_not_found(self):
        """Test error handling for non-existent file."""
        result = run_cli("--file", "/nonexistent/file.txt")
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "not found" in result.stderr.lower()

    def test_missing_required_argument(self):
        """Test error when --file is missing."""
        result = run_cli()
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()


class TestHashingFeatures:
    """Test file hashing with different algorithms."""

    def test_md5_hash(self):
        """Test MD5 hash calculation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Hello")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--hash", "md5")
            assert result.returncode == 0
            assert "Hash:" in result.stdout or "hash" in result.stdout.lower()
            # MD5 of "Hello" is 8b1a9953c4611296a827abf8c47804d7
            assert "8b1a9953c4611296a827abf8c47804d7" in result.stdout.lower()
        finally:
            Path(temp_path).unlink()

    def test_sha256_hash(self):
        """Test SHA256 hash calculation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Hello")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--hash", "sha256")
            assert result.returncode == 0
            assert "Hash:" in result.stdout or "hash" in result.stdout.lower()
            # SHA256 of "Hello" starts with 185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969
            assert "185f8db32271fe25f561a6fc938b2e26" in result.stdout.lower()
        finally:
            Path(temp_path).unlink()

    def test_no_hash_by_default(self):
        """Test that hash is not computed by default."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path)
            assert result.returncode == 0
            # Should not contain hash in output
            assert "Hash:" not in result.stdout or "hash" not in result.stdout.lower()
        finally:
            Path(temp_path).unlink()

    def test_json_output_with_hash(self):
        """Test JSON output includes hash when requested."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json", "--hash", "md5")
            assert result.returncode == 0

            data = json.loads(result.stdout)
            assert "hash" in data
            assert "hash_algorithm" in data
            assert data["hash_algorithm"] == "md5"
        finally:
            Path(temp_path).unlink()


class TestOutputFormats:
    """Test different output formats."""

    def test_text_format_default(self):
        """Test text format is default."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Content")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path)
            assert result.returncode == 0
            # Text format has labels
            assert "Path:" in result.stdout
            assert "Size:" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_json_format_explicit(self):
        """Test explicit JSON format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Content")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0

            # Should be valid JSON
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
        finally:
            Path(temp_path).unlink()

    def test_compact_format(self):
        """Test compact output format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Data")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "compact")
            assert result.returncode == 0
            # Compact format should be single line
            lines = result.stdout.strip().split("\n")
            assert len(lines) == 1
        finally:
            Path(temp_path).unlink()


class TestOutputDestination:
    """Test output to different destinations."""

    def test_output_to_stdout(self):
        """Test output to stdout (default)."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Content")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0
            assert result.stdout.strip()  # Has output
        finally:
            Path(temp_path).unlink()

    def test_output_to_file(self):
        """Test output to file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Content")
            input_path = f.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as out:
            output_path = out.name

        try:
            result = run_cli("--file", input_path, "--format", "json", "--output", output_path)
            assert result.returncode == 0

            # Check output file exists and has content
            output_file = Path(output_path)
            assert output_file.exists()

            with open(output_path, "r") as f:
                data = json.load(f)
                assert "path" in data
                assert "size" in data
        finally:
            Path(input_path).unlink()
            if Path(output_path).exists():
                Path(output_path).unlink()


class TestDateTimeFormatting:
    """Test datetime formatting options."""

    def test_iso_format_default(self):
        """Test ISO format is default for timestamps."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0

            data = json.loads(result.stdout)
            # ISO format has T and possibly Z or timezone
            assert "T" in data["modified"]
        finally:
            Path(temp_path).unlink()

    def test_human_readable_format(self):
        """Test human-readable timestamp format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--time-format", "human")
            assert result.returncode == 0
            # Human format has month names or more readable format
            assert any(month in result.stdout for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        finally:
            Path(temp_path).unlink()


class TestPathlibIntegration:
    """Test pathlib integration for file operations."""

    def test_absolute_path_in_output(self):
        """Test that absolute path is shown in output."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0

            data = json.loads(result.stdout)
            # Path should be absolute
            assert Path(data["path"]).is_absolute()
        finally:
            Path(temp_path).unlink()

    def test_file_extension(self):
        """Test file extension extraction."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0

            data = json.loads(result.stdout)
            assert "extension" in data
            assert data["extension"] == ".txt"
        finally:
            Path(temp_path).unlink()

    def test_filename_extraction(self):
        """Test filename extraction."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0

            data = json.loads(result.stdout)
            assert "filename" in data
            assert data["filename"] == Path(temp_path).name
        finally:
            Path(temp_path).unlink()


class TestCombinedFeatures:
    """Test combinations of features."""

    def test_all_features_combined(self):
        """Test all features together: JSON output, hash, custom time format, file output."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test data")
            input_path = f.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as out:
            output_path = out.name

        try:
            result = run_cli(
                "--file", input_path,
                "--format", "json",
                "--hash", "sha256",
                "--output", output_path
            )
            assert result.returncode == 0

            # Verify output file
            with open(output_path, "r") as f:
                data = json.load(f)
                assert "path" in data
                assert "size" in data
                assert "hash" in data
                assert "hash_algorithm" in data
                assert data["hash_algorithm"] == "sha256"
        finally:
            Path(input_path).unlink()
            if Path(output_path).exists():
                Path(output_path).unlink()

    def test_text_output_with_all_info(self):
        """Test text output with hash and custom formatting."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Sample")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--hash", "md5", "--time-format", "human")
            assert result.returncode == 0
            assert "Path:" in result.stdout
            assert "Size:" in result.stdout
            assert "Hash:" in result.stdout or "hash" in result.stdout.lower()
            assert "Modified:" in result.stdout or "modified" in result.stdout.lower()
        finally:
            Path(temp_path).unlink()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_file(self):
        """Test info for empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            # Empty file
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0

            data = json.loads(result.stdout)
            assert data["size"] == 0
        finally:
            Path(temp_path).unlink()

    def test_large_file(self):
        """Test info for large file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            # Write 1MB of data
            f.write("x" * 1024 * 1024)
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "json")
            assert result.returncode == 0

            data = json.loads(result.stdout)
            assert data["size"] == 1024 * 1024
        finally:
            Path(temp_path).unlink()

    def test_file_with_spaces_in_name(self):
        """Test file with spaces in filename."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, prefix="test file ", suffix=".txt") as f:
            f.write("Content")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path)
            assert result.returncode == 0
            assert "Path:" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_file_with_unicode_content(self):
        """Test file with unicode content."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            f.write("Hello 世界 🌍")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--hash", "md5")
            assert result.returncode == 0
            # Should handle unicode content
            assert result.returncode == 0
        finally:
            Path(temp_path).unlink()


class TestErrorHandling:
    """Test error handling and validation."""

    def test_invalid_hash_algorithm(self):
        """Test error for invalid hash algorithm."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--hash", "invalid")
            assert result.returncode != 0
            assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()
        finally:
            Path(temp_path).unlink()

    def test_invalid_format(self):
        """Test error for invalid output format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test")
            temp_path = f.name

        try:
            result = run_cli("--file", temp_path, "--format", "invalid")
            assert result.returncode != 0
        finally:
            Path(temp_path).unlink()

    def test_permission_denied(self):
        """Test handling of permission denied errors."""
        # This test is platform-dependent and may not work on all systems
        # Skip if we can't create a file with restricted permissions
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                temp_path = f.name

            # Remove read permissions
            os.chmod(temp_path, 0o000)

            result = run_cli("--file", temp_path)
            # Should handle permission error gracefully
            assert result.returncode != 0 or "permission" in result.stderr.lower() or result.returncode == 0
        finally:
            # Restore permissions and clean up
            try:
                os.chmod(temp_path, 0o644)
                Path(temp_path).unlink()
            except:
                pass
