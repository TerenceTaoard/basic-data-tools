import pytest

from scripts.textstats import count_words, filter_min_length, tokenize


def test_tokenize_tokenizes_basic_text():
    text = "Hello, world!"

    tokens = tokenize(text)

    assert tokens == ["Hello", "world"]


def test_tokenize_includes_apostrophe():
    text = "don't"

    tokens = tokenize(text)

    assert tokens == ["don't"]


def test_tokenize_includes_hyphens():
    text = "e-mail, state-of-the-art, rock--roll"

    tokens = tokenize(text)

    assert tokens == ["e-mail", "state-of-the-art", "rock--roll"]


def test_tokenize_includes_digits():
    text = "3.14"

    tokens = tokenize(text)

    assert tokens == ["3", "14"]


def test_tokenize_supports_unicode():
    text = "café"

    tokens = tokenize(text)

    assert tokens == ["café"]


def test_tokenize_preserves_case_by_default():
    text = "What what"

    tokens = tokenize(text)

    assert tokens == ["What", "what"]


def test_tokenize_lowercases_when_requested():
    text = "What WHAT"

    tokens = tokenize(text, lowercase=True)

    assert tokens == ["what", "what"]


def test_filter_min_length_default_length_keeps_one_character_tokens():
    tokens = ["what", "a", "day"]

    filtered_tokens = filter_min_length(tokens)

    assert filtered_tokens == ["what", "a", "day"]


def test_filter_min_length_shorter_tokens_removed():
    tokens = ["what", "a", "day"]

    filtered_tokens = filter_min_length(tokens, 3)

    assert filtered_tokens == ["what", "day"]


def test_filter_min_length_tokens_at_threshold_retained():
    tokens = ["it", "is"]

    filtered_tokens = filter_min_length(tokens, 2)

    assert filtered_tokens == ["it", "is"]


def test_filter_min_length_all_tokens_may_be_removed():
    tokens = ["what", "a", "day"]

    filtered_tokens = filter_min_length(tokens, 5)

    assert filtered_tokens == []


def test_filter_min_length_nonpositive_min_length_raises():
    tokens = ["hi"]

    with pytest.raises(
        ValueError, match="min_length must be > 0, but received min_length of 0"
    ):
        filter_min_length(tokens, 0)


def test_count_words_no_tokens_returns_empty_list():
    tokens = []

    word_counts = count_words(tokens)

    assert word_counts == []


def test_count_words_counts_repeated_words():
    tokens = ["one", "two", "one", "two", "three", "four"]

    word_counts = count_words(tokens)

    assert word_counts == [
        {"word": "one", "count": 2},
        {"word": "two", "count": 2},
        {"word": "three", "count": 1},
        {"word": "four", "count": 1},
    ]
