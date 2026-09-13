import pytest

from scripts.logsum import parse_log_line


def test_parse_log_line_parses_normal_line():
    line = "2026-09-10T12:32Z INFO user=12 status=active"

    parsed_line = parse_log_line(line)

    assert parsed_line == {
        "timestamp": "2026-09-10T12:32Z",
        "level": "INFO",
        "fields": {"user": "12", "status": "active"},
    }


def test_parse_log_line_parses_valid_no_field_line():
    line = "2026-09-10T12:32Z INFO"

    parsed_line = parse_log_line(line)

    assert parsed_line == {
        "timestamp": "2026-09-10T12:32Z",
        "level": "INFO",
        "fields": {},
    }


def test_parse_log_line_handles_extra_whitespace():
    line = "  2026-09-10T12:32Z    INFO  user=12  status=active  "

    parsed_line = parse_log_line(line)

    assert parsed_line == {
        "timestamp": "2026-09-10T12:32Z",
        "level": "INFO",
        "fields": {"user": "12", "status": "active"},
    }


def test_parse_log_line_parses_multiple_equals():
    line = "2026-09-10T12:32Z INFO user=jeb=12 status=active"

    parsed_line = parse_log_line(line)

    assert parsed_line["fields"] == {"user": "jeb=12", "status": "active"}


def test_parse_log_line_parses_empty_value():
    line = "2026-09-10T12:32Z INFO user=12 status="

    parsed_line = parse_log_line(line)

    assert parsed_line["fields"] == {"user": "12", "status": ""}


def test_parse_log_line_blank_line_raises():
    line = ""

    with pytest.raises(ValueError, match="line '' has less than two tokens"):
        parse_log_line(line)


def test_parse_log_line_one_token_line_raises():
    line = "INFO"

    with pytest.raises(ValueError, match="line 'INFO' has less than two tokens"):
        parse_log_line(line)


def test_parse_log_line_field_without_equals_sign_raises():
    line = "2026-09-10T12:32Z INFO user"

    with pytest.raises(
        ValueError,
        match="fields must be of form key=value, but field in line '2026-09-10T12:32Z INFO user' has form 'user'",
    ):
        parse_log_line(line)


def test_parse_log_line_empty_key_raises():
    line = "2026-09-10T12:32Z INFO =active"

    with pytest.raises(
        ValueError,
        match="fields must be of form key=value, but field in line '2026-09-10T12:32Z INFO =active' has form '=active'",
    ):
        parse_log_line(line)


def test_parse_log_line_duplicate_key_raises():
    line = "2026-09-10T12:32Z INFO user=12 user=13"

    with pytest.raises(
        ValueError,
        match="duplicate key in line '2026-09-10T12:32Z INFO user=12 user=13'",
    ):
        parse_log_line(line)
