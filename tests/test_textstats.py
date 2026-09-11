import pytest

from scripts.textstats import tokenize


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
