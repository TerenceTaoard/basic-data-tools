import pytest

from scripts.textstats import count_words, filter_min_length, sort_top_words, tokenize


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


def test_sort_top_words_sorts_by_count_descending():
    word_counts = [
        {"word": "one", "count": 2},
        {"word": "two", "count": 2},
        {"word": "three", "count": 1},
        {"word": "four", "count": 3},
    ]

    sorted_word_counts = sort_top_words(word_counts)

    assert sorted_word_counts == [
        {"word": "four", "count": 3},
        {"word": "one", "count": 2},
        {"word": "two", "count": 2},
        {"word": "three", "count": 1},
    ]


def test_sort_top_words_sorts_by_lexicographic_ascending_on_ties():
    word_counts = [
        {"word": "ad", "count": 2},
        {"word": "ac", "count": 2},
        {"word": "ab", "count": 2},
    ]

    sorted_word_counts = sort_top_words(word_counts)

    assert sorted_word_counts == [
        {"word": "ab", "count": 2},
        {"word": "ac", "count": 2},
        {"word": "ad", "count": 2},
    ]


def test_sort_top_words_applies_limit_after_sorting():
    word_counts = [
        {"word": "one", "count": 2},
        {"word": "two", "count": 2},
        {"word": "three", "count": 1},
        {"word": "four", "count": 3},
    ]

    sorted_word_counts = sort_top_words(word_counts, 2)

    assert sorted_word_counts == [
        {"word": "four", "count": 3},
        {"word": "one", "count": 2},
    ]


def test_sort_top_words_requesting_more_words_than_exists_keeps_all_words():
    word_counts = [{"word": "one", "count": 1}, {"word": "two", "count": 2}]

    sorted_word_counts = sort_top_words(word_counts, 3)

    assert sorted_word_counts == [
        {"word": "two", "count": 2},
        {"word": "one", "count": 1},
    ]


def test_sort_top_words_empty_word_counts_returns_empty():
    word_counts = []

    sorted_word_counts = sort_top_words(word_counts)

    assert sorted_word_counts == []


def test_sort_top_words_nonpositive_limit_raises():
    word_counts = [{"word": "one", "count": 1}]

    with pytest.raises(ValueError, match="limit must be > 0, but received limit of 0"):
        sort_top_words(word_counts, 0)
