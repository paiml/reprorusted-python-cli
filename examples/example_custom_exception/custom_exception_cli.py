#!/usr/bin/env python3
"""Custom Exception CLI.

Custom exception classes with inheritance patterns.
"""

import argparse
import sys


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, field: str, message: str):
        super().__init__(f"{field}: {message}", code=400)
        self.field = field


class NotFoundError(AppError):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} '{identifier}' not found", code=404)
        self.resource = resource
        self.identifier = identifier


class AuthenticationError(AppError):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code=401)


class AuthorizationError(AppError):
    """Authorization error."""

    def __init__(self, action: str, resource: str):
        super().__init__(f"Not authorized to {action} {resource}", code=403)
        self.action = action
        self.resource = resource


class RateLimitError(AppError):
    """Rate limit exceeded error."""

    def __init__(self, limit: int, window: int):
        super().__init__(f"Rate limit {limit} per {window}s exceeded", code=429)
        self.limit = limit
        self.window = window


def validate_username(username: str) -> str:
    """Validate username format."""
    if len(username) < 3:
        raise ValidationError("username", "must be at least 3 characters")
    if len(username) > 20:
        raise ValidationError("username", "must be at most 20 characters")
    if not username.isalnum():
        raise ValidationError("username", "must be alphanumeric")
    return username


def validate_email(email: str) -> str:
    """Validate email format."""
    if "@" not in email:
        raise ValidationError("email", "must contain @")
    parts = email.split("@")
    if len(parts) != 2:
        raise ValidationError("email", "invalid format")
    if not parts[0] or not parts[1]:
        raise ValidationError("email", "missing local or domain part")
    return email


def validate_age(age: int) -> int:
    """Validate age value."""
    if age < 0:
        raise ValidationError("age", "cannot be negative")
    if age > 150:
        raise ValidationError("age", "unrealistic value")
    return age


def validate_password(password: str) -> str:
    """Validate password strength."""
    if len(password) < 8:
        raise ValidationError("password", "must be at least 8 characters")
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_upper and has_lower and has_digit):
        raise ValidationError("password", "must have upper, lower, and digit")
    return password


def find_user(users: dict[str, str], user_id: str) -> str:
    """Find user by ID."""
    if user_id not in users:
        raise NotFoundError("User", user_id)
    return users[user_id]


def find_item(items: dict[int, str], item_id: int) -> str:
    """Find item by ID."""
    if item_id not in items:
        raise NotFoundError("Item", str(item_id))
    return items[item_id]


def authenticate(token: str, valid_tokens: list[str]) -> bool:
    """Authenticate with token."""
    if token not in valid_tokens:
        raise AuthenticationError("Invalid token")
    return True


def authorize_action(user_role: str, required_role: str, action: str, resource: str) -> bool:
    """Authorize user action."""
    roles = ["guest", "user", "admin"]
    if roles.index(user_role) < roles.index(required_role):
        raise AuthorizationError(action, resource)
    return True


def check_rate_limit(count: int, limit: int, window: int) -> bool:
    """Check if rate limit exceeded."""
    if count > limit:
        raise RateLimitError(limit, window)
    return True


def safe_validate_username(username: str) -> tuple[bool, str]:
    """Safely validate username, return status and message."""
    try:
        validate_username(username)
        return (True, "valid")
    except ValidationError as e:
        return (False, e.message)


def safe_find_user(users: dict[str, str], user_id: str) -> str | None:
    """Safely find user, return None if not found."""
    try:
        return find_user(users, user_id)
    except NotFoundError:
        return None


def get_error_code(error: AppError) -> int:
    """Get error code from exception."""
    return error.code


def format_error(error: AppError) -> str:
    """Format error for display."""
    return f"[{error.code}] {error.message}"


def handle_validation_errors(fields: dict[str, str]) -> list[str]:
    """Validate multiple fields, collect errors."""
    errors: list[str] = []
    if "username" in fields:
        try:
            validate_username(fields["username"])
        except ValidationError as e:
            errors.append(e.message)
    if "email" in fields:
        try:
            validate_email(fields["email"])
        except ValidationError as e:
            errors.append(e.message)
    return errors


def validate_registration(username: str, email: str, password: str) -> dict[str, str]:
    """Validate registration data, raise first error."""
    validate_username(username)
    validate_email(email)
    validate_password(password)
    return {"username": username, "email": email, "status": "valid"}


def try_authenticate_and_authorize(
    token: str, valid_tokens: list[str], user_role: str, required_role: str
) -> str:
    """Try to authenticate and authorize."""
    try:
        authenticate(token, valid_tokens)
        authorize_action(user_role, required_role, "access", "resource")
        return "success"
    except AuthenticationError:
        return "auth_failed"
    except AuthorizationError:
        return "not_authorized"


def main() -> int:
    parser = argparse.ArgumentParser(description="Custom exception CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # validate
    val_p = subparsers.add_parser("validate", help="Validate input")
    val_p.add_argument("--username")
    val_p.add_argument("--email")
    val_p.add_argument("--password")

    # find
    find_p = subparsers.add_parser("find", help="Find resource")
    find_p.add_argument("resource")
    find_p.add_argument("id")

    # auth
    auth_p = subparsers.add_parser("auth", help="Authenticate")
    auth_p.add_argument("token")

    args = parser.parse_args()

    if args.command == "validate":
        try:
            if args.username:
                validate_username(args.username)
                print(f"Username '{args.username}' is valid")
            if args.email:
                validate_email(args.email)
                print(f"Email '{args.email}' is valid")
            if args.password:
                validate_password(args.password)
                print("Password is valid")
        except ValidationError as e:
            print(f"Validation error: {e.message}")
            return 1

    elif args.command == "find":
        try:
            users = {"1": "alice", "2": "bob"}
            result = find_user(users, args.id)
            print(f"Found: {result}")
        except NotFoundError as e:
            print(f"Not found: {e.message}")
            return 1

    elif args.command == "auth":
        try:
            valid = ["token123", "token456"]
            authenticate(args.token, valid)
            print("Authentication successful")
        except AuthenticationError as e:
            print(f"Auth error: {e.message}")
            return 1

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
