import re


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
        - min_length >= 1

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


def sort_top_words(counts: list[dict], limit: int | None = None) -> list[dict]:
    """
    Sort word counts in the form [{"word": <word>, "count": <count>, ...}] by count descending,
    then by word in ascending lexicographic order, keeping only the top limit words.

    Args:
        counts: Word counts in the form [{"word": <word>, "count": <count>, ...}].
        limit: The number of top word counts to keep. If None, keep all words.

    Preconditions:
        - limit > 0

    Returns:
        Top word counts in the form [{"word": <word>, "count": <count>, ...}].
    """
    if limit is not None and limit < 1:
        raise ValueError(f"limit must be > 0, but received limit of {limit}")

    sorted_counts = sorted(counts, key=lambda x: (-x["count"], x["word"]))

    if limit is not None:
        sorted_counts = sorted_counts[:limit]

    return sorted_counts
