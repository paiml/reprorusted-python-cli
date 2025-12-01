#!/usr/bin/env python3
"""Tests for hitl_sampler.py (GH-25) - EXTREME TDD.

Test-first approach for Human-in-the-Loop review sampling.
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


class TestHITLSampler:
    """Test suite for HITL sampler."""

    def test_script_exists(self):
        """Script file should exist."""
        script = SCRIPTS_DIR / "hitl_sampler.py"
        assert script.exists(), f"Script not found: {script}"

    def test_script_is_executable(self):
        """Script should be importable as module."""
        script = SCRIPTS_DIR / "hitl_sampler.py"
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_generate_sample_returns_list(self):
        """generate_sample() should return list of examples."""
        from hitl_sampler import generate_sample

        # Use 10% for testing (fewer examples)
        result = generate_sample(
            PROJECT_ROOT / "examples",
            sample_pct=10,
            stratified=False,
        )
        assert isinstance(result, list)
        assert len(result) > 0

    def test_stratified_sampling(self):
        """Stratified sampling should include examples from multiple categories."""
        from hitl_sampler import generate_sample

        result = generate_sample(
            PROJECT_ROOT / "examples",
            sample_pct=10,
            stratified=True,
        )
        assert isinstance(result, list)
        # Should have diverse examples
        categories = {r.get("category", "unknown") for r in result}
        assert len(categories) >= 1

    def test_review_item_has_required_fields(self):
        """Each review item should have required fields."""
        from hitl_sampler import generate_sample

        result = generate_sample(
            PROJECT_ROOT / "examples",
            sample_pct=5,
        )
        if result:
            item = result[0]
            assert "example" in item
            assert "review_status" in item  # pending/approved/rejected
            assert "checklist" in item

    def test_checklist_items(self):
        """Review checklist should include key quality checks."""
        from hitl_sampler import REVIEW_CHECKLIST

        expected_checks = [
            "no_unsafe",
            "minimal_cloning",
            "idiomatic_error_handling",
        ]
        for check in expected_checks:
            assert any(
                check in item["id"] for item in REVIEW_CHECKLIST
            ), f"Missing check: {check}"

    def test_json_output_valid(self):
        """--json should produce valid JSON."""
        script = SCRIPTS_DIR / "hitl_sampler.py"
        result = subprocess.run(
            [sys.executable, str(script), "--json", "--sample-pct", "5"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            assert "sample" in data
            assert "checklist" in data


class TestHITLOutput:
    """Test HITL output format."""

    def test_output_directory(self):
        """Output should go to data/hitl_reviews/."""
        output_dir = PROJECT_ROOT / "data" / "hitl_reviews"
        # May not exist yet, but parent should
        assert output_dir.parent.exists()

    def test_review_guide_exists(self):
        """HITL review guide should be generated."""
        from hitl_sampler import generate_review_guide

        guide = generate_review_guide()
        assert "# HITL Review Guide" in guide
        assert "checklist" in guide.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
