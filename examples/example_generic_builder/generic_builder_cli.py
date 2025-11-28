"""Generic Builder Pattern CLI.

Demonstrates builder pattern for constructing complex objects.
"""

import sys
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class HttpRequest:
    """HTTP request object."""

    method: str = "GET"
    url: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None
    timeout: int = 30
    follow_redirects: bool = True


class HttpRequestBuilder:
    """Builder for HttpRequest."""

    def __init__(self) -> None:
        self._method = "GET"
        self._url = ""
        self._headers: dict[str, str] = {}
        self._body: str | None = None
        self._timeout = 30
        self._follow_redirects = True

    def method(self, method: str) -> "HttpRequestBuilder":
        """Set HTTP method."""
        self._method = method
        return self

    def url(self, url: str) -> "HttpRequestBuilder":
        """Set URL."""
        self._url = url
        return self

    def header(self, key: str, value: str) -> "HttpRequestBuilder":
        """Add header."""
        self._headers[key] = value
        return self

    def body(self, body: str) -> "HttpRequestBuilder":
        """Set body."""
        self._body = body
        return self

    def timeout(self, timeout: int) -> "HttpRequestBuilder":
        """Set timeout."""
        self._timeout = timeout
        return self

    def follow_redirects(self, follow: bool) -> "HttpRequestBuilder":
        """Set follow redirects."""
        self._follow_redirects = follow
        return self

    def build(self) -> HttpRequest:
        """Build the request."""
        if not self._url:
            raise ValueError("URL is required")
        return HttpRequest(
            method=self._method,
            url=self._url,
            headers=self._headers,
            body=self._body,
            timeout=self._timeout,
            follow_redirects=self._follow_redirects,
        )


@dataclass
class Query:
    """SQL-like query object."""

    table: str = ""
    columns: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    order_by: str | None = None
    order_desc: bool = False
    limit: int | None = None
    offset: int | None = None


class QueryBuilder:
    """Builder for queries."""

    def __init__(self) -> None:
        self._table = ""
        self._columns: list[str] = []
        self._conditions: list[str] = []
        self._order_by: str | None = None
        self._order_desc = False
        self._limit: int | None = None
        self._offset: int | None = None

    def table(self, table: str) -> "QueryBuilder":
        """Set table name."""
        self._table = table
        return self

    def select(self, *columns: str) -> "QueryBuilder":
        """Add columns to select."""
        self._columns.extend(columns)
        return self

    def where(self, condition: str) -> "QueryBuilder":
        """Add WHERE condition."""
        self._conditions.append(condition)
        return self

    def order_by(self, column: str, desc: bool = False) -> "QueryBuilder":
        """Set ORDER BY."""
        self._order_by = column
        self._order_desc = desc
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """Set LIMIT."""
        self._limit = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """Set OFFSET."""
        self._offset = offset
        return self

    def build(self) -> Query:
        """Build the query."""
        if not self._table:
            raise ValueError("Table is required")
        return Query(
            table=self._table,
            columns=self._columns if self._columns else ["*"],
            conditions=self._conditions,
            order_by=self._order_by,
            order_desc=self._order_desc,
            limit=self._limit,
            offset=self._offset,
        )

    def to_sql(self) -> str:
        """Build SQL string."""
        query = self.build()
        sql = f"SELECT {', '.join(query.columns)} FROM {query.table}"

        if query.conditions:
            sql += f" WHERE {' AND '.join(query.conditions)}"

        if query.order_by:
            direction = "DESC" if query.order_desc else "ASC"
            sql += f" ORDER BY {query.order_by} {direction}"

        if query.limit is not None:
            sql += f" LIMIT {query.limit}"

        if query.offset is not None:
            sql += f" OFFSET {query.offset}"

        return sql


@dataclass
class Config:
    """Configuration object."""

    values: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        return self.values.get(key, default)

    def get_str(self, key: str, default: str = "") -> str:
        """Get string value."""
        return str(self.values.get(key, default))

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer value."""
        value = self.values.get(key, default)
        return int(value) if value is not None else default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean value."""
        value = self.values.get(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "yes", "1")


class ConfigBuilder:
    """Builder for Config."""

    def __init__(self) -> None:
        self._values: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> "ConfigBuilder":
        """Set config value."""
        self._values[key] = value
        return self

    def set_if_absent(self, key: str, value: Any) -> "ConfigBuilder":
        """Set config value if not present."""
        if key not in self._values:
            self._values[key] = value
        return self

    def merge(self, other: dict[str, Any]) -> "ConfigBuilder":
        """Merge another dict into config."""
        self._values.update(other)
        return self

    def build(self) -> Config:
        """Build config."""
        return Config(values=dict(self._values))


@dataclass
class Email:
    """Email message."""

    from_addr: str = ""
    to_addrs: list[str] = field(default_factory=list)
    cc_addrs: list[str] = field(default_factory=list)
    bcc_addrs: list[str] = field(default_factory=list)
    subject: str = ""
    body: str = ""
    html_body: str | None = None
    attachments: list[str] = field(default_factory=list)
    priority: int = 3


class EmailBuilder:
    """Builder for Email."""

    def __init__(self) -> None:
        self._from = ""
        self._to: list[str] = []
        self._cc: list[str] = []
        self._bcc: list[str] = []
        self._subject = ""
        self._body = ""
        self._html_body: str | None = None
        self._attachments: list[str] = []
        self._priority = 3

    def from_addr(self, addr: str) -> "EmailBuilder":
        """Set from address."""
        self._from = addr
        return self

    def to(self, addr: str) -> "EmailBuilder":
        """Add to address."""
        self._to.append(addr)
        return self

    def cc(self, addr: str) -> "EmailBuilder":
        """Add CC address."""
        self._cc.append(addr)
        return self

    def bcc(self, addr: str) -> "EmailBuilder":
        """Add BCC address."""
        self._bcc.append(addr)
        return self

    def subject(self, subject: str) -> "EmailBuilder":
        """Set subject."""
        self._subject = subject
        return self

    def body(self, body: str) -> "EmailBuilder":
        """Set plain text body."""
        self._body = body
        return self

    def html_body(self, html: str) -> "EmailBuilder":
        """Set HTML body."""
        self._html_body = html
        return self

    def attachment(self, path: str) -> "EmailBuilder":
        """Add attachment."""
        self._attachments.append(path)
        return self

    def priority(self, priority: int) -> "EmailBuilder":
        """Set priority (1=highest, 5=lowest)."""
        self._priority = max(1, min(5, priority))
        return self

    def build(self) -> Email:
        """Build email."""
        if not self._from:
            raise ValueError("From address is required")
        if not self._to:
            raise ValueError("At least one recipient is required")
        return Email(
            from_addr=self._from,
            to_addrs=self._to,
            cc_addrs=self._cc,
            bcc_addrs=self._bcc,
            subject=self._subject,
            body=self._body,
            html_body=self._html_body,
            attachments=self._attachments,
            priority=self._priority,
        )


class GenericBuilder(Generic[T]):
    """Generic builder using reflection-like approach."""

    def __init__(self, target_class: type[T]) -> None:
        self._class = target_class
        self._values: dict[str, Any] = {}

    def set(self, name: str, value: Any) -> "GenericBuilder[T]":
        """Set a field value."""
        self._values[name] = value
        return self

    def build(self) -> T:
        """Build the object."""
        return self._class(**self._values)


@dataclass
class Person:
    """Simple person for demonstration."""

    name: str = ""
    age: int = 0
    email: str = ""


def simulate_builder(operations: list[str]) -> list[str]:
    """Simulate builder operations."""
    results = []
    http_builder = HttpRequestBuilder()
    query_builder = QueryBuilder()

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "http_url":
            http_builder.url(parts[1])
            results.append("ok")
        elif cmd == "http_method":
            http_builder.method(parts[1])
            results.append("ok")
        elif cmd == "http_header":
            k, v = parts[1].split("=", 1)
            http_builder.header(k, v)
            results.append("ok")
        elif cmd == "http_build":
            try:
                req = http_builder.build()
                results.append(f"{req.method} {req.url}")
            except ValueError as e:
                results.append(f"error:{e}")
        elif cmd == "query_table":
            query_builder.table(parts[1])
            results.append("ok")
        elif cmd == "query_select":
            query_builder.select(*parts[1].split(","))
            results.append("ok")
        elif cmd == "query_where":
            query_builder.where(parts[1])
            results.append("ok")
        elif cmd == "query_sql":
            try:
                results.append(query_builder.to_sql())
            except ValueError as e:
                results.append(f"error:{e}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: generic_builder_cli.py <command> [args...]")
        print("Commands: http, query, email, config")
        return 1

    cmd = sys.argv[1]

    if cmd == "http":
        builder = HttpRequestBuilder()
        builder.url("https://example.com")
        builder.method("GET")
        req = builder.build()
        print(f"{req.method} {req.url}")

    elif cmd == "query":
        sql = (
            QueryBuilder()
            .table("users")
            .select("id", "name")
            .where("active = 1")
            .limit(10)
            .to_sql()
        )
        print(sql)

    elif cmd == "email":
        email = (
            EmailBuilder()
            .from_addr("sender@example.com")
            .to("recipient@example.com")
            .subject("Hello")
            .body("Test message")
            .build()
        )
        print(f"From: {email.from_addr}")
        print(f"To: {', '.join(email.to_addrs)}")
        print(f"Subject: {email.subject}")

    elif cmd == "config":
        config = (
            ConfigBuilder().set("host", "localhost").set("port", 8080).set("debug", True).build()
        )
        print(f"host={config.get_str('host')}")
        print(f"port={config.get_int('port')}")
        print(f"debug={config.get_bool('debug')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
