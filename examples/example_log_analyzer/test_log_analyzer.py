#!/usr/bin/env python3
"""
Test suite for log_analyzer - Generator functions with yield and groupby

Tests generator functions, yield statements, itertools.groupby, and regex parsing.
Following EXTREME TDD methodology with 100% coverage goal.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


# Test data fixtures
@pytest.fixture
def sample_log_data():
    """Sample log entries"""
    return [
        "[2025-11-17 10:30:45] INFO: Application started",
        "[2025-11-17 10:30:46] DEBUG: Loading configuration",
        "[2025-11-17 10:31:15] INFO: Database connected",
        "[2025-11-17 10:31:20] WARN: Cache miss for key user_123",
        "[2025-11-17 10:32:10] ERROR: Failed to connect to external API",
        "[2025-11-17 11:15:30] INFO: Request processed",
        "[2025-11-17 11:15:31] DEBUG: Response sent",
        "[2025-11-17 11:45:00] ERROR: Timeout waiting for response",
    ]


@pytest.fixture
def sample_log_file(tmp_path, sample_log_data):
    """Create temporary log file"""
    log_file = tmp_path / "test.log"
    with open(log_file, "w") as f:
        f.write("\n".join(sample_log_data))
    return log_file


@pytest.fixture
def malformed_log_file(tmp_path):
    """Log file with some malformed lines"""
    log_file = tmp_path / "malformed.log"
    lines = [
        "[2025-11-17 10:30:45] INFO: Valid line",
        "Invalid line without timestamp",
        "[2025-11-17 10:30:46] DEBUG: Another valid line",
        "Another invalid line",
    ]
    with open(log_file, "w") as f:
        f.write("\n".join(lines))
    return log_file


class TestLogParsing:
    """Test generator function for parsing log lines"""

    def test_parse_valid_log_lines(self, sample_log_file):
        """Parse all valid log entries"""
        from log_analyzer import parse_log_lines

        entries = list(parse_log_lines(str(sample_log_file)))

        assert len(entries) == 8
        assert all(len(entry) == 3 for entry in entries)  # (timestamp, level, message)

        # Check first entry
        timestamp, level, message = entries[0]
        assert timestamp == "2025-11-17 10:30:45"
        assert level == "INFO"
        assert message == "Application started"

    def test_parse_yields_tuples(self, sample_log_file):
        """Generator should yield tuples"""
        from log_analyzer import parse_log_lines

        gen = parse_log_lines(str(sample_log_file))
        first_entry = next(gen)

        assert isinstance(first_entry, tuple)
        assert len(first_entry) == 3

    def test_parse_handles_malformed_lines(self, malformed_log_file):
        """Should skip malformed lines"""
        from log_analyzer import parse_log_lines

        entries = list(parse_log_lines(str(malformed_log_file)))

        # Only 2 valid lines
        assert len(entries) == 2

    def test_parse_empty_file(self, tmp_path):
        """Parse empty log file"""
        from log_analyzer import parse_log_lines

        empty_file = tmp_path / "empty.log"
        empty_file.touch()

        entries = list(parse_log_lines(str(empty_file)))
        assert len(entries) == 0


class TestCountByLevel:
    """Test counting log entries by level"""

    def test_count_all_levels(self, sample_log_file):
        """Count entries for each log level"""
        from log_analyzer import count_by_level

        counts = count_by_level(str(sample_log_file))

        assert counts["INFO"] == 3
        assert counts["DEBUG"] == 2
        assert counts["WARN"] == 1
        assert counts["ERROR"] == 2

    def test_count_returns_dict(self, sample_log_file):
        """Should return dict of level counts"""
        from log_analyzer import count_by_level

        counts = count_by_level(str(sample_log_file))

        assert isinstance(counts, dict)
        assert all(isinstance(k, str) for k in counts.keys())
        assert all(isinstance(v, int) for v in counts.values())

    def test_count_single_level(self, tmp_path):
        """File with only one level"""
        from log_analyzer import count_by_level

        log_file = tmp_path / "single.log"
        with open(log_file, "w") as f:
            f.write("[2025-11-17 10:30:45] INFO: Line 1\n")
            f.write("[2025-11-17 10:30:46] INFO: Line 2\n")

        counts = count_by_level(str(log_file))

        assert len(counts) == 1
        assert counts["INFO"] == 2


class TestGroupByHour:
    """Test grouping entries by hour using itertools.groupby"""

    def test_group_by_hour(self, sample_log_file):
        """Group log entries by hour"""
        from log_analyzer import group_by_hour

        hour_counts = group_by_hour(str(sample_log_file))

        assert hour_counts["10"] == 5  # 5 entries in 10:xx
        assert hour_counts["11"] == 3  # 3 entries in 11:xx

    def test_group_returns_dict(self, sample_log_file):
        """Should return dict of hour counts"""
        from log_analyzer import group_by_hour

        hour_counts = group_by_hour(str(sample_log_file))

        assert isinstance(hour_counts, dict)
        assert all(isinstance(k, str) for k in hour_counts.keys())
        assert all(isinstance(v, int) for v in hour_counts.values())

    def test_group_single_hour(self, tmp_path):
        """All entries in same hour"""
        from log_analyzer import group_by_hour

        log_file = tmp_path / "single_hour.log"
        with open(log_file, "w") as f:
            f.write("[2025-11-17 14:00:00] INFO: Entry 1\n")
            f.write("[2025-11-17 14:15:00] INFO: Entry 2\n")
            f.write("[2025-11-17 14:30:00] INFO: Entry 3\n")

        hour_counts = group_by_hour(str(log_file))

        assert len(hour_counts) == 1
        assert hour_counts["14"] == 3


class TestFilterByLevel:
    """Test generator that filters entries by level"""

    def test_filter_info_level(self, sample_log_file):
        """Filter only INFO entries"""
        from log_analyzer import filter_by_level

        info_entries = list(filter_by_level(str(sample_log_file), "INFO"))

        assert len(info_entries) == 3
        assert all(entry[1] == "INFO" for entry in info_entries)

    def test_filter_error_level(self, sample_log_file):
        """Filter only ERROR entries"""
        from log_analyzer import filter_by_level

        error_entries = list(filter_by_level(str(sample_log_file), "ERROR"))

        assert len(error_entries) == 2
        assert all(entry[1] == "ERROR" for entry in error_entries)

    def test_filter_nonexistent_level(self, sample_log_file):
        """Filter level that doesn't exist"""
        from log_analyzer import filter_by_level

        entries = list(filter_by_level(str(sample_log_file), "CRITICAL"))

        assert len(entries) == 0

    def test_filter_yields_generator(self, sample_log_file):
        """Should return generator"""
        from log_analyzer import filter_by_level

        gen = filter_by_level(str(sample_log_file), "INFO")

        # Generator should not consume entries until iterated
        assert hasattr(gen, "__iter__")
        assert hasattr(gen, "__next__")


class TestCLIInterface:
    """Test command-line interface"""

    def test_cli_help(self):
        """Test --help flag"""
        result = subprocess.run(
            [sys.executable, "log_analyzer.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "Analyze log files" in result.stdout

    def test_cli_version(self):
        """Test --version flag"""
        result = subprocess.run(
            [sys.executable, "log_analyzer.py", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_cli_count_levels(self, sample_log_file):
        """Test --count-levels flag"""
        result = subprocess.run(
            [sys.executable, "log_analyzer.py", str(sample_log_file), "--count-levels"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "INFO: 3" in result.stdout
        assert "ERROR: 2" in result.stdout

    def test_cli_group_by_hour(self, sample_log_file):
        """Test --group-by-hour flag"""
        result = subprocess.run(
            [sys.executable, "log_analyzer.py", str(sample_log_file), "--group-by-hour"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "10:00" in result.stdout
        assert "11:00" in result.stdout

    def test_cli_filter_level(self, sample_log_file):
        """Test --filter-level flag"""
        result = subprocess.run(
            [sys.executable, "log_analyzer.py", str(sample_log_file), "--filter-level", "ERROR"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "ERROR" in result.stdout
        assert result.stdout.count("ERROR") >= 2

    def test_cli_no_args(self):
        """Test CLI with no action flags"""
        result = subprocess.run(
            [sys.executable, "log_analyzer.py", "/tmp/test.log"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        # Should show help and exit with error
        assert result.returncode != 0


class TestPropertyBased:
    """Property-based tests for invariants"""

    def test_parsed_count_matches_valid_lines(self, sample_log_file):
        """Property: parsed entries = valid log lines"""
        from log_analyzer import parse_log_lines

        # Count valid lines in file
        with open(sample_log_file) as f:
            valid_lines = sum(1 for line in f if line.strip().startswith("["))

        parsed = list(parse_log_lines(str(sample_log_file)))

        assert len(parsed) == valid_lines

    def test_level_counts_sum_to_total(self, sample_log_file):
        """Property: sum(level_counts) = total entries"""
        from log_analyzer import count_by_level, parse_log_lines

        total_entries = len(list(parse_log_lines(str(sample_log_file))))
        counts = count_by_level(str(sample_log_file))

        assert sum(counts.values()) == total_entries

    def test_hour_counts_sum_to_total(self, sample_log_file):
        """Property: sum(hour_counts) = total entries"""
        from log_analyzer import group_by_hour, parse_log_lines

        total_entries = len(list(parse_log_lines(str(sample_log_file))))
        hour_counts = group_by_hour(str(sample_log_file))

        assert sum(hour_counts.values()) == total_entries

    def test_filter_subset_of_total(self, sample_log_file):
        """Property: filtered entries ≤ total entries"""
        from log_analyzer import filter_by_level, parse_log_lines

        total_entries = len(list(parse_log_lines(str(sample_log_file))))
        filtered = list(filter_by_level(str(sample_log_file), "INFO"))

        assert len(filtered) <= total_entries
