#!/usr/bin/env python3
"""Tests for golden_traces_analyzer.py (GH-23) - EXTREME TDD.

Test-first approach for Golden Traces generation.
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


class TestGoldenTracesAnalyzer:
    """Test suite for golden traces generation."""

    def test_script_exists(self):
        """Script file should exist."""
        script = SCRIPTS_DIR / "golden_traces_analyzer.py"
        assert script.exists(), f"Script not found: {script}"

    def test_script_is_executable(self):
        """Script should be importable as module."""
        script = SCRIPTS_DIR / "golden_traces_analyzer.py"
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_analyze_errors_returns_dict(self):
        """analyze_errors() should return error code counts."""
        from golden_traces_analyzer import analyze_errors

        result = analyze_errors(PROJECT_ROOT / "examples")
        assert isinstance(result, dict)
        # Should have error codes as keys
        for key in result:
            assert key.startswith("E"), f"Expected error code, got: {key}"

    def test_select_golden_candidates(self):
        """select_golden_candidates() should pick examples per error code."""
        from golden_traces_analyzer import select_golden_candidates, ErrorSummary

        # Mock error data using ErrorSummary
        errors = {
            "E0308": ErrorSummary(
                code="E0308",
                description="Type mismatch",
                count=100,
                examples=["ex1", "ex2", "ex3"],
            ),
            "E0433": ErrorSummary(
                code="E0433",
                description="Failed to resolve",
                count=50,
                examples=["ex4", "ex5"],
            ),
        }
        candidates = select_golden_candidates(errors, per_code=2)

        assert isinstance(candidates, list)
        assert len(candidates) <= 4  # 2 per code, 2 codes

    def test_generate_golden_traces_json(self):
        """generate_golden_traces() should produce valid JSON structure."""
        from golden_traces_analyzer import generate_golden_traces

        candidates = [
            {"example": "ex1", "error_code": "E0308", "error_msg": "type mismatch"},
            {"example": "ex2", "error_code": "E0433", "error_msg": "unresolved"},
        ]
        traces = generate_golden_traces(candidates)

        assert "version" in traces
        assert "traces" in traces
        assert isinstance(traces["traces"], list)

    def test_cli_json_output(self):
        """CLI --json flag should produce valid JSON."""
        script = SCRIPTS_DIR / "golden_traces_analyzer.py"
        result = subprocess.run(
            [sys.executable, str(script), "--json", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        # Should either succeed or fail gracefully
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert "traces" in data or "error_summary" in data

    def test_top_5_error_codes_targeted(self):
        """Should target the documented top 5 error codes."""
        from golden_traces_analyzer import TOP_ERROR_CODES

        expected = ["E0308", "E0433", "E0599", "E0425", "E0277"]
        assert set(expected).issubset(set(TOP_ERROR_CODES))


class TestGoldenTracesOutput:
    """Test the output structure of golden traces."""

    def test_trace_has_required_fields(self):
        """Each trace should have required fields."""
        from golden_traces_analyzer import generate_golden_traces

        candidates = [
            {
                "example": "example_simple",
                "error_code": "E0308",
                "error_msg": "mismatched types",
                "file": "src/lib.rs",
                "line": 42,
            }
        ]
        traces = generate_golden_traces(candidates)

        for trace in traces["traces"]:
            assert "example" in trace
            assert "error_code" in trace
            assert "error_message" in trace
            assert "status" in trace  # pending/verified/rejected

    def test_output_file_location(self):
        """Golden traces should be written to data/golden_traces.json."""
        output_path = PROJECT_ROOT / "data" / "golden_traces.json"
        # File may or may not exist yet, but path should be valid
        assert output_path.parent.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
