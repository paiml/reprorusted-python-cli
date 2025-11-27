"""Tests for func_pipeline_cli.py"""


from func_pipeline_cli import (
    Pipeline,
    add,
    apply,
    compose,
    constant,
    double,
    drop,
    filter_list,
    flip,
    head,
    identity,
    is_even,
    is_positive,
    join_by,
    lower,
    map_list,
    multiply,
    negate,
    pipe,
    pipeline,
    prefix,
    reduce_list,
    reverse,
    simulate_pipeline,
    split_by,
    square,
    strip,
    suffix,
    tail,
    take,
    tap,
    upper,
)


class TestPipe:
    def test_single_function(self):
        assert pipe(double)(5) == 10

    def test_two_functions(self):
        assert pipe(double, square)(3) == 36  # (3*2)^2

    def test_three_functions(self):
        assert pipe(double, add(1), square)(2) == 25  # ((2*2)+1)^2

    def test_empty_pipe(self):
        assert pipe()(5) == 5

    def test_string_functions(self):
        assert pipe(strip, upper)("  hello  ") == "HELLO"


class TestCompose:
    def test_single_function(self):
        assert compose(double)(5) == 10

    def test_two_functions(self):
        # compose applies right to left: square then double
        assert compose(double, square)(3) == 18  # (3^2)*2

    def test_three_functions(self):
        # Right to left: square, add(1), double
        assert compose(double, add(1), square)(2) == 10  # ((2^2)+1)*2

    def test_empty_compose(self):
        assert compose()(5) == 5


class TestIdentity:
    def test_int(self):
        assert identity(5) == 5

    def test_string(self):
        assert identity("hello") == "hello"

    def test_list(self):
        assert identity([1, 2, 3]) == [1, 2, 3]


class TestConstant:
    def test_returns_value(self):
        const_5 = constant(5)
        assert const_5() == 5
        assert const_5(10) == 5
        assert const_5(1, 2, 3) == 5

    def test_with_kwargs(self):
        const_hello = constant("hello")
        assert const_hello(foo="bar") == "hello"


class TestFlip:
    def test_flip_subtract(self):
        def sub(a, b):
            return a - b
        flipped_sub = flip(sub)
        assert sub(5, 3) == 2
        assert flipped_sub(5, 3) == -2

    def test_flip_divide(self):
        def div(a, b):
            return a / b
        flipped_div = flip(div)
        assert div(10, 2) == 5.0
        assert flipped_div(10, 2) == 0.2


class TestApply:
    def test_apply(self):
        assert apply(double, 5) == 10
        assert apply(square, 3) == 9


class TestTap:
    def test_tap_returns_original(self):
        side_effects = []
        tapped = tap(lambda x: side_effects.append(x))
        result = tapped(5)
        assert result == 5
        assert side_effects == [5]


class TestPipeline:
    def test_create(self):
        p = Pipeline(5)
        assert p.value == 5

    def test_map(self):
        result = Pipeline(5).map(double).get()
        assert result == 10

    def test_map_chain(self):
        result = Pipeline(5).map(double).map(add(3)).get()
        assert result == 13

    def test_tap(self):
        side_effects = []
        result = Pipeline(5).tap(lambda x: side_effects.append(x)).get()
        assert result == 5
        assert side_effects == [5]

    def test_filter_pass(self):
        result = Pipeline(6).filter(is_even).get()
        assert result == 6

    def test_filter_fail(self):
        result = Pipeline(5).filter(is_even).get()
        assert result is None

    def test_get_or(self):
        assert Pipeline(5).get_or(0) == 5
        assert Pipeline(None).get_or(0) == 0


class TestPipelineFunction:
    def test_create(self):
        p = pipeline(5)
        assert p.get() == 5

    def test_chain(self):
        result = pipeline(5).map(double).map(square).get()
        assert result == 100


class TestAdd:
    def test_add_positive(self):
        assert add(3)(5) == 8

    def test_add_negative(self):
        assert add(-3)(5) == 2

    def test_add_zero(self):
        assert add(0)(5) == 5


class TestMultiply:
    def test_multiply_positive(self):
        assert multiply(3)(5) == 15

    def test_multiply_zero(self):
        assert multiply(0)(5) == 0


class TestNegate:
    def test_positive(self):
        assert negate(5) == -5

    def test_negative(self):
        assert negate(-5) == 5

    def test_zero(self):
        assert negate(0) == 0


class TestDouble:
    def test_positive(self):
        assert double(5) == 10

    def test_negative(self):
        assert double(-3) == -6


class TestSquare:
    def test_positive(self):
        assert square(5) == 25

    def test_negative(self):
        assert square(-3) == 9


class TestPredicates:
    def test_is_even(self):
        assert is_even(4)
        assert not is_even(5)

    def test_is_positive(self):
        assert is_positive(5)
        assert not is_positive(-5)
        assert not is_positive(0)


class TestStringTransformations:
    def test_upper(self):
        assert upper("hello") == "HELLO"

    def test_lower(self):
        assert lower("HELLO") == "hello"

    def test_strip(self):
        assert strip("  hello  ") == "hello"

    def test_reverse(self):
        assert reverse("hello") == "olleh"

    def test_prefix(self):
        assert prefix("pre_")("test") == "pre_test"

    def test_suffix(self):
        assert suffix("_post")("test") == "test_post"

    def test_split_by(self):
        assert split_by(",")("a,b,c") == ["a", "b", "c"]

    def test_join_by(self):
        assert join_by("-")(["a", "b", "c"]) == "a-b-c"


class TestListTransformations:
    def test_map_list(self):
        assert map_list(double)([1, 2, 3]) == [2, 4, 6]

    def test_filter_list(self):
        assert filter_list(is_even)([1, 2, 3, 4]) == [2, 4]

    def test_reduce_list(self):
        def add_fn(a, b):
            return a + b
        assert reduce_list(add_fn, 0)([1, 2, 3, 4]) == 10

    def test_head(self):
        assert head([1, 2, 3]) == 1
        assert head([]) is None

    def test_tail(self):
        assert tail([1, 2, 3]) == [2, 3]
        assert tail([]) == []

    def test_take(self):
        assert take(2)([1, 2, 3, 4]) == [1, 2]
        assert take(10)([1, 2]) == [1, 2]

    def test_drop(self):
        assert drop(2)([1, 2, 3, 4]) == [3, 4]
        assert drop(10)([1, 2]) == []


class TestSimulatePipeline:
    def test_pipe_double(self):
        result = simulate_pipeline(["pipe:5,double"])
        assert result == ["10"]

    def test_pipe_chain(self):
        result = simulate_pipeline(["pipe:5,double,add(3)"])
        assert result == ["13"]

    def test_compose(self):
        result = simulate_pipeline(["compose:3,double,square"])
        assert result == ["18"]  # (3^2)*2

    def test_string_pipe(self):
        result = simulate_pipeline(["string_pipe:  hello  ,strip,upper"])
        assert result == ["HELLO"]

    def test_pipeline_fluent(self):
        result = simulate_pipeline(["pipeline:5,double,add(3)"])
        assert result == ["13"]


class TestComplexPipelines:
    def test_numeric_pipeline(self):
        result = pipe(
            double,       # 5 -> 10
            add(5),       # 10 -> 15
            square,       # 15 -> 225
            negate        # 225 -> -225
        )(5)
        assert result == -225

    def test_string_pipeline(self):
        result = pipe(
            strip,
            upper,
            prefix(">>> "),
            suffix(" <<<")
        )("  hello world  ")
        assert result == ">>> HELLO WORLD <<<"

    def test_list_pipeline(self):
        result = pipe(
            filter_list(is_even),
            map_list(double),
            take(2)
        )([1, 2, 3, 4, 5, 6])
        assert result == [4, 8]
