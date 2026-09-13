import json
import pytest

from pathlib import Path

from scripts.textstats import (
    compute_text_stats,
    count_words,
    filter_min_length,
    format_text_stats,
    read_text_file,
    sort_top_words,
    tokenize,
)


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


def test_sort_top_words_negative_limit_raises():
    word_counts = [{"word": "one", "count": 1}]

    with pytest.raises(
        ValueError, match="limit must be >= 0, but received limit of -1"
    ):
        sort_top_words(word_counts, -1)


def test_compute_text_stats_empty_string_gives_line_count_zero():
    text = ""

    text_stats = compute_text_stats(text)

    assert text_stats["line_count"] == 0


def test_compute_text_stats_counts_one_line():
    text = "hello"

    text_stats = compute_text_stats(text)

    assert text_stats["line_count"] == 1


def test_compute_text_stats_counts_one_line_with_newline():
    text = "hello\n"

    text_stats = compute_text_stats(text)

    assert text_stats["line_count"] == 1


def test_compute_text_stats_counts_two_lines():
    text = "hello\nworld"

    text_stats = compute_text_stats(text)

    assert text_stats["line_count"] == 2


def test_compute_text_stats_counts_blank_lines():
    text = "hello\n\nworld"

    text_stats = compute_text_stats(text)

    assert text_stats["line_count"] == 3


def test_compute_text_stats_counts_whitespace_only_lines_as_empty():
    text = "hello\n\nword"

    text_stats = compute_text_stats(text)

    assert text_stats["nonempty_line_count"] == 2


def test_compute_text_stats_punctuation_only_lines_as_nonempty():
    text = ".,"

    text_stats = compute_text_stats(text)

    assert text_stats["nonempty_line_count"] == 1


def test_compute_text_stats_counts_characters():
    text = "hello, world\n"

    text_stats = compute_text_stats(text)

    assert text_stats["character_count"] == 13


def test_compute_text_stats_counts_zero_characters_on_empty_text():
    text = ""

    text_stats = compute_text_stats(text)

    assert text_stats["character_count"] == 0


def test_compute_text_stats_case_differences_remain_separate_with_lowercasing():
    text = "hello Hello"

    text_stats = compute_text_stats(text, lowercase=True)

    assert text_stats["unique_word_count"] == 1


def test_compute_text_stats_case_differences_merge_without_lowercasing():
    text = "hello Hello"

    text_stats = compute_text_stats(text, lowercase=False)

    assert text_stats["unique_word_count"] == 2


def test_compute_text_stats_lowercasing_merges_counts():
    text = "hello Hello"

    text_stats = compute_text_stats(text, lowercase=True, top_words_limit=10)

    assert text_stats["top_words"] == [{"word": "hello", "count": 2}]


def test_compute_text_stats_word_counts_excludes_lengths_below_min_length():
    text = "This is an example\n\nAnd this example continues"

    text_stats = compute_text_stats(text, min_length=4)

    assert text_stats["word_count"] == 5


def test_compute_text_stats_computes_full_summary_correctly():
    text = "This is an example\n\nAnd this example continues"

    text_stats = compute_text_stats(
        text, lowercase=True, min_length=4, top_words_limit=3
    )

    assert text_stats == {
        "line_count": 3,
        "nonempty_line_count": 2,
        "character_count": 46,
        "word_count": 5,
        "unique_word_count": 3,
        "lowercase": True,
        "min_length": 4,
        "top_words_limit": 3,
        "top_words": [
            {"word": "example", "count": 2},
            {"word": "this", "count": 2},
            {"word": "continues", "count": 1},
        ],
    }


def test_format_text_stats_formats_text_correctly():
    text_stats = {
        "line_count": 4,
        "nonempty_line_count": 3,
        "character_count": 74,
        "word_count": 12,
        "unique_word_count": 9,
        "lowercase": True,
        "min_length": 1,
        "top_words_limit": None,
        "top_words": [],
    }

    formatted_text_stats = format_text_stats(text_stats, format="text")

    assert formatted_text_stats == (
        "Text statistics\n---------------\nLines: 4\nNonempty lines: 3\n"
        "Characters: 74\nWords: 12\nUnique words: 9\n"
    )


def test_format_text_stats_formats_top_words():
    text_stats = {
        "line_count": 4,
        "nonempty_line_count": 3,
        "character_count": 74,
        "word_count": 12,
        "unique_word_count": 9,
        "lowercase": True,
        "min_length": 1,
        "top_words_limit": 3,
        "top_words": [
            {"word": "python", "count": 3},
            {"word": "data", "count": 2},
            {"word": "file", "count": 2},
        ],
    }

    formatted_text_stats = format_text_stats(text_stats, format="text")

    assert formatted_text_stats == (
        "Text statistics\n---------------\nLines: 4\nNonempty lines: 3\n"
        "Characters: 74\nWords: 12\nUnique words: 9\n\nTop words:\n3  python\n2  data\n2  file\n"
    )


def test_format_text_stats_shows_none_when_top_words_requested_but_zero_words_remain():
    text_stats = {
        "line_count": 4,
        "nonempty_line_count": 3,
        "character_count": 74,
        "word_count": 12,
        "unique_word_count": 9,
        "lowercase": True,
        "min_length": 7,
        "top_words_limit": 3,
        "top_words": [],
    }

    formatted_text_stats = format_text_stats(text_stats, format="text")

    assert formatted_text_stats == (
        "Text statistics\n---------------\nLines: 4\nNonempty lines: 3\n"
        "Characters: 74\nWords: 12\nUnique words: 9\n\nTop words:\n(none)\n"
    )


def test_format_text_stats_json_formats_correctly():
    text_stats = {
        "line_count": 4,
        "nonempty_line_count": 3,
        "character_count": 74,
        "word_count": 12,
        "unique_word_count": 9,
        "lowercase": True,
        "min_length": 1,
        "top_words_limit": 3,
        "top_words": [
            {"word": "python", "count": 3},
            {"word": "data", "count": 2},
            {"word": "file", "count": 2},
        ],
    }

    formatted_text_stats = format_text_stats(text_stats, format="json")
    text_stats_from_json = json.loads(formatted_text_stats)

    assert text_stats_from_json["line_count"] == 4
    assert text_stats_from_json["nonempty_line_count"] == 3
    assert text_stats_from_json["character_count"] == 74
    assert text_stats_from_json["word_count"] == 12
    assert text_stats_from_json["unique_word_count"] == 9
    assert text_stats_from_json["lowercase"] == True
    assert text_stats_from_json["min_length"] == 1
    assert text_stats_from_json["top_words_limit"] == 3
    assert text_stats_from_json["top_words"] == [
        {"word": "python", "count": 3},
        {"word": "data", "count": 2},
        {"word": "file", "count": 2},
    ]


def test_format_text_stats_json_types_are_correct():
    text_stats = {
        "line_count": 4,
        "nonempty_line_count": 3,
        "character_count": 74,
        "word_count": 12,
        "unique_word_count": 9,
        "lowercase": True,
        "min_length": 1,
        "top_words_limit": 3,
        "top_words": [
            {"word": "python", "count": 3},
            {"word": "data", "count": 2},
            {"word": "file", "count": 2},
        ],
    }

    formatted_text_stats = format_text_stats(text_stats, format="json")
    text_stats_from_json = json.loads(formatted_text_stats)

    assert type(text_stats_from_json["line_count"]) == int
    assert type(text_stats_from_json["nonempty_line_count"]) == int
    assert type(text_stats_from_json["character_count"]) == int
    assert type(text_stats_from_json["word_count"]) == int
    assert type(text_stats_from_json["unique_word_count"]) == int
    assert type(text_stats_from_json["lowercase"]) == bool
    assert type(text_stats_from_json["min_length"]) == int
    assert type(text_stats_from_json["top_words_limit"]) == int
    assert type(text_stats_from_json["top_words"]) == list
    assert type(text_stats_from_json["top_words"][0]) == dict
    assert type(text_stats_from_json["top_words"][1]) == dict
    assert type(text_stats_from_json["top_words"][2]) == dict


def test_format_text_stats_json_with_top_words_limit_none_gives_null_limit_and_empty_list():
    text_stats = {
        "line_count": 4,
        "nonempty_line_count": 3,
        "character_count": 74,
        "word_count": 12,
        "unique_word_count": 9,
        "lowercase": True,
        "min_length": 1,
        "top_words_limit": None,
        "top_words": [],
    }

    formatted_text_stats = format_text_stats(text_stats, format="json")
    text_stats_from_json = json.loads(formatted_text_stats)

    assert text_stats_from_json["top_words_limit"] is None
    assert text_stats_from_json["top_words"] == []


def test_format_text_stats_invalid_format_raises():
    text_stats = {
        "line_count": 4,
        "nonempty_line_count": 3,
        "character_count": 74,
        "word_count": 12,
        "unique_word_count": 9,
        "lowercase": True,
        "min_length": 1,
        "top_words_limit": None,
        "top_words": [],
    }

    with pytest.raises(
        ValueError, match="format must be 'text' or 'json', but received 'csv'"
    ):
        format_text_stats(text_stats, format="csv")


def test_read_text_file_reads_text(tmp_path):
    input_path = tmp_path / "input.txt"
    input_path.write_text("hello\n", encoding="utf-8")

    text = read_text_file(input_path)

    assert text == "hello\n"
