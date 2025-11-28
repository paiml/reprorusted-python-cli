#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn KMeans CLI.

Academic Reference: Lloyd (1982) Least Squares Quantization in PCM [9]
Tests the fit/predict/labels pattern for K-means clustering.
"""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "kmeans_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestKmeansFit:
    """Test model fitting."""

    def test_fit_two_clusters(self):
        """Test fitting with 2 distinct clusters."""
        # Two obvious clusters
        data = json.dumps({
            "X": [[1, 1], [1, 2], [2, 1], [2, 2],
                  [8, 8], [8, 9], [9, 8], [9, 9]],
            "n_clusters": 2
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "labels" in result
        assert "centroids" in result
        assert len(result["labels"]) == 8
        assert len(result["centroids"]) == 2
        # Check first 4 points have same label, last 4 have same label
        assert len(set(result["labels"][:4])) == 1
        assert len(set(result["labels"][4:])) == 1
        assert result["labels"][0] != result["labels"][4]

    def test_fit_three_clusters(self):
        """Test fitting with 3 clusters."""
        data = json.dumps({
            "X": [[0, 0], [0, 1], [1, 0],
                  [5, 5], [5, 6], [6, 5],
                  [10, 0], [10, 1], [11, 0]],
            "n_clusters": 3
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["centroids"]) == 3
        assert len(result["labels"]) == 9

    def test_fit_default_clusters(self):
        """Test fitting with default n_clusters=2."""
        data = json.dumps({
            "X": [[1, 1], [2, 2], [8, 8], [9, 9]]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["centroids"]) == 2

    def test_fit_empty_data_fails(self):
        """Test that fitting on empty data fails."""
        data = json.dumps({"X": [], "n_clusters": 2})
        stdout, stderr, code = run(["fit"], data)
        assert code == 1


class TestKmeansPredict:
    """Test label prediction for new data."""

    def test_predict_with_centroids(self):
        """Test prediction assigns points to nearest centroid."""
        data = json.dumps({
            "X": [[0, 0], [10, 10]],
            "centroids": [[1, 1], [9, 9]]
        })
        stdout, stderr, code = run(["predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "labels" in result
        # [0,0] closer to [1,1] (cluster 0)
        # [10,10] closer to [9,9] (cluster 1)
        assert result["labels"][0] != result["labels"][1]

    def test_predict_boundary_case(self):
        """Test prediction at equidistant point."""
        data = json.dumps({
            "X": [[5, 5]],  # Equidistant from both centroids
            "centroids": [[0, 0], [10, 10]]
        })
        stdout, stderr, code = run(["predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["labels"]) == 1
        assert result["labels"][0] in [0, 1]  # Either cluster is valid


class TestKmeansCentroids:
    """Test centroid computation."""

    def test_centroids_are_means(self):
        """Test that centroids are at cluster means."""
        # Perfect clusters, centroids should be exact
        data = json.dumps({
            "X": [[0, 0], [2, 0], [0, 2], [2, 2],  # Mean: [1, 1]
                  [10, 10], [12, 10], [10, 12], [12, 12]],  # Mean: [11, 11]
            "n_clusters": 2
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        centroids = result["centroids"]
        # Sort centroids by first coordinate
        centroids.sort(key=lambda c: c[0])
        assert abs(centroids[0][0] - 1.0) < 0.5
        assert abs(centroids[0][1] - 1.0) < 0.5
        assert abs(centroids[1][0] - 11.0) < 0.5
        assert abs(centroids[1][1] - 11.0) < 0.5


class TestKmeansInertia:
    """Test inertia (within-cluster sum of squares)."""

    def test_inertia_returned(self):
        """Test that inertia is returned."""
        data = json.dumps({
            "X": [[0, 0], [1, 0], [10, 0], [11, 0]],
            "n_clusters": 2
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "inertia" in result
        assert result["inertia"] >= 0

    def test_inertia_zero_perfect_fit(self):
        """Test inertia = 0 when points are exactly at centroids."""
        data = json.dumps({
            "X": [[0, 0], [0, 0], [10, 10], [10, 10]],
            "n_clusters": 2
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["inertia"] < 0.01  # Should be essentially zero


class TestKmeansHelp:
    """Test help and usage messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "KMeans" in stdout or "kmeans" in stdout.lower()
        assert "fit" in stdout

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["fit", "--help"])
        assert code == 0


class TestKmeansEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_json_fails(self):
        """Test that invalid JSON input fails gracefully."""
        stdout, stderr, code = run(["fit"], "not valid json")
        assert code == 1

    def test_k_greater_than_n_fails(self):
        """Test that k > n fails."""
        data = json.dumps({
            "X": [[1, 1], [2, 2]],
            "n_clusters": 5
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 1

    def test_single_point(self):
        """Test with single point."""
        data = json.dumps({
            "X": [[1, 1]],
            "n_clusters": 1
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["labels"] == [0]


class TestKmeansParameters:
    """Test algorithm parameters."""

    def test_max_iter(self):
        """Test custom max iterations."""
        data = json.dumps({
            "X": [[0, 0], [1, 0], [10, 0], [11, 0]],
            "n_clusters": 2,
            "max_iter": 100
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0

    def test_random_state(self):
        """Test reproducibility with random state."""
        data = json.dumps({
            "X": [[0, 0], [1, 0], [10, 0], [11, 0]],
            "n_clusters": 2,
            "random_state": 42
        })
        stdout1, _, code1 = run(["fit"], data)
        stdout2, _, code2 = run(["fit"], data)
        assert code1 == 0 and code2 == 0
        # With same random state, results should be identical
        assert json.loads(stdout1)["labels"] == json.loads(stdout2)["labels"]
