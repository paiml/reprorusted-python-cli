"""Matrix Operations CLI.

Demonstrates matrix operations: add, mul, transpose, inverse.
"""

import math
import sys
from dataclasses import dataclass


@dataclass
class Matrix:
    """2D matrix of floats."""

    data: list[list[float]]
    rows: int
    cols: int

    @classmethod
    def from_list(cls, data: list[list[float]]) -> "Matrix":
        """Create matrix from nested list."""
        rows = len(data)
        cols = len(data[0]) if data else 0
        return cls(data, rows, cols)

    @classmethod
    def zeros(cls, rows: int, cols: int) -> "Matrix":
        """Create zero matrix."""
        data = [[0.0] * cols for _ in range(rows)]
        return cls(data, rows, cols)

    @classmethod
    def ones(cls, rows: int, cols: int) -> "Matrix":
        """Create matrix of ones."""
        data = [[1.0] * cols for _ in range(rows)]
        return cls(data, rows, cols)

    @classmethod
    def identity(cls, n: int) -> "Matrix":
        """Create identity matrix."""
        data = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        return cls(data, n, n)

    @classmethod
    def diagonal(cls, values: list[float]) -> "Matrix":
        """Create diagonal matrix."""
        n = len(values)
        data = [[values[i] if i == j else 0.0 for j in range(n)] for i in range(n)]
        return cls(data, n, n)

    def __getitem__(self, idx: tuple[int, int]) -> float:
        return self.data[idx[0]][idx[1]]

    def __setitem__(self, idx: tuple[int, int], value: float) -> None:
        self.data[idx[0]][idx[1]] = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix):
            return False
        if self.rows != other.rows or self.cols != other.cols:
            return False
        for i in range(self.rows):
            for j in range(self.cols):
                if abs(self.data[i][j] - other.data[i][j]) > 1e-10:
                    return False
        return True

    def add(self, other: "Matrix") -> "Matrix":
        """Matrix addition."""
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrix dimensions must match")
        result = Matrix.zeros(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[i][j] = self.data[i][j] + other.data[i][j]
        return result

    def sub(self, other: "Matrix") -> "Matrix":
        """Matrix subtraction."""
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrix dimensions must match")
        result = Matrix.zeros(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[i][j] = self.data[i][j] - other.data[i][j]
        return result

    def mul(self, other: "Matrix") -> "Matrix":
        """Matrix multiplication."""
        if self.cols != other.rows:
            raise ValueError(
                f"Cannot multiply {self.rows}x{self.cols} by {other.rows}x{other.cols}"
            )
        result = Matrix.zeros(self.rows, other.cols)
        for i in range(self.rows):
            for j in range(other.cols):
                total = 0.0
                for k in range(self.cols):
                    total += self.data[i][k] * other.data[k][j]
                result.data[i][j] = total
        return result

    def scale(self, scalar: float) -> "Matrix":
        """Scalar multiplication."""
        result = Matrix.zeros(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[i][j] = self.data[i][j] * scalar
        return result

    def transpose(self) -> "Matrix":
        """Matrix transpose."""
        result = Matrix.zeros(self.cols, self.rows)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[j][i] = self.data[i][j]
        return result

    def trace(self) -> float:
        """Sum of diagonal elements."""
        if self.rows != self.cols:
            raise ValueError("Trace requires square matrix")
        return sum(self.data[i][i] for i in range(self.rows))

    def det(self) -> float:
        """Calculate determinant using LU decomposition."""
        if self.rows != self.cols:
            raise ValueError("Determinant requires square matrix")
        n = self.rows
        lu = [row[:] for row in self.data]

        sign = 1
        for i in range(n):
            # Find pivot
            max_row = i
            for k in range(i + 1, n):
                if abs(lu[k][i]) > abs(lu[max_row][i]):
                    max_row = k
            if max_row != i:
                lu[i], lu[max_row] = lu[max_row], lu[i]
                sign *= -1

            if abs(lu[i][i]) < 1e-10:
                return 0.0

            for k in range(i + 1, n):
                factor = lu[k][i] / lu[i][i]
                for j in range(i, n):
                    lu[k][j] -= factor * lu[i][j]

        det_val = float(sign)
        for i in range(n):
            det_val *= lu[i][i]
        return det_val

    def inverse(self) -> "Matrix":
        """Calculate matrix inverse using Gauss-Jordan."""
        if self.rows != self.cols:
            raise ValueError("Inverse requires square matrix")
        n = self.rows

        # Augment with identity
        aug = [self.data[i][:] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        # Forward elimination
        for i in range(n):
            max_row = i
            for k in range(i + 1, n):
                if abs(aug[k][i]) > abs(aug[max_row][i]):
                    max_row = k
            aug[i], aug[max_row] = aug[max_row], aug[i]

            if abs(aug[i][i]) < 1e-10:
                raise ValueError("Matrix is singular")

            pivot = aug[i][i]
            for j in range(2 * n):
                aug[i][j] /= pivot

            for k in range(n):
                if k != i:
                    factor = aug[k][i]
                    for j in range(2 * n):
                        aug[k][j] -= factor * aug[i][j]

        result = Matrix.zeros(n, n)
        for i in range(n):
            for j in range(n):
                result.data[i][j] = aug[i][n + j]
        return result

    def frobenius_norm(self) -> float:
        """Frobenius norm."""
        total = 0.0
        for i in range(self.rows):
            for j in range(self.cols):
                total += self.data[i][j] ** 2
        return math.sqrt(total)

    def row(self, i: int) -> list[float]:
        """Get row."""
        return self.data[i][:]

    def col(self, j: int) -> list[float]:
        """Get column."""
        return [self.data[i][j] for i in range(self.rows)]

    def to_list(self) -> list[list[float]]:
        """Convert to nested list."""
        return [row[:] for row in self.data]


def dot(v1: list[float], v2: list[float]) -> float:
    """Dot product of vectors."""
    return sum(a * b for a, b in zip(v1, v2, strict=False))


def simulate_matrix(operations: list[str]) -> list[str]:
    """Simulate matrix operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "add":
            m1 = Matrix.from_list([[1, 2], [3, 4]])
            m2 = Matrix.from_list([[5, 6], [7, 8]])
            result = m1.add(m2)
            results.append(str(result.to_list()))
        elif cmd == "mul":
            m1 = Matrix.from_list([[1, 2], [3, 4]])
            m2 = Matrix.from_list([[5, 6], [7, 8]])
            result = m1.mul(m2)
            results.append(str(result.to_list()))
        elif cmd == "transpose":
            m = Matrix.from_list([[1, 2, 3], [4, 5, 6]])
            result = m.transpose()
            results.append(str(result.to_list()))
        elif cmd == "det":
            m = Matrix.from_list([[1, 2], [3, 4]])
            result = m.det()
            results.append(f"{result:.1f}")
        elif cmd == "inverse":
            m = Matrix.from_list([[4, 7], [2, 6]])
            result = m.inverse()
            results.append(str([[round(x, 2) for x in row] for row in result.to_list()]))
        elif cmd == "identity":
            n = int(parts[1])
            result = Matrix.identity(n)
            results.append(str(result.to_list()))

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: num_matrix_cli.py <command>")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        A = Matrix.from_list([[1, 2], [3, 4]])
        B = Matrix.from_list([[5, 6], [7, 8]])

        print(f"A = {A.to_list()}")
        print(f"B = {B.to_list()}")
        print(f"A + B = {A.add(B).to_list()}")
        print(f"A * B = {A.mul(B).to_list()}")
        print(f"A^T = {A.transpose().to_list()}")
        print(f"det(A) = {A.det()}")

        try:
            print(f"A^-1 = {A.inverse().to_list()}")
        except ValueError as e:
            print(f"Cannot invert: {e}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
