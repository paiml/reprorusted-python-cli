"""Lens/Optics CLI.

Demonstrates functional lenses for immutable data access and modification.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any, Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")
S = TypeVar("S")
T = TypeVar("T")


@dataclass(frozen=True)
class Lens(Generic[S, A]):
    """A lens focuses on a part of a data structure.

    Provides get and set operations for immutable updates.
    """

    getter: Callable[[S], A]
    setter: Callable[[S, A], S]

    def get(self, s: S) -> A:
        """Get the focused value."""
        return self.getter(s)

    def set(self, s: S, a: A) -> S:
        """Set the focused value, returning new structure."""
        return self.setter(s, a)

    def modify(self, s: S, f: Callable[[A], A]) -> S:
        """Modify the focused value with a function."""
        return self.set(s, f(self.get(s)))

    def compose(self, other: "Lens[A, B]") -> "Lens[S, B]":
        """Compose two lenses."""
        return Lens(
            getter=lambda s: other.get(self.get(s)),
            setter=lambda s, b: self.set(s, other.set(self.get(s), b)),
        )

    def __rshift__(self, other: "Lens[A, B]") -> "Lens[S, B]":
        """Compose lenses using >> operator."""
        return self.compose(other)


# Lens constructors for common cases
def attr_lens(name: str) -> Lens[Any, Any]:
    """Create a lens for a dataclass attribute."""
    return Lens(
        getter=lambda obj: getattr(obj, name), setter=lambda obj, val: replace(obj, **{name: val})
    )


def index_lens(idx: int) -> Lens[list[A], A]:
    """Create a lens for a list index."""

    def set_index(lst: list[A], val: A) -> list[A]:
        result = list(lst)
        result[idx] = val
        return result

    return Lens(getter=lambda lst: lst[idx], setter=set_index)


def key_lens(key: str) -> Lens[dict[str, A], A]:
    """Create a lens for a dict key."""

    def set_key(d: dict[str, A], val: A) -> dict[str, A]:
        result = dict(d)
        result[key] = val
        return result

    return Lens(getter=lambda d: d[key], setter=set_key)


# Example data structures
@dataclass(frozen=True)
class Address:
    """Address data."""

    street: str
    city: str
    zip_code: str


@dataclass(frozen=True)
class Person:
    """Person data."""

    name: str
    age: int
    address: Address


@dataclass(frozen=True)
class Company:
    """Company data."""

    name: str
    ceo: Person


# Pre-defined lenses
person_name: Lens[Person, str] = attr_lens("name")
person_age: Lens[Person, int] = attr_lens("age")
person_address: Lens[Person, Address] = attr_lens("address")

address_street: Lens[Address, str] = attr_lens("street")
address_city: Lens[Address, str] = attr_lens("city")
address_zip: Lens[Address, str] = attr_lens("zip_code")

company_name: Lens[Company, str] = attr_lens("name")
company_ceo: Lens[Company, Person] = attr_lens("ceo")

# Composed lenses
person_city: Lens[Person, str] = person_address >> address_city
person_street: Lens[Person, str] = person_address >> address_street
ceo_name: Lens[Company, str] = company_ceo >> person_name
ceo_city: Lens[Company, str] = company_ceo >> person_address >> address_city


# Prism for optional values
@dataclass(frozen=True)
class Prism(Generic[S, A]):
    """A prism focuses on a part that may not exist."""

    getter: Callable[[S], A | None]
    setter: Callable[[A], S]

    def get_option(self, s: S) -> A | None:
        """Try to get the focused value."""
        return self.getter(s)

    def review(self, a: A) -> S:
        """Build the structure from the focused value."""
        return self.setter(a)

    def modify_option(self, s: S, f: Callable[[A], A]) -> S | None:
        """Try to modify the focused value."""
        val = self.get_option(s)
        if val is not None:
            return self.review(f(val))
        return None


# Iso for bidirectional transformations
@dataclass(frozen=True)
class Iso(Generic[S, A]):
    """An isomorphism is a reversible transformation."""

    forward: Callable[[S], A]
    backward: Callable[[A], S]

    def get(self, s: S) -> A:
        """Transform forward."""
        return self.forward(s)

    def reverse_get(self, a: A) -> S:
        """Transform backward."""
        return self.backward(a)

    def modify(self, s: S, f: Callable[[A], A]) -> S:
        """Modify through the iso."""
        return self.backward(f(self.forward(s)))

    def reverse(self) -> "Iso[A, S]":
        """Reverse the iso."""
        return Iso(self.backward, self.forward)


# Common isos
celsius_fahrenheit: Iso[float, float] = Iso(
    forward=lambda c: c * 9 / 5 + 32, backward=lambda f: (f - 32) * 5 / 9
)

string_list: Iso[str, list[str]] = Iso(forward=lambda s: list(s), backward=lambda lst: "".join(lst))


def lens_path(*keys: str) -> Lens[dict, Any]:
    """Create a lens from a path of keys."""
    if not keys:
        return Lens(lambda d: d, lambda d, v: v)

    first, *rest = keys
    first_lens = key_lens(first)
    if not rest:
        return first_lens
    return first_lens.compose(lens_path(*rest))


def simulate_lens(operations: list[str]) -> list[str]:
    """Simulate lens operations."""
    results: list[str] = []

    # Create sample data
    addr = Address("123 Main St", "Boston", "02101")
    person = Person("Alice", 30, addr)
    company = Company("TechCorp", person)

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "get_name":
            results.append(person_name.get(person))
        elif cmd == "get_city":
            results.append(person_city.get(person))
        elif cmd == "set_name":
            new_person = person_name.set(person, parts[1])
            results.append(new_person.name)
        elif cmd == "set_city":
            new_person = person_city.set(person, parts[1])
            results.append(new_person.address.city)
        elif cmd == "modify_age":
            delta = int(parts[1])
            new_person = person_age.modify(person, lambda x, d=delta: x + d)
            results.append(str(new_person.age))
        elif cmd == "ceo_name":
            results.append(ceo_name.get(company))
        elif cmd == "ceo_city":
            results.append(ceo_city.get(company))
        elif cmd == "celsius_to_fahrenheit":
            f = celsius_fahrenheit.get(float(parts[1]))
            results.append(f"{f:.1f}")
        elif cmd == "fahrenheit_to_celsius":
            c = celsius_fahrenheit.reverse().get(float(parts[1]))
            results.append(f"{c:.1f}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: func_lens_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    addr = Address("123 Main St", "Boston", "02101")
    person = Person("Alice", 30, addr)

    if cmd == "get":
        lens_name = sys.argv[2] if len(sys.argv) > 2 else "name"
        if lens_name == "name":
            print(f"Name: {person_name.get(person)}")
        elif lens_name == "city":
            print(f"City: {person_city.get(person)}")
    elif cmd == "set" and len(sys.argv) > 3:
        lens_name = sys.argv[2]
        value = sys.argv[3]
        if lens_name == "name":
            new_person = person_name.set(person, value)
            print(f"New name: {new_person.name}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
