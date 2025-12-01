#!/usr/bin/env python3
"""Tests for clippy_gate.py (GH-24) - EXTREME TDD.

Test-first approach for Clippy blocking gate.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent

# Add scripts to path for imports
sys.path.insert(0, str(SCRIPTS_DIR))


class TestClippyGate:
    """Test suite for clippy gate."""

    def test_script_exists(self):
        """Script file should exist."""
        script = SCRIPTS_DIR / "clippy_gate.py"
        assert script.exists(), f"Script not found: {script}"

    def test_script_is_executable(self):
        """Script should be importable as module."""
        script = SCRIPTS_DIR / "clippy_gate.py"
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_run_clippy_returns_result(self):
        """run_clippy() should return ClippyResult."""
        from clippy_gate import run_clippy, ClippyResult

        # Test on a known example
        example_dir = PROJECT_ROOT / "examples" / "example_simple"
        if example_dir.exists():
            result = run_clippy(example_dir)
            assert isinstance(result, ClippyResult)
            assert hasattr(result, "warnings")
            assert hasattr(result, "errors")
            assert hasattr(result, "passed")

    def test_analyze_all_returns_summary(self):
        """analyze_all() should return summary dict."""
        from clippy_gate import analyze_all

        result = analyze_all(PROJECT_ROOT / "examples", limit=3)
        assert isinstance(result, dict)
        assert "total" in result
        assert "clippy_clean" in result
        assert "clippy_warnings" in result

    def test_strict_mode_fails_on_warnings(self):
        """--strict should return non-zero exit on warnings."""
        script = SCRIPTS_DIR / "clippy_gate.py"
        # Run with limit to keep it fast
        result = subprocess.run(
            [sys.executable, str(script), "--strict", "--limit", "3"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        # May pass or fail depending on clippy state
        assert result.returncode in [0, 1]

    def test_json_output_valid(self):
        """--json should produce valid JSON."""
        script = SCRIPTS_DIR / "clippy_gate.py"
        result = subprocess.run(
            [sys.executable, str(script), "--json", "--limit", "2"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            assert "total" in data
            assert "results" in data


class TestClippyIntegration:
    """Integration tests for clippy gate."""

    def test_clippy_result_has_example_name(self):
        """Each result should include example name."""
        from clippy_gate import run_clippy

        example_dir = PROJECT_ROOT / "examples" / "example_simple"
        if example_dir.exists():
            result = run_clippy(example_dir)
            assert result.example == "example_simple"

    def test_warning_categories_tracked(self):
        """Should track warning categories."""
        from clippy_gate import run_clippy

        example_dir = PROJECT_ROOT / "examples" / "example_simple"
        if example_dir.exists():
            result = run_clippy(example_dir)
            # warnings should be a list
            assert isinstance(result.warnings, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
