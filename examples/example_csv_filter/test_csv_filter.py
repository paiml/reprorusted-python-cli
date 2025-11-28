#!/usr/bin/env python3
"""
Test suite for csv_filter - Memory-efficient CSV filtering

Tests generator expressions, streaming I/O, and memory efficiency.
Following EXTREME TDD methodology with 100% coverage goal.
"""

import csv
import subprocess
import sys
from pathlib import Path

import pytest


# Test data fixtures
@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing"""
    return [
        {"name": "Alice", "age": "25", "city": "NYC"},
        {"name": "Bob", "age": "30", "city": "LA"},
        {"name": "Charlie", "age": "25", "city": "Chicago"},
        {"name": "Diana", "age": "35", "city": "NYC"},
        {"name": "Eve", "age": "25", "city": "Seattle"},
    ]


@pytest.fixture
def sample_csv_file(tmp_path, sample_csv_data):
    """Create temporary CSV file with sample data"""
    csv_file = tmp_path / "test.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])
        writer.writeheader()
        writer.writerows(sample_csv_data)
    return csv_file


@pytest.fixture
def empty_csv_file(tmp_path):
    """Create empty CSV file"""
    csv_file = tmp_path / "empty.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])
        writer.writeheader()
    return csv_file


class TestBasicFiltering:
    """Test core filtering functionality"""

    def test_filter_by_single_column(self, sample_csv_file, tmp_path):
        """Filter rows where age equals 25"""
        from csv_filter import filter_csv

        output_file = tmp_path / "output.csv"
        filter_csv(str(sample_csv_file), "age", "25", str(output_file))

        # Verify output
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert all(row["age"] == "25" for row in rows)
        assert {row["name"] for row in rows} == {"Alice", "Charlie", "Eve"}

    def test_filter_no_matches(self, sample_csv_file, tmp_path):
        """Filter with no matching rows"""
        from csv_filter import filter_csv

        output_file = tmp_path / "output.csv"
        filter_csv(str(sample_csv_file), "age", "99", str(output_file))

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 0

    def test_filter_all_match(self, tmp_path):
        """Filter where all rows match"""
        from csv_filter import filter_csv

        # Create file where all have same value
        csv_file = tmp_path / "test.csv"
        data = [{"name": f"Person{i}", "status": "active"} for i in range(5)]
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "status"])
            writer.writeheader()
            writer.writerows(data)

        output_file = tmp_path / "output.csv"
        filter_csv(str(csv_file), "status", "active", str(output_file))

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 5

    def test_filter_by_string_column(self, sample_csv_file, tmp_path):
        """Filter by city name"""
        from csv_filter import filter_csv

        output_file = tmp_path / "output.csv"
        filter_csv(str(sample_csv_file), "city", "NYC", str(output_file))

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert all(row["city"] == "NYC" for row in rows)

    def test_output_to_stdout(self, sample_csv_file, capsys):
        """Filter with output to stdout"""
        from csv_filter import filter_csv

        filter_csv(str(sample_csv_file), "age", "25", None)

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")

        # Header + 3 matching rows
        assert len(lines) == 4
        assert "name,age,city" in lines[0]


class TestAdvancedFiltering:
    """Test advanced filtering with multiple criteria"""

    def test_filter_multiple_criteria(self, sample_csv_file, tmp_path):
        """Filter with AND logic on multiple columns"""
        from csv_filter import filter_csv_advanced

        filters = {"age": "25", "city": "NYC"}
        output_file = tmp_path / "output.csv"
        filter_csv_advanced(str(sample_csv_file), filters, str(output_file))

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"

    def test_multiple_criteria_no_match(self, sample_csv_file, tmp_path):
        """Multiple criteria with no matching rows"""
        from csv_filter import filter_csv_advanced

        filters = {"age": "25", "city": "Boston"}  # No one age 25 in Boston
        output_file = tmp_path / "output.csv"
        filter_csv_advanced(str(sample_csv_file), filters, str(output_file))

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 0

    def test_empty_filters(self, sample_csv_file, tmp_path):
        """Empty filter dict should return all rows"""
        from csv_filter import filter_csv_advanced

        filters = {}
        output_file = tmp_path / "output.csv"
        filter_csv_advanced(str(sample_csv_file), filters, str(output_file))

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 5


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_input_file(self, empty_csv_file, tmp_path):
        """Filter empty CSV file"""
        from csv_filter import filter_csv

        output_file = tmp_path / "output.csv"
        filter_csv(str(empty_csv_file), "age", "25", str(output_file))

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 0

    def test_nonexistent_column(self, sample_csv_file, tmp_path):
        """Filter by non-existent column should raise KeyError"""
        from csv_filter import filter_csv

        output_file = tmp_path / "output.csv"

        with pytest.raises(KeyError):
            filter_csv(str(sample_csv_file), "nonexistent", "value", str(output_file))

    def test_nonexistent_input_file(self, tmp_path):
        """Non-existent input file should raise FileNotFoundError"""
        from csv_filter import filter_csv

        output_file = tmp_path / "output.csv"

        with pytest.raises(FileNotFoundError):
            filter_csv("/nonexistent/file.csv", "age", "25", str(output_file))


class TestMemoryEfficiency:
    """Test memory efficiency with large datasets"""

    def test_large_file_streaming(self, tmp_path):
        """Verify streaming behavior with 10K rows"""
        from csv_filter import filter_csv

        # Generate large CSV (10K rows)
        large_file = tmp_path / "large.csv"
        with open(large_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "value", "category"])
            writer.writeheader()
            for i in range(10000):
                writer.writerow({"id": str(i), "value": str(i % 100), "category": "A" if i % 2 == 0 else "B"})

        output_file = tmp_path / "output.csv"
        filter_csv(str(large_file), "category", "A", str(output_file))

        # Verify 5000 rows match (half are category A)
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 5000
        assert all(row["category"] == "A" for row in rows)


class TestCLIInterface:
    """Test command-line interface"""

    def test_cli_help(self):
        """Test --help flag"""
        result = subprocess.run(
            [sys.executable, "csv_filter.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "Filter CSV files" in result.stdout

    def test_cli_version(self):
        """Test --version flag"""
        result = subprocess.run(
            [sys.executable, "csv_filter.py", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_cli_basic_filter(self, sample_csv_file, tmp_path):
        """Test CLI basic filtering"""
        output_file = tmp_path / "output.csv"

        result = subprocess.run(
            [
                sys.executable,
                "csv_filter.py",
                str(sample_csv_file),
                "--column",
                "age",
                "--value",
                "25",
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        assert result.returncode == 0
        assert output_file.exists()

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3

    def test_cli_missing_required_args(self):
        """Test CLI with missing required arguments"""
        result = subprocess.run(
            [sys.executable, "csv_filter.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode != 0


class TestPropertyBased:
    """Property-based tests for invariants"""

    def test_filtered_count_less_than_input(self, sample_csv_file, tmp_path):
        """Property: filtered rows ≤ input rows"""
        from csv_filter import filter_csv

        # Count input rows
        with open(sample_csv_file) as f:
            input_count = sum(1 for _ in csv.DictReader(f))

        output_file = tmp_path / "output.csv"
        filter_csv(str(sample_csv_file), "age", "25", str(output_file))

        # Count output rows
        with open(output_file) as f:
            output_count = sum(1 for _ in csv.DictReader(f))

        assert output_count <= input_count

    def test_all_filtered_rows_match_predicate(self, sample_csv_file, tmp_path):
        """Property: all output rows match filter criteria"""
        from csv_filter import filter_csv

        output_file = tmp_path / "output.csv"
        filter_csv(str(sample_csv_file), "city", "NYC", str(output_file))

        with open(output_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                assert row["city"] == "NYC"

    def test_output_preserves_field_structure(self, sample_csv_file, tmp_path):
        """Property: output has same fields as input"""
        from csv_filter import filter_csv

        # Get input fieldnames
        with open(sample_csv_file) as f:
            input_fields = csv.DictReader(f).fieldnames

        output_file = tmp_path / "output.csv"
        filter_csv(str(sample_csv_file), "age", "25", str(output_file))

        # Get output fieldnames
        with open(output_file) as f:
            output_fields = csv.DictReader(f).fieldnames

        assert input_fields == output_fields

    def test_idempotent_filtering(self, sample_csv_file, tmp_path):
        """Property: filtering twice produces same result"""
        from csv_filter import filter_csv

        output1 = tmp_path / "output1.csv"
        output2 = tmp_path / "output2.csv"

        filter_csv(str(sample_csv_file), "age", "25", str(output1))
        filter_csv(str(output1), "age", "25", str(output2))

        # Read both outputs
        with open(output1) as f:
            rows1 = list(csv.DictReader(f))

        with open(output2) as f:
            rows2 = list(csv.DictReader(f))

        assert rows1 == rows2
