#!/usr/bin/env python3
"""Matrix Operations CLI.

Pure Python matrix operations without external dependencies.
"""

import argparse
import sys
from typing import TypeAlias

Matrix: TypeAlias = list[list[float]]
Vector: TypeAlias = list[float]


def zeros(rows: int, cols: int) -> Matrix:
    """Create zero matrix."""
    return [[0.0] * cols for _ in range(rows)]


def ones(rows: int, cols: int) -> Matrix:
    """Create matrix of ones."""
    return [[1.0] * cols for _ in range(rows)]


def identity(n: int) -> Matrix:
    """Create identity matrix."""
    result = zeros(n, n)
    for i in range(n):
        result[i][i] = 1.0
    return result


def shape(m: Matrix) -> tuple[int, int]:
    """Get matrix dimensions."""
    if not m:
        return 0, 0
    return len(m), len(m[0])


def transpose(m: Matrix) -> Matrix:
    """Transpose matrix."""
    if not m:
        return []
    rows, cols = shape(m)
    return [[m[i][j] for i in range(rows)] for j in range(cols)]


def add(a: Matrix, b: Matrix) -> Matrix:
    """Add two matrices."""
    rows_a, cols_a = shape(a)
    rows_b, cols_b = shape(b)

    if rows_a != rows_b or cols_a != cols_b:
        raise ValueError("Matrix dimensions must match")

    return [[a[i][j] + b[i][j] for j in range(cols_a)] for i in range(rows_a)]


def subtract(a: Matrix, b: Matrix) -> Matrix:
    """Subtract matrix b from a."""
    rows_a, cols_a = shape(a)
    rows_b, cols_b = shape(b)

    if rows_a != rows_b or cols_a != cols_b:
        raise ValueError("Matrix dimensions must match")

    return [[a[i][j] - b[i][j] for j in range(cols_a)] for i in range(rows_a)]


def scalar_multiply(m: Matrix, scalar: float) -> Matrix:
    """Multiply matrix by scalar."""
    rows, cols = shape(m)
    return [[m[i][j] * scalar for j in range(cols)] for i in range(rows)]


def multiply(a: Matrix, b: Matrix) -> Matrix:
    """Multiply two matrices."""
    rows_a, cols_a = shape(a)
    rows_b, cols_b = shape(b)

    if cols_a != rows_b:
        raise ValueError(f"Cannot multiply {rows_a}x{cols_a} by {rows_b}x{cols_b}")

    result = zeros(rows_a, cols_b)

    for i in range(rows_a):
        for j in range(cols_b):
            total = 0.0
            for k in range(cols_a):
                total += a[i][k] * b[k][j]
            result[i][j] = total

    return result


def hadamard(a: Matrix, b: Matrix) -> Matrix:
    """Element-wise multiplication."""
    rows_a, cols_a = shape(a)
    rows_b, cols_b = shape(b)

    if rows_a != rows_b or cols_a != cols_b:
        raise ValueError("Matrix dimensions must match")

    return [[a[i][j] * b[i][j] for j in range(cols_a)] for i in range(rows_a)]


def dot_product(a: Vector, b: Vector) -> float:
    """Vector dot product."""
    if len(a) != len(b):
        raise ValueError("Vector dimensions must match")

    return sum(a[i] * b[i] for i in range(len(a)))


def matrix_vector_multiply(m: Matrix, v: Vector) -> Vector:
    """Multiply matrix by vector."""
    rows, cols = shape(m)

    if cols != len(v):
        raise ValueError("Matrix columns must match vector length")

    return [sum(m[i][j] * v[j] for j in range(cols)) for i in range(rows)]


def trace(m: Matrix) -> float:
    """Calculate matrix trace (sum of diagonal)."""
    rows, cols = shape(m)
    if rows != cols:
        raise ValueError("Matrix must be square")

    return sum(m[i][i] for i in range(rows))


def determinant(m: Matrix) -> float:
    """Calculate determinant using LU decomposition."""
    rows, cols = shape(m)
    if rows != cols:
        raise ValueError("Matrix must be square")

    n = rows

    # Create a copy
    lu = [row[:] for row in m]
    det = 1.0

    for i in range(n):
        # Find pivot
        max_row = i
        for k in range(i + 1, n):
            if abs(lu[k][i]) > abs(lu[max_row][i]):
                max_row = k

        if abs(lu[max_row][i]) < 1e-10:
            return 0.0

        if max_row != i:
            lu[i], lu[max_row] = lu[max_row], lu[i]
            det *= -1

        det *= lu[i][i]

        for k in range(i + 1, n):
            factor = lu[k][i] / lu[i][i]
            for j in range(i, n):
                lu[k][j] -= factor * lu[i][j]

    return det


def minor(m: Matrix, row: int, col: int) -> Matrix:
    """Get minor matrix (removing row and column)."""
    return [[m[i][j] for j in range(len(m[0])) if j != col] for i in range(len(m)) if i != row]


def cofactor(m: Matrix) -> Matrix:
    """Calculate cofactor matrix."""
    rows, cols = shape(m)
    result = zeros(rows, cols)

    for i in range(rows):
        for j in range(cols):
            sign = (-1) ** (i + j)
            result[i][j] = sign * determinant(minor(m, i, j))

    return result


def adjoint(m: Matrix) -> Matrix:
    """Calculate adjoint (adjugate) matrix."""
    return transpose(cofactor(m))


def inverse(m: Matrix) -> Matrix:
    """Calculate matrix inverse."""
    det = determinant(m)
    if abs(det) < 1e-10:
        raise ValueError("Matrix is singular")

    adj = adjoint(m)
    return scalar_multiply(adj, 1.0 / det)


def lu_decomposition(m: Matrix) -> tuple[Matrix, Matrix]:
    """LU decomposition."""
    rows, cols = shape(m)
    if rows != cols:
        raise ValueError("Matrix must be square")

    n = rows
    L = identity(n)
    U = [row[:] for row in m]

    for i in range(n):
        for k in range(i + 1, n):
            if abs(U[i][i]) < 1e-10:
                raise ValueError("Zero pivot encountered")

            factor = U[k][i] / U[i][i]
            L[k][i] = factor
            for j in range(i, n):
                U[k][j] -= factor * U[i][j]

    return L, U


def frobenius_norm(m: Matrix) -> float:
    """Calculate Frobenius norm."""
    rows, cols = shape(m)
    total = 0.0
    for i in range(rows):
        for j in range(cols):
            total += m[i][j] ** 2
    return total**0.5


def max_norm(m: Matrix) -> float:
    """Calculate max (infinity) norm."""
    rows, cols = shape(m)
    max_val = 0.0
    for i in range(rows):
        for j in range(cols):
            max_val = max(max_val, abs(m[i][j]))
    return max_val


def row_echelon(m: Matrix) -> Matrix:
    """Convert to row echelon form."""
    rows, cols = shape(m)
    result = [row[:] for row in m]

    lead = 0
    for r in range(rows):
        if lead >= cols:
            break

        i = r
        while abs(result[i][lead]) < 1e-10:
            i += 1
            if i == rows:
                i = r
                lead += 1
                if lead == cols:
                    return result

        result[i], result[r] = result[r], result[i]

        div = result[r][lead]
        if abs(div) > 1e-10:
            result[r] = [x / div for x in result[r]]

        for i in range(rows):
            if i != r:
                mult = result[i][lead]
                result[i] = [result[i][j] - mult * result[r][j] for j in range(cols)]

        lead += 1

    return result


def rank(m: Matrix) -> int:
    """Calculate matrix rank."""
    ref = row_echelon(m)
    rows, cols = shape(ref)

    r = 0
    for i in range(rows):
        is_zero = all(abs(ref[i][j]) < 1e-10 for j in range(cols))
        if not is_zero:
            r += 1

    return r


def format_matrix(m: Matrix, precision: int = 2) -> str:
    """Format matrix for display."""
    rows, cols = shape(m)
    lines = []

    for i in range(rows):
        row_str = " ".join(f"{m[i][j]:>{precision + 6}.{precision}f}" for j in range(cols))
        lines.append(f"[ {row_str} ]")

    return "\n".join(lines)


def parse_matrix(s: str) -> Matrix:
    """Parse matrix from string format."""
    rows = s.strip().split(";")
    return [[float(x) for x in row.split(",")] for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="Matrix operations")
    parser.add_argument(
        "--mode",
        choices=[
            "add",
            "mult",
            "det",
            "inv",
            "trans",
            "trace",
            "rank",
            "lu",
            "identity",
            "demo",
        ],
        default="demo",
        help="Operation mode",
    )
    parser.add_argument("--a", help="Matrix A (format: '1,2;3,4')")
    parser.add_argument("--b", help="Matrix B")
    parser.add_argument("--n", type=int, default=3, help="Size for identity matrix")

    args = parser.parse_args()

    if args.mode == "identity":
        m = identity(args.n)
        print(f"Identity matrix ({args.n}x{args.n}):")
        print(format_matrix(m))

    elif args.mode == "demo":
        print("Matrix Operations Demo\n")

        A = [[1, 2, 3], [4, 5, 6], [7, 8, 10]]

        print("Matrix A:")
        print(format_matrix(A))
        print(f"\nDeterminant: {determinant(A):.2f}")
        print(f"Trace: {trace(A):.2f}")
        print(f"Rank: {rank(A)}")
        print(f"Frobenius Norm: {frobenius_norm(A):.4f}")

        print("\nTranspose:")
        print(format_matrix(transpose(A)))

        print("\nInverse:")
        print(format_matrix(inverse(A)))

        print("\nA * A^-1 (should be identity):")
        print(format_matrix(multiply(A, inverse(A))))

    elif args.a:
        A = parse_matrix(args.a)

        if args.mode == "det":
            print(f"Determinant: {determinant(A):.6f}")

        elif args.mode == "inv":
            print("Inverse:")
            print(format_matrix(inverse(A)))

        elif args.mode == "trans":
            print("Transpose:")
            print(format_matrix(transpose(A)))

        elif args.mode == "trace":
            print(f"Trace: {trace(A):.6f}")

        elif args.mode == "rank":
            print(f"Rank: {rank(A)}")

        elif args.mode == "lu":
            L, U = lu_decomposition(A)
            print("L:")
            print(format_matrix(L))
            print("\nU:")
            print(format_matrix(U))

        elif args.mode == "add" and args.b:
            B = parse_matrix(args.b)
            print("A + B:")
            print(format_matrix(add(A, B)))

        elif args.mode == "mult" and args.b:
            B = parse_matrix(args.b)
            print("A * B:")
            print(format_matrix(multiply(A, B)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
