"""Tests for func_curry_cli.py"""


from func_curry_cli import (
    Curried,
    add,
    clamp,
    compose,
    concat,
    const,
    curry,
    curry2,
    curry3,
    divide,
    drop,
    ends_with,
    equals,
    filter_func,
    flip,
    greater_than,
    identity,
    invoke,
    join,
    less_than,
    map_func,
    modulo,
    multiply,
    nth,
    partial_left,
    partial_right,
    pipe,
    power,
    prop,
    reduce_func,
    replace,
    simulate_curry,
    split,
    starts_with,
    subtract,
    take,
    uncurry2,
    uncurry3,
)


class TestCurry2:
    def test_basic(self):
        def add_uncurried(a, b):
            return a + b

        curried = curry2(add_uncurried)
        assert curried(2)(3) == 5

    def test_partial_application(self):
        def multiply_uncurried(a, b):
            return a * b

        curried = curry2(multiply_uncurried)
        double = curried(2)
        assert double(5) == 10
        assert double(7) == 14


class TestCurry3:
    def test_basic(self):
        def add3(a, b, c):
            return a + b + c

        curried = curry3(add3)
        assert curried(1)(2)(3) == 6

    def test_partial_applications(self):
        def add3(a, b, c):
            return a + b + c

        curried = curry3(add3)
        add_1 = curried(1)
        add_1_2 = add_1(2)
        assert add_1_2(3) == 6


class TestUncurry2:
    def test_basic(self):
        def curried(a):
            return lambda b: a + b
        uncurried = uncurry2(curried)
        assert uncurried(2, 3) == 5


class TestUncurry3:
    def test_basic(self):
        def curried(a):
            return lambda b: lambda c: a + b + c
        uncurried = uncurry3(curried)
        assert uncurried(1, 2, 3) == 6


class TestCurried:
    def test_create(self):
        c = Curried(lambda a, b: a + b, 2)
        assert c.arity == 2
        assert c.args == ()

    def test_single_arg(self):
        c = Curried(lambda a, b: a + b, 2)
        result = c(5)
        assert isinstance(result, Curried)
        assert result.args == (5,)

    def test_all_args(self):
        c = Curried(lambda a, b: a + b, 2)
        result = c(5)(3)
        assert result == 8

    def test_multiple_args_at_once(self):
        c = Curried(lambda a, b, c: a + b + c, 3)
        result = c(1, 2)(3)
        assert result == 6


class TestCurryDecorator:
    def test_auto_arity(self):
        @curry
        def add_three(a, b, c):
            return a + b + c

        assert add_three(1)(2)(3) == 6

    def test_explicit_arity(self):
        def my_func(a, b):
            return a * b

        curried = curry(my_func, 2)
        assert curried(3)(4) == 12


class TestPartialRight:
    def test_basic(self):
        def subtract(a, b):
            return a - b

        sub_from_10 = partial_right(subtract, 10)
        assert sub_from_10(15) == 5  # 15 - 10


class TestPartialLeft:
    def test_basic(self):
        def subtract(a, b):
            return a - b

        sub_10 = partial_left(subtract, 10)
        assert sub_10(3) == 7  # 10 - 3


class TestFlip:
    def test_basic(self):
        def subtract(a, b):
            return a - b

        flipped = flip(subtract)
        assert subtract(10, 3) == 7
        assert flipped(10, 3) == -7


class TestConst:
    def test_basic(self):
        always_5 = const(5)
        assert always_5() == 5
        assert always_5(10) == 5
        assert always_5(1, 2, 3, key="value") == 5


class TestIdentity:
    def test_basic(self):
        assert identity(5) == 5
        assert identity("hello") == "hello"
        assert identity([1, 2, 3]) == [1, 2, 3]


class TestAdd:
    def test_curried(self):
        assert add(2)(3) == 5

    def test_partial(self):
        add_5 = add(5)
        assert add_5(10) == 15


class TestSubtract:
    def test_curried(self):
        assert subtract(10)(3) == 7

    def test_partial(self):
        sub_from_100 = subtract(100)
        assert sub_from_100(30) == 70


class TestMultiply:
    def test_curried(self):
        assert multiply(3)(4) == 12

    def test_partial(self):
        double = multiply(2)
        assert double(5) == 10


class TestDivide:
    def test_curried(self):
        assert divide(10.0)(2.0) == 5.0


class TestModulo:
    def test_curried(self):
        assert modulo(10)(3) == 1


class TestPower:
    def test_curried(self):
        assert power(2.0)(3.0) == 8.0


class TestConcat:
    def test_curried(self):
        assert concat("hello ")("world") == "hello world"


class TestSplit:
    def test_curried(self):
        split_comma = split(",")
        assert split_comma("a,b,c") == ["a", "b", "c"]


class TestJoin:
    def test_curried(self):
        join_dash = join("-")
        assert join_dash(["a", "b", "c"]) == "a-b-c"


class TestReplace:
    def test_curried(self):
        replace_a = replace("a", "X")
        assert replace_a("banana") == "bXnXnX"


class TestStartsWith:
    def test_curried(self):
        starts_hello = starts_with("hello")
        assert starts_hello("hello world")
        assert not starts_hello("world hello")


class TestEndsWith:
    def test_curried(self):
        ends_txt = ends_with(".txt")
        assert ends_txt("file.txt")
        assert not ends_txt("file.py")


class TestMapFunc:
    def test_curried(self):
        double = multiply(2)
        double_all = map_func(double)
        assert double_all([1, 2, 3]) == [2, 4, 6]


class TestFilterFunc:
    def test_curried(self):
        def is_even(x):
            return x % 2 == 0
        filter_even = filter_func(is_even)
        assert filter_even([1, 2, 3, 4, 5]) == [2, 4]


class TestReduceFunc:
    def test_curried(self):
        def sum_fn(a, b):
            return a + b
        sum_from_0 = reduce_func(sum_fn)(0)
        assert sum_from_0([1, 2, 3, 4]) == 10


class TestTake:
    def test_curried(self):
        take_3 = take(3)
        assert take_3([1, 2, 3, 4, 5]) == [1, 2, 3]


class TestDrop:
    def test_curried(self):
        drop_2 = drop(2)
        assert drop_2([1, 2, 3, 4, 5]) == [3, 4, 5]


class TestNth:
    def test_curried(self):
        second = nth(1)
        assert second([10, 20, 30]) == 20


class TestEquals:
    def test_curried(self):
        is_5 = equals(5)
        assert is_5(5)
        assert not is_5(3)


class TestGreaterThan:
    def test_curried(self):
        gt_5 = greater_than(5)
        assert gt_5(10)
        assert not gt_5(3)


class TestLessThan:
    def test_curried(self):
        lt_5 = less_than(5)
        assert lt_5(3)
        assert not lt_5(10)


class TestClamp:
    def test_curried(self):
        clamp_0_100 = clamp(0.0)(100.0)
        assert clamp_0_100(50.0) == 50.0
        assert clamp_0_100(-10.0) == 0.0
        assert clamp_0_100(150.0) == 100.0


class TestCompose:
    def test_basic(self):
        double = multiply(2)
        add_1 = add(1)
        # compose applies right to left
        f = compose(double, add_1)  # double(add_1(x))
        assert f(5) == 12  # (5+1)*2

    def test_three_functions(self):
        double = multiply(2)
        add_1 = add(1)
        def square(x):
            return x * x
        f = compose(square, double, add_1)  # square(double(add_1(x)))
        assert f(3) == 64  # ((3+1)*2)^2


class TestPipe:
    def test_basic(self):
        double = multiply(2)
        add_1 = add(1)
        # pipe applies left to right
        f = pipe(double, add_1)  # add_1(double(x))
        assert f(5) == 11  # (5*2)+1

    def test_three_functions(self):
        double = multiply(2)
        add_1 = add(1)
        def square(x):
            return x * x
        f = pipe(add_1, double, square)  # square(double(add_1(x)))
        assert f(3) == 64


class TestProp:
    def test_dict(self):
        get_name = prop("name")
        assert get_name({"name": "Alice"}) == "Alice"


class TestInvoke:
    def test_basic(self):
        upper = invoke("upper")
        assert upper("hello") == "HELLO"


class TestSimulateCurry:
    def test_add(self):
        result = simulate_curry(["add:2,3"])
        assert result == ["5"]

    def test_multiply(self):
        result = simulate_curry(["multiply:3,4"])
        assert result == ["12"]

    def test_add_partial(self):
        result = simulate_curry(["add_partial:5,10"])
        assert result == ["15"]

    def test_compose(self):
        result = simulate_curry(["compose:5"])
        # double(add5(5)) = double(10) = 20
        assert result == ["20"]

    def test_pipe(self):
        result = simulate_curry(["pipe:5"])
        # add5(double(5)) = add5(10) = 15
        assert result == ["15"]

    def test_map_double(self):
        result = simulate_curry(["map_double:1,2,3"])
        assert result == ["[2, 4, 6]"]

    def test_filter_positive(self):
        result = simulate_curry(["filter_positive:-2,-1,0,1,2"])
        assert result == ["[1, 2]"]

    def test_clamp(self):
        result = simulate_curry(["clamp:0,100,150"])
        assert result == ["100.0"]

    def test_split_join(self):
        result = simulate_curry(["split_join:a,b,c"])
        assert result == ["a-b-c"]
