"""Syslog Protocol Parser CLI (RFC 5424).

Demonstrates syslog message parsing and formatting.
"""

import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum


class Facility(IntEnum):
    """Syslog facilities."""

    KERN = 0
    USER = 1
    MAIL = 2
    DAEMON = 3
    AUTH = 4
    SYSLOG = 5
    LPR = 6
    NEWS = 7
    UUCP = 8
    CRON = 9
    AUTHPRIV = 10
    FTP = 11
    NTP = 12
    AUDIT = 13
    ALERT = 14
    CLOCK = 15
    LOCAL0 = 16
    LOCAL1 = 17
    LOCAL2 = 18
    LOCAL3 = 19
    LOCAL4 = 20
    LOCAL5 = 21
    LOCAL6 = 22
    LOCAL7 = 23


class Severity(IntEnum):
    """Syslog severities."""

    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4
    NOTICE = 5
    INFO = 6
    DEBUG = 7


@dataclass
class StructuredDataElement:
    """RFC 5424 structured data element."""

    sd_id: str
    params: dict[str, str] = field(default_factory=dict)

    def to_string(self) -> str:
        """Format as string."""
        if not self.params:
            return f"[{self.sd_id}]"
        params_str = " ".join(f'{k}="{self._escape(v)}"' for k, v in self.params.items())
        return f"[{self.sd_id} {params_str}]"

    @staticmethod
    def _escape(value: str) -> str:
        """Escape special characters."""
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("]", "\\]")


@dataclass
class SyslogMessage:
    """RFC 5424 syslog message."""

    facility: Facility
    severity: Severity
    timestamp: datetime | None = None
    hostname: str = "-"
    app_name: str = "-"
    proc_id: str = "-"
    msg_id: str = "-"
    structured_data: list[StructuredDataElement] = field(default_factory=list)
    message: str = ""

    @property
    def priority(self) -> int:
        """Calculate PRI value."""
        return (self.facility * 8) + self.severity

    def to_rfc5424(self) -> str:
        """Format as RFC 5424 message."""
        # PRI
        pri = f"<{self.priority}>"

        # VERSION
        version = "1"

        # TIMESTAMP
        if self.timestamp:
            ts = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        else:
            ts = "-"

        # STRUCTURED-DATA
        if self.structured_data:
            sd = "".join(elem.to_string() for elem in self.structured_data)
        else:
            sd = "-"

        # Build message
        header = f"{pri}{version} {ts} {self.hostname} {self.app_name} {self.proc_id} {self.msg_id}"

        if self.message:
            return f"{header} {sd} {self.message}"
        return f"{header} {sd}"

    def to_rfc3164(self) -> str:
        """Format as RFC 3164 (BSD) message."""
        pri = f"<{self.priority}>"
        if self.timestamp:
            ts = self.timestamp.strftime("%b %d %H:%M:%S")
        else:
            ts = datetime.now().strftime("%b %d %H:%M:%S")

        tag = self.app_name
        if self.proc_id != "-":
            tag = f"{self.app_name}[{self.proc_id}]"

        return f"{pri}{ts} {self.hostname} {tag}: {self.message}"


class SyslogParseError(Exception):
    """Syslog parsing error."""

    pass


class SyslogParser:
    """Syslog message parser."""

    def __init__(self) -> None:
        self.pos = 0
        self.data = ""

    def parse(self, data: str) -> SyslogMessage:
        """Parse syslog message."""
        self.data = data
        self.pos = 0

        # Parse PRI
        if not self.data.startswith("<"):
            raise SyslogParseError("Missing PRI")

        end_pri = self.data.find(">")
        if end_pri == -1:
            raise SyslogParseError("Invalid PRI")

        try:
            pri = int(self.data[1:end_pri])
        except ValueError:
            raise SyslogParseError("Invalid PRI value") from None

        facility = Facility(pri // 8)
        severity = Severity(pri % 8)
        self.pos = end_pri + 1

        # Check if RFC 5424 (starts with version)
        if self.pos < len(self.data) and self.data[self.pos] == "1":
            return self._parse_rfc5424(facility, severity)
        else:
            return self._parse_rfc3164(facility, severity)

    def _parse_rfc5424(self, facility: Facility, severity: Severity) -> SyslogMessage:
        """Parse RFC 5424 format."""
        self.pos += 1  # Skip version
        self._skip_space()

        # TIMESTAMP
        timestamp = self._parse_timestamp()
        self._skip_space()

        # HOSTNAME
        hostname = self._parse_field()
        self._skip_space()

        # APP-NAME
        app_name = self._parse_field()
        self._skip_space()

        # PROCID
        proc_id = self._parse_field()
        self._skip_space()

        # MSGID
        msg_id = self._parse_field()
        self._skip_space()

        # STRUCTURED-DATA
        structured_data = self._parse_structured_data()

        # MESSAGE
        message = ""
        if self.pos < len(self.data):
            self._skip_space()
            message = self.data[self.pos :]

        return SyslogMessage(
            facility=facility,
            severity=severity,
            timestamp=timestamp,
            hostname=hostname,
            app_name=app_name,
            proc_id=proc_id,
            msg_id=msg_id,
            structured_data=structured_data,
            message=message,
        )

    def _parse_rfc3164(self, facility: Facility, severity: Severity) -> SyslogMessage:
        """Parse RFC 3164 (BSD) format."""
        # TIMESTAMP (Mmm dd hh:mm:ss)
        timestamp = None
        try:
            ts_str = self.data[self.pos : self.pos + 15]
            # Prepend current year to avoid deprecation warning for strptime without year
            current_year = datetime.now().year
            ts_with_year = f"{current_year} {ts_str}"
            timestamp = datetime.strptime(ts_with_year, "%Y %b %d %H:%M:%S")
            self.pos += 15
        except (ValueError, IndexError):
            pass

        self._skip_space()

        # HOSTNAME
        hostname = self._parse_field()
        self._skip_space()

        # TAG (app_name[proc_id]:)
        app_name = "-"
        proc_id = "-"
        tag_end = self.data.find(":", self.pos)
        if tag_end != -1:
            tag = self.data[self.pos : tag_end]
            self.pos = tag_end + 1

            bracket = tag.find("[")
            if bracket != -1:
                app_name = tag[:bracket]
                proc_id = tag[bracket + 1 : -1] if tag.endswith("]") else tag[bracket + 1 :]
            else:
                app_name = tag

        self._skip_space()
        message = self.data[self.pos :]

        return SyslogMessage(
            facility=facility,
            severity=severity,
            timestamp=timestamp,
            hostname=hostname,
            app_name=app_name,
            proc_id=proc_id,
            message=message,
        )

    def _skip_space(self) -> None:
        """Skip whitespace."""
        while self.pos < len(self.data) and self.data[self.pos] == " ":
            self.pos += 1

    def _parse_field(self) -> str:
        """Parse a space-delimited field."""
        start = self.pos
        while self.pos < len(self.data) and self.data[self.pos] not in " \n":
            self.pos += 1
        return self.data[start : self.pos]

    def _parse_timestamp(self) -> datetime | None:
        """Parse RFC 5424 timestamp."""
        field = self._parse_field()
        if field == "-":
            return None

        try:
            # Handle various timestamp formats
            if "." in field:
                ts_str = field.rstrip("Z")
                if len(ts_str) > 26:
                    ts_str = ts_str[:26]
                return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                return datetime.strptime(field.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

    def _parse_structured_data(self) -> list[StructuredDataElement]:
        """Parse structured data elements."""
        elements: list[StructuredDataElement] = []

        if self.pos >= len(self.data) or self.data[self.pos] == "-":
            if self.pos < len(self.data) and self.data[self.pos] == "-":
                self.pos += 1
            return elements

        while self.pos < len(self.data) and self.data[self.pos] == "[":
            elem = self._parse_sd_element()
            if elem:
                elements.append(elem)

        return elements

    def _parse_sd_element(self) -> StructuredDataElement | None:
        """Parse a single SD element."""
        if self.data[self.pos] != "[":
            return None

        self.pos += 1  # Skip [

        # Parse SD-ID
        sd_id_start = self.pos
        while self.pos < len(self.data) and self.data[self.pos] not in " ]":
            self.pos += 1
        sd_id = self.data[sd_id_start : self.pos]

        params: dict[str, str] = {}

        # Parse params
        while self.pos < len(self.data) and self.data[self.pos] != "]":
            self._skip_space()
            if self.data[self.pos] == "]":
                break

            # Parse param name
            name_start = self.pos
            while self.pos < len(self.data) and self.data[self.pos] != "=":
                self.pos += 1
            name = self.data[name_start : self.pos]

            self.pos += 1  # Skip =

            # Parse param value (quoted)
            if self.pos < len(self.data) and self.data[self.pos] == '"':
                self.pos += 1  # Skip opening quote
                value_start = self.pos
                while self.pos < len(self.data):
                    if self.data[self.pos] == "\\" and self.pos + 1 < len(self.data):
                        self.pos += 2  # Skip escaped char
                    elif self.data[self.pos] == '"':
                        break
                    else:
                        self.pos += 1
                value = self.data[value_start : self.pos]
                self.pos += 1  # Skip closing quote
                params[name] = value.replace('\\"', '"').replace("\\\\", "\\")

        if self.pos < len(self.data) and self.data[self.pos] == "]":
            self.pos += 1  # Skip ]

        return StructuredDataElement(sd_id, params)


def parse(data: str) -> SyslogMessage:
    """Parse syslog message."""
    parser = SyslogParser()
    return parser.parse(data)


def format_message(
    message: str,
    facility: Facility = Facility.USER,
    severity: Severity = Severity.INFO,
    app_name: str = "app",
    hostname: str = "localhost",
) -> str:
    """Format a syslog message."""
    msg = SyslogMessage(
        facility=facility,
        severity=severity,
        timestamp=datetime.now(),
        hostname=hostname,
        app_name=app_name,
        message=message,
    )
    return msg.to_rfc5424()


def simulate_syslog(operations: list[str]) -> list[str]:
    """Simulate syslog operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "parse":
            try:
                msg = parse(parts[1])
                results.append(f"facility={msg.facility.name} severity={msg.severity.name}")
            except SyslogParseError as e:
                results.append(f"error:{e}")
        elif cmd == "format":
            formatted = format_message(parts[1])
            results.append(formatted[:50] + "...")
        elif cmd == "priority":
            pri = int(parts[1])
            fac = Facility(pri // 8)
            sev = Severity(pri % 8)
            results.append(f"{fac.name}.{sev.name}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: proto_syslog_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]

    if cmd == "parse" and len(sys.argv) > 2:
        try:
            msg = parse(sys.argv[2])
            print(f"Facility: {msg.facility.name}")
            print(f"Severity: {msg.severity.name}")
            print(f"Hostname: {msg.hostname}")
            print(f"App: {msg.app_name}")
            print(f"Message: {msg.message}")
        except SyslogParseError as e:
            print(f"Error: {e}")
            return 1
    elif cmd == "format" and len(sys.argv) > 2:
        print(format_message(sys.argv[2]))
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
