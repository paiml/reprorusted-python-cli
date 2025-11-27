"""Tests for proto_syslog_cli.py"""


import pytest
from proto_syslog_cli import (
    Facility,
    Severity,
    StructuredDataElement,
    SyslogMessage,
    SyslogParseError,
    SyslogParser,
    format_message,
    parse,
    simulate_syslog,
)


class TestFacility:
    def test_values(self):
        assert Facility.KERN == 0
        assert Facility.USER == 1
        assert Facility.DAEMON == 3
        assert Facility.LOCAL0 == 16
        assert Facility.LOCAL7 == 23

    def test_all_facilities(self):
        assert len(Facility) == 24


class TestSeverity:
    def test_values(self):
        assert Severity.EMERGENCY == 0
        assert Severity.ALERT == 1
        assert Severity.CRITICAL == 2
        assert Severity.ERROR == 3
        assert Severity.WARNING == 4
        assert Severity.NOTICE == 5
        assert Severity.INFO == 6
        assert Severity.DEBUG == 7

    def test_all_severities(self):
        assert len(Severity) == 8


class TestStructuredDataElement:
    def test_create(self):
        elem = StructuredDataElement("exampleID")
        assert elem.sd_id == "exampleID"
        assert elem.params == {}

    def test_with_params(self):
        elem = StructuredDataElement("test", {"key": "value"})
        assert elem.params["key"] == "value"

    def test_to_string_no_params(self):
        elem = StructuredDataElement("myid")
        assert elem.to_string() == "[myid]"

    def test_to_string_with_params(self):
        elem = StructuredDataElement("id", {"key": "val"})
        assert elem.to_string() == '[id key="val"]'

    def test_escape_quotes(self):
        elem = StructuredDataElement("id", {"msg": 'say "hello"'})
        result = elem.to_string()
        assert '\\"' in result

    def test_escape_backslash(self):
        elem = StructuredDataElement("id", {"path": "C:\\test"})
        result = elem.to_string()
        assert "\\\\" in result


class TestSyslogMessage:
    def test_create(self):
        msg = SyslogMessage(Facility.USER, Severity.INFO)
        assert msg.facility == Facility.USER
        assert msg.severity == Severity.INFO

    def test_priority_calculation(self):
        # USER (1) * 8 + INFO (6) = 14
        msg = SyslogMessage(Facility.USER, Severity.INFO)
        assert msg.priority == 14

        # LOCAL0 (16) * 8 + ERROR (3) = 131
        msg = SyslogMessage(Facility.LOCAL0, Severity.ERROR)
        assert msg.priority == 131

    def test_to_rfc5424_minimal(self):
        msg = SyslogMessage(Facility.USER, Severity.INFO)
        result = msg.to_rfc5424()
        assert result.startswith("<14>1")
        assert "- - - - - -" in result

    def test_to_rfc5424_with_hostname(self):
        msg = SyslogMessage(Facility.USER, Severity.INFO, hostname="myhost")
        result = msg.to_rfc5424()
        assert "myhost" in result

    def test_to_rfc5424_with_message(self):
        msg = SyslogMessage(
            Facility.USER, Severity.INFO, message="Test message"
        )
        result = msg.to_rfc5424()
        assert "Test message" in result

    def test_to_rfc5424_with_structured_data(self):
        elem = StructuredDataElement("exampleSDID", {"key": "value"})
        msg = SyslogMessage(
            Facility.USER, Severity.INFO, structured_data=[elem]
        )
        result = msg.to_rfc5424()
        assert "[exampleSDID" in result
        assert 'key="value"' in result

    def test_to_rfc3164(self):
        msg = SyslogMessage(
            Facility.USER,
            Severity.INFO,
            hostname="localhost",
            app_name="test",
            message="hello",
        )
        result = msg.to_rfc3164()
        assert "<14>" in result
        assert "localhost" in result
        assert "test" in result
        assert "hello" in result

    def test_to_rfc3164_with_procid(self):
        msg = SyslogMessage(
            Facility.USER,
            Severity.INFO,
            hostname="host",
            app_name="app",
            proc_id="1234",
            message="msg",
        )
        result = msg.to_rfc3164()
        assert "app[1234]" in result


class TestSyslogParser:
    def test_parse_rfc5424_minimal(self):
        parser = SyslogParser()
        msg = parser.parse("<14>1 - - - - - -")
        assert msg.facility == Facility.USER
        assert msg.severity == Severity.INFO

    def test_parse_rfc5424_full(self):
        data = "<14>1 2023-01-15T10:30:00.000Z myhost myapp 1234 ID47 - Test message"
        msg = parse(data)
        assert msg.hostname == "myhost"
        assert msg.app_name == "myapp"
        assert msg.proc_id == "1234"
        assert msg.msg_id == "ID47"
        assert msg.message == "Test message"

    def test_parse_rfc5424_structured_data(self):
        data = '<14>1 - - - - - [exampleSDID@32473 key="value"] msg'
        msg = parse(data)
        assert len(msg.structured_data) == 1
        assert msg.structured_data[0].sd_id == "exampleSDID@32473"
        assert msg.structured_data[0].params["key"] == "value"

    def test_parse_rfc3164(self):
        data = "<14>Jan 15 10:30:00 myhost myapp[1234]: Test message"
        msg = parse(data)
        assert msg.facility == Facility.USER
        assert msg.hostname == "myhost"
        assert msg.app_name == "myapp"
        assert msg.proc_id == "1234"
        assert msg.message == "Test message"

    def test_parse_invalid_pri_missing(self):
        parser = SyslogParser()
        with pytest.raises(SyslogParseError):
            parser.parse("No PRI here")

    def test_parse_invalid_pri_unclosed(self):
        parser = SyslogParser()
        with pytest.raises(SyslogParseError):
            parser.parse("<14 unclosed")

    def test_parse_various_priorities(self):
        for fac in [Facility.KERN, Facility.USER, Facility.LOCAL7]:
            for sev in [Severity.EMERGENCY, Severity.INFO, Severity.DEBUG]:
                pri = fac * 8 + sev
                msg = parse(f"<{pri}>1 - - - - - -")
                assert msg.facility == fac
                assert msg.severity == sev


class TestParse:
    def test_simple(self):
        msg = parse("<14>1 - - - - - - hello")
        assert msg.message == "hello"

    def test_timestamp(self):
        msg = parse("<14>1 2023-06-15T12:00:00Z host app - - - msg")
        assert msg.timestamp is not None
        assert msg.timestamp.year == 2023
        assert msg.timestamp.month == 6

    def test_timestamp_with_microseconds(self):
        msg = parse("<14>1 2023-06-15T12:00:00.123456Z host app - - - msg")
        assert msg.timestamp is not None


class TestFormatMessage:
    def test_simple(self):
        result = format_message("Hello world")
        assert "Hello world" in result
        assert result.startswith("<")

    def test_custom_facility(self):
        result = format_message(
            "Test", facility=Facility.LOCAL0, severity=Severity.ERROR
        )
        # LOCAL0 (16) * 8 + ERROR (3) = 131
        assert "<131>" in result

    def test_custom_app_name(self):
        result = format_message("Test", app_name="myapp")
        assert "myapp" in result


class TestSimulateSyslog:
    def test_parse(self):
        result = simulate_syslog(["parse:<14>1 - - - - - -"])
        assert "facility=USER" in result[0]
        assert "severity=INFO" in result[0]

    def test_format(self):
        result = simulate_syslog(["format:Test message"])
        assert "..." in result[0]

    def test_priority(self):
        result = simulate_syslog(["priority:14"])
        assert "USER.INFO" in result[0]

    def test_priority_local(self):
        result = simulate_syslog(["priority:131"])  # LOCAL0.ERROR
        assert "LOCAL0.ERROR" in result[0]


class TestRoundTrip:
    def test_rfc5424_roundtrip(self):
        original = SyslogMessage(
            facility=Facility.USER,
            severity=Severity.WARNING,
            hostname="testhost",
            app_name="testapp",
            proc_id="999",
            msg_id="MSGID",
            message="Test roundtrip",
        )
        formatted = original.to_rfc5424()
        parsed = parse(formatted)

        assert parsed.facility == original.facility
        assert parsed.severity == original.severity
        assert parsed.hostname == original.hostname
        assert parsed.app_name == original.app_name
        assert parsed.message == original.message


class TestMultipleStructuredData:
    def test_multiple_elements(self):
        elem1 = StructuredDataElement("id1", {"a": "1"})
        elem2 = StructuredDataElement("id2", {"b": "2"})
        msg = SyslogMessage(
            Facility.USER, Severity.INFO, structured_data=[elem1, elem2]
        )
        result = msg.to_rfc5424()
        assert "[id1" in result
        assert "[id2" in result


class TestEdgeCases:
    def test_empty_message(self):
        msg = SyslogMessage(Facility.USER, Severity.INFO, message="")
        result = msg.to_rfc5424()
        assert result.endswith("-")

    def test_special_chars_in_message(self):
        msg = SyslogMessage(
            Facility.USER,
            Severity.INFO,
            message="Test: special chars <>&\"'",
        )
        result = msg.to_rfc5424()
        assert "<>&" in result

    def test_nilvalue_fields(self):
        msg = SyslogMessage(
            Facility.USER,
            Severity.INFO,
            hostname="-",
            app_name="-",
            proc_id="-",
            msg_id="-",
        )
        result = msg.to_rfc5424()
        assert "- - - -" in result
