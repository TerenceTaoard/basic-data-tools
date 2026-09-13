import pytest

from scripts.logsum import filter_records, group_counts, parse_log_file, parse_log_line


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


def test_parse_log_file_gives_correct_counts():
    lines = [
        "2026-07-04T12:10:15Z INFO user=42 path=/home status=200 duration_ms=17",
        "2026-07-04T12:10:20Z ERROR user=19 broken-token",
        "2026-07-04T12:10:16Z ERROR user=19 path=/api/pay status=500 duration_ms=243",
    ]

    parsed_lines = parse_log_file(lines)

    assert parsed_lines["total_line_count"] == 3
    assert parsed_lines["parsed_record_count"] == 2
    assert parsed_lines["malformed_line_count"] == 1


def test_parse_log_file_parses_fields():
    lines = [
        "2026-07-04T12:10:15Z INFO user=42 path=/home status=200 duration_ms=17",
        "2026-07-04T12:10:20Z ERROR user=19 broken-token",
        "2026-07-04T12:10:16Z ERROR user=19 path=/api/pay status=500 duration_ms=243",
    ]

    parsed_lines = parse_log_file(lines)

    assert parsed_lines["parsed_records"] == [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "42",
                "path": "/home",
                "status": "200",
                "duration_ms": "17",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "level": "ERROR",
            "fields": {
                "user": "19",
                "path": "/api/pay",
                "status": "500",
                "duration_ms": "243",
            },
        },
    ]


def test_parse_log_file_empty_input_gives_all_zero_counts():
    lines = []

    parsed_lines = parse_log_file(lines)

    assert parsed_lines["total_line_count"] == 0
    assert parsed_lines["parsed_record_count"] == 0
    assert parsed_lines["malformed_line_count"] == 0


def test_filter_records_no_level_filter_returns_every_record():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "42",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "level": "ERROR",
            "fields": {
                "user": "19",
            },
        },
    ]

    filtered_records = filter_records(records)

    assert filtered_records == records


def test_filter_records_filters_for_level():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "42",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "level": "ERROR",
            "fields": {
                "user": "19",
            },
        },
    ]

    filtered_records = filter_records(records, level="ERROR")

    assert filtered_records == [records[1]]


def test_filter_records_filter_with_zero_matches_returns_empty():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "42",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "level": "ERROR",
            "fields": {
                "user": "19",
            },
        },
    ]

    filtered_records = filter_records(records, level="WARNING")

    assert filtered_records == []


def test_filter_records_missing_level_field_raises():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "42",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "fields": {
                "user": "19",
            },
        },
    ]

    with pytest.raises(
        ValueError, match=f"record contains no 'level' field: {records[1]!r}"
    ):
        filter_records(records)


def test_group_counts_counts_repeated_values():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "42",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "level": "ERROR",
            "fields": {
                "user": "42",
            },
        },
    ]

    grouped_records = group_counts(records, field="user")

    assert grouped_records["groups"] == [{"value": "42", "count": 2}]


def test_group_counts_record_missing_group_field_excluded_and_counted_separately():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "42",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "level": "ERROR",
            "fields": {
                "name": "fred",
            },
        },
    ]

    grouped_records = group_counts(records, field="user")

    assert grouped_records["missing_group_field"] == 1
    assert grouped_records["groups"] == [
        {"value": "42", "count": 1},
    ]


def test_group_counts_absent_group_field_produces_zero_groups():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "42",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "fields": {
                "user": "19",
            },
        },
    ]

    grouped_records = group_counts(records, field="name")

    assert grouped_records["groups"] == []


def test_group_counts_empty_field_values_can_form_a_group():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "level": "ERROR",
            "fields": {
                "user": "",
            },
        },
    ]

    grouped_records = group_counts(records, field="user")

    assert grouped_records["groups"] == [{"value": "", "count": 2}]


def test_group_counts_record_lacking_fields_key_raises():
    records = [
        {
            "timestamp": "2026-07-04T12:10:15Z",
            "level": "INFO",
            "fields": {
                "user": "",
            },
        },
        {
            "timestamp": "2026-07-04T12:10:16Z",
            "level": "ERROR",
        },
    ]

    with pytest.raises(
        ValueError, match=f"record lacks a fields entry: {records[1]!r}"
    ):
        group_counts(records, field="user")
