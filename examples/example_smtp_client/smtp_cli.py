#!/usr/bin/env python3
"""SMTP Protocol CLI.

Parse and encode SMTP protocol messages.
"""

import argparse
import base64
import sys
from dataclasses import dataclass, field
from enum import Enum


class SMTPState(Enum):
    """SMTP connection states."""

    INIT = "init"
    GREETED = "greeted"
    AUTHENTICATED = "authenticated"
    MAIL_FROM = "mail_from"
    RCPT_TO = "rcpt_to"
    DATA = "data"
    QUIT = "quit"


@dataclass
class SMTPCommand:
    """SMTP command."""

    verb: str
    args: str = ""

    def encode(self) -> bytes:
        """Encode command to bytes."""
        if self.args:
            return f"{self.verb} {self.args}\r\n".encode()
        return f"{self.verb}\r\n".encode()


@dataclass
class SMTPResponse:
    """SMTP response."""

    code: int
    message: str
    is_multiline: bool = False
    lines: list[str] = field(default_factory=list)


@dataclass
class EmailMessage:
    """Email message structure."""

    from_addr: str
    to_addrs: list[str]
    subject: str
    body: str
    headers: dict[str, str] = field(default_factory=dict)


# SMTP response codes
SMTP_CODES = {
    211: "System status",
    214: "Help message",
    220: "Service ready",
    221: "Service closing",
    235: "Authentication successful",
    250: "OK",
    251: "User not local; will forward",
    252: "Cannot VRFY user",
    334: "Server challenge",
    354: "Start mail input",
    421: "Service not available",
    450: "Mailbox unavailable",
    451: "Local error",
    452: "Insufficient storage",
    500: "Syntax error",
    501: "Syntax error in parameters",
    502: "Command not implemented",
    503: "Bad sequence of commands",
    504: "Parameter not implemented",
    550: "Mailbox unavailable",
    551: "User not local",
    552: "Storage exceeded",
    553: "Mailbox name not allowed",
    554: "Transaction failed",
}


def parse_response(data: bytes) -> SMTPResponse:
    """Parse SMTP response from bytes."""
    text = data.decode("utf-8", errors="replace")
    lines = text.strip().split("\r\n")

    if not lines:
        raise ValueError("Empty response")

    # Parse first line
    first_line = lines[0]
    if len(first_line) < 3:
        raise ValueError("Invalid response format")

    code = int(first_line[:3])
    is_multiline = len(first_line) > 3 and first_line[3] == "-"

    all_lines = []
    for line in lines:
        if len(line) > 4:
            all_lines.append(line[4:])
        elif len(line) > 3:
            all_lines.append(line[4:] if len(line) > 4 else "")

    message = all_lines[0] if all_lines else ""

    return SMTPResponse(code=code, message=message, is_multiline=is_multiline, lines=all_lines)


def encode_response(code: int, message: str, multiline: list[str] | None = None) -> bytes:
    """Encode SMTP response to bytes."""
    if multiline:
        lines = []
        for _i, line in enumerate(multiline[:-1]):
            lines.append(f"{code}-{line}")
        lines.append(f"{code} {multiline[-1]}")
        return ("\r\n".join(lines) + "\r\n").encode("utf-8")

    return f"{code} {message}\r\n".encode()


def parse_command(data: bytes) -> SMTPCommand:
    """Parse SMTP command from bytes."""
    text = data.decode("utf-8", errors="replace").strip()

    if " " in text:
        verb, args = text.split(" ", 1)
    else:
        verb = text
        args = ""

    return SMTPCommand(verb=verb.upper(), args=args)


def validate_email(email: str) -> bool:
    """Basic email validation."""
    if not email or "@" not in email:
        return False

    parts = email.split("@")
    if len(parts) != 2:
        return False

    local, domain = parts
    if not local or not domain:
        return False

    if "." not in domain:
        return False

    return True


def extract_email(address: str) -> str:
    """Extract email from address format like '<user@example.com>'."""
    address = address.strip()

    if address.startswith("<") and address.endswith(">"):
        return address[1:-1]

    return address


def format_email(email: str) -> str:
    """Format email in angle bracket notation."""
    email = extract_email(email)
    return f"<{email}>"


def encode_auth_plain(username: str, password: str) -> str:
    """Encode credentials for AUTH PLAIN."""
    # Format: \0username\0password
    auth_string = f"\0{username}\0{password}"
    return base64.b64encode(auth_string.encode("utf-8")).decode("ascii")


def decode_auth_plain(encoded: str) -> tuple[str, str]:
    """Decode AUTH PLAIN credentials."""
    decoded = base64.b64decode(encoded).decode("utf-8")
    parts = decoded.split("\0")

    if len(parts) != 3:
        raise ValueError("Invalid AUTH PLAIN format")

    return parts[1], parts[2]  # username, password


def encode_auth_login(data: str) -> str:
    """Encode for AUTH LOGIN."""
    return base64.b64encode(data.encode("utf-8")).decode("ascii")


def decode_auth_login(encoded: str) -> str:
    """Decode AUTH LOGIN."""
    return base64.b64decode(encoded).decode("utf-8")


def build_message(message: EmailMessage) -> str:
    """Build raw email message content."""
    lines = []

    # Standard headers
    lines.append(f"From: {message.from_addr}")
    lines.append(f"To: {', '.join(message.to_addrs)}")
    lines.append(f"Subject: {message.subject}")

    # Custom headers
    for key, value in message.headers.items():
        lines.append(f"{key}: {value}")

    # Empty line before body
    lines.append("")

    # Body
    lines.append(message.body)

    return "\r\n".join(lines)


def parse_message(data: str) -> EmailMessage:
    """Parse raw email message content."""
    # Split headers and body
    parts = data.split("\r\n\r\n", 1)
    header_section = parts[0]
    body = parts[1] if len(parts) > 1 else ""

    headers = {}
    current_key = None
    current_value = ""

    for line in header_section.split("\r\n"):
        if line.startswith(" ") or line.startswith("\t"):
            # Continuation of previous header
            current_value += " " + line.strip()
        else:
            if current_key:
                headers[current_key] = current_value

            if ":" in line:
                current_key, current_value = line.split(":", 1)
                current_key = current_key.strip()
                current_value = current_value.strip()
            else:
                current_key = None

    if current_key:
        headers[current_key] = current_value

    from_addr = headers.get("From", "")
    to_addrs = [addr.strip() for addr in headers.get("To", "").split(",")]
    subject = headers.get("Subject", "")

    # Remove standard headers from dict
    for key in ["From", "To", "Subject"]:
        headers.pop(key, None)

    return EmailMessage(
        from_addr=from_addr, to_addrs=to_addrs, subject=subject, body=body, headers=headers
    )


def escape_dot(line: str) -> str:
    """Escape leading dot for DATA command."""
    if line.startswith("."):
        return "." + line
    return line


def unescape_dot(line: str) -> str:
    """Unescape leading dot from DATA command."""
    if line.startswith(".."):
        return line[1:]
    return line


class SMTPSession:
    """SMTP session state machine."""

    def __init__(self, domain: str = "localhost"):
        self.state = SMTPState.INIT
        self.domain = domain
        self.mail_from: str | None = None
        self.rcpt_to: list[str] = []
        self.data_lines: list[str] = []
        self.authenticated = False

    def process_command(self, cmd: SMTPCommand) -> SMTPResponse:
        """Process command and return response."""
        verb = cmd.verb

        if verb == "HELO":
            self.state = SMTPState.GREETED
            return SMTPResponse(250, f"Hello {cmd.args}, pleased to meet you")

        if verb == "EHLO":
            self.state = SMTPState.GREETED
            return SMTPResponse(
                250,
                self.domain,
                is_multiline=True,
                lines=[self.domain, "AUTH PLAIN LOGIN", "SIZE 35882577", "8BITMIME"],
            )

        if verb == "AUTH":
            if self.state != SMTPState.GREETED:
                return SMTPResponse(503, "Bad sequence of commands")
            # Simplified - accept any auth
            self.authenticated = True
            self.state = SMTPState.AUTHENTICATED
            return SMTPResponse(235, "Authentication successful")

        if verb == "MAIL":
            if self.state not in (SMTPState.GREETED, SMTPState.AUTHENTICATED):
                return SMTPResponse(503, "Bad sequence of commands")
            self.mail_from = extract_email(cmd.args.replace("FROM:", "").strip())
            self.state = SMTPState.MAIL_FROM
            return SMTPResponse(250, "OK")

        if verb == "RCPT":
            if self.state not in (SMTPState.MAIL_FROM, SMTPState.RCPT_TO):
                return SMTPResponse(503, "Bad sequence of commands")
            rcpt = extract_email(cmd.args.replace("TO:", "").strip())
            self.rcpt_to.append(rcpt)
            self.state = SMTPState.RCPT_TO
            return SMTPResponse(250, "OK")

        if verb == "DATA":
            if self.state != SMTPState.RCPT_TO:
                return SMTPResponse(503, "Bad sequence of commands")
            self.state = SMTPState.DATA
            return SMTPResponse(354, "End data with <CR><LF>.<CR><LF>")

        if verb == "RSET":
            self.mail_from = None
            self.rcpt_to = []
            self.data_lines = []
            self.state = SMTPState.GREETED if self.state != SMTPState.INIT else SMTPState.INIT
            return SMTPResponse(250, "OK")

        if verb == "NOOP":
            return SMTPResponse(250, "OK")

        if verb == "QUIT":
            self.state = SMTPState.QUIT
            return SMTPResponse(221, f"{self.domain} closing connection")

        return SMTPResponse(500, f"Command not recognized: {verb}")

    def reset(self) -> None:
        """Reset transaction state."""
        self.mail_from = None
        self.rcpt_to = []
        self.data_lines = []


def main() -> int:
    parser = argparse.ArgumentParser(description="SMTP protocol parser")
    parser.add_argument(
        "--mode",
        choices=["command", "response", "message", "auth", "session"],
        default="command",
        help="Operation mode",
    )
    parser.add_argument("--verb", default="EHLO", help="SMTP command verb")
    parser.add_argument("--args", default="", help="Command arguments")
    parser.add_argument("--code", type=int, default=250, help="Response code")
    parser.add_argument("--from", dest="from_addr", help="From address")
    parser.add_argument("--to", dest="to_addr", help="To address")
    parser.add_argument("--subject", default="Test", help="Subject")
    parser.add_argument("--body", default="Hello!", help="Body")
    parser.add_argument("--username", help="Username for auth")
    parser.add_argument("--password", help="Password for auth")

    args = parser.parse_args()

    if args.mode == "command":
        cmd = SMTPCommand(verb=args.verb, args=args.args)
        encoded = cmd.encode()
        print(f"Command: {args.verb} {args.args}")
        print(f"Encoded: {encoded}")
        print(f"Hex: {encoded.hex()}")

    elif args.mode == "response":
        message = SMTP_CODES.get(args.code, "OK")
        encoded = encode_response(args.code, message)
        print(f"Response: {args.code} {message}")
        print(f"Encoded: {encoded}")

    elif args.mode == "message":
        if args.from_addr and args.to_addr:
            msg = EmailMessage(
                from_addr=args.from_addr,
                to_addrs=[args.to_addr],
                subject=args.subject,
                body=args.body,
            )
            raw = build_message(msg)
            print("Raw message:")
            print(raw)

    elif args.mode == "auth":
        if args.username and args.password:
            plain = encode_auth_plain(args.username, args.password)
            print(f"AUTH PLAIN: {plain}")

            login_user = encode_auth_login(args.username)
            login_pass = encode_auth_login(args.password)
            print(f"AUTH LOGIN username: {login_user}")
            print(f"AUTH LOGIN password: {login_pass}")

    elif args.mode == "session":
        session = SMTPSession("mail.example.com")
        commands = [
            SMTPCommand("EHLO", "client.example.com"),
            SMTPCommand("MAIL", "FROM:<sender@example.com>"),
            SMTPCommand("RCPT", "TO:<recipient@example.com>"),
            SMTPCommand("DATA"),
            SMTPCommand("QUIT"),
        ]

        for cmd in commands:
            response = session.process_command(cmd)
            print(f"C: {cmd.verb} {cmd.args}")
            print(f"S: {response.code} {response.message}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
