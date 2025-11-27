#!/usr/bin/env python3
"""Secrets Example - Cryptographic random CLI."""

import argparse
import secrets
import string


def cmd_token(args):
    """Generate secure token. Depyler: proven to terminate"""
    if args.type == "hex":
        print(secrets.token_hex(args.bytes))
    elif args.type == "url":
        print(secrets.token_urlsafe(args.bytes))
    else:
        print(secrets.token_bytes(args.bytes).hex())


def cmd_password(args):
    """Generate secure password. Depyler: proven to terminate"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(alphabet) for _ in range(args.length))
    print(password)


def cmd_randbelow(args):
    """Generate random int below n. Depyler: proven to terminate"""
    print(secrets.randbelow(args.n))


def main():
    parser = argparse.ArgumentParser(description="Secure random tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    token = subparsers.add_parser("token")
    token.add_argument("--type", choices=["hex", "url", "bytes"], default="hex")
    token.add_argument("--bytes", type=int, default=32)

    pwd = subparsers.add_parser("password")
    pwd.add_argument("--length", type=int, default=16)

    rand = subparsers.add_parser("randbelow")
    rand.add_argument("n", type=int)

    args = parser.parse_args()
    {"token": cmd_token, "password": cmd_password, "randbelow": cmd_randbelow}[args.command](args)


if __name__ == "__main__":
    main()
