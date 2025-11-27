#!/usr/bin/env python3
"""
Dataclass Example - Structured data CLI

Demonstrates:
- @dataclass decorator
- Type annotations
- Default values
- JSON serialization

This validates depyler's ability to transpile dataclasses
to Rust (struct with serde derive).
"""

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass
class Person:
    """A person record. Depyler: proven to terminate"""

    name: str
    age: int
    email: str = ""


def cmd_create(args):
    """Create a person record. Depyler: proven to terminate"""
    person = Person(name=args.name, age=args.age, email=args.email or "")

    if args.json:
        print(json.dumps(asdict(person)))
    else:
        print(f"Name: {person.name}")
        print(f"Age: {person.age}")
        if person.email:
            print(f"Email: {person.email}")


def main():
    """Main entry point. Depyler: proven to terminate"""
    parser = argparse.ArgumentParser(description="Structured data tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create person record")
    create_parser.add_argument("--name", required=True, help="Person name")
    create_parser.add_argument("--age", type=int, required=True, help="Person age")
    create_parser.add_argument("--email", help="Email address")
    create_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args)


if __name__ == "__main__":
    main()
