#!/usr/bin/env python3
"""UUID Example - UUID generation CLI."""

import argparse
import uuid


def cmd_uuid4(args):
    """Generate random UUID. Depyler: proven to terminate"""
    print(uuid.uuid4())


def cmd_uuid5(args):
    """Generate UUID5 from namespace+name. Depyler: proven to terminate"""
    ns = {"dns": uuid.NAMESPACE_DNS, "url": uuid.NAMESPACE_URL, "oid": uuid.NAMESPACE_OID}[
        args.namespace
    ]
    print(uuid.uuid5(ns, args.name))


def cmd_parse(args):
    """Parse UUID string. Depyler: proven to terminate"""
    u = uuid.UUID(args.uuid)
    print(f"Version: {u.version}")
    print(f"Variant: {u.variant}")
    print(f"Hex: {u.hex}")


def main():
    parser = argparse.ArgumentParser(description="UUID tool")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("uuid4")
    u5 = subs.add_parser("uuid5")
    u5.add_argument("--namespace", choices=["dns", "url", "oid"], required=True)
    u5.add_argument("--name", required=True)
    p = subs.add_parser("parse")
    p.add_argument("uuid")
    args = parser.parse_args()
    {"uuid4": cmd_uuid4, "uuid5": cmd_uuid5, "parse": cmd_parse}[args.command](args)


if __name__ == "__main__":
    main()
