"""Tests for func_either_cli.py"""


from func_either_cli import (
    Left,
    ParseError,
    Right,
    ValidationError,
    left,
    parse_float,
    parse_int,
    parse_positive,
    partition_eithers,
    right,
    sequence,
    simulate_either,
    traverse,
    try_except,
    validate_email,
    validate_min_length,
    validate_non_empty,
    validate_range,
)


class TestLeft:
    def test_create(self):
        l = Left("error")
        assert l.value == "error"

    def test_is_left(self):
        assert Left("error").is_left()

    def test_is_right(self):
        assert not Left("error").is_right()

    def test_map(self):
        result = Left("error").map(lambda x: x * 2)
        assert result == Left("error")

    def test_map_left(self):
        result = Left("error").map_left(lambda x: x.upper())
        assert result == Left("ERROR")

    def test_flat_map(self):
        result = Left("error").flat_map(lambda x: Right(x * 2))
        assert result == Left("error")

    def test_get_or(self):
        assert Left("error").get_or(5) == 5

    def test_get_or_else(self):
        result = Left("error").get_or_else(lambda e: len(e))
        assert result == 5

    def test_fold(self):
        result = Left("error").fold(
            lambda l: f"Error: {l}",
            lambda r: f"Success: {r}"
        )
        assert result == "Error: error"

    def test_swap(self):
        assert Left("error").swap() == Right("error")

    def test_to_option(self):
        assert Left("error").to_option() is None

    def test_repr(self):
        assert repr(Left("error")) == "Left('error')"


class TestRight:
    def test_create(self):
        r = Right(5)
        assert r.value == 5

    def test_is_left(self):
        assert not Right(5).is_left()

    def test_is_right(self):
        assert Right(5).is_right()

    def test_map(self):
        result = Right(5).map(lambda x: x * 2)
        assert result == Right(10)

    def test_map_left(self):
        result = Right(5).map_left(lambda x: x.upper())
        assert result == Right(5)

    def test_flat_map(self):
        result = Right(5).flat_map(lambda x: Right(x * 2))
        assert result == Right(10)

    def test_flat_map_to_left(self):
        result = Right(5).flat_map(lambda x: Left("failed"))
        assert result == Left("failed")

    def test_get_or(self):
        assert Right(5).get_or(0) == 5

    def test_get_or_else(self):
        result = Right(5).get_or_else(lambda e: 0)
        assert result == 5

    def test_fold(self):
        result = Right(5).fold(
            lambda l: f"Error: {l}",
            lambda r: f"Success: {r}"
        )
        assert result == "Success: 5"

    def test_swap(self):
        assert Right(5).swap() == Left(5)

    def test_to_option(self):
        assert Right(5).to_option() == 5

    def test_repr(self):
        assert repr(Right(5)) == "Right(5)"


class TestConstructors:
    def test_left(self):
        result = left("error")
        assert isinstance(result, Left)
        assert result == Left("error")

    def test_right(self):
        result = right(5)
        assert isinstance(result, Right)
        assert result == Right(5)


class TestValidationError:
    def test_create(self):
        err = ValidationError("name", "required")
        assert err.field == "name"
        assert err.message == "required"

    def test_str(self):
        err = ValidationError("name", "required")
        assert str(err) == "name: required"


class TestParseError:
    def test_create(self):
        err = ParseError("abc", "not a number")
        assert err.input == "abc"
        assert err.reason == "not a number"

    def test_str(self):
        err = ParseError("abc", "not a number")
        assert "abc" in str(err)
        assert "not a number" in str(err)


class TestTryExcept:
    def test_success(self):
        result = try_except(lambda: 5 + 3)
        assert result == Right(8)

    def test_exception(self):
        result = try_except(lambda: 1 / 0)
        assert result.is_left()


class TestParseInt:
    def test_success(self):
        result = parse_int("42")
        assert result == Right(42)

    def test_failure(self):
        result = parse_int("abc")
        assert result.is_left()
        assert isinstance(result.fold(lambda x: x, lambda x: None), ParseError)


class TestParseFloat:
    def test_success(self):
        result = parse_float("3.14")
        assert result == Right(3.14)

    def test_failure(self):
        result = parse_float("abc")
        assert result.is_left()


class TestParsePositive:
    def test_positive(self):
        result = parse_positive("5")
        assert result == Right(5)

    def test_zero(self):
        result = parse_positive("0")
        assert result.is_left()

    def test_negative(self):
        result = parse_positive("-5")
        assert result.is_left()

    def test_invalid(self):
        result = parse_positive("abc")
        assert result.is_left()


class TestValidateNonEmpty:
    def test_valid(self):
        result = validate_non_empty("name", "John")
        assert result == Right("John")

    def test_strips_whitespace(self):
        result = validate_non_empty("name", "  John  ")
        assert result == Right("John")

    def test_empty(self):
        result = validate_non_empty("name", "")
        assert result.is_left()

    def test_whitespace_only(self):
        result = validate_non_empty("name", "   ")
        assert result.is_left()


class TestValidateMinLength:
    def test_valid(self):
        result = validate_min_length("password", "secret123", 8)
        assert result == Right("secret123")

    def test_too_short(self):
        result = validate_min_length("password", "short", 8)
        assert result.is_left()


class TestValidateEmail:
    def test_valid(self):
        result = validate_email("test@example.com")
        assert result == Right("test@example.com")

    def test_missing_at(self):
        result = validate_email("testexample.com")
        assert result.is_left()

    def test_missing_domain(self):
        result = validate_email("test@")
        assert result.is_left()


class TestValidateRange:
    def test_in_range(self):
        result = validate_range("age", 25, 0, 120)
        assert result == Right(25)

    def test_below_range(self):
        result = validate_range("age", -1, 0, 120)
        assert result.is_left()

    def test_above_range(self):
        result = validate_range("age", 150, 0, 120)
        assert result.is_left()


class TestSequence:
    def test_all_right(self):
        result = sequence([Right(1), Right(2), Right(3)])
        assert result == Right([1, 2, 3])

    def test_contains_left(self):
        result = sequence([Right(1), Left("error"), Right(3)])
        assert result.is_left()

    def test_empty(self):
        result = sequence([])
        assert result == Right([])


class TestTraverse:
    def test_all_success(self):
        result = traverse(parse_int, ["1", "2", "3"])
        assert result == Right([1, 2, 3])

    def test_contains_failure(self):
        result = traverse(parse_int, ["1", "abc", "3"])
        assert result.is_left()


class TestPartitionEithers:
    def test_mixed(self):
        eithers = [Right(1), Left("a"), Right(2), Left("b")]
        lefts, rights = partition_eithers(eithers)
        assert lefts == ["a", "b"]
        assert rights == [1, 2]

    def test_all_right(self):
        lefts, rights = partition_eithers([Right(1), Right(2)])
        assert lefts == []
        assert rights == [1, 2]

    def test_all_left(self):
        lefts, rights = partition_eithers([Left("a"), Left("b")])
        assert lefts == ["a", "b"]
        assert rights == []


class TestSimulateEither:
    def test_left(self):
        result = simulate_either(["left:error"])
        assert result == ["Left('error')"]

    def test_right(self):
        result = simulate_either(["right:5"])
        assert result == ["Right(5)"]

    def test_parse_int_success(self):
        result = simulate_either(["parse_int:42"])
        assert result == ["Right(42)"]

    def test_validate_email_success(self):
        result = simulate_either(["validate_email:test@example.com"])
        assert "Right" in result[0]

    def test_map(self):
        result = simulate_either(["map:5,double"])
        assert result == ["Right(10)"]

    def test_get_or(self):
        result = simulate_either(["get_or:left,99"])
        assert result == ["99"]

    def test_fold_left(self):
        result = simulate_either(["fold:left:oops"])
        assert result == ["Error: oops"]

    def test_fold_right(self):
        result = simulate_either(["fold:42"])
        assert result == ["Success: 42"]


class TestChaining:
    def test_validation_chain(self):
        def validate_user(email: str, age_str: str):
            return (
                validate_email(email)
                .flat_map(lambda e: parse_positive(age_str).map(lambda a: (e, a)))
            )

        result = validate_user("test@example.com", "25")
        assert result.is_right()

        result = validate_user("invalid", "25")
        assert result.is_left()

        result = validate_user("test@example.com", "-5")
        assert result.is_left()
