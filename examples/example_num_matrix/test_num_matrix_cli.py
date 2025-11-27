"""Tests for num_matrix_cli.py"""

import math

import pytest
from num_matrix_cli import Matrix, dot, simulate_matrix


class TestMatrixCreation:
    def test_from_list(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        assert m.rows == 2
        assert m.cols == 2

    def test_zeros(self):
        m = Matrix.zeros(2, 3)
        assert m.rows == 2
        assert m.cols == 3
        assert m.data == [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

    def test_ones(self):
        m = Matrix.ones(2, 2)
        assert m.data == [[1.0, 1.0], [1.0, 1.0]]

    def test_identity(self):
        m = Matrix.identity(3)
        assert m.data == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    def test_diagonal(self):
        m = Matrix.diagonal([1, 2, 3])
        assert m.data == [[1, 0, 0], [0, 2, 0], [0, 0, 3]]


class TestMatrixAccess:
    def test_getitem(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        assert m[0, 0] == 1
        assert m[1, 1] == 4

    def test_setitem(self):
        m = Matrix.zeros(2, 2)
        m[0, 1] = 5.0
        assert m[0, 1] == 5.0

    def test_row(self):
        m = Matrix.from_list([[1, 2, 3], [4, 5, 6]])
        assert m.row(0) == [1, 2, 3]

    def test_col(self):
        m = Matrix.from_list([[1, 2], [3, 4], [5, 6]])
        assert m.col(1) == [2, 4, 6]


class TestMatrixAdd:
    def test_basic(self):
        m1 = Matrix.from_list([[1, 2], [3, 4]])
        m2 = Matrix.from_list([[5, 6], [7, 8]])
        result = m1.add(m2)
        assert result.data == [[6, 8], [10, 12]]

    def test_dimension_mismatch(self):
        m1 = Matrix.from_list([[1, 2], [3, 4]])
        m2 = Matrix.from_list([[1, 2, 3]])
        with pytest.raises(ValueError):
            m1.add(m2)


class TestMatrixSub:
    def test_basic(self):
        m1 = Matrix.from_list([[5, 6], [7, 8]])
        m2 = Matrix.from_list([[1, 2], [3, 4]])
        result = m1.sub(m2)
        assert result.data == [[4, 4], [4, 4]]


class TestMatrixMul:
    def test_square(self):
        m1 = Matrix.from_list([[1, 2], [3, 4]])
        m2 = Matrix.from_list([[5, 6], [7, 8]])
        result = m1.mul(m2)
        assert result.data == [[19, 22], [43, 50]]

    def test_non_square(self):
        m1 = Matrix.from_list([[1, 2, 3], [4, 5, 6]])  # 2x3
        m2 = Matrix.from_list([[7, 8], [9, 10], [11, 12]])  # 3x2
        result = m1.mul(m2)  # Should be 2x2
        assert result.rows == 2
        assert result.cols == 2

    def test_dimension_mismatch(self):
        m1 = Matrix.from_list([[1, 2], [3, 4]])
        m2 = Matrix.from_list([[1, 2, 3]])
        with pytest.raises(ValueError):
            m1.mul(m2)

    def test_identity_mul(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        i = Matrix.identity(2)
        result = m.mul(i)
        assert result == m


class TestMatrixScale:
    def test_basic(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        result = m.scale(2)
        assert result.data == [[2, 4], [6, 8]]

    def test_zero(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        result = m.scale(0)
        assert result == Matrix.zeros(2, 2)


class TestMatrixTranspose:
    def test_square(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        result = m.transpose()
        assert result.data == [[1, 3], [2, 4]]

    def test_non_square(self):
        m = Matrix.from_list([[1, 2, 3], [4, 5, 6]])
        result = m.transpose()
        assert result.rows == 3
        assert result.cols == 2
        assert result.data == [[1, 4], [2, 5], [3, 6]]

    def test_double_transpose(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        result = m.transpose().transpose()
        assert result == m


class TestMatrixTrace:
    def test_basic(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        assert m.trace() == 5

    def test_identity(self):
        m = Matrix.identity(5)
        assert m.trace() == 5

    def test_non_square(self):
        m = Matrix.from_list([[1, 2, 3], [4, 5, 6]])
        with pytest.raises(ValueError):
            m.trace()


class TestMatrixDet:
    def test_2x2(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        assert abs(m.det() - (-2)) < 1e-10

    def test_3x3(self):
        m = Matrix.from_list([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
        assert abs(m.det() - (-3)) < 1e-10

    def test_identity(self):
        m = Matrix.identity(4)
        assert abs(m.det() - 1) < 1e-10

    def test_singular(self):
        m = Matrix.from_list([[1, 2], [2, 4]])
        assert abs(m.det()) < 1e-10


class TestMatrixInverse:
    def test_2x2(self):
        m = Matrix.from_list([[4, 7], [2, 6]])
        inv = m.inverse()
        result = m.mul(inv)
        identity = Matrix.identity(2)
        # Check it's close to identity
        for i in range(2):
            for j in range(2):
                assert abs(result[i, j] - identity[i, j]) < 1e-10

    def test_singular(self):
        m = Matrix.from_list([[1, 2], [2, 4]])
        with pytest.raises(ValueError):
            m.inverse()


class TestFrobeniusNorm:
    def test_basic(self):
        m = Matrix.from_list([[1, 2], [3, 4]])
        norm = m.frobenius_norm()
        expected = math.sqrt(1 + 4 + 9 + 16)
        assert abs(norm - expected) < 1e-10


class TestDot:
    def test_basic(self):
        assert dot([1, 2, 3], [4, 5, 6]) == 32


class TestSimulateMatrix:
    def test_add(self):
        result = simulate_matrix(["add:"])
        assert "[[6, 8], [10, 12]]" in result[0]

    def test_mul(self):
        result = simulate_matrix(["mul:"])
        assert "19" in result[0] and "22" in result[0] and "43" in result[0] and "50" in result[0]

    def test_transpose(self):
        result = simulate_matrix(["transpose:"])
        assert "[[1, 4], [2, 5], [3, 6]]" in result[0]

    def test_det(self):
        result = simulate_matrix(["det:"])
        assert result == ["-2.0"]

    def test_identity(self):
        result = simulate_matrix(["identity:2"])
        assert "[[1.0, 0.0], [0.0, 1.0]]" in result[0]
