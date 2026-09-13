def parse_log_line(line: str) -> dict:
    """
    Returns a parsed dictionary record of line of the form:
    {"timestamp": <timestamp>,
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
