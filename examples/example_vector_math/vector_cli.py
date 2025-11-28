#!/usr/bin/env python3
"""Vector Math CLI.

Pure Python vector operations without external dependencies.
"""

import argparse
import math
import sys
from dataclasses import dataclass


@dataclass
class Vector:
    """N-dimensional vector."""

    components: list[float]

    def __len__(self) -> int:
        return len(self.components)

    def __getitem__(self, i: int) -> float:
        return self.components[i]

    def __str__(self) -> str:
        return f"({', '.join(f'{c:.4f}' for c in self.components)})"

    @property
    def dimension(self) -> int:
        return len(self.components)


def add(v1: Vector, v2: Vector) -> Vector:
    """Add two vectors."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have same dimension")
    return Vector([v1[i] + v2[i] for i in range(len(v1))])


def subtract(v1: Vector, v2: Vector) -> Vector:
    """Subtract v2 from v1."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have same dimension")
    return Vector([v1[i] - v2[i] for i in range(len(v1))])


def scalar_multiply(v: Vector, scalar: float) -> Vector:
    """Multiply vector by scalar."""
    return Vector([c * scalar for c in v.components])


def dot(v1: Vector, v2: Vector) -> float:
    """Calculate dot product."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have same dimension")
    return sum(v1[i] * v2[i] for i in range(len(v1)))


def cross(v1: Vector, v2: Vector) -> Vector:
    """Calculate cross product (3D only)."""
    if len(v1) != 3 or len(v2) != 3:
        raise ValueError("Cross product requires 3D vectors")

    return Vector(
        [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0],
        ]
    )


def magnitude(v: Vector) -> float:
    """Calculate vector magnitude (Euclidean norm)."""
    return math.sqrt(sum(c * c for c in v.components))


def normalize(v: Vector) -> Vector:
    """Normalize vector to unit length."""
    mag = magnitude(v)
    if mag == 0:
        raise ValueError("Cannot normalize zero vector")
    return Vector([c / mag for c in v.components])


def distance(v1: Vector, v2: Vector) -> float:
    """Calculate Euclidean distance between vectors."""
    return magnitude(subtract(v1, v2))


def angle_between(v1: Vector, v2: Vector) -> float:
    """Calculate angle between vectors in radians."""
    mag1 = magnitude(v1)
    mag2 = magnitude(v2)

    if mag1 == 0 or mag2 == 0:
        raise ValueError("Cannot calculate angle with zero vector")

    cos_angle = dot(v1, v2) / (mag1 * mag2)
    # Clamp to handle floating point errors
    cos_angle = max(-1, min(1, cos_angle))
    return math.acos(cos_angle)


def project(v: Vector, onto: Vector) -> Vector:
    """Project v onto another vector."""
    onto_mag_sq = dot(onto, onto)
    if onto_mag_sq == 0:
        raise ValueError("Cannot project onto zero vector")

    scalar = dot(v, onto) / onto_mag_sq
    return scalar_multiply(onto, scalar)


def reject(v: Vector, from_: Vector) -> Vector:
    """Calculate rejection of v from another vector."""
    return subtract(v, project(v, from_))


def reflect(v: Vector, normal: Vector) -> Vector:
    """Reflect vector across a plane defined by normal."""
    n = normalize(normal)
    return subtract(v, scalar_multiply(n, 2 * dot(v, n)))


def lerp(v1: Vector, v2: Vector, t: float) -> Vector:
    """Linear interpolation between vectors."""
    return add(scalar_multiply(v1, 1 - t), scalar_multiply(v2, t))


def hadamard(v1: Vector, v2: Vector) -> Vector:
    """Element-wise (Hadamard) product."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have same dimension")
    return Vector([v1[i] * v2[i] for i in range(len(v1))])


def triple_scalar(v1: Vector, v2: Vector, v3: Vector) -> float:
    """Calculate scalar triple product: v1 · (v2 × v3)."""
    return dot(v1, cross(v2, v3))


def triple_vector(v1: Vector, v2: Vector, v3: Vector) -> Vector:
    """Calculate vector triple product: v1 × (v2 × v3)."""
    return cross(v1, cross(v2, v3))


def is_orthogonal(v1: Vector, v2: Vector, tolerance: float = 1e-10) -> bool:
    """Check if two vectors are orthogonal."""
    return abs(dot(v1, v2)) < tolerance


def is_parallel(v1: Vector, v2: Vector, tolerance: float = 1e-10) -> bool:
    """Check if two vectors are parallel."""
    if len(v1) != len(v2):
        return False

    # Check if cross product is zero (for 3D)
    if len(v1) == 3:
        c = cross(v1, v2)
        return magnitude(c) < tolerance

    # For general case, check if one is scalar multiple of other
    if magnitude(v2) == 0:
        return magnitude(v1) == 0

    # Find non-zero component
    for i in range(len(v1)):
        if abs(v2[i]) > tolerance:
            ratio = v1[i] / v2[i]
            break
    else:
        return magnitude(v1) < tolerance

    for i in range(len(v1)):
        expected = ratio * v2[i]
        if abs(v1[i] - expected) > tolerance:
            return False

    return True


def outer_product(v1: Vector, v2: Vector) -> list[list[float]]:
    """Calculate outer product (returns matrix)."""
    return [[v1[i] * v2[j] for j in range(len(v2))] for i in range(len(v1))]


def component_in_direction(v: Vector, direction: Vector) -> float:
    """Calculate scalar component of v in given direction."""
    return dot(v, normalize(direction))


def gram_schmidt(vectors: list[Vector]) -> list[Vector]:
    """Gram-Schmidt orthogonalization."""
    if not vectors:
        return []

    orthogonal = []

    for v in vectors:
        # Subtract projections onto all previous vectors
        result = v
        for u in orthogonal:
            result = subtract(result, project(v, u))

        if magnitude(result) > 1e-10:
            orthogonal.append(result)

    return orthogonal


def orthonormalize(vectors: list[Vector]) -> list[Vector]:
    """Orthonormalize a set of vectors."""
    orthogonal = gram_schmidt(vectors)
    return [normalize(v) for v in orthogonal]


def centroid(vectors: list[Vector]) -> Vector:
    """Calculate centroid of a set of vectors."""
    if not vectors:
        raise ValueError("Need at least one vector")

    n = len(vectors)
    dim = len(vectors[0])

    result = [0.0] * dim
    for v in vectors:
        for i in range(dim):
            result[i] += v[i]

    return Vector([x / n for x in result])


def norm_p(v: Vector, p: float) -> float:
    """Calculate p-norm of vector."""
    if p <= 0:
        raise ValueError("p must be positive")
    if p == float("inf"):
        return max(abs(c) for c in v.components)

    return sum(abs(c) ** p for c in v.components) ** (1 / p)


def cosine_similarity(v1: Vector, v2: Vector) -> float:
    """Calculate cosine similarity between vectors."""
    mag1 = magnitude(v1)
    mag2 = magnitude(v2)

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot(v1, v2) / (mag1 * mag2)


def parse_vector(s: str) -> Vector:
    """Parse vector from comma-separated string."""
    return Vector([float(x) for x in s.split(",")])


def main() -> int:
    parser = argparse.ArgumentParser(description="Vector operations")
    parser.add_argument(
        "--mode",
        choices=[
            "add",
            "dot",
            "cross",
            "mag",
            "normalize",
            "angle",
            "project",
            "distance",
            "demo",
        ],
        default="demo",
        help="Operation mode",
    )
    parser.add_argument("--v1", help="First vector (comma-separated)")
    parser.add_argument("--v2", help="Second vector (comma-separated)")

    args = parser.parse_args()

    if args.mode == "demo":
        print("Vector Operations Demo\n")

        v1 = Vector([1.0, 2.0, 3.0])
        v2 = Vector([4.0, 5.0, 6.0])

        print(f"v1 = {v1}")
        print(f"v2 = {v2}")
        print(f"\nv1 + v2 = {add(v1, v2)}")
        print(f"v1 - v2 = {subtract(v1, v2)}")
        print(f"v1 · v2 = {dot(v1, v2):.4f}")
        print(f"v1 × v2 = {cross(v1, v2)}")
        print(f"|v1| = {magnitude(v1):.4f}")
        print(f"normalize(v1) = {normalize(v1)}")
        print(f"angle(v1, v2) = {math.degrees(angle_between(v1, v2)):.2f}°")
        print(f"distance(v1, v2) = {distance(v1, v2):.4f}")
        print(f"project(v1, v2) = {project(v1, v2)}")
        print(f"cosine_similarity = {cosine_similarity(v1, v2):.4f}")

    elif args.v1:
        v1 = parse_vector(args.v1)

        if args.mode == "mag":
            print(f"|v| = {magnitude(v1):.6f}")

        elif args.mode == "normalize":
            print(f"normalize(v) = {normalize(v1)}")

        elif args.v2:
            v2 = parse_vector(args.v2)

            if args.mode == "add":
                print(f"v1 + v2 = {add(v1, v2)}")

            elif args.mode == "dot":
                print(f"v1 · v2 = {dot(v1, v2):.6f}")

            elif args.mode == "cross":
                print(f"v1 × v2 = {cross(v1, v2)}")

            elif args.mode == "angle":
                angle = angle_between(v1, v2)
                print(f"angle = {math.degrees(angle):.4f}°")

            elif args.mode == "project":
                print(f"project(v1, v2) = {project(v1, v2)}")

            elif args.mode == "distance":
                print(f"distance = {distance(v1, v2):.6f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
