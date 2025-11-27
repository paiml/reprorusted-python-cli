"""Tests for func_lens_cli.py"""

import pytest
from func_lens_cli import (
    Address,
    Company,
    Iso,
    Lens,
    Person,
    Prism,
    attr_lens,
    celsius_fahrenheit,
    ceo_city,
    ceo_name,
    index_lens,
    key_lens,
    lens_path,
    person_age,
    person_city,
    person_name,
    person_street,
    simulate_lens,
    string_list,
)


class TestLens:
    def test_get(self):
        lens = Lens(lambda x: x[0], lambda x, v: [v] + x[1:])
        assert lens.get([1, 2, 3]) == 1

    def test_set(self):
        lens = Lens(lambda x: x[0], lambda x, v: [v] + x[1:])
        assert lens.set([1, 2, 3], 10) == [10, 2, 3]

    def test_modify(self):
        lens = Lens(lambda x: x[0], lambda x, v: [v] + x[1:])
        assert lens.modify([1, 2, 3], lambda x: x * 2) == [2, 2, 3]

    def test_compose(self):
        # Lens focusing on first element
        first = Lens(lambda x: x[0], lambda x, v: [v] + x[1:])
        # Lens focusing on "value" key
        value_lens = key_lens("value")

        composed = first.compose(value_lens)
        data = [{"value": 10}, {"value": 20}]

        assert composed.get(data) == 10
        assert composed.set(data, 100) == [{"value": 100}, {"value": 20}]

    def test_rshift_compose(self):
        first = index_lens(0)
        value_lens = key_lens("value")

        composed = first >> value_lens
        data = [{"value": 10}, {"value": 20}]

        assert composed.get(data) == 10


class TestAttrLens:
    def test_get(self):
        addr = Address("123 Main", "Boston", "02101")
        lens = attr_lens("city")
        assert lens.get(addr) == "Boston"

    def test_set(self):
        addr = Address("123 Main", "Boston", "02101")
        lens = attr_lens("city")
        new_addr = lens.set(addr, "Cambridge")
        assert new_addr.city == "Cambridge"
        assert addr.city == "Boston"  # Original unchanged


class TestIndexLens:
    def test_get(self):
        lens = index_lens(1)
        assert lens.get([10, 20, 30]) == 20

    def test_set(self):
        lens = index_lens(1)
        result = lens.set([10, 20, 30], 200)
        assert result == [10, 200, 30]

    def test_modify(self):
        lens = index_lens(0)
        result = lens.modify([5, 10, 15], lambda x: x * 2)
        assert result == [10, 10, 15]


class TestKeyLens:
    def test_get(self):
        lens = key_lens("name")
        assert lens.get({"name": "Alice", "age": 30}) == "Alice"

    def test_set(self):
        lens = key_lens("name")
        result = lens.set({"name": "Alice", "age": 30}, "Bob")
        assert result == {"name": "Bob", "age": 30}

    def test_modify(self):
        lens = key_lens("count")
        result = lens.modify({"count": 5}, lambda x: x + 1)
        assert result == {"count": 6}


class TestAddress:
    def test_create(self):
        addr = Address("123 Main", "Boston", "02101")
        assert addr.street == "123 Main"
        assert addr.city == "Boston"
        assert addr.zip_code == "02101"

    def test_immutable(self):
        addr = Address("123 Main", "Boston", "02101")
        with pytest.raises(Exception):  # FrozenInstanceError
            addr.city = "Cambridge"  # type: ignore


class TestPerson:
    def test_create(self):
        addr = Address("123 Main", "Boston", "02101")
        person = Person("Alice", 30, addr)
        assert person.name == "Alice"
        assert person.age == 30
        assert person.address == addr


class TestPersonLenses:
    def test_person_name_get(self):
        addr = Address("123 Main", "Boston", "02101")
        person = Person("Alice", 30, addr)
        assert person_name.get(person) == "Alice"

    def test_person_name_set(self):
        addr = Address("123 Main", "Boston", "02101")
        person = Person("Alice", 30, addr)
        new_person = person_name.set(person, "Bob")
        assert new_person.name == "Bob"
        assert person.name == "Alice"

    def test_person_age_modify(self):
        addr = Address("123 Main", "Boston", "02101")
        person = Person("Alice", 30, addr)
        new_person = person_age.modify(person, lambda a: a + 1)
        assert new_person.age == 31


class TestComposedLenses:
    def test_person_city_get(self):
        addr = Address("123 Main", "Boston", "02101")
        person = Person("Alice", 30, addr)
        assert person_city.get(person) == "Boston"

    def test_person_city_set(self):
        addr = Address("123 Main", "Boston", "02101")
        person = Person("Alice", 30, addr)
        new_person = person_city.set(person, "Cambridge")
        assert new_person.address.city == "Cambridge"
        assert person.address.city == "Boston"

    def test_person_street_get(self):
        addr = Address("123 Main", "Boston", "02101")
        person = Person("Alice", 30, addr)
        assert person_street.get(person) == "123 Main"


class TestCompanyLenses:
    def test_ceo_name_get(self):
        addr = Address("123 Main", "Boston", "02101")
        ceo = Person("Alice", 30, addr)
        company = Company("TechCorp", ceo)
        assert ceo_name.get(company) == "Alice"

    def test_ceo_name_set(self):
        addr = Address("123 Main", "Boston", "02101")
        ceo = Person("Alice", 30, addr)
        company = Company("TechCorp", ceo)
        new_company = ceo_name.set(company, "Bob")
        assert new_company.ceo.name == "Bob"

    def test_ceo_city_get(self):
        addr = Address("123 Main", "Boston", "02101")
        ceo = Person("Alice", 30, addr)
        company = Company("TechCorp", ceo)
        assert ceo_city.get(company) == "Boston"

    def test_ceo_city_set(self):
        addr = Address("123 Main", "Boston", "02101")
        ceo = Person("Alice", 30, addr)
        company = Company("TechCorp", ceo)
        new_company = ceo_city.set(company, "NYC")
        assert new_company.ceo.address.city == "NYC"


class TestPrism:
    def test_get_option_some(self):
        prism = Prism(
            getter=lambda x: x if x > 0 else None,
            setter=lambda x: x
        )
        assert prism.get_option(5) == 5

    def test_get_option_none(self):
        prism = Prism(
            getter=lambda x: x if x > 0 else None,
            setter=lambda x: x
        )
        assert prism.get_option(-5) is None

    def test_review(self):
        prism = Prism(
            getter=lambda x: x if x > 0 else None,
            setter=lambda x: x
        )
        assert prism.review(10) == 10


class TestIso:
    def test_get(self):
        iso = Iso(lambda x: x * 2, lambda x: x // 2)
        assert iso.get(5) == 10

    def test_reverse_get(self):
        iso = Iso(lambda x: x * 2, lambda x: x // 2)
        assert iso.reverse_get(10) == 5

    def test_modify(self):
        iso = Iso(lambda x: x * 2, lambda x: x // 2)
        result = iso.modify(5, lambda x: x + 2)
        assert result == 6  # 5 -> 10 -> 12 -> 6

    def test_reverse(self):
        iso = Iso(lambda x: x * 2, lambda x: x // 2)
        reversed_iso = iso.reverse()
        assert reversed_iso.get(10) == 5
        assert reversed_iso.reverse_get(5) == 10


class TestCelsiusFahrenheit:
    def test_celsius_to_fahrenheit(self):
        assert celsius_fahrenheit.get(0) == 32
        assert celsius_fahrenheit.get(100) == 212

    def test_fahrenheit_to_celsius(self):
        assert celsius_fahrenheit.reverse_get(32) == 0
        assert abs(celsius_fahrenheit.reverse_get(212) - 100) < 0.01


class TestStringList:
    def test_string_to_list(self):
        assert string_list.get("hello") == ["h", "e", "l", "l", "o"]

    def test_list_to_string(self):
        assert string_list.reverse_get(["h", "e", "l", "l", "o"]) == "hello"


class TestLensPath:
    def test_single_key(self):
        lens = lens_path("name")
        data = {"name": "Alice", "age": 30}
        assert lens.get(data) == "Alice"

    def test_nested_keys(self):
        lens = lens_path("address", "city")
        data = {"address": {"city": "Boston", "zip": "02101"}}
        assert lens.get(data) == "Boston"

    def test_set_nested(self):
        lens = lens_path("address", "city")
        data = {"address": {"city": "Boston", "zip": "02101"}}
        result = lens.set(data, "Cambridge")
        assert result["address"]["city"] == "Cambridge"


class TestSimulateLens:
    def test_get_name(self):
        result = simulate_lens(["get_name:"])
        assert result == ["Alice"]

    def test_get_city(self):
        result = simulate_lens(["get_city:"])
        assert result == ["Boston"]

    def test_set_name(self):
        result = simulate_lens(["set_name:Bob"])
        assert result == ["Bob"]

    def test_set_city(self):
        result = simulate_lens(["set_city:Cambridge"])
        assert result == ["Cambridge"]

    def test_modify_age(self):
        result = simulate_lens(["modify_age:5"])
        assert result == ["35"]

    def test_ceo_name(self):
        result = simulate_lens(["ceo_name:"])
        assert result == ["Alice"]

    def test_ceo_city(self):
        result = simulate_lens(["ceo_city:"])
        assert result == ["Boston"]

    def test_celsius_to_fahrenheit(self):
        result = simulate_lens(["celsius_to_fahrenheit:0"])
        assert result == ["32.0"]

    def test_fahrenheit_to_celsius(self):
        result = simulate_lens(["fahrenheit_to_celsius:32"])
        assert result == ["0.0"]
