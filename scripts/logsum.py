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
