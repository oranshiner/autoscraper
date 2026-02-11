"""
Comprehensive tests for the utils module.

Tests cover all utility functions including:
- unique_stack_list
- unique_hashable
- get_non_rec_text
- normalize
- text_match
- ResultItem class
- FuzzyText class
"""
import re
import unicodedata
from unittest.mock import MagicMock

import pytest

from autoscraper.utils import (
    FuzzyText,
    ResultItem,
    get_non_rec_text,
    normalize,
    text_match,
    unique_hashable,
    unique_stack_list,
)


class TestUniqueStackList:
    """Tests for unique_stack_list function."""

    def test_removes_duplicate_stacks(self):
        """Test that duplicate stacks with same hash are removed."""
        stack1 = {"hash": "abc123", "content": [("div", {})]}
        stack2 = {"hash": "def456", "content": [("span", {})]}
        stack3 = {"hash": "abc123", "content": [("div", {})]}  # duplicate

        stack_list = [stack1, stack2, stack3]
        result = unique_stack_list(stack_list)

        assert len(result) == 2
        assert result[0] == stack1
        assert result[1] == stack2

    def test_preserves_order(self):
        """Test that order of first occurrence is preserved."""
        stack1 = {"hash": "aaa", "content": []}
        stack2 = {"hash": "bbb", "content": []}
        stack3 = {"hash": "ccc", "content": []}
        stack4 = {"hash": "bbb", "content": []}  # duplicate of stack2

        stack_list = [stack1, stack2, stack3, stack4]
        result = unique_stack_list(stack_list)

        assert len(result) == 3
        assert [s["hash"] for s in result] == ["aaa", "bbb", "ccc"]

    def test_empty_list(self):
        """Test with empty list."""
        result = unique_stack_list([])
        assert result == []

    def test_single_item(self):
        """Test with single item."""
        stack = {"hash": "xyz", "content": []}
        result = unique_stack_list([stack])
        assert result == [stack]


class TestUniqueHashable:
    """Tests for unique_hashable function."""

    def test_removes_duplicates(self):
        """Test that duplicates are removed."""
        items = ["apple", "banana", "apple", "orange", "banana"]
        result = unique_hashable(items)
        assert result == ["apple", "banana", "orange"]

    def test_preserves_order(self):
        """Test that order of first occurrence is preserved."""
        items = ["z", "a", "m", "a", "z"]
        result = unique_hashable(items)
        assert result == ["z", "a", "m"]

    def test_empty_list(self):
        """Test with empty list."""
        result = unique_hashable([])
        assert result == []

    def test_no_duplicates(self):
        """Test list with no duplicates."""
        items = ["a", "b", "c"]
        result = unique_hashable(items)
        assert result == ["a", "b", "c"]

    def test_all_duplicates(self):
        """Test list with all same elements."""
        items = ["same", "same", "same"]
        result = unique_hashable(items)
        assert result == ["same"]

    def test_with_numbers(self):
        """Test with numeric items."""
        items = [1, 2, 1, 3, 2, 4]
        result = unique_hashable(items)
        assert result == [1, 2, 3, 4]


class TestGetNonRecText:
    """Tests for get_non_rec_text function."""

    def test_extracts_direct_text_only(self):
        """Test that only direct text is extracted, not from children."""
        element = MagicMock()
        element.find_all.return_value = ["Direct text", " more "]

        result = get_non_rec_text(element)

        assert result == "Direct text more"
        element.find_all.assert_called_once_with(text=True, recursive=False)

    def test_strips_whitespace(self):
        """Test that whitespace is properly stripped."""
        element = MagicMock()
        element.find_all.return_value = ["  text  ", "  more  "]

        result = get_non_rec_text(element)

        # Joining preserves internal whitespace from both strings
        assert result == "text    more"

    def test_empty_element(self):
        """Test with element that has no text."""
        element = MagicMock()
        element.find_all.return_value = []

        result = get_non_rec_text(element)

        assert result == ""


class TestNormalize:
    """Tests for normalize function."""

    def test_normalizes_unicode(self):
        """Test that unicode is normalized using NFKD."""
        # Using combining characters
        text = "café"  # e with acute accent
        result = normalize(text)
        # NFKD decomposes characters
        expected = unicodedata.normalize("NFKD", "café")
        assert result == expected

    def test_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        text = "  hello world  "
        result = normalize(text)
        assert result == "hello world"

    def test_handles_non_strings(self):
        """Test that non-string items are returned as-is."""
        assert normalize(123) == 123
        assert normalize(None) is None
        assert normalize([]) == []

    def test_empty_string(self):
        """Test with empty string."""
        result = normalize("")
        assert result == ""

    def test_unicode_whitespace(self):
        """Test with various unicode whitespace."""
        text = "\u00A0hello\u00A0"  # non-breaking spaces
        result = normalize(text)
        assert result.strip() == "hello"


class TestTextMatch:
    """Tests for text_match function."""

    def test_exact_match_with_ratio_1(self):
        """Test exact string matching when ratio is 1.0."""
        assert text_match("hello", "hello", 1.0) is True
        assert text_match("hello", "world", 1.0) is False

    def test_fuzzy_match_with_partial_ratio(self):
        """Test fuzzy matching with ratio < 1.0."""
        # "hello" and "helo" should match with low ratio
        assert text_match("hello", "helo", 0.8) is True
        # Very different strings shouldn't match even with low ratio
        assert text_match("hello", "xyz", 0.8) is False

    def test_regex_pattern_matching(self):
        """Test matching with compiled regex pattern."""
        pattern = re.compile(r"test\d+")
        assert text_match(pattern, "test123", 1.0) is True
        assert text_match(pattern, "test", 1.0) is False
        assert text_match(pattern, "other", 1.0) is False

    def test_case_sensitive_matching(self):
        """Test that matching is case sensitive by default."""
        assert text_match("Hello", "hello", 1.0) is False

    def test_zero_ratio(self):
        """Test with ratio of 0 - everything should match."""
        assert text_match("any", "thing", 0.0) is True

    def test_high_similarity_threshold(self):
        """Test with high similarity threshold."""
        # Similar strings
        assert text_match("testing", "testin", 0.9) is True
        # Different strings
        assert text_match("testing", "other", 0.9) is False


class TestResultItem:
    """Tests for ResultItem class."""

    def test_initialization(self):
        """Test ResultItem initialization."""
        item = ResultItem("test text", 5)
        assert item.text == "test text"
        assert item.index == 5

    def test_string_representation(self):
        """Test __str__ method returns text."""
        item = ResultItem("content", 10)
        assert str(item) == "content"

    def test_with_various_types(self):
        """Test ResultItem with various data types."""
        # String text
        item1 = ResultItem("string", 0)
        assert item1.text == "string"

        # None text
        item2 = ResultItem(None, 1)
        assert item2.text is None

        # Numeric text
        item3 = ResultItem(123, 2)
        assert item3.text == 123


class TestFuzzyText:
    """Tests for FuzzyText class."""

    def test_initialization(self):
        """Test FuzzyText initialization."""
        fuzzy = FuzzyText("test", 0.8)
        assert fuzzy.text == "test"
        assert fuzzy.ratio_limit == 0.8
        assert fuzzy.match is None

    def test_search_exact_match(self):
        """Test search with exact match."""
        fuzzy = FuzzyText("hello", 1.0)
        assert fuzzy.search("hello") is True
        assert fuzzy.search("world") is False

    def test_search_fuzzy_match(self):
        """Test search with fuzzy matching."""
        fuzzy = FuzzyText("testing", 0.8)
        # Close match should succeed
        assert fuzzy.search("testin") is True
        # Very different should fail
        assert fuzzy.search("xyz") is False

    def test_search_partial_similarity(self):
        """Test search with various similarity levels."""
        fuzzy = FuzzyText("python", 0.7)
        # High similarity
        assert fuzzy.search("python") is True
        assert fuzzy.search("pythons") is True
        # Medium similarity
        assert fuzzy.search("pyton") is True
        # Low similarity
        assert fuzzy.search("abc") is False

    def test_case_sensitive_search(self):
        """Test that search is case sensitive."""
        fuzzy = FuzzyText("Hello", 1.0)
        assert fuzzy.search("Hello") is True
        assert fuzzy.search("hello") is False

    def test_low_ratio_threshold(self):
        """Test with very low ratio threshold."""
        fuzzy = FuzzyText("test", 0.3)
        # Should match many strings with low threshold
        assert fuzzy.search("test") is True
        assert fuzzy.search("tst") is True
        assert fuzzy.search("t") is True


class TestEdgeCases:
    """Tests for edge cases and corner scenarios."""

    def test_normalize_with_combined_unicode(self):
        """Test normalize with complex unicode combinations."""
        # Emoji with combining characters
        text = "Hello 👋🏻"
        result = normalize(text)
        assert isinstance(result, str)

    def test_text_match_with_empty_strings(self):
        """Test text_match with empty strings."""
        assert text_match("", "", 1.0) is True
        assert text_match("hello", "", 1.0) is False
        assert text_match("", "hello", 1.0) is False

    def test_fuzzy_text_with_special_characters(self):
        """Test FuzzyText with special characters."""
        fuzzy = FuzzyText("test@#$%", 0.8)
        assert fuzzy.search("test@#$%") is True
        assert fuzzy.search("test@#$") is True

    def test_unique_hashable_with_none_values(self):
        """Test unique_hashable with None values."""
        items = ["a", None, "b", None, "a"]
        result = unique_hashable(items)
        assert result == ["a", None, "b"]

    def test_result_item_with_empty_string(self):
        """Test ResultItem with empty string."""
        item = ResultItem("", 0)
        assert item.text == ""
        assert str(item) == ""
