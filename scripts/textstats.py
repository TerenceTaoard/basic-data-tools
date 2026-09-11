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
