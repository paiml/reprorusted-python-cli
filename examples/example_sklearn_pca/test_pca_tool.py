#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn PCA CLI.

Academic Reference: van der Maaten & Hinton (2008) Dimensionality reduction [10]
Tests Principal Component Analysis for dimensionality reduction.
"""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "pca_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestPcaFit:
    """Test PCA fitting."""

    def test_fit_reduces_dimensions(self):
        """Test that PCA reduces to specified n_components."""
        data = json.dumps({
            "X": [[1, 2, 3], [2, 4, 6], [3, 6, 9], [4, 8, 12]],
            "n_components": 2
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "components" in result
        assert len(result["components"]) == 2  # 2 principal components

    def test_fit_default_components(self):
        """Test default n_components equals n_features."""
        data = json.dumps({
            "X": [[1, 2], [2, 4], [3, 6], [4, 8]]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["components"]) == 2

    def test_fit_empty_fails(self):
        """Test that fitting on empty data fails."""
        data = json.dumps({"X": [], "n_components": 2})
        stdout, stderr, code = run(["fit"], data)
        assert code == 1


class TestPcaTransform:
    """Test PCA transformation."""

    def test_transform_reduces_dim(self):
        """Test that transform reduces dimensionality."""
        data = json.dumps({
            "X": [[1, 2, 3], [2, 4, 6]],
            "components": [[0.577, 0.577, 0.577], [0.707, -0.707, 0]],
            "mean": [1.5, 3.0, 4.5]
        })
        stdout, stderr, code = run(["transform"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "X_transformed" in result
        assert len(result["X_transformed"][0]) == 2  # Reduced to 2D


class TestPcaFitTransform:
    """Test combined fit-transform."""

    def test_fit_transform(self):
        """Test fit_transform returns transformed data."""
        data = json.dumps({
            "X": [[1, 2], [2, 4], [3, 6], [4, 8]],
            "n_components": 1
        })
        stdout, stderr, code = run(["fit-transform"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "X_transformed" in result
        assert len(result["X_transformed"][0]) == 1  # Reduced to 1D
        assert "components" in result


class TestPcaExplainedVariance:
    """Test explained variance ratio."""

    def test_explained_variance_returned(self):
        """Test that explained variance ratio is returned."""
        data = json.dumps({
            "X": [[1, 2], [2, 4], [3, 6], [4, 8]],
            "n_components": 2
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "explained_variance_ratio" in result
        assert len(result["explained_variance_ratio"]) == 2
        # Sum should be <= 1.0
        assert sum(result["explained_variance_ratio"]) <= 1.01

    def test_first_component_captures_most(self):
        """Test that first PC captures most variance for correlated data."""
        # Highly correlated data - first PC should capture most variance
        data = json.dumps({
            "X": [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]],
            "n_components": 2
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        # First component should capture nearly all variance
        assert result["explained_variance_ratio"][0] > 0.9


class TestPcaHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "PCA" in stdout or "pca" in stdout.lower()

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["fit", "--help"])
        assert code == 0


class TestPcaEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["fit"], "not json")
        assert code == 1

    def test_n_components_too_large_fails(self):
        """Test n_components > n_features fails."""
        data = json.dumps({
            "X": [[1, 2], [3, 4]],
            "n_components": 5
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 1
