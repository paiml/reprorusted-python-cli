"""Tests for calc_cli.py"""

import math

import pytest
from calc_cli import (
    Lexer,
    TokenType,
    evaluate,
    tokenize,
)


class TestLexer:
    def test_number(self):
        lexer = Lexer("42")
        token = lexer.next_token()
        assert token.type == TokenType.NUMBER
        assert token.value == 42.0

    def test_float(self):
        lexer = Lexer("3.14")
        token = lexer.next_token()
        assert token.type == TokenType.NUMBER
        assert token.value == pytest.approx(3.14)

    def test_operators(self):
        tokens = tokenize("+ - * / ^ %")
        types = [t.type for t in tokens[:-1]]  # Exclude EOF
        assert types == [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.POWER,
            TokenType.MODULO,
        ]

    def test_parentheses(self):
        tokens = tokenize("()")
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.RPAREN

    def test_identifier(self):
        lexer = Lexer("sin")
        token = lexer.next_token()
        assert token.type == TokenType.IDENTIFIER
        assert token.value == "sin"

    def test_whitespace(self):
        tokens = tokenize("  1  +  2  ")
        values = [t.value for t in tokens if t.type == TokenType.NUMBER]
        assert values == [1.0, 2.0]

    def test_expression(self):
        tokens = tokenize("2 + 3 * 4")
        types = [t.type for t in tokens[:-1]]
        assert types == [
            TokenType.NUMBER,
            TokenType.PLUS,
            TokenType.NUMBER,
            TokenType.MULTIPLY,
            TokenType.NUMBER,
        ]


class TestParser:
    def test_number(self):
        assert evaluate("42") == 42

    def test_addition(self):
        assert evaluate("2 + 3") == 5

    def test_subtraction(self):
        assert evaluate("5 - 3") == 2

    def test_multiplication(self):
        assert evaluate("2 * 3") == 6

    def test_division(self):
        assert evaluate("6 / 2") == 3

    def test_modulo(self):
        assert evaluate("7 % 3") == 1

    def test_power(self):
        assert evaluate("2 ^ 3") == 8

    def test_precedence(self):
        assert evaluate("2 + 3 * 4") == 14
        assert evaluate("2 * 3 + 4") == 10

    def test_parentheses(self):
        assert evaluate("(2 + 3) * 4") == 20

    def test_nested_parentheses(self):
        assert evaluate("((2 + 3) * (4 - 1))") == 15

    def test_unary_minus(self):
        assert evaluate("-5") == -5
        assert evaluate("2 + -3") == -1
        assert evaluate("--5") == 5

    def test_unary_plus(self):
        assert evaluate("+5") == 5

    def test_power_right_associative(self):
        # 2^3^2 should be 2^9 = 512, not 8^2 = 64
        assert evaluate("2 ^ 3 ^ 2") == 512


class TestFunctions:
    def test_sin(self):
        assert evaluate("sin(0)") == pytest.approx(0)
        assert evaluate("sin(pi/2)") == pytest.approx(1)

    def test_cos(self):
        assert evaluate("cos(0)") == pytest.approx(1)
        assert evaluate("cos(pi)") == pytest.approx(-1)

    def test_sqrt(self):
        assert evaluate("sqrt(4)") == 2
        assert evaluate("sqrt(2)") == pytest.approx(math.sqrt(2))

    def test_abs(self):
        assert evaluate("abs(-5)") == 5
        assert evaluate("abs(5)") == 5

    def test_log(self):
        assert evaluate("log(e)") == pytest.approx(1)

    def test_exp(self):
        assert evaluate("exp(0)") == 1
        assert evaluate("exp(1)") == pytest.approx(math.e)

    def test_floor_ceil(self):
        assert evaluate("floor(3.7)") == 3
        assert evaluate("ceil(3.2)") == 4

    def test_min_max(self):
        assert evaluate("min(3, 5)") == 3
        assert evaluate("max(3, 5)") == 5
        assert evaluate("min(1, 2, 3)") == 1

    def test_pow(self):
        assert evaluate("pow(2, 3)") == 8

    def test_nested_functions(self):
        assert evaluate("sqrt(abs(-16))") == 4


class TestConstants:
    def test_pi(self):
        assert evaluate("pi") == pytest.approx(math.pi)

    def test_e(self):
        assert evaluate("e") == pytest.approx(math.e)

    def test_tau(self):
        assert evaluate("tau") == pytest.approx(math.tau)

    def test_in_expression(self):
        assert evaluate("2 * pi") == pytest.approx(2 * math.pi)


class TestVariables:
    def test_simple(self):
        assert evaluate("x + 1", {"x": 5}) == 6

    def test_multiple(self):
        assert evaluate("x + y", {"x": 2, "y": 3}) == 5

    def test_in_expression(self):
        assert evaluate("2 * x + 3 * y", {"x": 4, "y": 2}) == 14


class TestErrors:
    def test_division_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            evaluate("1 / 0")

    def test_unknown_identifier(self):
        with pytest.raises(SyntaxError):
            evaluate("unknown")

    def test_unknown_function(self):
        with pytest.raises(SyntaxError):
            evaluate("foo(1)")

    def test_unexpected_token(self):
        # Parser handles unary +, so "1 + + 2" is valid (= 1 + (+2) = 3)
        # Use truly invalid syntax
        with pytest.raises(SyntaxError):
            evaluate("1 2 +")

    def test_unclosed_paren(self):
        with pytest.raises(SyntaxError):
            evaluate("(1 + 2")

    def test_unexpected_char(self):
        with pytest.raises(SyntaxError):
            evaluate("1 @ 2")


class TestComplexExpressions:
    def test_complex_1(self):
        result = evaluate("(1 + 2) * (3 + 4) / 7")
        assert result == pytest.approx(3)

    def test_complex_2(self):
        result = evaluate("2 ^ 3 + 4 * 5 - 6 / 2")
        assert result == pytest.approx(25)  # 8 + 20 - 3

    def test_scientific(self):
        result = evaluate("sqrt(3^2 + 4^2)")
        assert result == pytest.approx(5)

    def test_trig(self):
        result = evaluate("sin(pi/6)")
        assert result == pytest.approx(0.5)

    def test_logarithm(self):
        result = evaluate("log(e^2)")
        assert result == pytest.approx(2)
