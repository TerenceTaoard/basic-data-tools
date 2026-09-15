def parse_log_line(line: str) -> dict:
    """
    Returns a parsed dictionary record of line of the form:
    {
        "timestamp": <timestamp>,
        "level": <level>,
        "fields": {
            <key>: <value>
            <key>: <value>
            ...
        }
    }

    Args:
    - line: One log line of the form <TIMESTAMP> <LEVEL> [key=value ...], with tokens separated by
    whitespace.

    Preconditions:
    - Line must have at least two tokens (the timestamp and level).
    - Every token thereafter must be of the form key=value (no space).
    - Keys must be unique, non-empty, and contain no whitespace.
    """
    tokens = line.split()

    if len(tokens) < 2:
        raise ValueError(f"line {line!r} has less than two tokens")

    fields = {}

    for token in tokens[2:]:
        parts = token.split("=", maxsplit=1)

        if len(parts) != 2 or parts[0] == "":
            raise ValueError(
                f"fields must be of form key=value, but field in line {line!r} has form {token!r}"
            )

        key = parts[0]
        value = parts[1]

        if key in fields:
            raise ValueError(f"duplicate key in line {line!r}")

        fields[key] = value

    timestamp = tokens[0]
    level = tokens[1]

    return {"timestamp": timestamp, "level": level, "fields": fields}


def parse_log_file(lines: list[str]) -> dict:
    """
    Returns a dictionary of total line count, successfully parsed record count, malformed record
    count, and a list of parsed records.

    Args:
        lines: A list of log file lines.
    """
    parsed_result = {}

    parsed_result["total_line_count"] = len(lines)
    parsed_result["parsed_record_count"] = 0
    parsed_result["malformed_line_count"] = 0
    parsed_result["parsed_records"] = []

    for line in lines:
        try:
            parsed_line = parse_log_line(line)
            parsed_result["parsed_record_count"] += 1
            parsed_result["parsed_records"].append(parsed_line)
        except ValueError:
            parsed_result["malformed_line_count"] += 1

    return parsed_result


def filter_records(records: list[dict], level: str | None = None) -> list[dict]:
    """
    Returns a list of records filtered by level.

    Args:
        records: A list of records of the form
            {
                "timestamp": <timestamp>,
                "level": <level>,
                "fields": {
                    <key>: <value>
                    <key>: <value>
                    ...
                }
            }
        level: Keep only records with this level. If None, keep all records.

    Preconditions:
        - Every record must have a 'level' field.
    """
    filtered_records = []

    for record in records:
        if "level" not in record:
            raise ValueError(f"record contains no 'level' field: {record!r}")
        if level is None or record["level"] == level:
            filtered_records.append(record)

    return filtered_records


def group_counts(records: list[dict], field: str) -> dict:
    """
    Returns a dictionary with records grouped by field value of form:
    {
        "missing_group_field": <number of fields lacking group key>
        "groups": [
            {"value": <value>, "count", <count>},
            ...
        ]
    }

    Args:
        records: A list of records with 'fields' key of form
            "fields": {
                    <key>: <value>
                    <key>: <value>
                    ...
                }
        field: The field key on which to group by.
    """
    missing_group_field = 0
    count_by_value = {}

    for record in records:
        if "fields" not in record:
            raise ValueError(f"record lacks a fields entry: {record!r}")
        if field not in record["fields"]:
            missing_group_field += 1
            continue
        value = record["fields"][field]
        count_by_value[value] = count_by_value.get(value, 0) + 1

    groups = [
        {"value": value, "count": count} for (value, count) in count_by_value.items()
    ]

    grouped_records = {"missing_group_field": missing_group_field, "groups": groups}

    return grouped_records


def sort_groups(counts: list[dict], limit: int | None = None) -> list[dict]:
    """
    Given a list of group counts of the form {"value": <value>, "count": <count>}, returns a sorted
    list of the top 'limit' groups, or all groups if 'limit' is None. Groups are sorted first by
    descending count, then by ascending lexicographic order.

    Args:
        counts: A list of group counts of the form {"value": <value>, "count": <count>}
        limit: Return the top 'limit' groups. If limit is None, return all groups.

    Preconditions:
        - limit > 0
    """
    if limit is not None and limit < 1:
        raise ValueError(f"limit must be > 0, but received limit of {limit}")

    sorted_counts = sorted(counts, key=lambda x: (-x["count"], x["value"]))

    if limit is None:
        return sorted_counts

    return sorted_counts[:limit]


def build_summary(
    log_text: str,
    level_filter: str | None = None,
    group_by: str | None = None,
    group_limit: int | None = None,
) -> dict:
    """
    Builds a summary of a log.

    Args:
        log_text: Text from a log file.
        level_filter: Include only log entries with this level. If None, include entries of all levels.
        group_by: Group values of fields with key 'group_by'. If None, don't group any.
        group_limit: The maximum number of groups to include. If None, include all matching groups.

    Preconditions:
        - group_limit > 0

    Returns:
        A dictionary summary of a log.

        Keys:
            "total_lines" (int): The number of lines in log_text.
            "parsed_records" (int): The number of successfully parsed lines.
            "malformed_lines" (int): The number of lines that couldn't be parsed.
            "matching_records" (int): The number of lines of level 'level_filter'.
            "level_filter" (str | None): The chosen level filtered. If None, all levels were
                included.
            "group_by" (str | None): The key grouped on. If None, no groups formed.
            "missing_group_field" (int): Number of matching records without the 'group_by' field.
                If no 'group_by' provided, always 0.
            "groups" (list[dict]): Matching groups with entries of form
                {"value": <value>, "count": <count>}, sorted first by descending count, then by
                ascending lexicographic order of value.
    """
    lines = log_text.splitlines()

    parsed_lines = parse_log_file(
        lines
    )  # keys: total_line_count, parsed_record_count, malformed_line_count, parsed_records

    total_line_count = parsed_lines["total_line_count"]
    parsed_record_count = parsed_lines["parsed_record_count"]
    malformed_line_count = parsed_lines["malformed_line_count"]

    parsed_records = parsed_lines[
        "parsed_records"
    ]  # each element has keys: timestamp, level, fields

    filtered_records = filter_records(parsed_records, level=level_filter)

    matching_record_count = len(filtered_records)

    if group_by is not None:
        grouped_fields = group_counts(
            filtered_records, field=group_by
        )  # keys: missing_group_field, groups

        missing_group_field = grouped_fields["missing_group_field"]

        groups = grouped_fields[
            "groups"
        ]  # each element: {"value": <value>, "count": <count>}
        groups = sort_groups(groups, limit=group_limit)
    else:
        missing_group_field = 0
        groups = []

    summary = {
        "total_lines": total_line_count,
        "parsed_records": parsed_record_count,
        "malformed_lines": malformed_line_count,
        "matching_records": matching_record_count,
        "level_filter": level_filter,
        "group_by": group_by,
        "missing_group_field": missing_group_field,
        "groups": groups,
    }

    return summary
