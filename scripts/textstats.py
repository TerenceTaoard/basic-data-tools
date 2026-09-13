import argparse
import json
import re
import sys
from pathlib import Path


def tokenize(text: str, lowercase: bool = False) -> list[str]:
    """
    Tokenize text, where tokens are consecutive sequences of letters, numbers, apostrophes, or
    hyphens.

    Args:
        text: The text to tokenize.
        lowercase: If True, all letters are first converted to lowercase before tokenization.

    Returns:
        A list of tokens in text.
    """
    if lowercase:
        text = text.lower()

    token_regex = r"[\w\d'-]+"

    tokens = re.findall(token_regex, text)

    return tokens


def filter_min_length(tokens: list[str], min_length: int = 1) -> list[str]:
    """
    Filter out tokens less than min_length.

    Args:
        tokens: The list of tokens to filter.
        min_length: The minimum length of token to keep.

    Preconditions:
        - min_length > 0

    Returns:
        A list of tokens of at least length min_length.
    """
    if min_length < 1:
        raise ValueError(
            f"min_length must be > 0, but received min_length of {min_length}"
        )

    filtered_tokens = [token for token in tokens if len(token) >= min_length]

    return filtered_tokens


def count_words(tokens: list[str]) -> list[dict]:
    """
    Produce a histogram of unique token counts.

    Args:
        tokens: The list of tokens to count.

    Returns:
        A list of dictionaries of the form
        [{"word": <word>, "count": <count>, ...}]
    """
    count_by_word = {}

    for token in tokens:
        count_by_word[token] = count_by_word.get(token, 0) + 1

    word_counts = [
        {"word": word, "count": count} for (word, count) in count_by_word.items()
    ]

    return word_counts


def sort_top_words(counts: list[dict], limit: int = 10) -> list[dict]:
    """
    Sort word counts in the form [{"word": <word>, "count": <count>, ...}] by count descending,
    then by word in ascending lexicographic order, keeping only the top limit words.

    Args:
        counts: Word counts in the form [{"word": <word>, "count": <count>, ...}].
        limit: The number of top word counts to keep.

    Preconditions:
        - limit >= 0

    Returns:
        Top word counts in the form [{"word": <word>, "count": <count>, ...}].
    """
    if limit < 1:
        raise ValueError(f"limit must be >= 0, but received limit of {limit}")

    sorted_counts = sorted(counts, key=lambda x: (-x["count"], x["word"]))
    sorted_counts = sorted_counts[:limit]

    return sorted_counts


def compute_text_stats(
    text: str,
    lowercase: bool = False,
    min_length: int = 1,
    top_words_limit: int | None = None,
) -> dict:
    """
    Summarizes line and word statistics for a text.

    Args:
        text: The text to summarize.
        lowercase: If True, all letters are first converted to lowercase before tokenization.
        min_length: The minimum length of token to keep.
        top_words_limit: The number of top word counts to keep. If None, top words list is empty.

    Preconditions:
        - min_length > 0
        - top_words_limit >= 0 (if provided)

    Returns:
        A dictionary summarizing line and word statistics for text.

        Keys:
            "line_count" (int): The number of lines in text.
            "nonempty_line_count" (int): The number of lines in text containing non-whitespace
                characters.
            "character_count" (int): The number of characters in text.
            "word_count" (int): The number of words in text of length at least min_length.
            "unique_word_count" (int): The number of unique words in text of length at least min_length.
            "lowercase" (bool): True if lowercase option was requested.
            "min_length" (int): The minimum length of word that was counted for word statistics.
            "top_words_limit" (int | None): The max number of words to return in top_words. If
                None, top_words is empty.
            "top_words" (list[dict]): A list of the most frequent words in text in the form
                [{"word": <word>, "count": <count>, ...}], sorted by count descending, then in
                ascending lexicographic order.
    """
    lines = text.splitlines()
    nonempty_lines = [line for line in lines if line.strip() != ""]

    line_count = len(lines)
    nonempty_line_count = len(nonempty_lines)
    character_count = len(text)

    tokens = tokenize(text, lowercase=lowercase)
    filtered_tokens = filter_min_length(tokens, min_length=min_length)

    word_count = len(filtered_tokens)
    word_counts = count_words(filtered_tokens)
    unique_word_count = len(word_counts)

    if top_words_limit is not None:
        top_words = sort_top_words(word_counts, limit=top_words_limit)
    else:
        top_words = []

    text_stats = {
        "line_count": line_count,
        "nonempty_line_count": nonempty_line_count,
        "character_count": character_count,
        "word_count": word_count,
        "unique_word_count": unique_word_count,
        "lowercase": lowercase,
        "min_length": min_length,
        "top_words_limit": top_words_limit,
        "top_words": top_words,
    }

    return text_stats


def format_text_stats(stats: dict, format: str = "text") -> str:
    """
    Format text stats into a displayable form.

    Args:
        stats: A text stats dictionary.
        format: The output format - 'text' or 'json'.

    Preconditions:
        - 'stats' must contain line_count, nonempty_line_count, character_count, word_count,
          unique_word_count, lowercase, min_length, top_words_limit, and top_words fields.
        - 'format' must be either 'text' or 'json'.

    Returns:
        A formatted representation of the text stats.
    """

    if format == "text":
        formatted_text = (
            f"Text statistics\n---------------\n"
            f"Lines: {stats['line_count']}\n"
            f"Nonempty lines: {stats['nonempty_line_count']}\n"
            f"Characters: {stats['character_count']}\n"
            f"Words: {stats['word_count']}\n"
            f"Unique words: {stats['unique_word_count']}\n"
        )

        if stats["top_words_limit"] is not None:
            top_words_header = "\nTop words:\n"

            formatted_top_words = ""

            for word_count in stats["top_words"]:
                formatted_top_words += f"{word_count['count']}  {word_count['word']}\n"

            if formatted_top_words == "":
                formatted_top_words = "(none)\n"

            formatted_text = formatted_text + top_words_header + formatted_top_words

        return formatted_text
    elif format == "json":
        return json.dumps(stats, indent=2)
    else:
        raise ValueError(f"format must be 'text' or 'json', but received {format!r}")


def read_text_file(path: Path) -> str:
    """
    Read text from file, interpreted as UTF-8.

    Args:
        path: Path to file to read.

    Returns:
        The text in the file pointed to by 'path', where file text is interpreted as UTF-8.
    """
    text = path.read_text(encoding="utf-8")

    return text


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compute simple statistics for a text file"
    )

    parser.add_argument(
        "--input", required=True, metavar="PATH", help="input file path"
    )
    parser.add_argument(
        "--top-words", type=int, metavar="N", help="show the top N words"
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=1,
        metavar="N",
        help="ignore tokens shorter than N characters",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        metavar="TEXT|JSON",
        help="output format",
    )
    parser.add_argument(
        "--lowercase",
        action="store_true",
        help="convert all letters to lowercase if flag provided",
    )

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    input_path = Path(args.input)

    try:
        text = read_text_file(input_path)
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"error: input path is not a file: {args.input}", file=sys.stderr)
        return 1
    except PermissionError:
        print(
            f"error: don't have permission to open file: {args.input}", file=sys.stderr
        )
        return 1
    except UnicodeDecodeError:
        print(f"error: couldn't decode input as UTF-8: {args.input}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"error: couldn't read {args.input}: {e}", file=sys.stderr)
        return 1

    try:
        text_stats = compute_text_stats(
            text,
            lowercase=args.lowercase,
            min_length=args.min_length,
            top_words_limit=args.top_words,
        )
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    try:
        formatted_text_stats = format_text_stats(text_stats, format=args.format)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(formatted_text_stats)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
